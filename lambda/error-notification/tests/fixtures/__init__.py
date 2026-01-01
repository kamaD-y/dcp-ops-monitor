"""テスト用 fixtures"""

from .cloudwatch_logs_events import create_cloudwatch_logs_event, create_error_log_message

__all__ = [
    "create_cloudwatch_logs_event",
    "create_error_log_message",
]
