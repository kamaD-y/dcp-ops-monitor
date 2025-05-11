from domain.dcp_ops_domain import (
    DcpOperationsStatusScraper,
    DcpOperationStatusExtractor,
    DcpOperationStatusNotifier,
    DcpOperationStatusTransformer,
)


def main() -> None:
    """確定拠出年金 Web ページをスクレイピングし、結果を整形し通知する"""
    scraper = DcpOperationsStatusScraper()
    scraper.scrape()

    extractor = DcpOperationStatusExtractor()
    assets_info = extractor.extract(scraper.html_source)

    transformer = DcpOperationStatusTransformer()
    operational_indicators = transformer.transform(assets_info)

    notifier = DcpOperationStatusNotifier()
    message = notifier.make_message(assets_info, operational_indicators)
    notifier.notify(message)
