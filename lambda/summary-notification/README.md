# summary-notification

Google Spreadsheet に蓄積された資産情報を取得し、運用指標を計算してサマリを LINE 通知する Lambda 関数です。

## 機能概要

- EventBridge による週次スケジュール実行（毎週日曜 09:00 JST）
- Google Spreadsheet から最新の資産情報を取得
- 運用指標（運用年数、利回り、想定受取額）を計算
- サマリメッセージをフォーマットし LINE 経由で通知

## 通知内容

- 総評価（拠出金額累計、評価損益、資産評価額）
- 運用指標（運用年数、運用利回り、想定受取額）
- 資産評価額推移（直近1週間）

### サンプルメッセージ

```
確定拠出年金 運用状況通知Bot

拠出金額累計: 2,280,000円
評価損益: 456,000円
資産評価額: 2,736,000円

運用年数: 9.4年
運用利回り: 0.051
想定受取額(60歳): 6,540,000円

資産評価額推移（直近1週間）
2025-12-01: 2,720,000円 -
2025-12-02: 2,725,000円 +5,000円
2025-12-03: 2,730,000円 +5,000円
2025-12-04: 2,736,000円 +6,000円
2025-12-05: 2,736,000円 +0円
```

## 環境変数

この Lambda は以下の環境変数を使用します:

| 環境変数 | 説明 | デフォルト値 |
|---------|------|-------------|
| `LINE_MESSAGE_PARAMETER_NAME` | LINE 通知に必要な各種パラメータ（Channel Access Token、送信先 User ID 等）を格納した SSM パラメータ名 | - |
| `SPREADSHEET_PARAMETER_NAME` | Google Spreadsheet の接続設定（スプレッドシート ID、シート名、認証情報等）を格納した SSM パラメータ名 | - |
| `POWERTOOLS_LOG_LEVEL` | ログレベル (ERROR, WARNING, INFO, DEBUG) | INFO |

**注**: `LINE_MESSAGE_PARAMETER_NAME` と `SPREADSHEET_PARAMETER_NAME` は必須です。

## 開発ガイド

開発環境のセットアップ、テスト実行、Lint/Format については、[CLAUDE.md](../../CLAUDE.md) を参照してください。
