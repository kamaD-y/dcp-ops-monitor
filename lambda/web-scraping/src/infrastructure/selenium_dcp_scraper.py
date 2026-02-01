from tempfile import mkdtemp

from selenium import webdriver
from selenium.webdriver.common.by import By

from src.config.settings import get_logger
from src.domain import DcpAssetInfo, DcpAssets, IDcpScraper, ScrapingFailed, ScrapingParams

logger = get_logger()


class SeleniumDcpScraper(IDcpScraper):
    """Selenium WebDriverを提供するクラス"""

    def __init__(
        self,
        user_agent: str,
        scraping_params: ScrapingParams,
        chrome_binary_location: str = "/opt/chrome/chrome",
        chrome_driver_path: str = "/opt/chromedriver",
    ) -> None:
        self.chrome_binary_location = chrome_binary_location
        self.chrome_driver_path = chrome_driver_path
        self.user_agent = user_agent
        self.driver = self._get_driver()
        self.user_id = scraping_params.login_user_id
        self.password = scraping_params.login_password
        self.birthdate = scraping_params.login_birthdate
        self.start_url = scraping_params.start_url

    def _get_driver(self) -> webdriver.Chrome:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--window-size=1280x1696")
        chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
        chrome_options.add_argument(f"--data-path={mkdtemp()}")
        chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--log-level=0")
        chrome_options.add_argument("--v=99")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument(f"--user-agent={self.user_agent}")

        # ref: https://github.com/umihico/docker-selenium-lambda/blob/main/main.py
        chrome_options.binary_location = self.chrome_binary_location
        service = webdriver.ChromeService(self.chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # スクレイピング全体通して暗黙的に待機する時間を10秒に設定
        driver.implicitly_wait(10)

        return driver

    def fetch_asset_valuation(self) -> DcpAssets:
        """資産評価情報を取得する

        Returns:
            DcpAssets: 資産評価情報
        """
        logger.info("資産評価情報の取得開始")
        self.driver.get(self.start_url)

        self._login()
        self._navigate_to_asset_page()
        assets = self._extract_asset_valuation()
        self._logout()
        self.driver.quit()
        logger.info("資産評価情報の取得完了")
        return assets

    def _login(self) -> None:
        try:
            logger.info("ログイン処理開始")
            input_user_id = self.driver.find_element(By.NAME, "userId")
            input_password = self.driver.find_element(By.NAME, "password")
            input_birthdate = self.driver.find_element(By.NAME, "birthDate")
            input_user_id.send_keys(self.user_id)
            input_password.send_keys(self.password)
            input_birthdate.send_keys(self.birthdate)

            btn_login = self.driver.find_element(By.ID, "btnLogin")
            btn_login.submit()

            # ログアウトボタンがなければログイン失敗とする
            self.driver.find_element(By.LINK_TEXT, "ログアウト")
            logger.info("ログイン処理完了")

        except Exception as e:
            screenshot_path = "/tmp/error_login.png"
            self.driver.save_screenshot(screenshot_path)
            self.driver.quit()
            raise ScrapingFailed.during_login(tmp_screenshot_path=screenshot_path) from e

    def _navigate_to_asset_page(self) -> None:
        """資産評価額照会ページへ遷移する"""
        try:
            logger.info("資産評価額照会ページへの遷移開始")
            link_asset_valuation = self.driver.find_element(By.ID, "mainMenu01")
            link_asset_valuation.click()

            # 資産評価額照会ページの読み込み完了を確認
            self.driver.find_element(By.CLASS_NAME, "total")
            logger.info("資産評価額照会ページへの遷移完了")
        except Exception as e:
            screenshot_path = "/tmp/error_asset_valuation.png"
            self.driver.save_screenshot(screenshot_path)
            self._logout()
            self.driver.quit()
            raise ScrapingFailed.during_page_fetch(tmp_screenshot_path=screenshot_path) from e

    def _extract_asset_valuation(self) -> DcpAssets:
        """資産評価額照会ページから資産情報を抽出する

        Returns:
            DcpAssets: 抽出された資産情報
        """
        try:
            logger.info("資産情報の抽出開始")
            total_assets = self._extract_total_assets()
            products_assets = self._extract_product_assets()
            logger.info("資産情報の抽出完了")
            return DcpAssets(total=total_assets, products=products_assets)
        except Exception as e:
            html_path = "/tmp/error_extraction.html"
            try:
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
            except Exception as write_error:
                logger.warning("HTML ファイルの保存に失敗しました。", error=str(write_error))
                html_path = None
            self._logout()
            self.driver.quit()
            raise ScrapingFailed.during_extraction(tmp_html_path=html_path) from e

    def _extract_total_assets(self) -> DcpAssetInfo:
        """総評価額を抽出する

        Returns:
            DcpAssetInfo: 総評価額情報
        """
        logger.info("総評価額の抽出開始")
        total_elem = self.driver.find_element(By.CLASS_NAME, "total")
        dd_elements = total_elem.find_elements(By.TAG_NAME, "dd")

        total_assets = DcpAssetInfo.from_html_strings(
            cumulative_contributions_str=dd_elements[0].text,
            gains_or_losses_str=dd_elements[1].text,
            asset_valuation_str=dd_elements[2].text,
        )

        logger.info(
            "総評価額の抽出完了",
            extra=total_assets.__dict__,
        )
        return total_assets

    def _extract_product_assets(self) -> dict[str, DcpAssetInfo]:
        """商品別資産を抽出する

        Returns:
            dict[str, DcpAssetInfo]: 商品別資産情報
        """
        logger.info("商品別の資産評価額の抽出開始")

        product_info = self.driver.find_element(By.ID, "prodInfo")
        products = product_info.find_elements(By.CSS_SELECTOR, ".infoDetailUnit_02.pc_mb30")

        assets_each_product: dict[str, DcpAssetInfo] = {}
        for product in products:
            table_body = product.find_element(By.TAG_NAME, "tbody")
            table_rows = table_body.find_elements(By.TAG_NAME, "tr")

            product_assets = DcpAssetInfo.from_html_strings(
                cumulative_contributions_str=table_rows[2].find_elements(By.TAG_NAME, "td")[-1].text,
                gains_or_losses_str=table_rows[5].find_elements(By.TAG_NAME, "td")[-1].text,
                asset_valuation_str=table_rows[2].find_elements(By.TAG_NAME, "td")[2].text,
            )

            product_name = product.find_element(By.CLASS_NAME, "infoHdWrap00").text.strip()
            assets_each_product[product_name] = product_assets
            logger.debug(
                f"商品別資産評価額情報: {product_name}.",
                extra=product_assets.__dict__,
            )

        logger.info(
            "商品別の資産評価額の抽出完了",
            extra={
                "product_count": len(assets_each_product),
                "product_names": list(assets_each_product.keys()),
            },
        )
        return assets_each_product

    def _logout(self) -> None:
        try:
            logger.info("ログアウト処理開始")
            link_logout = self.driver.find_element(By.LINK_TEXT, "ログアウト")
            link_logout.click()
            logger.info("ログアウト処理完了")
        except Exception:
            # ログアウト失敗はログのみ出力して無視
            logger.warning("ログアウト処理中に問題が発生しました。")
