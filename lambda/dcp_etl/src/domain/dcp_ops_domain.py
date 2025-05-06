import os
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from src.domain.dcp_value_object import DcpAssetsInfo, DcpAssetsInfoProduct, DcpOpsIndicators
from src.infrastructure.aws.sns import publish
from src.infrastructure.aws.ssm import get_parameter
from src.infrastructure.scraping.dcp_scraping import ScrapingError, scrape
from src.settings.settings import get_logger, get_settings

logger = get_logger()
settings = get_settings()


class ExtractError(Exception):
    pass


class DcpOperationsStatusScraper:
    """確定拠出年金の運用状況をスクレイピングするクラス"""

    def __init__(self):
        self.html_source = None
        self.user_id = None
        self.password = None
        self.birthdate = None

        if os.getenv("LOGIN_PARAMETER_ARN"):
            parameters = get_parameter(os.getenv("LOGIN_PARAMETER_ARN"))
            if parameters:
                os.environ["USER_ID"] = parameters.get("USER_ID")
                os.environ["PASSWORD"] = parameters.get("PASSWORD")
            settings = get_settings(
                user_id=os.getenv("USER_ID"), password=os.getenv("PASSWORD"), birthdate=os.getenv("BIRTHDATE")
            )
            self.user_id = settings.user_id
            self.password = settings.password
            self.birthdate = settings.birthdate

    def scrape(self) -> str:
        """スクレイピングを実行する"""
        try:
            if not self.user_id or not self.password or not self.birthdate:
                raise ScrapingError("user_id, password, and birthdate must be set.")

            self.html_source = scrape(self.user_id, self.password.get_secret_value(), self.birthdate)
        except ScrapingError:
            logger.exception("scrape error")
            # TODO: e.error_image_path の画像をS3にアップロードする処理を追加する
            raise


class DcpOperationStatusExtractor:
    """確定拠出年金の運用状況を抽出するクラス"""

    def __init__(self):
        self.assets_info = DcpAssetsInfo()

    def extract(self, html_source):
        """スクレイピング結果から資産情報を抽出する"""
        try:
            soup = BeautifulSoup(html_source, "html.parser")

            # 総評価額を取得
            logger.info("extract total...")
            self._extract_assets_total(soup)
            logger.debug("asset_info total.", total=self.assets_info.total)

            # 商品別
            logger.info("extract products...")
            self._extract_assets_products(soup)
            logger.debug("asset_info products.", products=self.assets_info.products)

        except Exception:
            logger.exception("extract_assets error")
            # TODO: html_sourceをS3にアップロードする処理を追加する
            raise ExtractError("extract_assets error")

    def _extract_assets_total(self, soup: BeautifulSoup) -> dict:
        """総評価額を抽出する"""
        total = soup.find(class_="total")
        # 拠出金額累計
        self.assets_info.total.cumulative_contributions = total.find_all("dd")[0].text
        # 評価損益
        self.assets_info.total.total_gains_or_losses = total.find_all("dd")[1].text
        # 資産評価額
        self.assets_info.total.total_asset_valuation = total.find_all("dd")[2].text

    def _extract_assets_products(self, soup: BeautifulSoup) -> dict:
        """商品別の資産評価額を抽出する"""
        products = soup.find(id="prodInfo").find_all(class_="infoDetailUnit_02 pc_mb30")
        logger.info(f"products count: {len(products)}")

        for product in products:
            product_name = product.find(class_="infoHdWrap00").text

            table_rows = product.find("tbody").find_all("tr")

            self.assets_info.products[product_name] = DcpAssetsInfoProduct()

            # 取得価額累計 テーブル3行目の最終列の要素
            self.assets_info.products[product_name].cumulative_acquisition_costs = table_rows[2].find_all("td")[-1].text
            # 損益 テーブル6行目の最終列の要素
            self.assets_info.products[product_name].gains_or_losses = table_rows[5].find_all("td")[-1].text
            # 資産評価額 テーブル3行目の3列目の要素
            self.assets_info.products[product_name].asset_valuation = table_rows[2].find_all("td")[2].text

            logger.debug(
                f"product_info {product_name}.",
                product_info=self.assets_info.products[product_name],
            )


class DcpOperationStatusTransformer:
    """確定拠出年金の運用状況を変換するクラス"""

    def __init__(self):
        self.operational_indicators = DcpOpsIndicators()

    def transform(self, assets_info: DcpAssetsInfo) -> None:
        """資産情報を変換する"""

        if not assets_info.total:
            return

        # 運用年数の算出
        today = datetime.today()
        # 運用開始日: 2016/10/01
        operation_start_dt = datetime(2016, 10, 1)
        operation_years = (today - operation_start_dt) / timedelta(days=365)
        operation_years = round(operation_years, 2)

        # 年間利回りの算出
        cumulative_contributions = self.yen_to_int(assets_info.total.cumulative_contributions)
        total_gains_or_losses = self.yen_to_int(assets_info.total.total_gains_or_losses)
        # 年間利回りの計算式: 利回り = 利益 / 拠出額 / 運用年数 × 100
        actual_yield_rate = total_gains_or_losses / cumulative_contributions / operation_years * 100
        actual_yield_rate = round((actual_yield_rate / 100), 3)

        # 60歳まで運用した場合の想定受取額, 60歳までの運用年数: 26年とする
        # 計算式: 24万(年積立額) * (((1+利回り)**年数26年 - 1) / 利回り)
        total_amount_at_60age = int(240000 * (((1 + actual_yield_rate) ** 26 - 1) / actual_yield_rate))
        total_amount_at_60age = "{:,.0f}".format(total_amount_at_60age) + "円"

        # 計算した値で運用指標を更新
        self.operational_indicators.operation_years = operation_years
        self.operational_indicators.actual_yield_rate = actual_yield_rate
        self.operational_indicators.total_amount_at_60age = total_amount_at_60age
        logger.info(
            "operational_indicators",
            operational_indicators=self.operational_indicators,
        )

    def yen_to_int(self, yen: str) -> int:
        """円表記の文字列を数値に変換する"""
        return int(yen.replace("円", "").replace(",", ""))


class DcpOperationStatusNotifier:
    """確定拠出年金の運用状況を通知するクラス"""

    def __init__(self):
        pass

    def make_message(self, assets_info: DcpAssetsInfo, operational_indicators: DcpOpsIndicators) -> str:
        message = "確定拠出年金 運用状況通知Bot\n\n"
        message += "総評価\n"
        message += f"拠出金額累計: {assets_info.total.cumulative_contributions}\n"
        message += f"評価損益: {assets_info.total.total_gains_or_losses}\n"
        message += f"資産評価額: {assets_info.total.total_asset_valuation}\n"
        message += "\n"
        message += f"運用年数: {operational_indicators.operation_years}年\n"
        message += f"運用利回り: {operational_indicators.actual_yield_rate}\n"
        message += "目標利回り: 0.06\n"
        message += f"想定受取額(60歳): {operational_indicators.total_amount_at_60age}\n"
        message += "\n"

        message += "商品別\n"
        for p_name, p_v in assets_info.products.items():
            message += f"{p_name}\n"
            message += f"取得価額累計: {p_v.cumulative_acquisition_costs}\n"
            message += f"損益: {p_v.gains_or_losses}\n"
            message += f"資産評価額: {p_v.asset_valuation}\n"
            message += "\n"

        return message

    def notify(self, message) -> str:
        """通知用メッセージを作成する"""
        publish(
            topic_arn=settings.sns_topic_arn,
            message=message,
            subject="確定拠出年金 運用状況",
        )
