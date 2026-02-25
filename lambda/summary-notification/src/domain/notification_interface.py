from abc import ABC, abstractmethod


class INotifier(ABC):
    """通知インターフェース（LINE非依存）"""

    @abstractmethod
    def notify(self, messages: list[str]) -> None:
        """通知を送信

        Args:
            messages: 通知メッセージリスト

        Raises:
            NotificationFailed: 通知送信失敗時
        """
        pass
