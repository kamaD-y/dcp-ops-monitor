"""ILineNotifier Mock implementation"""

from src.domain import ILineNotifier, LineMessage


class MockLineNotifier(ILineNotifier):
    """LINE通知クライアントのMock実装（外部API呼び出しのため）"""

    def __init__(self):
        self.send_messages_called = False
        self.messages_sent: list[LineMessage] = []

    def send_messages(self, messages: list[LineMessage]) -> None:
        """メッセージ送信（Mock）"""
        self.send_messages_called = True
        self.messages_sent = messages
