# 要求内容: ドキュメント最新化 (issue-137)

## 背景

複数の改善PRにより、以下の変更が行われた。しかし README 等のドキュメントに反映されていない箇所が存在する。

### 変更済みの主な実装変更

| PR / コミット | 変更内容 |
|---|---|
| improve/issue-127 系 | summary-notification の資産情報取得元を S3 → Google Spreadsheet に変更 |
| improve/issue-127 系 | web-scraping の資産情報保存先を S3 → Google Spreadsheet に変更 |
| improve/issue-127 系 | summary-notification から S3 依存を除去し SSM スプレッドシート設定を追加 |

---

## ドキュメントとコードの乖離

### 1. `lambda/web-scraping/README.md`

| 箇所 | 現在の記載 | 正しい内容 |
|---|---|---|
| 主な機能（L12） | "資産情報の JSON 形式での S3 保存" | Google Spreadsheet への資産レコード保存 |
| シーケンス図（L17-38） | `S3 as S3` → `JSON 保存（assets/{YYYY}/{MM}/{DD}.json）` | `GSheet as Google Spreadsheet` → 資産レコード保存（日次フラットレコード） |
| 環境変数テーブル（L44-51） | `SPREADSHEET_PARAMETER_NAME` が未記載 | 追加が必要 |
| 環境変数テーブル（L44-51） | `DATA_BUCKET_NAME` の説明が不明確 | エラーアーティファクト保存用 S3 バケット名 であることを明確化 |

### 2. `lambda/summary-notification/README.md`

| 箇所 | 現在の記載 | 正しい内容 |
|---|---|---|
| 機能概要（L8） | "S3 から最新の資産情報 JSON を取得" | Google Spreadsheet から最新の資産情報を取得 |
| ディレクトリ構成（L54） | `s3_asset_repository.py  # S3 資産リポジトリ` | `google_sheet_asset_repository.py  # Google Spreadsheet 資産リポジトリ` |
| ディレクトリ構成（L55） | `ssm_parameter.py  # SSM パラメータ取得` | 削除（shared パッケージに移動済み） |
| 環境変数セクション | 存在しない | `LINE_MESSAGE_PARAMETER_NAME`, `SPREADSHEET_PARAMETER_NAME`, `POWERTOOLS_LOG_LEVEL` を記載 |

### 3. `docs/functional-design.md`

最新コミット（5de1987）で既に Google Spreadsheet 対応の内容に更新済み。変更不要。

---

## 要求

- `lambda/web-scraping/README.md` を実装の現状に合わせて更新する
- `lambda/summary-notification/README.md` を実装の現状に合わせて更新する
