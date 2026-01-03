# error-notification Lambda

## 概要

error-notification Lambda は、スクレイピング Lambda で発生したエラーを検知し、LINE Messaging API を通じて通知するための関数です。

## 主な機能

- CloudWatch Logs Subscription Filter をトリガーとして起動
- ERROR レベルのログを自動検知
- ログメッセージをパース・バリデーション（Pydantic 使用）
- LINE Messaging API へテキストメッセージ送信
- エラーハンドリング（S3 画像取得失敗時は テキストのみ送信）

## 処理シーケンス

```mermaid
sequenceDiagram
    participant CWL as CloudWatch Logs
    participant Filter as Subscription Filter
    participant ErrorLambda as エラー通知 Lambda
    participant S3 as S3
    participant LINE as LINE Messaging API

    Note over CWL: ERROR ログを受信

    CWL->>Filter: ログ配信
    activate Filter

    Filter->>ErrorLambda: トリガー (Subscription)
    activate ErrorLambda
    deactivate Filter

    ErrorLambda->>ErrorLambda: ログパース (Pydantic)
    Note right of ErrorLambda: ERROR レベルのみ抽出

    ErrorLambda->>LINE: テキストメッセージ送信
    activate LINE
    Note right of LINE: エラー詳細を通知
    LINE-->>ErrorLambda: 送信完了
    deactivate LINE
    deactivate ErrorLambda

    Note over ErrorLambda,LINE: 現在は画像送信未実装（テキストのみ送信）
```

## 環境変数

この Lambda は以下の環境変数を使用します:

| 環境変数 | 説明 | デフォルト値 |
|---------|------|-------------|
| `LINE_MESSAGE_PARAMETER_NAME` | LINE Message API 接続に必要な URL と Token を格納した SSM パラメータ名 | - |
| `ERROR_BUCKET_NAME` | エラー保存用 S3 バケット名 | - |
| `POWERTOOLS_LOG_LEVEL` | ログレベル (ERROR, WARNING, INFO, DEBUG) | INFO |

**注**: `LINE_MESSAGE_PARAMETER_NAME` と `ERROR_BUCKET_NAME` は必須です。

## 開発ガイド

開発環境のセットアップ、テスト実行、Lint/Format については、[CLAUDE.md](../../CLAUDE.md) を参照してください。

- **ディレクトリ構成**: 「Lambda 共通のディレクトリ構成」セクション
- **テスト戦略**: 「テスト戦略」セクション
- **開発コマンド**: 「開発コマンド」セクション
