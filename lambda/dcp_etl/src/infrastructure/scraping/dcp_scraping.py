import glob
from tempfile import mkdtemp

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from settings.settings import get_logger, get_settings

logger = get_logger()
settings = get_settings()


class ScrapingError(Exception):
    def __init__(self, error_image_path: str):
        super().__init__("Scraping Error")
        self.error_image_path = error_image_path


def get_chrome_driver(
    chrome_path: str = "/opt/chrome/linux64/*/chrome", driver_path: str = "/opt/chromedriver/linux64/*/chromedriver"
) -> WebDriver:
    """WebDriverを取得する"""
    if not glob.glob(chrome_path):
        raise FileNotFoundError(f"Chrome binary path not found: {chrome_path}")
    if not glob.glob(driver_path):
        raise FileNotFoundError(f"ChromeDriver binary not found: {driver_path}")

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

    chrome_binary_path = glob.glob(chrome_path)[0]
    chrome_options.binary_location = chrome_binary_path

    driver_path = glob.glob(driver_path)[0]

    service = ChromeService(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # スクレイピング全体通して暗黙的に待機する時間を10秒に設定
    driver.implicitly_wait(10)

    return driver


def scrape(user_id: str, password: str, birthdate: str, driver: WebDriver) -> str:
    """NRKページをスクレイピングし、資産情報ページをhtml形式の文字列で返却する"""
    try:
        # NRKログインページへ遷移
        logger.info("try goto login page...")
        driver.get(settings.login_url)

        # ログイン
        logger.info("try login...")
        _try_login(driver, user_id, password, birthdate)

        # 資産評価額照会ページへ遷移
        logger.info("try goto assets page...")
        _try_goto_assets_page(driver)

        # 資産評価額照会ページをhtmlに出力
        page_source = driver.page_source

        try:
            # ログアウト
            logger.info("try logout...")
            _try_logout(driver)
        except Exception:
            # スクレイピングの目的は達成している為、ログアウトに失敗してもエラー通知のみとし処理を続行する
            logger.exception("logout error")
            error_image = "/tmp/error.png"
            driver.save_screenshot(error_image)
            # TODO: S3にエラー画像をアップロードする

        return page_source

    except Exception:
        logger.exception("scrape_nrk error")
        error_image = "/tmp/error.png"
        driver.save_screenshot(error_image)
        # TODO: S3にエラー画像をアップロードする
        raise ScrapingError(error_image_path=error_image)

    finally:
        driver.quit()
        logger.info("driver quit.")


def _try_login(driver: WebDriver, user_id: str, password: str, birthdate: str) -> None:
    """ログインを試みる"""
    user_id_input = driver.find_element(By.NAME, "userId")
    password_input = driver.find_element(By.NAME, "password")
    birthdate_input = driver.find_element(By.NAME, "birthDate")
    user_id_input.send_keys(user_id)
    password_input.send_keys(password)
    birthdate_input.send_keys(birthdate)

    login_btn = driver.find_element(By.ID, "btnLogin")
    login_btn.submit()


def _try_goto_assets_page(driver: WebDriver) -> None:
    """資産評価額照会ページへ遷移する"""
    menu01 = driver.find_element(By.ID, "mainMenu01")
    menu01.click()

    # class=totalの要素が表示されるまで待機.暗黙的に待機時間を設定している為、ここでは明示的に待機処理は不要
    driver.find_element(By.CLASS_NAME, "total")


def _try_logout(driver: WebDriver) -> None:
    """ログアウトを試みる"""
    logout_a = driver.find_element(By.LINK_TEXT, "ログアウト")
    logout_a.click()
