"""LINE 通知インターフェース"""

from abc import ABC, abstractmethod

from .line_message import LineMessage


class ILineNotifier(ABC):
    """LINE 通知インターフェース"""

    @abstractmethod
    def send_messages(self, messages: list[LineMessage]) -> None:
        """LINE メッセージを送信

        Args:
            messages: 送信するメッセージリスト

        Raises:
            LineNotificationError: 送信失敗時
        """
        pass
