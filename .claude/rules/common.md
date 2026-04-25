# 共通開発ガイドライン

## 命名規則

### ファイル・ディレクトリ

| 種別 | 規則 | 例 |
|------|------|-----|
| Python ファイル | snake_case | `web_scraping_service.py` |
| TypeScript ファイル | kebab-case | `dcp-ops-monitor-stack.ts` |
| ディレクトリ | kebab-case | `summary-notification`, `web-scraping` |

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
├── docs/{ドキュメント名}  # ドキュメント更新
└── chore/{対象}          # ビルド・設定の変更
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

変更対象のモジュール名（例: `web-scraping`, `summary-notification`, `cdk`）

#### 例

```shell
feat(summary-notification): 運用指標の計算ロジックを追加

サマリ通知に運用利回りと想定受取額の
計算ロジックを追加
```

```shell
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

### コミット粒度

- pre-commit フックでテストが自動実行されるため、**テストが通る単位**でコミットする
- ソースコードとそれに対応するテストは同一コミットに含める
- 関連する変更を別々にコミットするとテストが壊れる場合は、一括でコミットする

### 必須事項

- 動作するコードを段階的にコミットする
- 既存の実装から学ぶ
- 3 回失敗したら停止して再評価する
