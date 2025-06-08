from tempfile import mkdtemp

from selenium import webdriver
from selenium.webdriver.common.by import By

from settings.settings import get_logger, get_settings

logger = get_logger()
settings = get_settings()
error_image_path = "/tmp/error.png"


class ScrapingError(Exception):
    def __init__(self) -> None:
        super().__init__("Scraping Error")
        self.error_image_path = error_image_path


class LoginError(ScrapingError):
    def __init__(self) -> None:
        super().__init__()
        self.message = "ログインに失敗しました。ユーザーID、パスワード、生年月日を確認してください。"


class ScrapingProcessError(ScrapingError):
    def __init__(self, message: str = "スクレイピング処理中にエラーが発生しました。") -> None:
        super().__init__()
        self.message = message


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
    # NOTE: 以下のオプションは、Seleniumが自動操作していること(navigator.webdriver)をFalseにする
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # ref: https://github.com/umihico/docker-selenium-lambda/blob/main/main.py
    chrome_options.binary_location = "/opt/chrome/chrome"
    service = webdriver.ChromeService("/opt/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # スクレイピング全体通して暗黙的に待機する時間を10秒に設定
    driver.implicitly_wait(10)

    return driver


def scrape(user_id: str, password: str, birthdate: str, driver: webdriver.Chrome) -> str:
    """日本レコードキーピング(NRK)ページをスクレイピングし、資産情報ページをhtml形式の文字列で返却する

    Args:
        user_id (str): ログイン用ユーザーID
        password (str): ログイン用パスワード
        birthdate (str): ログイン用生年月日
        driver (WebDriver): ChromeのWebDriver

    Returns:
        str: 資産情報ページのhtml
    """
    try:
        # ログインページへ遷移
        driver.get(settings.login_url)

        # ログイン
        _try_login(driver, user_id, password, birthdate)

        # 資産評価額照会ページへ遷移
        _try_goto_assets_page(driver)

        # 資産評価額照会ページをhtmlに出力
        page_source = driver.page_source

        # ログアウト
        _try_logout(driver)
        return page_source

    except ScrapingError as e:
        logger.exception("An error occurred during the scraping process.")
        if isinstance(e, ScrapingProcessError):
            # ログイン後の処理でエラーが発生した場合は、ログアウトを試みる
            _try_logout(driver)
        raise

    finally:
        driver.quit()
        logger.info("driver quit.")


def _try_login(driver: webdriver.Chrome, user_id: str, password: str, birthdate: str) -> None:
    """ログインを試みる

    Args:
        driver (webdriver.Chrome): ChromeのWebDriver
        user_id (str): ログイン用ユーザーID
        password (str): ログイン用パスワード
        birthdate (str): ログイン用生年月日

    Returns:
        None
    """
    try:
        logger.info("_try_login start.")

        user_id_input = driver.find_element(By.NAME, "userId")
        password_input = driver.find_element(By.NAME, "password")
        birthdate_input = driver.find_element(By.NAME, "birthDate")
        user_id_input.send_keys(user_id)
        password_input.send_keys(password)
        birthdate_input.send_keys(birthdate)

        login_btn = driver.find_element(By.ID, "btnLogin")
        login_btn.submit()

        # ログイン後のページが読み込まれるまで待機
        driver.find_element(By.ID, "mainMenu01")

        logger.info("_try_login end.")
    except Exception as e:
        driver.save_screenshot(error_image_path)
        raise LoginError() from e


def _try_goto_assets_page(driver: webdriver.Chrome) -> None:
    """資産評価額照会ページへ遷移する

    Args:
        driver (webdriver.Chrome): ChromeのWebDriver

    Returns:
        None
    """
    try:
        logger.info("_try_goto_assets_page start.")

        menu01 = driver.find_element(By.ID, "mainMenu01")
        menu01.click()

        # class=totalの要素が表示されるまで待機.暗黙的に待機時間を設定している為、ここでは明示的に待機処理は不要
        driver.find_element(By.CLASS_NAME, "total")

        logger.info("_try_goto_assets_page end.")
    except Exception as e:
        driver.save_screenshot(error_image_path)
        raise ScrapingProcessError("資産評価額照会ページへの遷移に失敗しました。") from e


def _try_logout(driver: webdriver.Chrome) -> None:
    """ログアウトを試みる

    Args:
        driver (webdriver.Chrome): ChromeのWebDriver

    Returns:
        None
    """
    try:
        logger.info("_try_logout start.")

        logout_a = driver.find_element(By.LINK_TEXT, "ログアウト")
        logout_a.click()

        logger.info("_try_logout end.")
    except Exception:
        # ログアウトに失敗してもエラー通知のみとする
        logger.exception("logout error")
