# 要求定義: Lambda ディレクトリ構造リファクタリング

## 背景

現在 `lambda/` 配下は機能毎（web-scraping, summary-notification）にサブディレクトリを分けており、
各機能が独立した `pyproject.toml` と `uv.lock` を持っている。
domain や config など共通部分が重複しており、共通依存のバージョン管理も分散している。

## 目的

- 共通コードの一元管理により保守性を向上させる
- uv workspace で依存パッケージを一元管理しつつ、機能固有のパッケージを分離する
- 管理の容易さを優先する

## 要求

### R1: uv workspace の導入

- `lambda/` を uv workspace root（virtual workspace）として構成する
- shared, web-scraping, summary-notification を workspace member とする
- 共通パッケージ（boto3, pydantic, powertools 等）は shared で管理する
- 機能固有パッケージは各機能の pyproject.toml で管理する
  - web-scraping: selenium
  - summary-notification: requests
- `uv.lock` は workspace root に一本化する

### R2: shared パッケージの作成

- 以下の共通コードを shared パッケージに切り出す
  - `ssm_parameter.py` - SSM Parameter Store アクセス
  - `config/base_settings.py` - Logger 生成、BaseSettings
  - `domain/asset_object.py` - DcpAssetInfo 基本モデル
- 各機能は shared パッケージを workspace 依存として参照する

### R3: CDK バンドリングの変更

- summary-notification を `PythonFunction` (alpha) → `lambda.Function` + `Code.fromAsset` に変更する
- web-scraping の Docker ビルドコンテキストを `lambda/` に拡大し、shared を参照可能にする
- `@aws-cdk/aws-lambda-python-alpha` パッケージを削除する

### R4: 既存動作の維持

- 各機能の handler、ビジネスロジック、テストの動作は変更しない
- テストコマンド（`test:web-scraping`, `test:summary-notification`）は個別に維持する
- pre-commit フック（lefthook）は引き続き動作する
- CDK スナップショットテストは更新して通るようにする

### R5: ドキュメントの更新

- `docs/` 内のドキュメントに変更が影響する箇所を更新する

## スコープ外

- テストコマンドの統一
- shared パッケージのテスト追加（後続タスクとする）
