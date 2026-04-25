# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 環境

- パッケージマネージャー: [mise](https://mise.jdx.dev/installing-mise.html)

## セットアップ

```bash
# ツールインストール
mise trust && mise install

# Node 依存関係 + pre-commit フック
npm ci && npx lefthook install

# Python 依存関係（uv workspace）
cd lambda && uv sync

# 環境変数（Docker Compose 用）
cp .env.example .env.local
```

CDK 初回ブートストラップ（初回のみ）: `cdk bootstrap aws://ACCOUNT-NUMBER/REGION`

## 開発コマンド

### Lint / Format

```bash
npm run lint          # TypeScript + Python lint（auto-fix）
npm run lint:ci       # lint（fix なし、CI 用）
npm run format        # TypeScript + Python format（auto-fix）
npm run format:ci     # format（check only、CI 用）
```

### 型チェック

```bash
npm run type-check    # web-scraping の型チェック（summary-notification は未対応）
```

### テスト

```bash
# CDK スナップショットテスト
npm run test:cdk

# Lambda テスト（全体）
npm run test:web-scraping
npm run test:summary-notification

# Lambda テスト（単一ファイル）
cd lambda/web-scraping && ENV=test uv run pytest tests/domain/test_asset_record_object.py -v
cd lambda/summary-notification && ENV=test uv run pytest tests/domain/test_asset_object.py -v

# Lambda テスト（単一関数）
cd lambda/web-scraping && ENV=test uv run pytest tests/domain/test_asset_record_object.py::test_function_name -v
```

### ローカル実行（Docker Compose）

web-scraping Lambda を LocalStack と組み合わせて動かす:

```bash
docker compose up          # LocalStack + web-scraping コンテナ起動
docker compose up --build  # イメージ再ビルドして起動
```

LocalStack 起動時に `localstack/ready.sh` が S3 バケットと SSM パラメータを自動作成する（`.env.local` の値を使用）。

## 開発プロセス

### 機能追加・修正時の手順

#### 1. 影響分析

- 永続的ドキュメント（`ARCHITECTURE.md`、`CONTRIBUTING.md`、`docs/`）への影響を確認
- 変更が基本設計に影響する場合は該当ドキュメントを更新

#### 2. ステアリングディレクトリ作成

`.steering-docs/` は `.gitignore` により未追跡（ローカル専用）。

```bash
mkdir -p .steering-docs/[YYYYMMDD]-[開発タイトル]
# 例: mkdir -p .steering-docs/20260126-add-tag-feature
```

#### 3. 作業ドキュメント作成

各ファイル作成後、必ず確認・承認を得てから次に進む:

1. `.steering-docs/[YYYYMMDD]-[開発タイトル]/requirements.md` — 要求内容
2. `.steering-docs/[YYYYMMDD]-[開発タイトル]/design.md` — 設計
3. `.steering-docs/[YYYYMMDD]-[開発タイトル]/task-list.md` — タスクリスト

**重要**: 1 ファイル毎に作成後、必ず確認・承認を得てから次のファイル作成を行う

**タスクリスト作成時の注意**: コミット単位でタスクをグループ化する。pre-commit フックでテストが自動実行されるため、テストが通る単位を意識してタスクを分割する

#### 4. 永続的ドキュメント更新（必要な場合のみ）

変更が基本設計に影響する場合、該当する永続ドキュメント（`ARCHITECTURE.md`、`CONTRIBUTING.md`、`docs/`）を更新する

#### 5. 実装

`.steering-docs/[YYYYMMDD]-[開発タイトル]/task-list.md` に基づいて実装を進める

## ドキュメント管理

### 永続的ドキュメント

基本設計を記述し、大きな設計変更時のみ更新する。

| ファイル | 内容 |
|---------|------|
| @ARCHITECTURE.md | アーキテクチャ概要（概要、コードマップ、不変条件） |
| @CONTRIBUTING.md | Lambda アーキテクチャ方針・shared の背景・各 Lambda の実装詳細 |

### 作業単位のドキュメント (`.steering-docs/`)

特定の作業・変更に特化し、作業ごとに新しいディレクトリを作成する。作業完了後も変更の意図と経緯の記録として保持する。
