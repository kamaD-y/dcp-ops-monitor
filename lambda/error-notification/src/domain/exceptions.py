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


class NotificationFailed(ErrorNotificationError):
    """通知送信エラー"""

    @classmethod
    def during_request(cls) -> "NotificationFailed":
        """通知送信中にエラーが発生した場合の例外インスタンスを生成する名前付きコンストラクタ

        Returns:
            NotificationFailed: 生成された例外インスタンス
        """
        return cls("通知送信中にエラーが発生しました")

    @classmethod
    def before_request(cls) -> "NotificationFailed":
        """通知送信前にエラーが発生した場合の例外インスタンスを生成する名前付きコンストラクタ

        Returns:
            NotificationFailed: 生成された例外インスタンス
        """
        return cls("通知送信前にエラーが発生しました")


class LogsParseFailed(ErrorNotificationError):
    """ログイベントのパースエラー"""

    def __init__(self, message="ログイベントのパースに失敗しました") -> None:
        super().__init__(message)
