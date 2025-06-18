from domain.dcp_ops_domain import (
    DcpOperationsStatusScraper,
    DcpOperationStatusExtractor,
    DcpOperationStatusNotifier,
    DcpOperationStatusTransformer,
)


def main() -> None:
    """確定拠出年金 Web ページをスクレイピングし、結果を整形し通知する"""
    # スクレイピング
    scraper = DcpOperationsStatusScraper()
    html_source = scraper.scrape()

    # データ抽出
    extractor = DcpOperationStatusExtractor()
    assets_info = extractor.extract(html_source)

    # データ変換
    transformer = DcpOperationStatusTransformer()
    operational_indicators = transformer.transform(assets_info.total)
    message = transformer.make_message(assets_info, operational_indicators)

    # 通知
    notifier = DcpOperationStatusNotifier()
    notifier.notify(message)
