from domain.dcp_ops_domain import (
    DcpOperationsStatusScraper,
    DcpOperationStatusExtractor,
    DcpOperationStatusNotifier,
    DcpOperationStatusTransformer,
)


def main() -> None:
    """確定拠出年金 Web ページをスクレイピングし、結果を整形し通知する"""
    scraper = DcpOperationsStatusScraper()
    html_source = scraper.scrape()

    extractor = DcpOperationStatusExtractor()
    assets_info = extractor.extract(html_source)

    transformer = DcpOperationStatusTransformer()
    operational_indicators = transformer.transform(assets_info.total)
    message = transformer.make_message(assets_info, operational_indicators)

    notifier = DcpOperationStatusNotifier()
    notifier.notify(message)
