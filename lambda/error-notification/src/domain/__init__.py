"""Domain レイヤー: モデル、インターフェース、例外"""

from .cloudwatch_logs_parser_interface import ICloudWatchLogsParser
from .error_log_record import ErrorLogRecord
from .exceptions import (
    CloudWatchLogsParseError,
    ErrorNotificationError,
    LineNotificationError,
    ObjectDownloadError,
    S3ImageDownloadError,
)
from .interfaces import IObjectRepository
from .line_message import LineImageMessage, LineMessage, LineTextMessage
from .line_notifier_interface import ILineNotifier
from .models import StorageLocation
from .parsed_cloudwatch_logs_data import ParsedCloudWatchLogsData
from .s3_client_interface import IS3Client

__all__ = [
    # Models
    "ErrorLogRecord",
    "ParsedCloudWatchLogsData",
    "StorageLocation",
    "LineTextMessage",
    "LineImageMessage",
    "LineMessage",
    # Interfaces
    "ICloudWatchLogsParser",
    "IS3Client",
    "ILineNotifier",
    "IObjectRepository",
    # Exceptions
    "ErrorNotificationError",
    "CloudWatchLogsParseError",
    "S3ImageDownloadError",
    "ObjectDownloadError",
    "LineNotificationError",
]
