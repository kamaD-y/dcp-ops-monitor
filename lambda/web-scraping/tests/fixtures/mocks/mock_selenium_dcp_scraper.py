from typing import Optional

from domain import IDcpScraper, ScrapingFailed, ScrapingParams


class MockSeleniumDcpScraper(IDcpScraper):
    """Selenium WebDriver のMock実装（E2Eテスト用）

    実際にブラウザを起動せず、事前に用意したHTMLを返すMockオブジェクト
    """

    def __init__(
        self,
        mock_html: str,
        user_agent: str = "",
        scraping_params: Optional[ScrapingParams] = None,
        chrome_binary_location: str = "",
        chrome_driver_path: str = "",
        should_fail: bool = False,
    ) -> None:
        """コンストラクタ

        Args:
            user_agent (str): ユーザーエージェント（使用しない）
            scraping_params (Optional[ScrapingParams]): スクレイピングパラメータ（使用しない）
            chrome_binary_location (str): Chromeバイナリの場所（使用しない）
            chrome_driver_path (str): ChromeDriverのパス（使用しない）
            mock_html (Optional[str]): 返却するHTMLソース（指定しない場合はデフォルトHTML）
            should_fail (bool): Trueの場合、fetch_asset_valuation_htmlで例外を発生させる
        """
        self.user_agent = user_agent
        self.scraping_params = scraping_params
        self.chrome_binary_location = chrome_binary_location
        self.chrome_driver_path = chrome_driver_path
        self.mock_html = mock_html
        self.should_fail = should_fail
        self.error_image_path: Optional[str] = None
        self.fetch_called = False

    def fetch_asset_valuation_html(self) -> str:
        """資産評価情報ページの HTML ソースを返す（Mock実装）

        Returns:
            str: 資産評価情報ページの HTML ソース

        Raises:
            ScrapingFailed: should_fail=True の場合
        """
        self.fetch_called = True

        if self.should_fail:
            self.error_image_path = "/tmp/mock_error.png"
            with open(self.error_image_path, "wb") as f:
                f.write(b"Mock error image content")
            print("[Mock] Scraping failed (simulated)")
            raise ScrapingFailed.during_login()

        print(f"[Mock] Scraping succeeded (html_length={len(self.mock_html)})")
        return self.mock_html

    def get_error_image_path(self) -> Optional[str]:
        """エラー時のスクリーンショット画像のパスを返す

        Returns:
            Optional[str]: エラー時のスクリーンショット画像のパス
        """
        return self.error_image_path
