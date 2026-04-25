# 要求: summary-notification の資産情報取得元を Google Spreadsheet に変更

## 背景

web-scraping Lambda の資産蓄積方式が S3 JSON（`assets/{YYYY}/{MM}/{DD}.json`）から Google Spreadsheet（日次フラットレコード）に変更された（`steering-docs/20260211-asset-accumulation-review/` で対応済み）。

summary-notification Lambda は現在 `S3AssetRepository` で S3 から `DcpAssets` を取得しているが、新しいデータが S3 に蓄積されなくなるため、Google Spreadsheet からの取得に切り替える。

## 要求事項

### 資産情報の取得元変更

- S3 からの JSON 取得（`S3AssetRepository`）を廃止する
- Google Spreadsheet から最新の資産レコードを取得し、`DcpAssets` に変換する
- 既存の `IAssetRepository` インターフェースを維持し、Application 層に影響を与えない

### データ変換

- スプレッドシートには商品別フラットレコード（`AssetRecord` 形式）が蓄積されている
- 最新日付のレコードを取得し、`DcpAssets`（total + products）に変換する
- `total` は全商品の合算で算出する（スプレッドシートに total 行は存在しない）

### shared パッケージの整理

- `BaseEnvSettings` から `data_bucket_name` を除外し、web-scraping のローカル設定に移動する
- shared の `IAssetRecordRepository` は変更しない
- domain（`AssetRecord` モデル等）は shared に残し、infrastructure は各機能で個別実装する

### S3 依存の除去

- summary-notification Lambda から S3 への依存を完全に除去する
- CDK スタックから summary-notification の S3 関連設定（環境変数・権限）を削除する
- テストから LocalStack 依存を除去する

### CDK スタック更新

- summary-notification Lambda に `SPREADSHEET_PARAMETER_NAME` 環境変数と SSM 権限を追加する

## スコープ外

- shared の `IAssetRecordRepository` インターフェースの変更
- Application 層（指標計算・メッセージフォーマット）の変更
- `SummaryNotificationService` の変更
- LINE 通知機能の変更
