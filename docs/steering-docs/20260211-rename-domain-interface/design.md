# 設計: ドメインインターフェースの表記揺れ修正

## 命名変更マッピング

| 対象 | Before | After |
|------|--------|-------|
| ファイル名 | `storage_interface.py` | `artifact_interface.py` |
| クラス名 | `IObjectRepository` | `IArtifactRepository` |
| メソッド名 | `upload_file` | `save_error_artifact` |
| メソッド名 | `put_json` | `save_assets` |
| インフラファイル名 | `s3_object_repository.py` | `s3_artifact_repository.py` |
| インフラクラス名 | `S3ObjectRepository` | `S3ArtifactRepository` |
| 変数名 | `object_repository` | `artifact_repository` |

## 修正対象ファイル

影響範囲は web-scraping Lambda 内 + docs に閉じる。

### ソースコード（6ファイル）

| # | ファイル | 変更内容 |
|---|---------|---------|
| 1 | `lambda/web-scraping/src/domain/storage_interface.py` | ファイルリネーム → `artifact_interface.py`、クラス名・メソッド名・docstring 変更 |
| 2 | `lambda/web-scraping/src/domain/__init__.py` | import 元・export 名の変更 |
| 3 | `lambda/web-scraping/src/infrastructure/s3_object_repository.py` | ファイルリネーム → `s3_artifact_repository.py`、クラス名・メソッド名・import 変更 |
| 4 | `lambda/web-scraping/src/infrastructure/__init__.py` | import 元・export 名の変更 |
| 5 | `lambda/web-scraping/src/application/web_scraping_service.py` | import・型注釈・変数名・メソッド呼び出し変更 |
| 6 | `lambda/web-scraping/src/presentation/asset_collection_handler.py` | import・変数名・メソッド呼び出し変更 |

### ドキュメント（1ファイル）

| # | ファイル | 変更内容 |
|---|---------|---------|
| 7 | `docs/functional-design.md` | インターフェース設計セクションのクラス名・メソッド名更新 |

### 変更不要

- **テストファイル**: `main()` 経由の E2E テストで、インターフェース名を直接参照していない
- **shared パッケージ**: 参照なし
- **summary-notification Lambda**: 参照なし

## 設計判断

- メソッドのシグネチャ（引数の型・数）は変更しない。名前のみの変更に留める
- `IArtifactRepository` という命名は、web-scraping Lambda が生成する成果物（資産データ JSON + エラー診断ファイル）の永続化を担うインターフェースとして適切
