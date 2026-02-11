from shared.domain.asset_object import DcpAssetInfo

from src.domain import IScraper, ScrapingFailed, ScrapingParams


class MockSeleniumScraper(IScraper):
    """Selenium WebDriver のMock実装（E2Eテスト用）

    実際にブラウザを起動せず、事前に用意した商品別資産情報を返すMockオブジェクト
    """

    def __init__(
        self,
        mock_products: dict[str, DcpAssetInfo] | None = None,
        user_agent: str = "",
        scraping_params: ScrapingParams | None = None,
        chrome_binary_location: str = "",
        chrome_driver_path: str = "",
        should_fail: bool = False,
        should_fail_extraction: bool = False,
    ) -> None:
        """コンストラクタ

        Args:
            mock_products: 返却する商品別資産情報（指定しない場合はデフォルト値）
            user_agent: ユーザーエージェント（使用しない）
            scraping_params: スクレイピングパラメータ（使用しない）
            chrome_binary_location: Chromeバイナリの場所（使用しない）
            chrome_driver_path: ChromeDriverのパス（使用しない）
            should_fail: Trueの場合、スクレイピング失敗を模擬する
            should_fail_extraction: Trueの場合、抽出失敗を模擬する
        """
        self.user_agent = user_agent
        self.scraping_params = scraping_params
        self.chrome_binary_location = chrome_binary_location
        self.chrome_driver_path = chrome_driver_path
        self.mock_products = mock_products
        self.should_fail = should_fail
        self.should_fail_extraction = should_fail_extraction
        self.fetch_called = False

    def fetch_asset_valuation(self) -> dict[str, DcpAssetInfo]:
        """資産評価情報を返す（Mock実装）

        Returns:
            dict[str, DcpAssetInfo]: 商品別の資産評価情報

        Raises:
            ScrapingFailed: should_fail=True または should_fail_extraction=True の場合
        """
        self.fetch_called = True

        if self.should_fail:
            screenshot_path = "/tmp/mock_error.png"
            with open(screenshot_path, "wb") as f:
                f.write(b"Mock error image content")
            print("[Mock] Scraping failed (simulated)")
            raise ScrapingFailed.during_login(tmp_screenshot_path=screenshot_path)

        if self.should_fail_extraction:
            html_path = "/tmp/mock_error_extraction.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write("<html>invalid</html>")
            print("[Mock] Extraction failed (simulated)")
            raise ScrapingFailed.during_extraction(tmp_html_path=html_path)

        if self.mock_products is None:
            msg = "mock_products must be provided when should_fail=False and should_fail_extraction=False"
            raise ValueError(msg)

        print(f"[Mock] Scraping succeeded (products={len(self.mock_products)})")
        return self.mock_products
