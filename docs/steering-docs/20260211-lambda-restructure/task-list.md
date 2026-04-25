# タスクリスト: Lambda ディレクトリ構造リファクタリング

## コミット 1: shared パッケージの作成と uv workspace セットアップ

shared パッケージを作成し、workspace を構成する。
この時点では各機能はまだ shared を参照しない（テストに影響なし）。

- [ ] `lambda/pyproject.toml` 作成（virtual workspace root）
- [ ] `lambda/shared/pyproject.toml` 作成
- [ ] `lambda/shared/src/shared/__init__.py` 作成
- [ ] `lambda/shared/src/shared/config/__init__.py` 作成
- [ ] `lambda/shared/src/shared/config/base_settings.py` 作成（`get_logger()` + `BaseEnvSettings`）
- [ ] `lambda/shared/src/shared/infrastructure/__init__.py` 作成
- [ ] `lambda/shared/src/shared/infrastructure/ssm_parameter.py` 作成
- [ ] `lambda/shared/src/shared/domain/__init__.py` 作成
- [ ] `lambda/shared/src/shared/domain/asset_object.py` 作成（`DcpAssetInfo` + `DcpAssets`）
- [ ] 各機能の `pyproject.toml` を更新（shared 依存追加、共通パッケージ削除、workspace source 追加）
- [ ] 各機能の `uv.lock` を削除（workspace root に統合）
- [ ] `uv sync` で workspace のロックファイル生成・依存解決を確認

## コミット 2: web-scraping を shared に移行

web-scraping の共通コードを shared からの import に切り替える。

- [ ] `web-scraping/src/config/settings.py` 変更（`BaseEnvSettings` 継承、`get_logger` re-export）
- [ ] `web-scraping/src/domain/extraction_object.py` 変更（shared の `DcpAssetInfo` を継承、`DcpAssets` を re-export）
- [ ] `web-scraping/src/domain/__init__.py` 変更（import 元調整）
- [ ] `web-scraping/src/infrastructure/__init__.py` 変更（`get_ssm_json_parameter` を shared から re-export）
- [ ] `web-scraping/src/infrastructure/ssm_parameter.py` 削除
- [ ] `test:web-scraping` が通ることを確認

## コミット 3: summary-notification を shared に移行

summary-notification の共通コードを shared からの import に切り替える。

- [ ] `summary-notification/src/config/settings.py` 変更（`BaseEnvSettings` 継承、`get_logger` re-export）
- [ ] `summary-notification/src/domain/__init__.py` 変更（`DcpAssetInfo`, `DcpAssets` を shared から import）
- [ ] `summary-notification/src/domain/asset_object.py` 削除
- [ ] `summary-notification/src/infrastructure/__init__.py` 変更（`get_ssm_json_parameter` を shared から re-export）
- [ ] `summary-notification/src/infrastructure/ssm_parameter.py` 削除
- [ ] `test:summary-notification` が通ることを確認

## コミット 4: CDK スタックの変更

CDK バンドリング方式を変更し、`@aws-cdk/aws-lambda-python-alpha` を削除する。

- [ ] `lib/dcp-ops-monitor-stack.ts` 変更
  - summary-notification: `PythonFunction` → `lambda.Function` + `Code.fromAsset`
  - web-scraping: `fromImageAsset` のパスとファイル指定を変更
  - `PythonFunction` の import 削除
- [ ] `web-scraping/Dockerfile` 変更（workspace 対応のビルドコンテキスト）
- [ ] `package.json` から `@aws-cdk/aws-lambda-python-alpha` 削除
- [ ] `npm install` で依存更新
- [ ] `test:cdk`（スナップショットテスト）を更新して通るようにする

## コミット 5: lefthook と CI の調整

pre-commit フックの glob パターンを調整し、shared 変更時にもテストが実行されるようにする。

- [ ] `lefthook.yml` 変更
  - `test:web-scraping` の glob に `lambda/shared/**/*.py` 追加
  - `test:summary-notification` の glob に `lambda/shared/**/*.py` 追加
- [ ] `package.json` の type-check コマンドのパス確認・必要に応じて調整

## コミット 6: ドキュメント更新

- [ ] `docs/functional-design.md` 更新（コンポーネント設計のディレクトリ構造に shared を追記）
- [ ] `CLAUDE.md` 更新（ディレクトリ構成セクション、Python 実行環境のセットアップ手順）
