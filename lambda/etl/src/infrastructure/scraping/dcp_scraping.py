from tempfile import mkdtemp
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By

from domain.interface import AbstractScraper
from settings.settings import get_logger, get_settings

logger = get_logger()
settings = get_settings()


class ScrapingError(Exception):
    def __init__(self, message: str, error_image_path: Optional[str] = None) -> None:
        super().__init__(message)
        self.error_image_path = error_image_path


def get_chrome_driver() -> webdriver.Chrome:
    """WebDriverを取得する

    Returns:
        webdriver.Chrome: ChromeのWebDriver
    """
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
    chrome_options.add_argument(f"--user-agent={settings.user_agent}")

    # ref: https://github.com/umihico/docker-selenium-lambda/blob/main/main.py
    chrome_options.binary_location = "/opt/chrome/chrome"
    service = webdriver.ChromeService("/opt/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # スクレイピング全体通して暗黙的に待機する時間を10秒に設定
    driver.implicitly_wait(10)

    return driver


class NRKScraper(AbstractScraper):
    """日本レコードキーピング(NRK)ページをスクレイピングするクラス"""

    def __init__(self, user_id: str, password: str, birthdate: str, driver: Optional[webdriver.Chrome] = None) -> None:
        self.user_id = user_id
        self.password = password
        self.birthdate = birthdate
        self.driver = driver if driver else get_chrome_driver()
        self.is_login = False

    def scrape(self, start_url: str) -> str:
        """資産情報ページをスクレイピングし、取得ページをhtml形式の文字列で返す

        Args:
            start_url (str): スクレイピングを開始するURL

        Returns:
            str: スクレイピング結果のHTMLソース
        """
        try:
            logger.info("Scraping start.")

            # ログイン - ログインページにアクセス
            self.driver.get(start_url)

            # ログイン - ログイン情報入力
            input_user_id = self.driver.find_element(By.NAME, "userId")
            input_password = self.driver.find_element(By.NAME, "password")
            input_birthdate = self.driver.find_element(By.NAME, "birthDate")
            input_user_id.send_keys(self.user_id)
            input_password.send_keys(self.password)
            input_birthdate.send_keys(self.birthdate)

            # ログイン - ログインボタンをクリック
            btn_login = self.driver.find_element(By.ID, "btnLogin")
            btn_login.submit()

            # ログイン - メインメニューの表示を確認
            li_menu01 = self.driver.find_element(By.ID, "mainMenu01")
            self.is_login = True
            logger.info("Login succeeded.")

            # 資産評価額紹介ページ取得 - 資産評価額照会ページをクリック
            li_menu01.click()
            logger.info("Click mainMenu01.")

            # 資産評価額紹介ページ取得 - 資産評価額の要素が表示されるまで暗黙的に待機
            self.driver.find_element(By.CLASS_NAME, "total")
            logger.info("Displayed total assets.")
            page_source = self.driver.page_source

            # ログアウト
            self._logout()
            logger.info("Scraping succeeded.")
            return page_source

        except Exception as e:
            if not self.is_login:
                raise ScrapingError("Login failed.") from e

            error_image_path = "/tmp/error.png"
            self.driver.save_screenshot(error_image_path)

            # ログアウト
            self._logout()
            raise ScrapingError("Scraping process failed.", error_image_path) from e

        finally:
            self.driver.quit()
            logger.info("Driver quit.")

    def _logout(self) -> None:
        """ログアウト処理を行う"""
        if not self.is_login:
            logger.warning("Not logged in, cannot logout.")
            return

        try:
            logger.info("Logout trying.")
            link_logout = self.driver.find_element(By.LINK_TEXT, "ログアウト")
            link_logout.click()
            self.is_login = False
            logger.info("Logout succeeded.")
        except Exception as e:
            # ログアウト失敗は直接的に処理に影響がない為、エラーログを出力し処理を継続
            logger.exception("Logout failed.")
