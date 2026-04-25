# 設計: 資産情報蓄積方式の見直し

## 概要

現在の S3 JSON 日次ファイル保存を、BI ツールで可視化しやすいフラットなレコード形式での蓄積に置き換える。
データストアは Google Spreadsheet とし、将来 CSV / DynamoDB 等への切り替えが可能な設計とする。

---

## shared パッケージ変更

### DcpAssets の廃止

`shared/domain/asset_object.py` から `DcpAssets` クラスを削除する。`DcpAssetInfo` はそのまま残す。

### AssetRecord（新規: `shared/domain/asset_record_object.py`）

商品別のフラットなレコードモデル。

```python
class AssetRecord(BaseModel):
    date: date
    product: str
    asset_valuation: int
    cumulative_contributions: int
    gains_or_losses: int

    @staticmethod
    def from_dcp_asset_products(
        target_date: date,
        products: dict[str, DcpAssetInfo],
    ) -> list[AssetRecord]:
        """商品別 DcpAssetInfo から AssetRecord のリストを生成する"""
```

### IAssetRecordRepository（新規: `shared/domain/asset_record_interface.py`）

CSV / Google Spreadsheet / DynamoDB 等に対応可能な共通インターフェース。

```python
class IAssetRecordRepository(ABC):
    @abstractmethod
    def save_daily_records(self, records: list[AssetRecord]) -> None:
        """日次の資産レコードを保存する

        冪等性を保証する。同一日付のレコードが既に存在する場合は
        既存レコードを削除してから保存する（upsert セマンティクス）。

        Raises:
            AssetRecordError: レコード保存失敗時
        """
```

### AssetRecordError（新規: `shared/domain/exceptions.py`）

```python
class AssetRecordError(Exception):
    """資産レコード操作の例外"""
```

---

## web-scraping 変更

### IScraper 戻り値の変更

`DcpAssets` → `dict[str, DcpAssetInfo]`（商品別のみ、total 廃止）。

```python
class IScraper(ABC):
    @abstractmethod
    def fetch_asset_valuation(self) -> dict[str, DcpAssetInfo]:
        """資産評価情報を取得する"""
```

- `SeleniumScraper`: total の抽出を除外し、products のみ返却するよう変更
- `WebScrapingService.scrape()`: 戻り値を `dict[str, DcpAssetInfo]` に変更
- `extraction_object.py`: `DcpAssets` のインポート・エクスポートを削除

### IArtifactRepository の変更

`save_assets` メソッドを削除。エラーアーティファクト保存のみの責務とする。

```python
class IArtifactRepository(ABC):
    @abstractmethod
    def save_error_artifact(self, key: str, file_path: str) -> None:
        """エラーアーティファクトを保存する"""
```

`S3ArtifactRepository` からも `save_assets` を削除。

### GoogleSheetAssetRecordRepository（新規）

`web-scraping/infrastructure/google_sheet_asset_record_repository.py`

```python
class GoogleSheetAssetRecordRepository(IAssetRecordRepository):
    def __init__(self, spreadsheet_id: str, sheet_name: str, credentials: dict) -> None:
        """Google Spreadsheet クライアントを初期化"""

    def save_daily_records(self, records: list[AssetRecord]) -> None:
        """日次の資産レコードをスプレッドシートに保存する

        冪等性の実現方法:
        1. シート内から対象日付の既存行を検索（date カラム一致）
        2. 既存行があれば削除
        3. 新しいレコードを末尾に追記
        """
```

**ライブラリ**: `gspread` + `google-auth`

**認証**: サービスアカウント JSON を SSM Parameter Store から取得

**SSM パラメータ構造**:

```json
{
  "spreadsheet_id": "スプレッドシートID",
  "sheet_name": "シート名",
  "credentials": {
    "type": "service_account",
    "project_id": "...",
    "private_key": "...",
    ...
  }
}
```

**スプレッドシート前提**:

- ヘッダ行が事前設定済み: `date | product | asset_valuation | cumulative_contributions | gains_or_losses`
- サービスアカウントに編集権限が付与済み

### EnvSettings

```python
class EnvSettings(BaseEnvSettings):
    user_agent: str = "..."
    scraping_parameter_name: str
    spreadsheet_parameter_name: str  # 追加
```

### asset_collection_handler（Presentation 層）

`IAssetRecordRepository` を DI し、スクレイピング後にレコードを追記する。

```python
def main(
    scraper: Optional[IScraper] = None,
    asset_record_repository: Optional[IAssetRecordRepository] = None,
) -> None:
    # ... scraper setup (既存)

    artifact_repository = S3ArtifactRepository(settings.data_bucket_name)

    if asset_record_repository is None:
        spreadsheet_param = get_ssm_json_parameter(
            name=settings.spreadsheet_parameter_name, decrypt=True
        )
        asset_record_repository = GoogleSheetAssetRecordRepository(
            spreadsheet_id=spreadsheet_param["spreadsheet_id"],
            sheet_name=spreadsheet_param["sheet_name"],
            credentials=spreadsheet_param["credentials"],
        )

    web_scraping_service = WebScrapingService(
        scraper=scraper,
        artifact_repository=artifact_repository,
    )
    products = web_scraping_service.scrape()

    today = datetime.now(ZoneInfo("Asia/Tokyo")).date()
    records = AssetRecord.from_dcp_asset_products(target_date=today, products=products)
    asset_record_repository.save_daily_records(records)
```

### handler.py

`AssetRecordError` のキャッチを追加。

### 依存関係の追加（pyproject.toml）

```toml
dependencies = [
    "shared",
    "selenium>=4.33.0",
    "gspread>=6.0.0",        # 追加
    "google-auth>=2.0.0",    # 追加
]
```

---

## summary-notification 最低限修正

shared から `DcpAssets` が削除されるため、summary-notification のローカルに移動する。

### 新規: `summary-notification/src/domain/asset_object.py`

```python
from pydantic import BaseModel
from shared.domain.asset_object import DcpAssetInfo


class DcpAssets(BaseModel):
    """資産情報（総評価 + 商品別）"""
    total: DcpAssetInfo
    products: dict[str, DcpAssetInfo]
```

### 変更: `summary-notification/src/domain/__init__.py`

```python
# 変更前
from shared.domain.asset_object import DcpAssetInfo, DcpAssets

# 変更後
from shared.domain.asset_object import DcpAssetInfo
from .asset_object import DcpAssets
```

application 層・infrastructure 層は `src.domain` 経由でインポートしているため変更不要。

---

## CDK スタック変更

- SSM パラメータ参照（`SpreadsheetParameter`）を追加
- web-scraping Lambda に環境変数 `SPREADSHEET_PARAMETER_NAME` を追加
- SSM 読み取り権限を追加
- S3 バケット・PutObject 権限はエラーアーティファクト保存で引き続き必要

---

## ファイル構成（変更箇所）

```
lambda/
├── shared/src/shared/
│   └── domain/
│       ├── asset_object.py              # 変更: DcpAssets 削除
│       ├── asset_record_object.py       # 新規: AssetRecord モデル
│       ├── asset_record_interface.py    # 新規: IAssetRecordRepository
│       └── exceptions.py               # 新規: AssetRecordError
├── web-scraping/src/
│   ├── config/
│   │   └── settings.py                 # 変更: spreadsheet_parameter_name 追加
│   ├── domain/
│   │   ├── artifact_interface.py       # 変更: save_assets 削除
│   │   ├── extraction_object.py        # 変更: DcpAssets 参照削除
│   │   ├── scraping_interface.py       # 変更: 戻り値型変更
│   │   └── __init__.py                 # 変更: エクスポート更新
│   ├── application/
│   │   └── web_scraping_service.py     # 変更: 戻り値型変更
│   ├── infrastructure/
│   │   ├── s3_artifact_repository.py   # 変更: save_assets 削除
│   │   ├── google_sheet_asset_record_repository.py  # 新規
│   │   └── __init__.py                 # 変更: エクスポート追加
│   ├── presentation/
│   │   └── asset_collection_handler.py # 変更: DI・レコード追記処理
│   ├── handler.py                      # 変更: AssetRecordError キャッチ追加
│   └── pyproject.toml                  # 変更: gspread, google-auth 追加
├── summary-notification/src/
│   └── domain/
│       ├── asset_object.py             # 新規: DcpAssets ローカル定義
│       └── __init__.py                 # 変更: import 元変更
└── lib/dcp-ops-monitor-stack.ts        # 変更: SSM パラメータ・環境変数追加
```

---

## 注意事項

- 本変更により、S3 への資産情報 JSON 保存が停止する
- summary-notification Lambda は引き続き S3 から読み取るため、新しい日次データが取得できなくなる（既存データは残る）
- summary-notification の本格改修は別タスクで対応する
