# web-scraping

平日 09:00 JST に EventBridge で起動し、確定拠出年金 Web ページをスクレイピングして資産情報を Google Spreadsheet に保存する Lambda 関数です。

Selenium の依存関係の問題を回避するため、Docker コンテナイメージとしてデプロイします。

詳細は [CONTRIBUTING.md](../../docs/CONTRIBUTING.md) を参照してください。
