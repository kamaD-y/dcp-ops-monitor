---
globs: "lambda/**/*.py"
---

# Lambda（Python）開発ガイドライン

## コーディング規約

### 一般原則

- Python 3.13 を使用
- Pydantic でデータモデルを定義
- 型ヒントを必須とする
- docstring は関数・クラスの目的が明確な場合は省略可

### インポート順序

1. 標準ライブラリ
2. サードパーティライブラリ
3. ローカルモジュール

各グループは空行で区切り、アルファベット順に並べる（Ruff が自動整理）

### 例外処理

- 説明的なメッセージで早期に失敗させる
- 例外を黙って握りつぶさない
- 適切なレイヤーでエラーを処理する
- デバッグのためのコンテキストを含める

---

## 命名規則

| 種別 | 規則 | 例 |
|------|------|-----|
| クラス | PascalCase | `DcpAssetInfo`, `WebScrapingService` |
| 関数・メソッド | snake_case | `fetch_asset_valuation`, `send_notification` |
| 変数 | snake_case | `error_message`, `asset_valuation` |
| 定数 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| プライベート | 先頭に `_` | `_parse_html`, `_validate_input` |
| インターフェース | 先頭に `I` | `IScraper`, `INotifier` |

---

## テスト命名規則

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
