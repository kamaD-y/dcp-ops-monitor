"""エラー通知機能のカスタム例外定義"""


class ErrorNotificationError(Exception):
    """エラー通知機能のベース例外"""

    pass


class CloudWatchLogsParseError(ErrorNotificationError):
    """CloudWatch Logs イベントのパースエラー"""

    pass


class S3ImageDownloadError(ErrorNotificationError):
    """S3 からの画像ダウンロードエラー"""

    pass


class LineNotificationError(ErrorNotificationError):
    """LINE 通知送信エラー"""

    pass
