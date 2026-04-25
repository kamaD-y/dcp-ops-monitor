# 設計: DcpAssets 廃止・AssetEvaluation への責務集約

## 変更方針

`DcpAssets` を廃止し `dict[str, AssetEvaluation]` を直接使用する。
合計計算ロジックは `AssetEvaluation.aggregate()` として shared に集約する。

---

## 1. shared/domain/asset_object.py

`AssetEvaluation` に `aggregate()` クラスメソッドを追加する。

```python
from collections.abc import Iterable

@classmethod
def aggregate(cls, evaluations: Iterable["AssetEvaluation"]) -> "AssetEvaluation":
    """複数の AssetEvaluation を合算して単一の AssetEvaluation を生成する"""
    items = list(evaluations)
    return cls(
        cumulative_contributions=sum(e.cumulative_contributions for e in items),
        gains_or_losses=sum(e.gains_or_losses for e in items),
        asset_valuation=sum(e.asset_valuation for e in items),
    )
```

---

## 2. summary-notification/src/domain/asset_object.py

`DcpAssets` クラスを廃止し、ファイルを削除する。

---

## 3. summary-notification/src/domain/__init__.py

- `DcpAssets` のインポート・エクスポートを削除する
- `AssetEvaluation` は引き続き shared からインポートして re-export する

---

## 4. summary-notification/src/domain/asset_interface.py

戻り値の型を `DcpAssets` から `dict[str, AssetEvaluation]` へ変更する。

```python
# Before
def get_latest_assets(self) -> DcpAssets: ...
def get_weekly_assets(self) -> dict[date, DcpAssets]: ...

# After
def get_latest_assets(self) -> dict[str, AssetEvaluation]: ...
def get_weekly_assets(self) -> dict[date, dict[str, AssetEvaluation]]: ...
```

---

## 5. summary-notification/src/infrastructure/google_sheet_asset_repository.py

- `_to_dcp_assets()` を削除し、`_to_products()` に置き換える
- 戻り値の型を `DcpAssets` から `dict[str, AssetEvaluation]` へ変更する

```python
# Before
def _to_dcp_assets(self, rows: list[dict]) -> DcpAssets:
    products: dict[str, AssetEvaluation] = {}
    for row in rows:
        products[row["product"]] = AssetEvaluation(...)
    return DcpAssets(products=products)

# After
def _to_products(self, rows: list[dict]) -> dict[str, AssetEvaluation]:
    products: dict[str, AssetEvaluation] = {}
    for row in rows:
        products[row["product"]] = AssetEvaluation(...)
    return products
```

---

## 6. summary-notification/src/application/summary_notification_service.py

- `assets.calculate_total()` → `AssetEvaluation.aggregate(products.values())`
- `_calculate_weekly_valuations()` の引数型を `dict[date, DcpAssets]` → `dict[date, dict[str, AssetEvaluation]]` に変更

```python
# Before
assets = self.asset_repository.get_latest_assets()        # DcpAssets
total = assets.calculate_total()
weekly_assets = self.asset_repository.get_weekly_assets() # dict[date, DcpAssets]
weekly_valuations = self._calculate_weekly_valuations(weekly_assets)

# After
products = self.asset_repository.get_latest_assets()         # dict[str, AssetEvaluation]
total = AssetEvaluation.aggregate(products.values())
weekly_products = self.asset_repository.get_weekly_assets()  # dict[date, dict[str, AssetEvaluation]]
weekly_valuations = self._calculate_weekly_valuations(weekly_products)
```

`_calculate_weekly_valuations()` 内部の変更:
```python
# Before
valuations = {d: weekly_assets[d].calculate_total().asset_valuation ...}

# After
valuations = {d: AssetEvaluation.aggregate(weekly_products[d].values()).asset_valuation ...}
```

---

## 7. テスト変更

### tests/domain/test_asset_object.py

- `TestDcpAssets` クラスを削除する
- `TestAssetEvaluation` に `aggregate()` のテストを追加する
  - 複数商品の合算が正しく行われること
  - 空リストの場合に全フィールド 0 の `AssetEvaluation` が返ること

### tests/fixtures/mocks/mock_asset_repository.py

- `DcpAssets` 参照を削除する
- 型を `dict[str, AssetEvaluation]` / `dict[date, dict[str, AssetEvaluation]]` に変更する

### tests/application/test_summary_notification_service.py

- `DcpAssets` を使ったフィクスチャを `dict[str, AssetEvaluation]` に置き換える

---

## 8. docs/functional-design.md

`DcpAssets` のデータモデル定義セクションを削除し、
`AssetEvaluation.aggregate()` の説明を追加する。

---

## 依存関係への影響

web-scraping Lambda はもともと `DcpAssets` を使用していないため影響なし。
