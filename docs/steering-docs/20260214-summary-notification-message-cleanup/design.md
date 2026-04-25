# 設計: SummaryNotification 通知メッセージ整理

## 変更対象ファイル一覧

| レイヤー | ファイル | 変更内容 |
|---------|---------|---------|
| Domain | `asset_object.py` | `DcpAssets` から `total` 削除、`calculate_total()` 追加 |
| Domain | `asset_interface.py` | `IAssetRepository` に `get_weekly_assets()` 追加 |
| Domain | `indicator_object.py` | `DcpOpsIndicators` から `expected_yield_rate` 削除 |
| Application | `indicators_calculator.py` | `EXPECTED_YIELD_RATE` 定数・戻り値から削除 |
| Application | `message_formatter.py` | メッセージフォーマットを再設計 |
| Application | `summary_notification_service.py` | 週次データ取得・資産評価額推移計算の追加 |
| Infrastructure | `google_sheet_asset_repository.py` | `get_weekly_assets()` 実装、`_to_dcp_assets` から total 算出削除 |
| Tests | 全テストファイル | 上記変更に追従 |
| Docs | `docs/functional-design.md` | データモデル・インターフェース・シーケンス図更新 |

## Domain 層の変更

### DcpAssets（asset_object.py）

`total` フィールドを削除し、products から算出するメソッドを追加する。

```python
class DcpAssets(BaseModel):
    """資産情報（商品別）"""
    products: dict[str, DcpAssetInfo]

    def calculate_total(self) -> DcpAssetInfo:
        """全商品の合計を算出する"""
        return DcpAssetInfo(
            cumulative_contributions=sum(p.cumulative_contributions for p in self.products.values()),
            gains_or_losses=sum(p.gains_or_losses for p in self.products.values()),
            asset_valuation=sum(p.asset_valuation for p in self.products.values()),
        )
```

### IAssetRepository（asset_interface.py）

直近1週間のデータ取得メソッドを追加する。

```python
from datetime import date

class IAssetRepository(ABC):
    @abstractmethod
    def get_latest_assets(self) -> DcpAssets:
        """最新の資産情報を取得"""

    @abstractmethod
    def get_weekly_assets(self) -> dict[date, DcpAssets]:
        """直近1週間の資産情報を日付別に取得

        Returns:
            dict[date, DcpAssets]: 日付 → 資産情報のマッピング
            データが存在しない日は含まない
        """
```

### DcpOpsIndicators（indicator_object.py）

`expected_yield_rate` フィールドを削除する。

```python
class DcpOpsIndicators(BaseModel):
    operation_years: float
    actual_yield_rate: float
    total_amount_at_60age: int
```

## Application 層の変更

### indicators_calculator.py

- `EXPECTED_YIELD_RATE` 定数を削除
- `calculate_indicators()` の戻り値から `expected_yield_rate` を削除

### message_formatter.py

シグネチャと出力フォーマットを変更する。

```python
from datetime import date

def format_summary_message(
    total: DcpAssetInfo,
    indicators: DcpOpsIndicators,
    weekly_valuations: list[tuple[date, int, int | None]],
) -> str:
```

- `weekly_valuations`: `(日付, 資産評価額, 前日比 or None)` のリスト（新しい日付順）

**出力例:**

```
確定拠出年金 運用状況通知Bot

拠出金額累計: 900,000円
評価損益: 300,000円
資産評価額: 1,200,000円

運用年数: 9.34年
運用利回り: 0.036
想定受取額(60歳): 15,000,000円

資産評価額推移（直近1週間）
2026-02-14: 1,200,000円 +5,000円
2026-02-13: 1,195,000円 -2,000円
2026-02-12: 1,197,000円 +3,000円
2026-02-11: 1,194,000円 +1,000円
2026-02-10: 1,193,000円 -
```

### summary_notification_service.py

処理フローを変更する。

```python
def send_summary(self) -> None:
    # 1. 最新の資産情報を取得
    latest_assets = self.asset_repository.get_latest_assets()
    total = latest_assets.calculate_total()

    # 2. 運用指標を計算
    indicators = calculate_indicators(total)

    # 3. 直近1週間の資産評価額推移を取得・計算
    weekly_assets = self.asset_repository.get_weekly_assets()
    weekly_valuations = self._calculate_weekly_valuations(weekly_assets)

    # 4. メッセージフォーマット・送信
    message_text = format_summary_message(total, indicators, weekly_valuations)
    self.notifier.notify([NotificationMessage(text=message_text)])
```

`_calculate_weekly_valuations()` メソッドを追加:

```python
def _calculate_weekly_valuations(
    self, weekly_assets: dict[date, DcpAssets]
) -> list[tuple[date, int, int | None]]:
    """週次データから日毎の資産評価額と前日比を算出する

    Args:
        weekly_assets: 日付別の資産情報

    Returns:
        (日付, 資産評価額, 前日比 or None) のリスト（新しい日付順）
    """
    sorted_dates = sorted(weekly_assets.keys())
    result = []
    for i, d in enumerate(sorted_dates):
        valuation = weekly_assets[d].calculate_total().asset_valuation
        if i == 0:
            diff = None
        else:
            prev_valuation = weekly_assets[sorted_dates[i - 1]].calculate_total().asset_valuation
            diff = valuation - prev_valuation
        result.append((d, valuation, diff))
    return list(reversed(result))  # 新しい日付順
```

## Infrastructure 層の変更

### google_sheet_asset_repository.py

#### `_to_dcp_assets()` の変更

total 算出ロジックを削除し、products のみを構築する。

#### `get_weekly_assets()` の追加

```python
from datetime import date, timedelta

def get_weekly_assets(self) -> dict[date, DcpAssets]:
    """直近カレンダー7日分の資産情報を日付別に取得する"""
    headers = self.worksheet.row_values(self.HEADER_ROW)
    date_col = headers.index("date") + 1
    date_values = self.worksheet.col_values(date_col)
    data_dates = date_values[self.HEADER_ROW:]

    if not data_dates:
        return {}

    latest_date = max(data_dates)
    latest_dt = date.fromisoformat(latest_date)
    cutoff_dt = latest_dt - timedelta(days=7)

    target_dates = {d for d in data_dates if date.fromisoformat(d) > cutoff_dt}

    result: dict[date, DcpAssets] = {}
    num_cols = len(headers)
    for target_date in target_dates:
        target_rows = [i + self.HEADER_ROW + 1 for i, d in enumerate(data_dates) if d == target_date]
        ranges = [f"{rowcol_to_a1(row, 1)}:{rowcol_to_a1(row, num_cols)}" for row in target_rows]
        results = self.worksheet.batch_get(ranges)
        rows = [dict(zip(headers, row[0])) for row in results if row and row[0]]
        result[date.fromisoformat(target_date)] = self._to_dcp_assets(rows)

    return result
```

## 通知メッセージの変更（Before / After）

### Before

```
確定拠出年金 運用状況通知Bot

総評価
拠出金額累計: 900,000円
評価損益: 300,000円
資産評価額: 1,200,000円

運用年数: 9.34年
運用利回り: 0.036
目標利回り: 0.06
想定受取額(60歳): 15,000,000円

商品別
商品A
取得価額累計: 450,000円
損益: 150,000円
資産評価額: 600,000円

商品B
取得価額累計: 450,000円
損益: 150,000円
資産評価額: 600,000円
```

### After

```
確定拠出年金 運用状況通知Bot

拠出金額累計: 900,000円
評価損益: 300,000円
資産評価額: 1,200,000円

運用年数: 9.34年
運用利回り: 0.036
想定受取額(60歳): 15,000,000円

資産評価額推移（直近1週間）
2026-02-14: 1,200,000円 +5,000円
2026-02-13: 1,195,000円 -2,000円
2026-02-12: 1,197,000円 +3,000円
2026-02-11: 1,194,000円 +1,000円
2026-02-10: 1,193,000円 -
```
