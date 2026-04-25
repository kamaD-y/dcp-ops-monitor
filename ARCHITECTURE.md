# ARCHITECTURE.md

## Overview

DCP Ops Monitor は、確定拠出年金（Defined Contribution Plan）の運用状況を自動監視するシステムです。

平日に確定拠出年金 Web ページをスクレイピングして資産情報を Google Spreadsheet に蓄積し、週次で運用サマリを LINE に通知します。手動でのログイン・確認作業を自動化し、管理負荷を軽減することを目的としています。

## Code Map

### トップレベル

- `bin/dcp-ops-monitor.ts` — CDK アプリケーションエントリーポイント
- `lib/dcp-ops-monitor-stack.ts` — AWS リソース定義（Lambda、EventBridge、S3、SSM、CloudWatch Alarm、SNS）
- `lambda/` — Lambda 関数コード（uv workspace）
- `docs/` — 設計・要件ドキュメント

### Lambda

```text
lambda/
├── shared/          # 共通パッケージ（AssetEvaluation、AssetRecord、SSM クライアント）
├── web-scraping/    # 資産情報収集 Lambda（平日 09:00 JST 実行）
└── summary-notification/  # サマリ通知 Lambda（日曜 09:00 JST 実行）
```

各 Lambda は `presentation / application / domain / infrastructure` の 4 層構造で実装されています。詳細は `CONTRIBUTING.md` を参照。

### AWS サービス

| サービス | 用途 |
|---------|------|
| EventBridge | Lambda スケジュール実行 |
| Lambda | スクレイピング処理・通知処理 |
| SSM Parameter Store | 認証情報・設定値の管理 |
| S3 | スクレイピングエラー時のアーティファクト保存 |
| CloudWatch Alarm + SNS | Lambda エラー監視・通知 |

### 外部サービス

| サービス | 用途 |
|---------|------|
| Google Spreadsheet | 資産レコードの蓄積・取得 |
| LINE Messaging API | 週次サマリ通知 |

## Architecture Invariants

**依存方向（クリーンアーキテクチャ）**

```
Presentation → Application → Domain ← Infrastructure
```

- Domain 層は他のいかなる層にも依存しない
- Lambda 間の直接呼び出しは行わない（EventBridge によるスケジュール実行のみ）
- 認証情報はコードに埋め込まず、すべて SSM Parameter Store から取得する

## Cross-cutting Concerns

### エラーハンドリング

失敗は早期に検知し、ERROR ログを出力する。握りつぶさない。

- スクレイピング失敗時: スクリーンショット/HTML を S3 の `errors/` に保存してから ERROR ログ出力
- 通知失敗時: ERROR ログ出力 + Lambda リトライ（`NotificationFailed` 例外を raise）

### 監視

各 Lambda の `Errors` メトリクスを CloudWatch Alarm で監視し、エラー発生時は SNS Topic 経由で通知する。Lambda 未実行時（データポイントなし）はアラームを発火しない（`TreatMissingData: NOT_BREACHING`）。
