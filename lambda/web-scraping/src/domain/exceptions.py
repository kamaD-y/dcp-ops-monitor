from typing import Optional


class AssetExtractionError(Exception):
    """資産情報抽出処理のエラー

    Attributes:
        message (str): エラーメッセージ
        error_file_key (Optional[str]): エラー時のHTMLソース
    """

    def __init__(self, message: str, error_file_key: Optional[str] = None):
        super().__init__(message)
        self.error_file_key = error_file_key


class WebScrapingFailed(Exception):
    """Web スクレイピング機能のベース例外"""

    pass


class NotificationFailed(WebScrapingFailed):
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


class ScrapingFailed(WebScrapingFailed):
    """スクレイピング処理のエラー

    Attributes:
        message (str): エラーメッセージ
        error_file_key (Optional[str]): エラー時のスクリーンショット画像のS3キー
    """

    def __init__(self, message: str, error_file_key: Optional[str] = None):
        super().__init__(message)
        self.error_file_key = error_file_key

    @classmethod
    def during_login(cls, error_file_key: Optional[str] = None) -> "ScrapingFailed":
        """ログイン処理中にエラーが発生した場合の例外を生成

        Args:
            error_file_key: エラー時のスクリーンショット画像のS3キー

        Returns:
            ScrapingFailed: 生成された例外インスタンス
        """
        return cls("ログイン処理に失敗しました", error_file_key)

    @classmethod
    def during_page_fetch(cls, error_file_key: Optional[str] = None) -> "ScrapingFailed":
        """ページ取得処理中にエラーが発生した場合の例外を生成

        Args:
            error_file_key: エラー時のスクリーンショット画像のS3キー

        Returns:
            ScrapingFailed: 生成された例外インスタンス
        """
        return cls("資産評価額照会ページの取得に失敗しました", error_file_key)

    @classmethod
    def during_logout(cls, error_file_key: Optional[str] = None) -> "ScrapingFailed":
        """ログアウト処理中にエラーが発生した場合の例外を生成

        Args:
            error_file_key: エラー時のスクリーンショット画像のS3キー

        Returns:
            ScrapingFailed: 生成された例外インスタンス
        """
        return cls("ログアウト処理に失敗しました", error_file_key)
