"""Domain レイヤー: モデル、インターフェース、例外"""

from .error_log_interface import IErrorLogEventsAdapter
from .error_log_object import ErrorLogEvents, ErrorRecord
from .exceptions import (
    CouldNotGenerateTemporaryUrl,
    ErrorNotificationFailed,
    LogsParseFailed,
    NotificationFailed,
)
from .interfaces import IObjectRepository
from .models import StorageLocation
from .notification_interface import INotifier
from .notification_object import NotificationMessage

__all__ = [
    # Models
    "ErrorRecord",
    "ErrorLogEvents",
    "StorageLocation",
    "NotificationMessage",
    # Interfaces
    "IErrorLogEventsAdapter",
    "IObjectRepository",
    "INotifier",
    # Exceptions
    "ErrorNotificationFailed",
    "LogsParseFailed",
    "NotificationFailed",
    "CouldNotGenerateTemporaryUrl",
]
