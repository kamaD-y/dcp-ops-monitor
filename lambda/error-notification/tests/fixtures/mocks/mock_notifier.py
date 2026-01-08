"""テスト用 Mock Notifier"""

from src.domain import INotifier, NotificationMessage


class MockNotifier(INotifier):
    """テスト用 Mock Notifier

    notify() の呼び出しを記録し、テストで検証可能にする
    """

    def __init__(self) -> None:
        """Mock Notifier を初期化"""
        self.notify_called = False
        self.messages_sent: list[NotificationMessage] = []

    def notify(self, messages: list[NotificationMessage]) -> None:
        """通知を送信 (Mock: 実際には送信せず記録のみ)

        Args:
            messages: 通知メッセージリスト
        """
        self.notify_called = True
        self.messages_sent.extend(messages)
