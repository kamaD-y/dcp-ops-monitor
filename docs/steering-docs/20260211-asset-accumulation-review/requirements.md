# 要求定義: 資産情報蓄積方式の見直し

## 背景

現在、web-scraping Lambda は資産情報を日次の JSON ファイルとして S3 に保存している（`assets/{YYYY}/{MM}/{DD}.json`）。
この方式では BI ツールでの可視化に不向きなため、蓄積方式を見直す。

## 目的

- 収集した資産情報を BI ツールで可視化できるデータ形式で蓄積する
- 将来的なデータストア変更（CSV / Google Spreadsheet / DynamoDB 等）に対応可能な設計とする

## 機能要件

### データ蓄積機能

- web-scraping Lambda でスクレイピング完了後、資産情報をデータストアに追記する
- データストアの初回実装は Google Spreadsheet とする
- Google Spreadsheet API の認証情報は SSM Parameter Store で管理する

### データ構造

商品別のフラットなレコード形式で蓄積する（総合 (total) は合計で算出可能なため持たない）。

| カラム | 型 | 説明 |
|--------|-----|------|
| date | date | 取得日 |
| product | str | 商品名 |
| asset_valuation | int | 資産評価額 |
| cumulative_contributions | int | 拠出金額累計 |
| gains_or_losses | int | 評価損益 |

### 既存機能の変更

- 現在の S3 への JSON 保存（`assets/{YYYY}/{MM}/{DD}.json`）を廃止し、新しい蓄積方式に置き換える

## 設計方針

- 共通インターフェース・ドメインモデルは `lambda/shared/` パッケージに配置する
  - summary-notification Lambda からも将来的に同じインターフェースで参照可能にするため
- Infrastructure 層の Google Spreadsheet 実装は `lambda/web-scraping/` に配置する

## スコープ

### 対象

- `lambda/shared/` - 共通ドメインモデル・インターフェースの追加
- `lambda/web-scraping/` - Infrastructure（Google Spreadsheet 実装）、Application、Presentation 各層の改修
- CDK スタック - SSM パラメータ参照の追加（Google Spreadsheet 認証情報）
- `docs/` - 機能設計書の更新

### スコープ外

- summary-notification Lambda の改修（別タスクで対応）
- BI ツール側の設定・ダッシュボード構築

## 影響範囲

### 影響を受けるコンポーネント

- `summary-notification` Lambda - S3 保存廃止により、資産情報の取得元を変更する必要がある（別タスクで対応。shared に配置した共通インターフェースを利用する想定）
