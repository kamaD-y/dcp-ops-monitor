# CLAUDE.md

## プロジェクト概要
このシステムは、確定拠出年金 (Defined Contribution Plan) の運用状況の管理を楽にする為、
週次で確定拠出年金 Web ページをスクレイピングし、運用指標をサマリして通知します。

## 環境

### パッケージマネージャー
- [mise](https://mise.jdx.dev/installing-mise.html): パッケージマネージャー

### 開発ツール
- `Docker`: Web スクレイピング用 Lambda ビルド/実行、及びローカルでの Docker Compose 用
- `aws-cli`: CDK で利用
- `Node.js`: CDK で利用
- `TypeScript`: CDK アプリケーションの実装、型チェックとコンパイル
- `Biome`: TypeScript コードのリンティング、フォーマット
- `Python`: Lambda の実装
- `uv`: Python パッケージマネージャー
- `Ruff`: Python コードのリンティング、フォーマット
- `Ty`: Python コードの型チェック

## ディレクトリ構成

```
├── bin/dcp-ops-monitor.ts        # CDK アプリケーション
├── lib/dcp-ops-monitor-stack.ts  # スタック
├── docs/                         # 設計/アーキテクチャ
├── localstack/ready.sh           # localstack 起動スクリプト (docker compose で使用)
├── test/cdk/                     # CDK 関連テスト
├── lambda/                       # Lambda コード
├── CLAUDE.md
├── README.md
├── biome.jsonc
├── cdk.json
├── docker-compose.yaml
├── jest.config.js
├── lefthook.yml
├── package-lock.json
├── package.json
├── pyproject.toml
└── tsconfig.json
```

## 開発コマンド
### cdk 開発環境の構築 (初回のみ)

[CDK 開発者ガイド](https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/getting_started.html)

- 環境のブートストラップ

```bash
$ aws login
$ cdk bootstrap aws://ACCOUNT-NUMBER/REGION
```

### ツールのインストール
```bash
$ mise trust
$ mise install
```

### Node 環境のセットアップ

```bash
# 依存関係のインストール
$ npm ci
# pre-commit の有効化
$ npx lefthook install
```

### Python 実行環境のセットアップ

各プロジェクト毎に依存関係を管理、分離しています

```bash
$ cd lambda/{specific_project_name}
$ uv sync
```

### 環境変数の設定

- サンプルの環境変数ファイルをコピーします

```bash
$ cp .env.example .env.local # docker compose で使用します
```

### Lint/Format

```bash
# Lint
$ npm run lint
$ npm run lint:ci

# Format
$ npm run format
$ npm run format:ci
```

### テスト

```bash
# CDK スナップショットテスト
$ npm run test:cdk

# Lambda コードテスト
$ npm run test:{feature}
```

## 詳細ドキュメント
- システム全体のアーキテクチャ図: @docs/dcp-ops-monitor.drawio.png
- アプリケーションアーキテクチャ: @docs/architecture.md
- テスト戦略: @docs/testing.md
