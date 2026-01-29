from abc import ABC, abstractmethod

from .notification_object import NotificationMessage


class INotifier(ABC):
    """通知インターフェース"""

    @abstractmethod
    def notify(self, messages: list[NotificationMessage]) -> None:
        """通知を送信

        Args:
            messages: 通知メッセージリスト

        Raises:
            NotificationFailed: 通知送信失敗時
        """
        pass
