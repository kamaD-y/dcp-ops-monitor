from tempfile import mkdtemp
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By

from config.settings import get_logger
from domain import IDcpScraper, ScrapingParams

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
        self.error_image_path: Optional[str] = None

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

    def fetch_asset_valuation_html(self) -> str:
        """資産評価情報ページの HTML ソースを取得する

        Returns:
            str: 資産評価情報ページの HTML ソース
        """
        self.driver.get(self.start_url)

        self._login()
        asset_valuation_html = self._get_asset_valuation_page()
        self._logout()
        self.driver.quit()
        return asset_valuation_html

    def _login(self) -> None:
        try:
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

        except Exception:
            self.error_image_path = "/tmp/error_login.png"
            self.driver.save_screenshot(self.error_image_path)
            self.driver.quit()
            raise

    def _get_asset_valuation_page(self) -> str:
        try:
            link_asset_valuation = self.driver.find_element(By.ID, "mainMenu01")
            link_asset_valuation.click()

            # 資産評価額照会ページ取得
            self.driver.find_element(By.CLASS_NAME, "total")
            return self.driver.page_source
        except Exception:
            self.error_image_path = "/tmp/error_asset_valuation.png"
            self.driver.save_screenshot(self.error_image_path)
            self._logout()
            self.driver.quit()
            raise

    def _logout(self) -> None:
        try:
            link_logout = self.driver.find_element(By.LINK_TEXT, "ログアウト")
            link_logout.click()
        except Exception:
            # ログアウト失敗はエラーログのみ出力して無視
            logger.exception("ログアウト処理中に問題が発生しました。")
            pass

    def get_error_image_path(self) -> Optional[str]:
        return self.error_image_path
