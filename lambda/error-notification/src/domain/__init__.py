"""Domain レイヤー: モデル、インターフェース、例外"""

from .error_log_interface import IErrorLogEventsAdapter
from .error_log_object import ErrorLogEvents, ErrorRecord
from .exceptions import (
    CouldNotGenerateTemporaryUrl,
    ErrorNotificationFailed,
    LogsParseFailed,
    NotificationFailed,
)
from .interfaces import INotifier, IObjectRepository
from .models import NotificationMessage, StorageLocation

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
