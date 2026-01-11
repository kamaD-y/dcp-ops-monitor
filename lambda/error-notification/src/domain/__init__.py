"""Domain レイヤー: モデル、インターフェース、例外"""

from .exceptions import (
    CouldNotGenerateTemporaryUrl,
    ErrorNotificationError,
    LogsParseError,
    NotificationFailed,
)
from .interfaces import INotifier, IObjectRepository
from .models import ErrorLogRecord, LogsEventData, NotificationMessage, StorageLocation

__all__ = [
    # Models
    "ErrorLogRecord",
    "LogsEventData",
    "StorageLocation",
    "NotificationMessage",
    # Interfaces
    "IObjectRepository",
    "INotifier",
    # Exceptions
    "ErrorNotificationError",
    "LogsParseError",
    "NotificationFailed",
    "CouldNotGenerateTemporaryUrl",
]
