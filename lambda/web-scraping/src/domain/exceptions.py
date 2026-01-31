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
    エラー発生時のスクリーンショットパスと HTML ファイルパスを保持する。

    Attributes:
        message (str): エラーメッセージ
        error_screenshot_key (str | None): スクリーンショットの S3 キー
        error_html_key (str | None): HTML ファイルの S3 キー
        tmp_screenshot_path (str | None): エラー時のスクリーンショット画像のローカルパス
        tmp_html_path (str | None): エラー時の HTML ファイルのローカルパス
    """

    def __init__(
        self,
        message: str,
        error_screenshot_key: str | None = None,
        error_html_key: str | None = None,
        tmp_screenshot_path: str | None = None,
        tmp_html_path: str | None = None,
    ):
        super().__init__(message)
        self.error_screenshot_key = error_screenshot_key
        self.error_html_key = error_html_key
        self.tmp_screenshot_path = tmp_screenshot_path
        self.tmp_html_path = tmp_html_path

    @classmethod
    def during_login(
        cls,
        tmp_screenshot_path: str | None = None,
    ) -> "ScrapingFailed":
        """ログイン処理中にエラーが発生した場合の例外を生成

        Args:
            tmp_screenshot_path: エラー時のスクリーンショット画像のローカルパス

        Returns:
            ScrapingFailed: 生成された例外インスタンス
        """
        return cls("ログイン処理に失敗しました", tmp_screenshot_path=tmp_screenshot_path)

    @classmethod
    def during_page_fetch(
        cls,
        tmp_screenshot_path: str | None = None,
    ) -> "ScrapingFailed":
        """ページ取得処理中にエラーが発生した場合の例外を生成

        Args:
            tmp_screenshot_path: エラー時のスクリーンショット画像のローカルパス

        Returns:
            ScrapingFailed: 生成された例外インスタンス
        """
        return cls("資産評価額照会ページの取得に失敗しました", tmp_screenshot_path=tmp_screenshot_path)

    @classmethod
    def during_extraction(
        cls,
        tmp_html_path: str | None = None,
    ) -> "ScrapingFailed":
        """資産情報抽出中にエラーが発生した場合の例外を生成

        Args:
            tmp_html_path: エラー時の HTML ファイルのローカルパス

        Returns:
            ScrapingFailed: 生成された例外インスタンス
        """
        return cls("資産情報の抽出に失敗しました", tmp_html_path=tmp_html_path)
