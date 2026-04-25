# CONTRIBUTING.md

## Lambda アーキテクチャ方針

### なぜクリーンアーキテクチャ 4 層構造か

各 Lambda は `presentation / application / domain / infrastructure` の 4 層構造で実装しています。

- Domain 層に外部依存を持ち込まないことで、ビジネスルールを独立してテスト・変更できる
- Infrastructure 実装を差し替え可能にすることで、ローカルテスト（Mock / LocalStack）が容易になる
- Presentation 層に依存性注入を集約することで、各層の責務を明確に分離できる

### なぜ shared パッケージがあるか

`lambda/shared` は uv workspace のメンバーとして、`web-scraping` と `summary-notification` の両 Lambda から依存されます。

各 Lambda は独立した uv プロジェクトであるため、共通コードをコピーせず shared パッケージとして一元管理することで整合性を保ちます。

共通化している内容:

| モジュール | 内容 |
|---|---|
| `domain/asset_object.py` | `AssetEvaluation` ドメインモデル（両 Lambda で同じ資産データを扱うため） |
| `domain/asset_record_object.py` | `AssetRecord` ドメインモデル（Google Spreadsheet への蓄積フォーマット） |
| `domain/asset_record_interface.py` | `IAssetRecordRepository`（Spreadsheet への読み書きを抽象化） |
| `infrastructure/ssm_parameter.py` | SSM Parameter Store クライアント |
| `config/base_settings.py` | Logger・BaseSettings（aws-lambda-powertools ベース） |

---

## web-scraping

### なぜ Docker コンテナを使うか

Selenium を Lambda の zip パッケージ方式でデプロイする場合、Chrome / ChromeDriver のバイナリと Python パッケージの依存関係の調整が煩雑になります。コンテナイメージ方式にすることでこの問題を回避しています。

### ECR ライフサイクルポリシー

この Lambda は Docker イメージを使用しており、デプロイのたびに CDK ブートストラップ用の ECR リポジトリにイメージがプッシュされます。コスト削減のため、初回セットアップ時に保持イメージを 1 つに制限するポリシーを設定します。

```bash
aws ecr put-lifecycle-policy \
  --repository-name cdk-hnb659fds-container-assets-{ACCOUNT_ID}-{REGION} \
  --lifecycle-policy-text '{
    "rules": [{
      "rulePriority": 1,
      "selection": {
        "tagStatus": "any",
        "countType": "imageCountMoreThan",
        "countNumber": 1
      },
      "action": { "type": "expire" }
    }]
  }'
```

> `cdk bootstrap` を再実行するとリセットされるため、再設定が必要です。

### 環境変数

| 環境変数 | 説明 |
|---------|------|
| `SCRAPING_PARAMETER_NAME` | スクレイピングパラメータ（URL、認証情報等）の SSM パラメータ名 |
| `SPREADSHEET_PARAMETER_NAME` | Google Spreadsheet 接続設定の SSM パラメータ名 |
| `DATA_BUCKET_NAME` | エラーアーティファクト保存用 S3 バケット名 |
| `USER_AGENT` | スクレイピング用ユーザーエージェント |
| `POWERTOOLS_LOG_LEVEL` | ログレベル（ERROR / WARNING / INFO / DEBUG）、デフォルト: INFO |

### ローカルでのスクレイピング動作確認

#### Python インタプリタから Selenium をインタラクティブに操作する

> スクレイピングの接続先は本物を使用します。

1. `selenium/standalone-chrome` を起動

```bash
docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" selenium/standalone-chrome:latest
```

2. http://localhost:7900 にブラウザで接続（パスワード: `secret`）

3. Python インタプリタから操作

```python
import os
from dotenv import load_dotenv
from selenium import webdriver

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), ".env.local"))
options = webdriver.ChromeOptions()
options.add_argument(f'--user-agent={os.environ["USER_AGENT"]}')
driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub', options=options)
driver.get(os.environ["START_URL"])
# localhost:7900 でブラウザが操作されていることを確認

driver.quit()  # 終了時
```

#### Docker Compose で Lambda コンテナを実行する

> Lambda コンテナでスクレイピングが正常に動作するか確認します。AWS リソースは LocalStack を使用し、スクレイピング先は本物を使用します。

1. `.env.local` の `SCRAPING_PARAMETER_VALUE` に実際の認証情報を入力

2. コンテナを起動

```bash
docker compose up -d --build
```

3. Lambda を呼び出す

```bash
curl -d "{}" http://localhost:8080/2015-03-31/functions/function/invocations
```

4. 終了

```bash
docker compose down
```

---

## summary-notification

### 通知内容サンプル

```
確定拠出年金 運用状況通知Bot

拠出金額累計: 2,280,000円
評価損益: 456,000円
資産評価額: 2,736,000円

運用年数: 9.4年
運用利回り: 0.051
想定受取額(60歳): 6,540,000円

資産評価額推移（直近1週間）
2025-12-05: 2,736,000円 +0円
2025-12-04: 2,736,000円 +6,000円
2025-12-03: 2,730,000円 +5,000円
2025-12-02: 2,725,000円 +5,000円
2025-12-01: 2,720,000円 -
```

### 環境変数

| 環境変数 | 説明 |
|---------|------|
| `LINE_MESSAGE_PARAMETER_NAME` | LINE 通知パラメータ（Channel Access Token、送信先 User ID 等）の SSM パラメータ名 |
| `SPREADSHEET_PARAMETER_NAME` | Google Spreadsheet 接続設定の SSM パラメータ名 |
| `POWERTOOLS_LOG_LEVEL` | ログレベル（ERROR / WARNING / INFO / DEBUG）、デフォルト: INFO |
