# タスクリスト: ドメインインターフェースの表記揺れ修正

## コミット 1: refactor(web-scraping): IObjectRepository を IArtifactRepository にリネーム

全ソースコードの命名変更を一括で行う。テストはインターフェース名を直接参照していないため、リネームのみでテストがパスする。

- [ ] `storage_interface.py` → `artifact_interface.py` にリネーム、クラス名・メソッド名・docstring 変更
- [ ] `domain/__init__.py` の import/export 更新
- [ ] `s3_object_repository.py` → `s3_artifact_repository.py` にリネーム、クラス名・メソッド名・import 変更
- [ ] `infrastructure/__init__.py` の import/export 更新
- [ ] `application/web_scraping_service.py` の import・変数名・メソッド呼び出し変更
- [ ] `presentation/asset_collection_handler.py` の import・変数名・メソッド呼び出し変更

## コミット 2: docs: 機能設計書の IObjectRepository 記述を更新

- [ ] `docs/functional-design.md` のインターフェース設計セクションを更新
