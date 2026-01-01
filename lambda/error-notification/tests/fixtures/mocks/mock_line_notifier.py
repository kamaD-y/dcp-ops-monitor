"""ILineNotifier Mock implementation"""

from src.domain import ILineNotifier, LineMessage


class MockLineNotifier(ILineNotifier):
    """LINE通知クライアントのMock実装（外部API呼び出しのため）"""

    def __init__(self, upload_should_fail: bool = False):
        self.send_messages_called = False
        self.messages_sent: list[LineMessage] = []
        self.upload_should_fail = upload_should_fail

    def send_messages(self, messages: list[LineMessage]) -> None:
        """メッセージ送信（Mock）"""
        self.send_messages_called = True
        self.messages_sent = messages

    def upload_image_and_get_url(self, image_data: bytes) -> str:
        """画像アップロード（Mock）"""
        if self.upload_should_fail:
            raise NotImplementedError("Mock: 画像アップロード機能は未実装です")
        return "https://example.com/mock_image.jpg"
