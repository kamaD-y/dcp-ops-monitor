from tempfile import mkdtemp
from typing import Any, Dict, Optional, TypeGuard

from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium import webdriver
from selenium.webdriver.common.by import By

from domain.interface import ScraperInterface
from domain.value_object import DcpAssetsInfo, DcpProductAssets, DcpTotalAssets
from settings import get_logger, get_settings

logger = get_logger()
settings = get_settings()


class ScrapingError(Exception):
    def __init__(self, message: str, error_image_path: Optional[str] = None) -> None:
        super().__init__(message)
        self.error_image_path = error_image_path


class ExtractError(Exception):
    pass


class ElementTypeError(ExtractError):
    pass


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


class NRKScraper(ScraperInterface):
    """日本レコードキーピング(NRK)ページをスクレイピングするクラス"""

    def __init__(self, user_id: str, password: str, birthdate: str, driver: Optional[webdriver.Chrome] = None) -> None:
        self.user_id = user_id
        self.password = password
        self.birthdate = birthdate
        self.driver = driver if driver else get_chrome_driver()
        self.is_login = False
        self.page_source = ""

    def scrape(self, start_url: str) -> None:
        """資産情報ページをスクレイピングしページを取得する

        Args:
            start_url (str): スクレイピングを開始するURL

        Raises:
            ScrapingError: スクレイピングに失敗した場合
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
            self.page_source = self.driver.page_source

            # ログアウト
            self._logout()
            logger.info("Scraping succeeded.")

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

    def extract(self) -> DcpAssetsInfo:
        """スクレイピング結果から資産情報を抽出する

        Returns:
            DcpAssetsInfo: 抽出した資産情報

        Raises:
            ExtractError: 抽出に失敗した場合
        """
        try:
            soup = BeautifulSoup(self.page_source, "html.parser")

            # 総評価額を取得
            total_assets = self._extract_total_assets(soup)

            # 商品別
            assets_each_product = self._extract_product_assets(soup)

            return DcpAssetsInfo(
                total=total_assets,
                products=assets_each_product,
            )

        except Exception as e:
            logger.exception("An error occurred during the extracting process.")
            raise ExtractError() from e

    def _extract_total_assets(self, soup: BeautifulSoup) -> DcpTotalAssets:
        """総評価額を抽出する

        Args:
            soup (BeautifulSoup): BeautifulSoupオブジェクト

        Returns:
            DcpTotalAssets: 抽出した総評価額情報
        """
        logger.info("_extract_total_assets start.")

        total = soup.find(class_="total")
        if not self._is_tag_element(total):
            raise ElementTypeError("total is not a tag element")

        total_assets = DcpTotalAssets(
            cumulative_contributions=total.find_all("dd")[0].text,
            total_gains_or_losses=total.find_all("dd")[1].text,
            total_asset_valuation=total.find_all("dd")[2].text,
        )
        logger.info(
            "_extract_total_assets end.",
            extra=total_assets.__dict__,
        )
        return total_assets

    def _extract_product_assets(self, soup: BeautifulSoup) -> Dict[str, DcpProductAssets]:
        """商品別の資産評価額を抽出する

        Args:
            soup (BeautifulSoup): BeautifulSoupオブジェクト

        Returns:
            Dict[str, DcpProductAssets]: 商品別の資産評価額情報
        """
        logger.info("_extract_product_assets start.")

        product_info = soup.find(id="prodInfo")
        if not self._is_tag_element(product_info):
            raise ElementTypeError("product_info is not a tag element")

        products = product_info.find_all(class_="infoDetailUnit_02 pc_mb30")
        if not self._is_tag_elements(products):
            raise ElementTypeError("products is not a tag element list")

        # 商品毎の資産評価額を取得する
        assets_each_product: Dict[str, DcpProductAssets] = {}
        for product in products:
            table_body = product.find("tbody")
            if not self._is_tag_element(table_body):
                raise ElementTypeError("table_body is not a tag element")

            table_rows = table_body.find_all("tr")
            if not self._is_tag_elements(table_rows):
                raise ElementTypeError("table_rows is not a tag element list")

            product_assets = DcpProductAssets(
                cumulative_acquisition_costs=table_rows[2].find_all("td")[-1].text,
                gains_or_losses=table_rows[5].find_all("td")[-1].text,
                asset_valuation=table_rows[2].find_all("td")[2].text,
            )

            product_info = product.find(class_="infoHdWrap00")
            if not self._is_tag_element(product_info):
                raise ElementTypeError("product_info is not a tag element")

            product_name = product_info.text.strip()
            assets_each_product[product_name] = product_assets
            logger.debug(
                f"product asset info: {product_name}.",
                extra=product_assets.__dict__,
            )

        logger.info(
            "_extract_product_assets end.",
            extra={
                "product_count": len(assets_each_product),
                "product_names": list(assets_each_product.keys()),
            },
        )
        return assets_each_product

    def _is_tag_element(self, element: Any) -> TypeGuard[Tag]:
        """要素がタグ要素かどうかを判定する型ガード

        Args:
            element (Any): 判定する要素

        Returns:
            TypeGuard[Tag]: 要素がタグ要素であるかどうか
        """
        if isinstance(element, Tag):
            return True
        return False

    def _is_tag_elements(self, elements: Any) -> TypeGuard[list[Tag]]:
        """要素がタグ要素のリストかどうかを判定する型ガード

        Args:
            elements (Any): 判定する要素

        Returns:
            TypeGuard[list[Tag]]: 要素がタグ要素のリストであるかどうか
        """
        if isinstance(elements, list) and all(isinstance(e, Tag) for e in elements):
            return True
        return False
