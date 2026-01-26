# 開発ガイドライン

## コーディング規約

### Python

#### 一般原則

- Python 3.13 を使用
- Pydantic でデータモデルを定義
- 型ヒントを必須とする
- docstring は関数・クラスの目的が明確な場合は省略可

#### インポート順序

1. 標準ライブラリ
2. サードパーティライブラリ
3. ローカルモジュール

各グループは空行で区切り、アルファベット順に並べる（Ruff が自動整理）

#### 例外処理

- 説明的なメッセージで早期に失敗させる
- 例外を黙って握りつぶさない
- 適切なレイヤーでエラーを処理する
- デバッグのためのコンテキストを含める

### TypeScript

#### 一般原則

- 型定義を必須とする
- `any` の使用を避ける
- 関数は単一責任を持つ

---

## 命名規則

### Python

| 種別 | 規則 | 例 |
|------|------|-----|
| クラス | PascalCase | `DcpAssetInfo`, `WebScrapingService` |
| 関数・メソッド | snake_case | `fetch_asset_page`, `send_notification` |
| 変数 | snake_case | `error_message`, `asset_valuation` |
| 定数 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| プライベート | 先頭に `_` | `_parse_html`, `_validate_input` |
| インターフェース | 先頭に `I` | `IDcpScraper`, `INotifier` |

### TypeScript

| 種別 | 規則 | 例 |
|------|------|-----|
| クラス・インターフェース | PascalCase | `DcpOpsMonitorStack` |
| 関数・変数 | camelCase | `errorBucket`, `webScrapingFunction` |
| 定数 | UPPER_SNAKE_CASE または camelCase | `LOG_LEVEL` |

### ファイル・ディレクトリ

| 種別 | 規則 | 例 |
|------|------|-----|
| Python ファイル | snake_case | `web_scraping_service.py` |
| TypeScript ファイル | kebab-case | `dcp-ops-monitor-stack.ts` |
| ディレクトリ | kebab-case | `error-notification`, `web-scraping` |

---

## スタイリング規約

リンティング / フォーマッタ の設定に従う

---

## テスト規約

### テスト戦略

- **LocalStack 使用**: AWS サービスは LocalStack でテスト
- **Mock 最小限の原則**: 外部 API のみ Mock を使用
- **カバレッジ要件**: 60% 以上

### テスト構成

```
lambda/{feature}/tests/
├── conftest.py           # pytest 設定、共通フィクスチャ
├── presentation/         # Presentation 層のテスト
├── application/          # Application 層のテスト
├── domain/               # Domain 層のテスト
├── infrastructure/       # Infrastructure 層のテスト
└── fixtures/             # テストデータ
```

### 命名規則

- テストファイル: `test_{対象モジュール名}.py`
- テスト関数: `test_{テスト対象}__{条件や期待結果}`

```python
def test_extract_total_assets__valid_html_returns_dcp_assets():
    """有効な HTML から資産情報が抽出できる"""
    ...

def test_send_notification__api_error_raises_exception():
    """API エラー時に例外が発生する"""
    ...
```

### テストの原則

- 実装ではなく動作をテストする
- テストごとに 1 つのアサーション（できる限り）
- シナリオを説明する明確なテスト名
- テストは決定論的であるべき

---

## Git 規約

### ブランチ戦略

```
main
├── feature/{機能名}      # 新機能開発
├── fix/{バグ名}          # バグ修正
├── improve/{対象}        # 既存機能の改善
├── refactor/{対象}       # リファクタリング
└── docs/{ドキュメント名}  # ドキュメント更新
```

### コミットメッセージ

[Conventional Commits](https://www.conventionalcommits.org/) に従う。

```
<type>(<scope>): <description>

[optional body]
```

#### Type

| Type | 説明 |
|------|------|
| feat | 新機能の追加 |
| improve | 既存機能の改善・強化 |
| fix | バグ修正 |
| refactor | リファクタリング（機能変更なし） |
| test | テストの追加・修正 |
| docs | ドキュメントのみの変更 |
| chore | ビルド・設定の変更 |

#### Scope（任意）

変更対象のモジュール名（例: `web-scraping`, `error-notification`, `cdk`）

#### 例

```
feat(error-notification): CloudWatch Logs リンクを通知に追加

エラー通知メッセージに CloudWatch Logs コンソールへの
直接リンクを追加し、デバッグを効率化
```

```
improve(web-scraping): エラーメッセージの詳細化

スクレイピング失敗時のエラーメッセージに
ページ URL とステータスコードを追加
```

### コミット前チェック

lefthook による pre-commit フックが以下を自動実行:

- Biome: TypeScript のリント・フォーマット
- Ruff: Python のリント・フォーマット
- 型チェック
- テスト実行

### 禁止事項

- `--no-verify` でフックをバイパスしない
- テストを無効化するのではなく修正する
- コンパイル・テストが通らないコードをコミットしない

### 必須事項

- 動作するコードを段階的にコミットする
- 既存の実装から学ぶ
- 3 回失敗したら停止して再評価する
