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

## 開発プロセス
### 機能追加・修正時の手順
#### 1. 影響分析

- 永続的ドキュメント (`docs/`) への影響を確認
- 変更が基本設計に影響する場合は `docs/` を更新

#### 2. ステアリングディレクトリ作成

新しい作業用のディレクトリを作成します。

```bash
$ mkdir -p .steering-docs/[YYYYMMDD]-[開発タイトル]
```

**例:**
```bash
$ mkdir -p .steering-docs/20260126-add-tag-feature
```

#### 3. 作業ドキュメント作成

作業単位のドキュメントを作成します。
各ドキュメント作成後、必ず確認・承認を得てから次に進みます。

1. `.steering-docs/[YYYYMMDD]-[開発タイトル]/requirements.md` - 要求内容
2. `.steering-docs/[YYYYMMDD]-[開発タイトル]/design.md` - 設計
3. `.steering-docs/[YYYYMMDD]-[開発タイトル]/task-list.md` - タスクリスト

**重要**: 1 ファイル毎に作成後、必ず確認・承認を得てから次のファイル作成を行う

#### 4. 永続的ドキュメント更新 (必要な場合のみ)

変更が基本設計に影響する場合、該当する `docs/` 内のドキュメントを更新する

##### 5. 実装開始

`.steering-docs/[YYYYMMDD]-[開発タイトル]/task-list.md` に基づいて実装を進めます。

##### 6. 品質チェック

## ドキュメント管理の原則
### 永続的ドキュメント (`docs/`)
- アプリケーションの基本設計を記述
- 頻繁に更新されない
- 大きな設計変更時のみ更新
- プロジェクト全体の「北極星」として機能

### 作業単位のドキュメント (`steering-docs/`)
- 特定の作業・変更に特化
- 作業ごとに新しいディレクトリを作成
- 作業完了後は履歴として保持
- 変更の意図と経緯を記録

## ドキュメント管理

プロダクト要件（ビジョン、機能要件、非機能要件）: @docs/product-requirements.md  
機能設計（データモデル、コンポーネント設計、処理フロー）: @docs/functional-design.md  
開発ガイドライン（コーディング規約、命名規則、Git 規約）: @docs/development-guidelines.md
