from domain.dcp_ops_domain import DcpOperationStatusNotifier
from domain.extraction import DcpOpsMonitorExtractor
from domain.transform import DcpOpsMonitorTransformer


def main() -> None:
    """確定拠出年金 Web ページをスクレイピングし、結果を整形し通知する"""

    # データ抽出
    assets_info = DcpOpsMonitorExtractor().extract()

    # データ変換
    transformer = DcpOpsMonitorTransformer()
    operational_indicators = transformer.calculate_ops_indicators(assets_info.total)
    message = transformer.make_message(assets_info, operational_indicators)

    # 通知
    notifier = DcpOperationStatusNotifier()
    notifier.notify(message)
