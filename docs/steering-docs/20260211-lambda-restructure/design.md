# 設計: Lambda ディレクトリ構造リファクタリング

## 1. ディレクトリ構造

### 変更後

```
lambda/
├── pyproject.toml              # uv virtual workspace root
├── uv.lock                     # workspace 共有ロックファイル
│
├── shared/                     # 共通パッケージ
│   ├── pyproject.toml
│   └── src/
│       └── shared/
│           ├── __init__.py
│           ├── config/
│           │   ├── __init__.py
│           │   └── base_settings.py
│           ├── infrastructure/
│           │   ├── __init__.py
│           │   └── ssm_parameter.py
│           └── domain/
│               ├── __init__.py
│               └── asset_object.py
│
├── web-scraping/               # 変更: pyproject.toml 書き換え、uv.lock 削除
│   ├── Dockerfile              # 変更: ビルドコンテキスト対応
│   ├── pyproject.toml          # 変更: shared 依存追加、共通パッケージ削除
│   ├── src/
│   │   ├── handler.py          # 変更: import パス
│   │   ├── config/
│   │   │   └── settings.py     # 変更: shared から継承
│   │   ├── domain/
│   │   │   ├── __init__.py     # 変更: DcpAssetInfo の re-export 元変更
│   │   │   ├── exceptions.py
│   │   │   ├── extraction_object.py  # 変更: shared の DcpAssetInfo を継承
│   │   │   ├── scraping_object.py
│   │   │   ├── scraping_interface.py
│   │   │   └── storage_interface.py
│   │   ├── application/
│   │   ├── infrastructure/
│   │   │   ├── __init__.py     # 変更: ssm_parameter の re-export 元変更
│   │   │   ├── s3_object_repository.py
│   │   │   └── selenium_scraper.py
│   │   └── presentation/
│   │       └── asset_collection_handler.py  # 変更: import パス
│   └── tests/
│
└── summary-notification/       # 変更: pyproject.toml 書き換え、uv.lock 削除
    ├── pyproject.toml          # 変更: shared 依存追加、共通パッケージ削除
    ├── src/
    │   ├── handler.py          # 変更: import パス
    │   ├── config/
    │   │   └── settings.py     # 変更: shared から継承
    │   ├── domain/
    │   │   ├── __init__.py     # 変更: DcpAssetInfo の re-export 元変更
    │   │   ├── asset_object.py # 削除: shared に移動
    │   │   ├── exceptions.py
    │   │   ├── indicator_object.py
    │   │   ├── notification_object.py
    │   │   ├── asset_interface.py
    │   │   └── notification_interface.py
    │   ├── application/
    │   ├── infrastructure/
    │   │   ├── __init__.py     # 変更: ssm_parameter の re-export 元変更
    │   │   ├── s3_asset_repository.py
    │   │   └── line_notifier.py
    │   └── presentation/
    └── tests/
```

---

## 2. shared パッケージの設計

### 2.1 pyproject.toml

```toml
[project]
name = "shared"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "aws-lambda-powertools>=3.11.0",
    "boto3>=1.38.8",
    "pydantic>=2.11.4",
    "pydantic-settings>=2.9.1",
]

[tool.uv]
package = true
```

### 2.2 shared/src/shared/config/base_settings.py

両機能の `config/settings.py` から共通部分を抽出する。

```python
from aws_lambda_powertools import Logger
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_logger(logger: Logger | None = None) -> Logger:
    if logger is None:
        logger = Logger()
    return logger


class BaseEnvSettings(BaseSettings):
    """共通設定の基底クラス"""

    powertools_log_level: str = "INFO"
    data_bucket_name: str

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
```

### 2.3 shared/src/shared/infrastructure/ssm_parameter.py

既存の `ssm_parameter.py` をそのまま移動する（両機能でほぼ同一のため）。

```python
"""SSM Parameter Store からパラメータを取得"""

import json
import os
from typing import Any

import boto3


def _get_client():
    if os.environ.get("ENV") in ["local", "test"]:
        return boto3.client("ssm", region_name="ap-northeast-1", endpoint_url=os.environ["LOCAL_STACK_CONTAINER_URL"])
    return boto3.client("ssm", region_name="ap-northeast-1")


def get_ssm_json_parameter(name: str, decrypt: bool = True) -> dict[str, Any]:  # noqa: FBT001, FBT002
    client = _get_client()
    response = client.get_parameter(Name=name, WithDecryption=decrypt)
    parameters_json = response["Parameter"]["Value"]
    return json.loads(parameters_json)
```

### 2.4 shared/src/shared/domain/asset_object.py

summary-notification の `asset_object.py` を移動する（基本モデルのみ）。

```python
from pydantic import BaseModel


class DcpAssetInfo(BaseModel):
    """確定拠出年金の資産評価を扱う値クラス"""

    cumulative_contributions: int
    gains_or_losses: int
    asset_valuation: int


class DcpAssets(BaseModel):
    """資産情報（総評価 + 商品別）"""

    total: DcpAssetInfo
    products: dict[str, DcpAssetInfo]
```

---

## 3. 各機能の変更設計

### 3.1 config/settings.py の変更

#### web-scraping

```python
from shared.config.base_settings import BaseEnvSettings, get_logger  # noqa: F401


class EnvSettings(BaseEnvSettings):
    """スクレイピング関数の設定"""

    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    scraping_parameter_name: str


def get_settings(settings_instance: EnvSettings | None = None) -> EnvSettings:
    if settings_instance is None:
        settings_instance = EnvSettings()  # type: ignore (missing-argument)
    return settings_instance
```

#### summary-notification

```python
from shared.config.base_settings import BaseEnvSettings, get_logger  # noqa: F401


class EnvSettings(BaseEnvSettings):
    """サマリ通知関数の設定"""

    line_message_parameter_name: str


def get_settings(settings_instance: EnvSettings | None = None) -> EnvSettings:
    if settings_instance is None:
        settings_instance = EnvSettings()  # type: ignore (missing-argument)
    return settings_instance
```

### 3.2 domain の変更

#### web-scraping/src/domain/extraction_object.py

`DcpAssetInfo` と `DcpAssets` を shared から import し、HTML パース機能を追加するサブクラスにする。

```python
from shared.domain.asset_object import DcpAssetInfo as BaseDcpAssetInfo
from shared.domain.asset_object import DcpAssets


class DcpAssetInfo(BaseDcpAssetInfo):
    """HTML パース機能付き DcpAssetInfo"""

    @classmethod
    def from_html_strings(cls, ...) -> "DcpAssetInfo":
        ...

    @staticmethod
    def _parse_yen_amount(yen_str: str) -> int:
        ...

# DcpAssets は shared からそのまま re-export
__all__ = ["DcpAssetInfo", "DcpAssets"]
```

#### web-scraping/src/domain/__init__.py

```python
from .exceptions import ArtifactUploadError, ScrapingFailed, WebScrapingFailed
from .extraction_object import DcpAssetInfo, DcpAssets  # shared 経由
from .scraping_interface import IScraper
from .scraping_object import ScrapingParams
from .storage_interface import IObjectRepository
```

#### summary-notification/src/domain/__init__.py

`asset_object.py` を削除し、shared から import する。

```python
from shared.domain.asset_object import DcpAssetInfo, DcpAssets  # shared から直接

from .asset_interface import IAssetRepository
from .exceptions import AssetNotFound, NotificationFailed, SummaryNotificationFailed
from .indicator_object import DcpOpsIndicators
from .notification_interface import INotifier
from .notification_object import NotificationMessage
```

### 3.3 infrastructure/__init__.py の変更

#### web-scraping

```python
from shared.infrastructure.ssm_parameter import get_ssm_json_parameter  # shared から

from .s3_object_repository import S3ObjectRepository
from .selenium_scraper import SeleniumScraper
```

#### summary-notification

```python
from shared.infrastructure.ssm_parameter import get_ssm_json_parameter  # shared から

from .line_notifier import LineNotifier
from .s3_asset_repository import S3AssetRepository
```

### 3.4 handler.py の変更

各機能の `handler.py` で `get_logger` の import 元が変わる。

```python
# 変更前
from src.config.settings import get_logger

# 変更後（settings.py が get_logger を re-export するため、変更不要）
from src.config.settings import get_logger  # settings.py 内で shared から re-export 済み
```

→ **handler.py は変更不要**（settings.py が `get_logger` を re-export するため）

---

## 4. uv workspace 設定

### lambda/pyproject.toml（workspace root）

```toml
[tool.uv.workspace]
members = ["shared", "web-scraping", "summary-notification"]
```

### 各機能の pyproject.toml 変更点

#### web-scraping/pyproject.toml

```diff
 dependencies = [
-    "aws-lambda-powertools>=3.11.0",
-    "boto3>=1.38.8",
-    "pydantic>=2.11.4",
-    "pydantic-settings>=2.9.1",
+    "shared",
     "selenium>=4.33.0",
 ]

+[tool.uv.sources]
+shared = { workspace = true }

 [tool.ruff]
-extend = "../../pyproject.toml"
+extend = "../../pyproject.toml"  # パス変更なし（workspace root は lambda/ だが ruff root は project root）
```

#### summary-notification/pyproject.toml

```diff
 dependencies = [
-    "aws-lambda-powertools>=3.11.0",
-    "boto3>=1.38.8",
-    "pydantic>=2.11.4",
-    "pydantic-settings>=2.8.3",
+    "shared",
     "requests>=2.32.3",
 ]

+[tool.uv.sources]
+shared = { workspace = true }
```

---

## 5. CDK の変更設計

### 5.1 summary-notification: PythonFunction → lambda.Function

```typescript
// 変更前
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';

const summaryNotificationFunction = new PythonFunction(this, 'SummaryNotificationFunction', {
  runtime: lambda.Runtime.PYTHON_3_13,
  entry: path.join(__dirname, '../lambda/summary-notification'),
  index: 'src/handler.py',
  handler: 'handler',
  bundling: {
    assetExcludes: ['.venv'],
  },
  ...
});

// 変更後
const summaryNotificationFunction = new lambda.Function(this, 'SummaryNotificationFunction', {
  runtime: lambda.Runtime.PYTHON_3_13,
  handler: 'src.handler.handler',
  code: lambda.Code.fromAsset(path.join(__dirname, '../lambda'), {
    bundling: {
      image: cdk.DockerImage.fromRegistry('ghcr.io/astral-sh/uv:python3.13-bookworm-slim'),
      command: [
        'bash', '-c', [
          'cd summary-notification',
          'uv export --no-hashes --no-dev -o /tmp/requirements.txt',
          'pip install -r /tmp/requirements.txt -t /asset-output/',
          'cp -r src/ /asset-output/src/',
          'cp -r ../shared/src/shared /asset-output/shared/',
        ].join(' && '),
      ],
    },
  }),
  memorySize: 128,
  timeout: cdk.Duration.seconds(30),
  loggingFormat: lambda.LoggingFormat.JSON,
  logGroup: logGroup,
  applicationLogLevel: props.logLevel,
  environment: { ... },
});
```

### 5.2 web-scraping: ビルドコンテキスト変更

```typescript
// 変更前
code: lambda.DockerImageCode.fromImageAsset(
  path.join(__dirname, '../lambda/web-scraping'),
  { file: 'Dockerfile', extraHash: props.env?.region }
)

// 変更後
code: lambda.DockerImageCode.fromImageAsset(
  path.join(__dirname, '../lambda'),
  { file: 'web-scraping/Dockerfile', extraHash: props.env?.region }
)
```

### 5.3 Dockerfile の変更

```dockerfile
# 変更前
FROM public.ecr.aws/lambda/python:3.13 as builder
...
WORKDIR /app
RUN python3.13 -m pip install uv
COPY . ./
RUN uv export -o requirements.txt --no-hashes

FROM public.ecr.aws/lambda/python:3.13
...
COPY --from=builder /app/requirements.txt ./
RUN python3.13 -m pip install -r requirements.txt -t .
...
COPY ./src ./src
CMD ["src.handler.handler"]

# 変更後
FROM public.ecr.aws/lambda/python:3.13 as builder
...
WORKDIR /app
RUN python3.13 -m pip install uv

# workspace root と shared をコピー
COPY pyproject.toml ./
COPY shared/ ./shared/
COPY web-scraping/pyproject.toml web-scraping/uv.lock ./web-scraping/
RUN cd web-scraping && uv export -o /tmp/requirements.txt --no-hashes --no-dev

FROM public.ecr.aws/lambda/python:3.13
...
COPY --from=builder /tmp/requirements.txt ./
RUN python3.13 -m pip install -r requirements.txt -t .
...
# shared と src をコピー
COPY shared/src/shared ./shared
COPY web-scraping/src ./src
CMD ["src.handler.handler"]
```

### 5.4 package.json の変更

```diff
 "dependencies": {
-    "@aws-cdk/aws-lambda-python-alpha": "^2.233.0-alpha.0",
     "aws-cdk-lib": "^2.233.0",
     "constructs": "^10.4.4"
 }
```

---

## 6. テストコマンドの変更

### package.json

```diff
-"test:web-scraping": "cd lambda/web-scraping && ENV=test uv run pytest --cov -v --tb=short --disable-warnings --maxfail=1",
-"test:summary-notification": "cd lambda/summary-notification && ENV=test uv run pytest --cov -v --tb=short --disable-warnings --maxfail=1",
+"test:web-scraping": "cd lambda/web-scraping && ENV=test uv run pytest --cov -v --tb=short --disable-warnings --maxfail=1",
+"test:summary-notification": "cd lambda/summary-notification && ENV=test uv run pytest --cov -v --tb=short --disable-warnings --maxfail=1",
```

テストコマンド自体は変更なし。uv workspace では各メンバーディレクトリで `uv run` するとそのメンバーの依存が使われる。

### lefthook.yml

```diff
 test:web-scraping:
   glob: "lambda/web-scraping/**/*.py"
-  run: cd lambda/web-scraping && ENV=test uv run pytest --cov -v --tb=short --disable-warnings --maxfail=1
+  run: cd lambda/web-scraping && ENV=test uv run pytest --cov -v --tb=short --disable-warnings --maxfail=1

 test:summary-notification:
   glob: "lambda/summary-notification/**/*.py"
-  run: cd lambda/summary-notification && ENV=test uv run pytest --cov -v --tb=short --disable-warnings --maxfail=1
+  run: cd lambda/summary-notification && ENV=test uv run pytest --cov -v --tb=short --disable-warnings --maxfail=1
```

テストコマンド自体は変更なし。ただし shared の変更時にも両方のテストが走るように glob を調整する。

```yaml
test:web-scraping:
  glob:
    - "lambda/web-scraping/**/*.py"
    - "lambda/shared/**/*.py"          # shared の変更でも実行
  run: cd lambda/web-scraping && ENV=test uv run pytest --cov -v --tb=short --disable-warnings --maxfail=1

test:summary-notification:
  glob:
    - "lambda/summary-notification/**/*.py"
    - "lambda/shared/**/*.py"          # shared の変更でも実行
  run: cd lambda/summary-notification && ENV=test uv run pytest --cov -v --tb=short --disable-warnings --maxfail=1
```

---

## 7. import パス変更の影響範囲まとめ

### web-scraping

| ファイル | 変更内容 |
|---------|---------|
| `src/config/settings.py` | `BaseEnvSettings` を shared から継承、`get_logger` を re-export |
| `src/domain/__init__.py` | 変更なし（extraction_object.py が内部で shared を使用） |
| `src/domain/extraction_object.py` | `DcpAssetInfo` を shared から継承、`DcpAssets` を re-export |
| `src/infrastructure/__init__.py` | `get_ssm_json_parameter` を shared から re-export |
| `src/infrastructure/ssm_parameter.py` | 削除（shared に移動） |
| `src/handler.py` | 変更なし |
| `src/presentation/asset_collection_handler.py` | 変更なし（__init__.py 経由で re-export されるため） |

### summary-notification

| ファイル | 変更内容 |
|---------|---------|
| `src/config/settings.py` | `BaseEnvSettings` を shared から継承、`get_logger` を re-export |
| `src/domain/__init__.py` | `DcpAssetInfo`, `DcpAssets` を shared から直接 import |
| `src/domain/asset_object.py` | 削除（shared に移動） |
| `src/infrastructure/__init__.py` | `get_ssm_json_parameter` を shared から re-export |
| `src/infrastructure/ssm_parameter.py` | 削除（shared に移動） |
| `src/handler.py` | 変更なし |
| `src/presentation/summary_notification_handler.py` | 変更なし |

---

## 8. ドキュメント更新

### docs/functional-design.md

コンポーネント設計のディレクトリ構造に shared パッケージを追記する。

```
lambda/
├── shared/src/shared/          # 共通パッケージ（NEW）
│   ├── config/
│   ├── domain/
│   └── infrastructure/
├── {feature}/src/
│   ├── handler.py
│   ├── config/
│   ├── presentation/
│   ├── application/
│   ├── domain/
│   └── infrastructure/
```

---

## 9. 削除対象ファイル

| ファイル | 理由 |
|---------|------|
| `lambda/web-scraping/uv.lock` | workspace root の `uv.lock` に統合 |
| `lambda/summary-notification/uv.lock` | workspace root の `uv.lock` に統合 |
| `lambda/web-scraping/src/infrastructure/ssm_parameter.py` | shared に移動 |
| `lambda/summary-notification/src/infrastructure/ssm_parameter.py` | shared に移動 |
| `lambda/summary-notification/src/domain/asset_object.py` | shared に移動 |
