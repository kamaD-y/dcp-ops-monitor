# summary-notification

S3 に蓄積された資産情報を取得し、運用指標を計算してサマリを LINE 通知する Lambda 関数です。

## 機能概要

- EventBridge による週次スケジュール実行（毎週日曜 09:00 JST）
- S3 から最新の資産情報 JSON を取得
- 運用指標（運用年数、利回り、想定受取額）を計算
- サマリメッセージをフォーマットし LINE 経由で通知

## 通知内容

- 総評価（拠出金額累計、評価損益、資産評価額）
- 運用指標（運用年数、運用利回り、目標利回り、想定受取額）
- 商品別資産情報

## セットアップ

```bash
cd lambda/summary-notification
uv sync
```

## テスト

```bash
ENV=test uv run pytest --cov -v --tb=short --disable-warnings
```

## アーキテクチャ

クリーンアーキテクチャに基づく 4 層構造:

```
src/
├── handler.py                    # Lambda エントリーポイント
├── config/
│   └── settings.py               # 環境設定
├── presentation/
│   └── summary_notification_handler.py  # イベント処理・DI
├── application/
│   ├── summary_notification_service.py  # サマリ通知サービス
│   ├── indicators_calculator.py         # 運用指標計算
│   └── message_formatter.py             # メッセージフォーマット
├── domain/
│   ├── asset_object.py           # DcpAssetInfo, DcpAssets
│   ├── indicator_object.py       # DcpOpsIndicators
│   ├── notification_object.py    # NotificationMessage
│   ├── asset_interface.py        # IAssetRepository
│   ├── notification_interface.py # INotifier
│   └── exceptions.py             # ドメイン例外
└── infrastructure/
    ├── s3_asset_repository.py    # S3 資産リポジトリ
    ├── line_notifier.py          # LINE 通知アダプター
    └── ssm_parameter.py          # SSM パラメータ取得
```
