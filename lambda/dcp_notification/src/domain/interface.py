from abc import ABC, abstractmethod


class Notification(ABC):
    """通知クラス(抽象クラス)"""

    @abstractmethod
    def send(self, message: str) -> bool:
        pass


class NotificationError(Exception):
    """通知に関するエラー"""

    pass
