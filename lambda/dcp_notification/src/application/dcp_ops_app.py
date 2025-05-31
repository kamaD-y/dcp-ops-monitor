from src.domain.factory import NotificationDestinationsFactory


def main(message: str) -> None:
    notifications = NotificationDestinationsFactory.create()
    notifications.notify(message)
