# タスクリスト: DcpAssets 廃止・AssetEvaluation への責務集約

## コミット 1: AssetEvaluation.aggregate() の追加

`DcpAssets` 廃止の前準備として、shared に `aggregate()` を追加する。

- [ ] `lambda/shared/src/shared/domain/asset_object.py`
  - `from collections.abc import Iterable` を追加
  - `AssetEvaluation.aggregate()` クラスメソッドを追加
- [ ] `lambda/summary-notification/tests/domain/test_asset_object.py`
  - `TestAssetEvaluation` に `aggregate()` のテストを追加
    - `test_aggregate__sums_all_evaluations`: 複数の AssetEvaluation を合算できる
    - `test_aggregate__empty_returns_zero`: 空リストの場合に全フィールド 0 が返る

## コミット 2: DcpAssets 廃止・全体の整合

`DcpAssets` を廃止し、関連する全ファイルを一括で更新する。
（部分的な変更ではテストが壊れるため一括コミット）

- [ ] `lambda/summary-notification/src/domain/asset_object.py` を削除
- [ ] `lambda/summary-notification/src/domain/__init__.py`
  - `DcpAssets` のインポート・エクスポートを削除
- [ ] `lambda/summary-notification/src/domain/asset_interface.py`
  - `get_latest_assets()` の戻り値型を `dict[str, AssetEvaluation]` に変更
  - `get_weekly_assets()` の戻り値型を `dict[date, dict[str, AssetEvaluation]]` に変更
- [ ] `lambda/summary-notification/src/infrastructure/google_sheet_asset_repository.py`
  - `_to_dcp_assets()` を `_to_products()` に置き換え
  - `get_latest_assets()` / `get_weekly_assets()` の戻り値型を変更
- [ ] `lambda/summary-notification/src/application/summary_notification_service.py`
  - `assets.calculate_total()` → `AssetEvaluation.aggregate(products.values())`
  - `_calculate_weekly_valuations()` の引数型・内部ロジックを更新
- [ ] `lambda/summary-notification/tests/domain/test_asset_object.py`
  - `TestDcpAssets` クラスを削除
- [ ] `lambda/summary-notification/tests/fixtures/mocks/mock_asset_repository.py`
  - 型を `dict[str, AssetEvaluation]` / `dict[date, dict[str, AssetEvaluation]]` に変更
- [ ] `lambda/summary-notification/tests/application/test_summary_notification_service.py`
  - `DcpAssets` フィクスチャを `dict[str, AssetEvaluation]` に置き換え

## コミット 3: ドキュメント更新

- [ ] `docs/functional-design.md`
  - データモデル定義の `DcpAssets` セクションを削除
  - `AssetEvaluation` に `aggregate()` メソッドの説明を追加
