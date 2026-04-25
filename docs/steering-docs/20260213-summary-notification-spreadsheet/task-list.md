# タスクリスト: summary-notification の資産情報取得元を Google Spreadsheet に変更

## Commit 1: summary-notification の資産取得元を S3 から Google Spreadsheet に変更

pre-commit フックで全テストが実行されるため、S3 依存の除去と Spreadsheet 対応を一括で行う。

- [ ] `lambda/shared/src/shared/config/base_settings.py` から `data_bucket_name` を削除
- [ ] `lambda/web-scraping/src/config/settings.py` の `EnvSettings` に `data_bucket_name` を追加
- [ ] `lambda/summary-notification/src/domain/exceptions.py` — `no_assets_in_bucket` → `no_assets_in_spreadsheet` に変更
- [ ] `lambda/summary-notification/src/config/settings.py` — `spreadsheet_parameter_name` を追加
- [ ] `lambda/summary-notification/src/infrastructure/google_sheet_asset_repository.py` を新規作成
- [ ] `lambda/summary-notification/src/infrastructure/s3_asset_repository.py` を削除
- [ ] `lambda/summary-notification/src/infrastructure/__init__.py` を更新
- [ ] `lambda/summary-notification/src/presentation/summary_notification_handler.py` の DI を更新
- [ ] `lambda/summary-notification/pyproject.toml` — dependencies 更新、env 設定更新
- [ ] `lambda/summary-notification/tests/conftest.py` を削除
- [ ] `lambda/summary-notification/tests/infrastructure/test_s3_asset_repository.py` を削除
- [ ] テスト内で `no_assets_in_bucket()` を使用している箇所を `no_assets_in_spreadsheet()` に更新
- [ ] `uv sync` で依存関係を反映

## Commit 2: CDK スタックを更新

- [ ] `lib/dcp-ops-monitor-stack.ts` — summary-notification Lambda の環境変数・IAM 権限を更新
- [ ] CDK スナップショットテストを更新（`npm run test:cdk`）

## Commit 3: ドキュメント更新

- [ ] `docs/functional-design.md` — サマリ通知機能のシーケンス図・サービス構成を更新
