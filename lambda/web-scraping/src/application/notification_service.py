from domain import DcpAssets, DcpOpsIndicators, INotifier


class NotificationService:
    def __init__(self, notifier: INotifier) -> None:
        self.notifier: INotifier = notifier

    def send_notification(self, assets_info: DcpAssets, ops_indicators: DcpOpsIndicators) -> None:
        message = self.notifier.create_message_by(assets_info, ops_indicators)
        self.notifier.send(message)
