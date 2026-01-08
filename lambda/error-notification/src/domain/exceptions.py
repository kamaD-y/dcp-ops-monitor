"""エラー通知機能のカスタム例外定義"""


class ErrorNotificationError(Exception):
    """エラー通知機能のベース例外"""

    pass


class ObjectDownloadError(ErrorNotificationError):
    """オブジェクトストレージからのダウンロードエラー"""

    pass


class NotificationError(ErrorNotificationError):
    """通知送信エラー"""

    pass


class LogsParseError(ErrorNotificationError):
    """ログイベントのパースエラー"""

    pass
