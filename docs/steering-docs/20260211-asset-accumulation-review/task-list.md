# タスクリスト: 資産情報蓄積方式の見直し

## Commit 1: shared 新規追加（AssetRecord, IAssetRecordRepository, AssetRecordError）

純粋な追加のみ。既存コードへの影響なし。

- [x] `shared/domain/asset_record_object.py` 作成
  - `AssetRecord` モデル（date, product, asset_valuation, cumulative_contributions, gains_or_losses）
  - `from_dcp_asset_products` ファクトリメソッド
- [x] `shared/domain/asset_record_interface.py` 作成
  - `IAssetRecordRepository` インターフェース（`save_daily_records` メソッド）
- [x] `shared/domain/exceptions.py` 作成
  - `AssetRecordError` 例外クラス
- [x] `web-scraping/tests/domain/` にテスト追加
  - `AssetRecord` のモデル生成テスト
  - `from_dcp_asset_products` の変換テスト
- [x] コミット

## Commit 2: web-scraping domain/application/infrastructure 変更

IScraper 戻り値変更・save_assets 削除・SeleniumScraper 変更。テストも同時に更新。

- [x] `web-scraping/domain/artifact_interface.py`: `save_assets` メソッド削除
- [x] `web-scraping/infrastructure/s3_artifact_repository.py`: `save_assets` メソッド削除
- [x] `web-scraping/domain/scraping_interface.py`: 戻り値を `dict[str, DcpAssetInfo]` に変更
- [x] `web-scraping/domain/extraction_object.py`: `DcpAssets` のインポート・エクスポート削除
- [x] `web-scraping/domain/__init__.py`: エクスポート更新
- [x] `web-scraping/infrastructure/selenium_scraper.py`: `_extract_asset_valuation` から total 返却を除外し `dict[str, DcpAssetInfo]` を返却。`_extract_total_assets` メソッド削除
- [x] `web-scraping/application/web_scraping_service.py`: 戻り値型を `dict[str, DcpAssetInfo]` に変更
- [x] テスト更新
  - `MockSeleniumScraper`: `DcpAssets` → `dict[str, DcpAssetInfo]` を返却するよう変更
  - `valid_assets` フィクスチャ: `dict[str, DcpAssetInfo]` 形式に変更
  - `presentation/test_asset_collection_handler.py`: S3 JSON 保存の検証を削除、戻り値型の変更に対応
- [x] コミット

## Commit 3: shared DcpAssets 削除 + summary-notification DcpAssets ローカル化

shared から DcpAssets を削除し、summary-notification にローカル定義を追加。

- [x] `shared/domain/asset_object.py`: `DcpAssets` クラス削除（`DcpAssetInfo` は残す）
- [x] `summary-notification/src/domain/asset_object.py` 新規作成: `DcpAssets` をローカル定義
- [x] `summary-notification/src/domain/__init__.py`: import 元を shared → ローカルに変更
- [x] `summary-notification/src/domain/asset_interface.py`: import 元を shared → ローカルに変更
- [x] summary-notification テスト: shared から直接 `DcpAssets` をインポートしている箇所があれば修正
- [x] コミット

## Commit 4: web-scraping infrastructure - GoogleSheetAssetRecordRepository 実装

新規 Infrastructure 実装とテスト。

- [x] `web-scraping/pyproject.toml`: `gspread`, `google-auth` 依存関係追加
- [x] `lambda/web-scraping` で `uv sync` 実行
- [x] `web-scraping/infrastructure/google_sheet_asset_record_repository.py` 作成
  - `GoogleSheetAssetRecordRepository` 実装
  - サービスアカウント認証・スプレッドシートオープン
  - `save_daily_records`: 冪等性実現（同一日付の既存行削除 → 新規追記）
- [x] `web-scraping/infrastructure/__init__.py`: エクスポート追加
- [x] テスト追加（`gspread` をモック）
  - 正常系: レコード追記の検証
  - 冪等性: 同一日付の既存行がある場合の削除・追記検証
  - 異常系: API エラー時の `AssetRecordError` 発生検証
- [x] コミット

## Commit 5: web-scraping presentation/handler/settings 改修

Presentation 層の DI 変更・レコード保存処理追加。

- [x] `web-scraping/config/settings.py`: `spreadsheet_parameter_name` 追加
- [x] `web-scraping/presentation/asset_collection_handler.py` 改修
  - `IAssetRecordRepository` の DI 追加（引数・SSM からの初期化）
  - `AssetRecord.from_dcp_asset_products` でレコード変換
  - `save_daily_records` 呼び出し
- [x] `web-scraping/handler.py`: `AssetRecordError` のキャッチ追加
- [x] テスト更新
  - `MockAssetRecordRepository` 作成
  - `test_asset_collection_handler.py`: レコード保存の検証追加
- [x] コミット

## Commit 6: CDK スタック変更

SSM パラメータ参照・環境変数・権限の追加。

- [x] `lib/dcp-ops-monitor-stack.ts` 改修
  - `DcpOpsMonitorStackProps` に `spreadsheetParameterName` 追加
  - SSM パラメータ参照（`SpreadsheetParameter`）追加
  - web-scraping Lambda の環境変数に `SPREADSHEET_PARAMETER_NAME` 追加
  - SSM 読み取り権限追加
- [x] `bin/dcp-ops-monitor.ts`: Props に `spreadsheetParameterName` 追加
- [x] CDK スナップショットテスト更新
- [x] コミット

## Commit 7: docs 更新

機能設計書を今回の変更に合わせて更新。

- [x] `docs/functional-design.md` 更新
  - データモデル定義: `AssetRecord` 追加、`DcpAssets` を summary-notification ローカルに移動した旨記載
  - インターフェース設計: `IAssetRecordRepository`（`save_daily_records`）追加、`IArtifactRepository` から `save_assets` 削除
  - 資産情報収集機能のシーケンス図: S3 JSON 保存 → Google Spreadsheet 保存に変更
  - コンポーネント設計: shared パッケージの構成更新
- [x] コミット
