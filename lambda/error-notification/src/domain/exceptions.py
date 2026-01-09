"""エラー通知機能のカスタム例外定義"""


class ErrorNotificationError(Exception):
    """エラー通知機能のベース例外"""

    pass


class TemporaryUrlGenerationError(ErrorNotificationError):
    """一時アクセス URL 生成エラー"""

    pass


class NotificationError(ErrorNotificationError):
    """通知送信エラー"""

    pass


class LogsParseError(ErrorNotificationError):
    """ログイベントのパースエラー"""

    pass
