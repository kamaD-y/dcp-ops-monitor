from domain.dcp_ops_domain import (
    DcpOperationStatusNotifier,
    DcpOperationStatusTransformer,
)
from domain.extraction import DcpOpsMonitorExtractor


def main() -> None:
    """確定拠出年金 Web ページをスクレイピングし、結果を整形し通知する"""

    # データ抽出
    assets_info = DcpOpsMonitorExtractor().extract()

    # データ変換
    transformer = DcpOperationStatusTransformer()
    operational_indicators = transformer.transform(assets_info.total)
    message = transformer.make_message(assets_info, operational_indicators)

    # 通知
    notifier = DcpOperationStatusNotifier()
    notifier.notify(message)
