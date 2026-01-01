"""Domain レイヤー: モデル、インターフェース、例外"""

from .cloudwatch_logs_parser_interface import ICloudWatchLogsParser
from .error_log_record import ErrorLogRecord
from .exceptions import (
    CloudWatchLogsParseError,
    ErrorNotificationError,
    LineNotificationError,
    S3ImageDownloadError,
)
from .line_message import LineImageMessage, LineMessage, LineTextMessage
from .line_notifier_interface import ILineNotifier
from .s3_client_interface import IS3Client

__all__ = [
    # Models
    "ErrorLogRecord",
    "LineTextMessage",
    "LineImageMessage",
    "LineMessage",
    # Interfaces
    "ICloudWatchLogsParser",
    "IS3Client",
    "ILineNotifier",
    # Exceptions
    "ErrorNotificationError",
    "CloudWatchLogsParseError",
    "S3ImageDownloadError",
    "LineNotificationError",
]
