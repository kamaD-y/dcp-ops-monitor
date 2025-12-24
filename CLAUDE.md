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
├── lambda                        # Lambda コード
│   ├── error-notification        # エラー通知用 Lambda
│   │   ├── README.md
│   │   ├── pyproject.toml
│   │   ├── requirements.txt
│   │   ├── src
│   |   │   ├── application
│   |   │   ├── config
│   |   │   ├── domain
│   |   │   ├── infrastructure
│   |   │   ├── presentation
│   |   │   └── handler.py
│   |   ├── tests
│   │   └── uv.lock
│   └── web-scraping              # Web スクレイピング Lambda (コンテナ利用)
│       ├── Dockerfile
│       ├── README.md
│       ├── pyproject.toml
│       ├── src
│       │   ├── application
│       │   ├── config
│       │   ├── domain
│       │   ├── infrastructure
│       │   ├── presentation
│       │   └── handler.py
│       ├── tests
│       └── uv.lock
├── CLAUDE.md
├── CONTRIBUTING.md
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

```
$ cdk bootstrap aws://ACCOUNT-NUMBER/REGION --profile xxx
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

1. サンプルの環境変数ファイルをコピーします

```bash
$ cp .env.example .env.local # docker compose で使用します
```

2. テキストエディタで`.env.local`ファイルを開きます

3. 以下の環境変数を適切な値で設定します  
  (本番環境へのデプロイは GitHub Actions を介して行う為、GitHub 変数及び、CDK Parameter を使用します)

- `POWERTOOLS_LOG_LEVEL`: アプリケーションのログレベル
- `USER_AGENT`: スクレイピングで使用するユーザーエージェント
- `SCRAPING_PARAMETER_NAME`: スクレイピングに必要な各種パラメータを格納したパラメータストア名
- `LINE_MESSAGE_PARAMETER_NAME`: LINE Message API 接続に必要な URL, Token を格納したパラメータストア名
- `ERROR_BUCKET_NAME`: エラー保存用 S3 バケット
- 以下は、開発環境での Docker-Compose を使用した動作確認で使用する設定
  - `ENV`: boto3 endpoint 切り替えの為、test もしくは local を代入
  - `SCRAPING_PARAMETER_VALUE`: スクレイピングに必要な各種パラメータ (JSON)
  - `LINE_MESSAGE_PARAMETER_VALUE`: LINE Message API 接続に必要な URL, Token (JSON)
- 以下は、LocalStack 用の設定
  - `AWS_DEFAULT_REGION`: LocalStack 用
  - `AWS_ACCESS_KEY_ID`: LocalStack 用のダミー
  - `AWS_SECRET_ACCESS_KEY`: LocalStack 用のダミー
  - `LOCAL_STACK_CONTAINER_URL`: LocalStack URL
  - `SERVICES`: LocalStack で使用する AWS サービス


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
$ npm run test:unit
```

### コミット

.husky/lefthook を使用し、コミット時に Lint/Format/Test を自動的に実行します。

## ローカル環境でのスクレイピング実行方法

### Python インタプリタからインタラクティブに Selenium を使用する

> [!NOTE]  
> スクレイピングの接続先は本物を使用します。

1. selenium/standalone-chrome を起動

```bash
# https://hub.docker.com/r/selenium/standalone-chrome
$ docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" selenium/standalone-chrome:latest
```

2. ブラウザに接続  
  http://localhost:7900 に接続  
  パスワードは`secret`を入力

3. Python インタプリタから driver を操作

```bash
$ python

>>> import os
>>> from dotenv import load_dotenv
>>> from selenium import webdriver
>>> env_path = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), ".env.local")
>>> load_dotenv(env_path)
>>> options = webdriver.ChromeOptions()
>>> options.add_argument(f'--user-agent={os.environ["USER_AGENT"]}')
>>> driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub', options=options)
>>> driver.get(os.environ["START_URL"])
# localhost:7900 で、ブラウザが操作されていること
...

# 操作終了時は quit する
>>> driver.quit()
```

### docker-compose で Lambda コンテナを実行する

> [!NOTE]  
> Lambda コンテナでスクレイピングが正常に動作するか確認する為使用します。
> AWS リソースについては LocalStack を使用しますが、スクレイピングの接続先は本物を使用します。

1. docker-compose で起動する

```bash
$ docker compose up -d --build
```

2. 起動した Lambda を呼び出す

```bash
$ curl -d "{}" http://localhost:8080/2015-03-31/functions/function/invocations
```

3. docker-compose を終了する

```bash
$ docker compose down
```

## デプロイ

### 事前作業

1. パラメータストアを手動で作成します (CDK で暗号化文字列を使用したパラメータを作成できない為手動としています)
- スクレイピング用パラメータ
```json
{"start_url": "https://xxx", "login_user_id":"xxxx","login_password":"xxxx","login_birthdate":"19701201"}
```
- LINE Message 用パラメータ
```json
{"url": "https://xxx", "token": "xxx"}
```

2. 作成したパラメータ名を props にセットします
- スクレイピング用パラメータ: `scrapingParameterName`
- LINE Message 用パラメータ: `lineMessageParameterName`

### デプロイ

[GitHub Actions ワークフロー](.github/workflows/) を利用してデプロイします
