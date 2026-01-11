"""エラー通知機能のカスタム例外定義"""


class ErrorNotificationError(Exception):
    """エラー通知機能のベース例外"""

    pass


class CouldNotGenerateTemporaryUrl(ErrorNotificationError):
    """一時アクセス URL 生成エラー"""

    @classmethod
    def from_location(cls, location: str) -> "CouldNotGenerateTemporaryUrl":
        """ロケーション情報から例外インスタンスを生成する名前付きコンストラクタ

        Args:
            location: ストレージ上の位置

        Returns:
            CouldNotGenerateTemporaryUrl: 生成された例外インスタンス
        """
        return cls(f"一時アクセス URL の生成に失敗しました (Location: {location})")


class NotificationError(ErrorNotificationError):
    """通知送信エラー"""

    pass


class LogsParseError(ErrorNotificationError):
    """ログイベントのパースエラー"""

    pass
