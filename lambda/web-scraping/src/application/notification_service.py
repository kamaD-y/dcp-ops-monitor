"""通知送信サービス"""

from application.message_formatter import format_dcp_ops_message
from domain import DcpAssets, DcpOpsIndicators, INotifier, NotificationMessage


class NotificationService:
    """通知送信サービス

    DCP 運用状況をメッセージにフォーマットし、通知を送信する
    """

    def __init__(self, notifier: INotifier) -> None:
        """通知送信サービスを初期化

        Args:
            notifier: 通知送信を行う実装
        """
        self.notifier = notifier

    def send_notification(self, assets_info: DcpAssets, ops_indicators: DcpOpsIndicators) -> None:
        """DCP 運用状況の通知を送信

        Args:
            assets_info: 資産情報
            ops_indicators: 運用指標

        Raises:
            NotificationFailed: 通知送信失敗時
        """
        # メッセージをフォーマット
        message_text = format_dcp_ops_message(assets_info, ops_indicators)

        # NotificationMessage を作成
        notification_message = NotificationMessage(text=message_text)

        # 通知を送信
        self.notifier.notify([notification_message])
