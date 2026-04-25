# 設計: summary-notification の資産情報取得元を Google Spreadsheet に変更

## 変更概要

summary-notification Lambda の資産情報取得元を S3 から Google Spreadsheet に切り替える。
`IAssetRepository` インターフェースはそのまま維持し、Infrastructure 層の実装を差し替える。

---

## 変更対象と方針

### 1. shared パッケージ: `BaseEnvSettings` から `data_bucket_name` を除外

**対象ファイル**: `lambda/shared/src/shared/config/base_settings.py`

`data_bucket_name` は web-scraping でのみ使用するため、shared から除外し web-scraping のローカル設定に移動する。

**変更前**:

```python
class BaseEnvSettings(BaseSettings):
    powertools_log_level: str = "INFO"
    data_bucket_name: str  # ← 除外
```

**変更後**:

```python
class BaseEnvSettings(BaseSettings):
    powertools_log_level: str = "INFO"
```

web-scraping 側の `EnvSettings` に `data_bucket_name` を追加:

```python
class EnvSettings(BaseEnvSettings):
    user_agent: str = "..."
    scraping_parameter_name: str
    spreadsheet_parameter_name: str
    data_bucket_name: str  # ← 追加
```

### 2. summary-notification Infrastructure 層: `GoogleSheetAssetRepository` の新規作成

**新規ファイル**: `lambda/summary-notification/src/infrastructure/google_sheet_asset_repository.py`

web-scraping の `GoogleSheetAssetRecordRepository`（書き込み用）とは異なり、読み取り専用のリポジトリ。
`IAssetRepository` を実装し、スプレッドシートから最新日付のレコードを取得して `DcpAssets` に変換する。

**データ取得の最適化**: 全レコード取得ではなく、date 列のみ先に取得して最新日付を特定し、該当行のみ取得する。

```python
class GoogleSheetAssetRepository(IAssetRepository):
    HEADER_ROW = 1

    def __init__(self, spreadsheet_id: str, sheet_name: str, credentials: dict) -> None:
        creds = Credentials.from_service_account_info(credentials, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(spreadsheet_id)
        self.worksheet = spreadsheet.worksheet(sheet_name)

    def get_latest_assets(self) -> DcpAssets:
        """最新日付の資産レコードを取得し DcpAssets に変換する

        1. date 列のみ取得し、最新日付と該当行番号を特定
        2. 該当行のデータのみ取得
        3. DcpAssets に変換（total は全商品の合算）
        """
        headers = self.worksheet.row_values(self.HEADER_ROW)
        date_col = headers.index("date") + 1
        date_values = self.worksheet.col_values(date_col)
        data_dates = date_values[self.HEADER_ROW:]  # ヘッダー行を除外

        if not data_dates:
            raise AssetNotFound.no_assets_in_spreadsheet()

        latest_date = max(data_dates)

        # 最新日付の行番号を特定（1-indexed、ヘッダー行分 +1）
        target_rows = [
            i + self.HEADER_ROW + 1
            for i, d in enumerate(data_dates)
            if d == latest_date
        ]

        # 該当行のみ取得（batch_get で API 呼び出しを最小化）
        num_cols = len(headers)
        end_col = chr(ord("A") + num_cols - 1)
        ranges = [f"A{row}:{end_col}{row}" for row in target_rows]
        results = self.worksheet.batch_get(ranges)
        rows = [dict(zip(headers, row[0])) for row in results]

        return self._to_dcp_assets(rows)

    def _to_dcp_assets(self, rows: list[dict]) -> DcpAssets:
        """フラットレコードから DcpAssets を構築する（total は全商品の合算）"""
        products: dict[str, DcpAssetInfo] = {}
        total_contributions = 0
        total_gains = 0
        total_valuation = 0

        for row in rows:
            info = DcpAssetInfo(
                asset_valuation=int(row["asset_valuation"]),
                cumulative_contributions=int(row["cumulative_contributions"]),
                gains_or_losses=int(row["gains_or_losses"]),
            )
            products[row["product"]] = info
            total_contributions += info.cumulative_contributions
            total_gains += info.gains_or_losses
            total_valuation += info.asset_valuation

        total = DcpAssetInfo(
            cumulative_contributions=total_contributions,
            gains_or_losses=total_gains,
            asset_valuation=total_valuation,
        )
        return DcpAssets(total=total, products=products)
```

### 3. summary-notification Domain 層: 例外の更新

**対象ファイル**: `lambda/summary-notification/src/domain/exceptions.py`

`AssetNotFound` の名前付きコンストラクタを S3 固有のものからスプレッドシート用に変更する。

**変更前**:

```python
class AssetNotFound(SummaryNotificationFailed):
    @classmethod
    def no_assets_in_bucket(cls) -> Self:
        return cls("S3 バケットに資産情報が見つかりません")
```

**変更後**:

```python
class AssetNotFound(SummaryNotificationFailed):
    @classmethod
    def no_assets_in_spreadsheet(cls) -> Self:
        return cls("スプレッドシートに資産情報が見つかりません")
```

### 4. summary-notification Config 層: 設定の更新

**対象ファイル**: `lambda/summary-notification/src/config/settings.py`

スプレッドシートパラメータ名を追加する。`BaseEnvSettings` から `data_bucket_name` が除去されるため、S3 関連の設定は不要。

**変更後**:

```python
class EnvSettings(BaseEnvSettings):
    line_message_parameter_name: str
    spreadsheet_parameter_name: str  # 追加
```

### 5. summary-notification Presentation 層: DI の更新

**対象ファイル**: `lambda/summary-notification/src/presentation/summary_notification_handler.py`

`S3AssetRepository` を `GoogleSheetAssetRepository` に差し替える。

**変更後**:

```python
from src.infrastructure import (
    GoogleSheetAssetRepository,
    LineNotifier,
    get_ssm_json_parameter,
)

def main(
    asset_repository: IAssetRepository | None = None,
    notifier: INotifier | None = None,
) -> None:
    if asset_repository is None:
        spreadsheet_parameter = get_ssm_json_parameter(
            name=settings.spreadsheet_parameter_name, decrypt=True
        )
        asset_repository = GoogleSheetAssetRepository(
            spreadsheet_id=spreadsheet_parameter["spreadsheet_id"],
            sheet_name=spreadsheet_parameter["sheet_name"],
            credentials=spreadsheet_parameter["credentials"],
        )
    # ...
```

### 6. summary-notification Infrastructure `__init__.py` の更新

**対象ファイル**: `lambda/summary-notification/src/infrastructure/__init__.py`

`S3AssetRepository` を `GoogleSheetAssetRepository` に差し替える。

```python
from .google_sheet_asset_repository import GoogleSheetAssetRepository
from .line_notifier import LineNotifier

__all__ = [
    "GoogleSheetAssetRepository",
    "LineNotifier",
    "get_ssm_json_parameter",
]
```

### 7. S3AssetRepository の削除

**削除ファイル**: `lambda/summary-notification/src/infrastructure/s3_asset_repository.py`

S3 依存を完全に除去する。

### 8. summary-notification の依存関係更新

**対象ファイル**: `lambda/summary-notification/pyproject.toml`

- `gspread` と `google-auth` を dependencies に追加
- `testcontainers[localstack]` を dev dependencies から削除
- `botocore[crt]` を dev dependencies から削除（S3 不要のため）
- `pytest.ini_options.env` から `DATA_BUCKET_NAME` を削除し、`SPREADSHEET_PARAMETER_NAME` を追加

### 9. テストの更新

**削除ファイル**:
- `lambda/summary-notification/tests/infrastructure/test_s3_asset_repository.py`
- `lambda/summary-notification/tests/conftest.py`（LocalStack 依存を除去、ファイル自体を削除）

**変更ファイル**:
- 他テストファイル内で `AssetNotFound.no_assets_in_bucket()` を使用していた箇所を `no_assets_in_spreadsheet()` に更新
- `tests/fixtures/mocks/mock_asset_repository.py` の例外メッセージ更新

### 10. CDK スタックの更新

**対象ファイル**: `lib/dcp-ops-monitor-stack.ts`

summary-notification Lambda の設定変更:

- 環境変数: `DATA_BUCKET_NAME` を削除し、`SPREADSHEET_PARAMETER_NAME` を追加
- IAM: S3 権限（`s3:GetObject`, `s3:ListBucket`）を削除し、SSM の `spreadsheetParameter` への `ssm:GetParameter` 権限を追加

```typescript
environment: {
  POWERTOOLS_SERVICE_NAME: 'summary-notification',
  POWERTOOLS_LOG_LEVEL: props.logLevel,
  LINE_MESSAGE_PARAMETER_NAME: lineMessageParameter.parameterName,
  SPREADSHEET_PARAMETER_NAME: spreadsheetParameter.parameterName,  // 追加
  // DATA_BUCKET_NAME 削除
},
```

```typescript
summaryNotificationFunction.addToRolePolicy(
  new iam.PolicyStatement({
    actions: ['ssm:GetParameter'],
    resources: [lineMessageParameter.parameterArn, spreadsheetParameter.parameterArn],  // spreadsheet 追加
  }),
);
// S3 権限の PolicyStatement を削除
```

### 11. ドキュメント更新

**対象ファイル**: `docs/functional-design.md`

- サマリ通知機能のシーケンス図を更新（S3 → Google Spreadsheet）
- 使用する AWS サービスから S3 を削除し、外部サービスに Google Spreadsheet を追加
- インターフェース設計の `IAssetRepository` 説明を更新

---

## 影響範囲

### 変更なし（影響を受けない）

- `IAssetRepository` インターフェース（メソッドシグネチャ不変）
- `SummaryNotificationService`（Application 層）
- `indicators_calculator.py`, `message_formatter.py`
- `LineNotifier`
- `INotifier` インターフェース
- shared の `IAssetRecordRepository`, `AssetRecord`, `DcpAssetInfo`
- web-scraping Lambda（`data_bucket_name` を EnvSettings に移動する変更のみ）

### 追加される依存

- `gspread>=6.0.0` — summary-notification の dependencies
- `google-auth>=2.0.0` — summary-notification の dependencies

### 除去される依存

- `testcontainers[localstack]` — summary-notification の dev dependencies
- `botocore[crt]` — summary-notification の dev dependencies
