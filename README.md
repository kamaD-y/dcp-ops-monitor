# dcp-ops-monitor

[![ci](https://github.com/kamaD-y/dcp-ops-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/kamaD-y/dcp-ops-monitor/actions/workflows/ci.yml)
[![cd](https://github.com/kamaD-y/dcp-ops-monitor/actions/workflows/cd.yml/badge.svg)](https://github.com/kamaD-y/dcp-ops-monitor/actions/workflows/cd.yml)
![last commit](https://img.shields.io/github/last-commit/kamaD-y/dcp-ops-monitor)

このシステムは、確定拠出年金 (Defined Contribution Plan) の運用状況の管理を楽にする為、
週次で確定拠出年金 Web ページをスクレイピングし、運用指標をサマリして通知します。

※運用商品の見直しなどの操作には、対応していません。

構成及び、処理の流れは下記のとおりです。

## 構成
### 構成図

![Architecture](docs/images/dcp-ops-monitor.drawio.png)

## 処理シーケンス
## スクレイピング Lambda 処理シーケンス
TODO: 実装後に更新する。エラー時の処理含めて書く

```mermaid
sequenceDiagram
    participant Scheduler as EventBridge
    participant Scraping as スクレイピング処理
    participant Web as Web Page
    participant Notifications as 通知サービス (LINE etc.)
   
    Scheduler->>Scraping: スケジュール実行トリガー
    activate Scraping
    
    Scraping->>Web: Web スクレイピング
    activate Web
    Web-->>Scraping: HTML データ取得
    deactivate Web
    
    Scraping->>Scraping: HTML データ加工処理
    Scraping->>Scraping: 通知メッセージ整形
    
    Scraping->>Notifications: 運用指標サマリを送信
    deactivate Scraping
```

## エラー通知 Lambda 処理シーケンス
TODO: 実装後に書き直す

```mermaid
sequenceDiagram
    participant Scheduler as EventBridge
    participant ETL as ETL Lambda
    participant Web as 対象サイト
    participant S3 as S3
    participant CWL as CloudWatch Logs
    participant Alarm as CloudWatch Alarm
    participant SNS_F as SNS Failure
    participant Notify as 通知 Lambda
    participant Notifications as 通知サービス (LINE etc.)

    Note over Scheduler, Notifications: 異常処理フロー
    
    Scheduler->>ETL: 週次実行トリガー
    activate ETL
    
    ETL->>Web: スクレイピング開始
    activate Web
    Web-->>ETL: エラー発生
    deactivate Web
    Note right of Web: デバッグ用スクリーンショット
    
    ETL->>S3: エラー画面を PNG 保存
    activate S3
    S3-->>ETL: 保存完了
    deactivate S3
    
    ETL->>ETL: 例外を Throw
    ETL->>CWL: エラーログ出力
    activate CWL
    deactivate ETL
    Note right of CWL: 詳細なエラー情報
    
    CWL->>Alarm: ログベースアラーム発火
    activate Alarm
    deactivate CWL
    
    Alarm->>SNS_F: アラーム通知
    activate SNS_F
    deactivate Alarm
    
    SNS_F->>Notify: Failure Event でトリガー
    activate Notify
    deactivate SNS_F
    
    Notify->>CWL: エラーログ取得
    activate CWL
    CWL-->>Notify: エラーログ返却
    deactivate CWL
       
    Notify->>Notifications: エラーメッセージ送信
    activate Notifications
    Note right of Notifications: エラー詳細と S3 画像 URL を通知
    Notifications-->>Notify: 送信完了
    deactivate Notifications
    deactivate Notify
    
    Note over Scheduler, Notifications: エラー処理完了
```
