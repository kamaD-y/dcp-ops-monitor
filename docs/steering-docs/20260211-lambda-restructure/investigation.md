# Lambda ディレクトリ構造 見直し検討

## 最終方針

### 優先順位

1. **管理の容易さ** - ディレクトリ構造、コマンド、設定をシンプルに保つ
2. **パッケージ依存の分離** - Selenium が summary-notification に混入しないようにする
3. **コード重複は許容** - 共通コードの切り出しはサイズが小さいため必須ではない

### 決定事項

- **アプローチ**: uv workspace + shared パッケージ（ハイブリッド構造）
- **CDK バンドリング**: summary-notification を `PythonFunction` (alpha) → `lambda.Function` + `Code.fromAsset` に変更
- **構造**: 縦割り（機能単位）は維持しつつ、共通部分のみ shared に切り出す
- **workspace root**: virtual workspace（パッケージを持たない）

### スコープ外

- テストコマンドの統一（`test:web-scraping`, `test:summary-notification` は現状維持）

---

## 1. 現状の構造

```
lambda/
├── web-scraping/           # Docker Lambda (Selenium使用)
│   ├── Dockerfile
│   ├── pyproject.toml      # selenium, boto3, pydantic, powertools 等
│   ├── uv.lock
│   ├── src/
│   │   ├── handler.py
│   │   ├── config/settings.py
│   │   ├── domain/         # exceptions, scraping_object, extraction_object, interfaces
│   │   ├── application/    # web_scraping_service
│   │   ├── infrastructure/ # ssm_parameter, s3_object_repository, selenium_scraper
│   │   └── presentation/   # asset_collection_handler
│   └── tests/
│
└── summary-notification/   # Python Lambda (PythonFunction alpha でバンドル)
    ├── pyproject.toml      # requests, boto3, pydantic, powertools 等
    ├── uv.lock
    ├── src/
    │   ├── handler.py
    │   ├── config/settings.py
    │   ├── domain/         # exceptions, asset_object, indicator_object, notification_object, interfaces
    │   ├── application/    # summary_notification_service, indicators_calculator, message_formatter
    │   ├── infrastructure/ # ssm_parameter, s3_asset_repository, line_notifier
    │   └── presentation/   # summary_notification_handler
    └── tests/
```

### 現状の課題

- `ssm_parameter.py`, `config/settings.py` 等の共通コードが機能毎に重複
- 各機能に独立した `pyproject.toml` と `uv.lock` があり、共通依存のバージョン管理が分散

---

## 2. 重複コードの詳細

| モジュール | 場所 | 重複度 | 内容 |
|-----------|------|--------|------|
| **SSM Parameter** | 両方の `infrastructure/ssm_parameter.py` | ~95% | `_get_client()`, `get_ssm_json_parameter()` - LocalStack 対応含む |
| **Config/Settings** | 両方の `config/settings.py` | ~90% | `get_logger()`, `EnvSettings`(BaseSettings), `get_settings()` |
| **DcpAssetInfo** | `extraction_object.py` / `asset_object.py` | ~40% | Pydantic モデル定義。web-scraping版は HTML パース用メソッド付き |
| **S3 クライアント初期化** | 両方の `infrastructure/s3_*.py` | ~30% | ENV に応じた LocalStack/本番の切り替えロジック |
| **Handler パターン** | 両方の `handler.py` | ~85% | logger 注入、try/except 構造 |

---

## 3. 依存パッケージの比較

| パッケージ | web-scraping | summary-notification | 共通化先 |
|-----------|:---:|:---:|:---:|
| aws-lambda-powertools | ✓ | ✓ | shared |
| boto3 | ✓ | ✓ | shared |
| pydantic | ✓ | ✓ | shared |
| pydantic-settings | ✓ | ✓ | shared |
| **selenium** | ✓ | - | web-scraping のみ |
| **requests** | - | ✓ | summary-notification のみ |

---

## 4. 提案する新しい構造

```
lambda/
├── pyproject.toml              # uv virtual workspace 定義
├── uv.lock                     # workspace 全体で共有するロックファイル
│
├── shared/                     # 共通パッケージ (workspace member)
│   ├── pyproject.toml          # boto3, pydantic, powertools 等の共通依存
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
├── web-scraping/               # (workspace member)
│   ├── Dockerfile
│   ├── pyproject.toml          # shared + selenium
│   ├── src/
│   │   ├── handler.py
│   │   ├── config/settings.py
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── presentation/
│   └── tests/
│
└── summary-notification/       # (workspace member)
    ├── pyproject.toml          # shared + requests
    ├── src/
    │   ├── handler.py
    │   ├── config/settings.py
    │   ├── domain/
    │   ├── application/
    │   ├── infrastructure/
    │   └── presentation/
    └── tests/
```

---

## 5. shared に切り出すもの / 切り出さないもの

### 切り出す

- `ssm_parameter.py` - ほぼ同一コード
- `config/base_settings.py` - `get_logger()` と基底 Settings クラス
- `domain/asset_object.py` - `DcpAssetInfo` 基本モデル

### 切り出さない

- `handler.py` - 機能固有の例外処理が異なる
- `exceptions.py` - 機能固有のドメイン例外
- S3 リポジトリ - メソッドが異なる（put vs get）
- インターフェース定義 - 機能固有の契約

---

## 6. CDK の変更

### summary-notification: PythonFunction → lambda.Function + Code.fromAsset

- `lambda/` 全体をマウントし、カスタムバンドリングで shared を含める
- `@aws-cdk/aws-lambda-python-alpha` 依存を削除

### web-scraping: ビルドコンテキスト変更

- `fromImageAsset` のパスを `lambda/web-scraping/` → `lambda/` に変更
- Dockerfile 内で shared を参照可能にする

---

## 7. その他の変更箇所

| 変更対象 | 内容 |
|---------|------|
| `package.json` | テストコマンドのパス調整、`@aws-cdk/aws-lambda-python-alpha` 削除 |
| `lefthook.yml` | テストフックのコマンドパス調整 |
| `pyproject.toml` (root) | Ruff 設定は変更不要（`**/*.py` 指定のため） |
| CDK スナップショットテスト | スタック変更に伴うスナップショット更新 |

---

## 8. リスク・注意点

- CDK バンドリングコマンドの動作確認が必要（`cdk synth` でテスト可能）
- Dockerfile のビルドコンテキスト変更で Docker キャッシュが効かなくなる可能性
- 既存の CDK スナップショットテストが破壊される（更新が必要）
- shared パッケージの変更が両機能に影響 → lefthook の glob パターン調整が必要
