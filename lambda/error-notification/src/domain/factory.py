from src.domain.interface import Notification, NotificationError
from src.infrastructure.notification.line_notification_impl import LineNotification
from src.settings import get_settings

settings = get_settings()


class NotificationDestinations:
    """
    Notificationクラスをファーストコレクションとして扱い、登録されたNotificationの通知を実行する
    """

    def __init__(self) -> None:
        self.destinations: list[Notification] = []

    def add(self, destination: Notification) -> None:
        self.destinations.append(destination)

    def send(self, message: str) -> None:
        for destination in self.destinations:
            destination.send(message)


class NotificationDestinationsFactory:
    """NoticeDestinationsのFactoryクラス"""

    @staticmethod
    def create() -> NotificationDestinations:
        notice_destinations = NotificationDestinations()

        try:
            # LINE通知の設定
            if settings.line_message_api_token:
                notice_destinations.add(
                    LineNotification(settings.line_message_api_url, settings.line_message_api_token.get_secret_value())
                )
            return notice_destinations
        except Exception as e:
            raise NotificationError("NotificationDestinationsの作成に失敗しました。") from e
