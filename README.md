# dcp-ops-status-notification

## Description

確定拠出年金 (Defined Contribution Plan) の運用状況を確認する為、
日本レコードキーピング (NRK) が提供する Web ページをスクレイピングし、サマリした情報を通知します。

## Architecture

![Architecture](docs/images/dcp-ops-status-notification.png)


## Development

### cdk 開発環境の構築 (初回のみ)

[CDK 開発者ガイド](https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/getting_started.html)

- 環境のブートストラップ

```
$ cdk bootstrap aws://ACCOUNT-NUMBER/REGION --profile xxx
```

- アプリケーションの作成

```
$ cdk init app --language typescript
```

### 開発環境の準備

#### 前提条件

以下のソフトウェアがインストールされていること

- `Node.js`: v18.16.0 以上
- `Python`: 3.12 以上
- `uv`
- `Docker`

#### 環境変数の設定

1. サンプルの環境変数ファイルをコピーします

```bash
$ cp .env.example .env
```

2. テキストエディタで`.env`ファイルを開きます

3. 以下の環境変数を適切な値で設定します
   本番環境へのデプロイは GitHub Actions を介して行う為、GitHub に変数を設定しておくこと

- `LOG_LEVEL`: アプリケーションのログレベル
- `LOGIN_URL`: スクレイピング対象サイトのログインページ
- `USER_ID`: ログイン用ユーザ ID
- `PASSWORD`: ログイン用パスワード
- `USER_AGENT`: スクレイピングで使用するユーザーエージェント
- 以下は LINE 通知関数用 (line_notification) 設定の設定
  - `LINE_NOTIFY_URL`: LINE Messaging API の URL
  - `LINE_NOTIFY_TOKEN`: LINE Messaging API の TOKEN
- 以下は開発環境での実行時に、Amazon SNS へ実行結果を通知する場合のみ指定
- ※本番環境で使用する場合は、2 通りを検討する。既存 SNS を使用する場合は開発環境と同じく環境変数を使用し、新規 SNS を作成する場合はスタックに追加する。
  - `SNS_TOPIC_ARN`: Amazon SNS の ARN
  - `AWS_ACCESS_KEY_ID`: 開発環境の Lambda コンテナで使用する IAM ユーザーの認証情報 (アクセスキー)
  - `AWS_SECRET_ACCESS_KEY`: 開発環境の Lambda コンテナで使用する IAM ユーザーの認証情報 (シークレットキー)
  - `AWS_DEFAULT_REGION`: 開発環境の Lambda コンテナで使用する IAM ユーザーのリージョン

#### Node 環境のセットアップ

```bash
$ npm ci
```

#### Python 実行環境のセットアップ

1. poetry インストール

- 仮想環境を使用している場合、仮想環境へ切り替え (Pyenv の例)
  - 仮想環境を使用しない場合は手順スキップ

```bash
$ pyenv install 3.12
$ pyenv versions
# インストールされた Python バージョンへ切り替え
$ pyenv local 3.12.xx
```

- poetry インストール

```bash
$ pip install poetry
```

2. 依存関係のインストール

```bash
$ cd lambda/scraping_nrk
$ poetry install
```

### ローカルでの開発手順

#### Python インタプリタからインタラクティブに Selenium を使用する

1. selenium/standalone-chrome を起動

```bash
# https://hub.docker.com/r/selenium/standalone-chrome
$ docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" selenium/standalone-chrome:latest
```

2. ブラウザに接続

- http://localhost:7900 に接続

  - パスワードは`secret`を入力

3. Python インタプリタから driver を操作

```bash
$ cd lambda/dcp_etl
$ uv sync

>>> import os
>>> from dotenv import load_dotenv
>>> from selenium import webdriver
>>> env_path = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), ".env")
>>> load_dotenv(env_path)
>>> options = webdriver.ChromeOptions()
>>> options.add_argument(f'--user-agent={os.environ["USER_AGENT"]}')
>>> driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub', options=options)
>>> driver.get(os.environ["LOGIN_URL"])
# localhost:7900 で、ブラウザが操作されていること
...

# 操作終了時は quit する
>>> driver.quit()
```

### テスト

#### スナップショット

```bash
$ npm run test:snapshot
```

#### ユニットテスト

```bash
$ npm run test:unit
```

### コミット

.husky を使用し、コミット時に Lint/Format を自動的に実行します。

### ローカルから Lambda コンテナでハンドラーを実行する

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

## Development

### デプロイ

```bash
$ cdk deploy --profile xxx
```

### デストロイ

```bash
$ cdk destroy --profile xxx
```
