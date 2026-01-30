from typing import Optional


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

    ページ遷移失敗と資産情報抽出失敗の両方を表す。
    エラー発生時のスクリーンショットパスと HTML ソースを保持する。

    Attributes:
        message (str): エラーメッセージ
        error_file_key (Optional[str]): エラーファイルの S3 キー
        screenshot_path (Optional[str]): エラー時のスクリーンショット画像のローカルパス
        html_source (Optional[str]): エラー時のページ HTML ソース
    """

    def __init__(
        self,
        message: str,
        error_file_key: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        html_source: Optional[str] = None,
    ):
        super().__init__(message)
        self.error_file_key = error_file_key
        self.screenshot_path = screenshot_path
        self.html_source = html_source

    @classmethod
    def during_login(
        cls,
        error_file_key: Optional[str] = None,
        screenshot_path: Optional[str] = None,
    ) -> "ScrapingFailed":
        """ログイン処理中にエラーが発生した場合の例外を生成

        Args:
            error_file_key: エラーファイルの S3 キー
            screenshot_path: エラー時のスクリーンショット画像のローカルパス

        Returns:
            ScrapingFailed: 生成された例外インスタンス
        """
        return cls("ログイン処理に失敗しました", error_file_key, screenshot_path=screenshot_path)

    @classmethod
    def during_page_fetch(
        cls,
        error_file_key: Optional[str] = None,
        screenshot_path: Optional[str] = None,
    ) -> "ScrapingFailed":
        """ページ取得処理中にエラーが発生した場合の例外を生成

        Args:
            error_file_key: エラーファイルの S3 キー
            screenshot_path: エラー時のスクリーンショット画像のローカルパス

        Returns:
            ScrapingFailed: 生成された例外インスタンス
        """
        return cls("資産評価額照会ページの取得に失敗しました", error_file_key, screenshot_path=screenshot_path)

    @classmethod
    def during_extraction(
        cls,
        html_source: Optional[str] = None,
    ) -> "ScrapingFailed":
        """資産情報抽出中にエラーが発生した場合の例外を生成

        Args:
            html_source: エラー時のページ HTML ソース

        Returns:
            ScrapingFailed: 生成された例外インスタンス
        """
        return cls("資産情報の抽出に失敗しました", html_source=html_source)
