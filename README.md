# dcp-ops-monitor

[![ci](https://github.com/kamaD-y/dcp-ops-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/kamaD-y/dcp-ops-monitor/actions/workflows/ci.yml)
[![cd](https://github.com/kamaD-y/dcp-ops-monitor/actions/workflows/cd.yml/badge.svg)](https://github.com/kamaD-y/dcp-ops-monitor/actions/workflows/cd.yml)
![last commit](https://img.shields.io/github/last-commit/kamaD-y/dcp-ops-monitor)

このシステムは、確定拠出年金 (Defined Contribution Plan) の運用状況の管理を楽にする為、
平日に確定拠出年金 Web ページをスクレイピングし、資産情報を S3 に蓄積します。

※運用商品の見直しなどの操作には、対応していません。

構成及び、処理の流れは下記のとおりです。

## 構成
### 構成図

![Architecture](docs/dcp-ops-monitor.drawio.png)

## 搭載機能

### 1. 資産情報収集
平日に確定拠出年金の Web ページにアクセスし、資産情報をスクレイピングして S3 に保存します。

**機能概要:**
- EventBridge によるスケジュール実行（平日 09:00 JST）
- Selenium を使用した Web スクレイピング
- 資産情報の JSON 形式での S3 保存

詳細は [lambda/web-scraping/README.md](lambda/web-scraping/README.md) を参照してください。

### 2. エラー通知
Web スクレイピングで発生したエラーを検知し、通知します。

**機能概要:**
- CloudWatch Logs Subscription Filter による自動起動
- ERROR レベルのログ抽出・パース
- エラーログの通知送信

詳細は [lambda/error-notification/README.md](lambda/error-notification/README.md) を参照してください。
