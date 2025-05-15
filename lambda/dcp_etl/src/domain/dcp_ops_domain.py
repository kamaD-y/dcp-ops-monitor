import os
from datetime import datetime, timedelta
from typing import Any, Dict, TypeGuard

from bs4 import BeautifulSoup
from bs4.element import Tag
from domain.dcp_value_object import DcpAssetsInfo, DcpOpsIndicators, DcpProductAssets, DcpTotalAssets
from infrastructure.aws.s3 import upload_file
from infrastructure.aws.sns import publish
from infrastructure.aws.ssm import get_parameter
from infrastructure.scraping.dcp_scraping import ScrapingError, get_chrome_driver, scrape
from settings.settings import get_logger, get_settings

logger = get_logger()
settings = get_settings()


class ExtractError(Exception):
    pass


class ElementTypeError(ExtractError):
    pass


class DcpOperationsStatusScraper:
    """確定拠出年金の運用状況をスクレイピングするクラス"""

    def __init__(self) -> None:
        self.user_id = settings.user_id
        self.password = settings.password
        self.birthdate = settings.birthdate

        if os.getenv("LOGIN_PARAMETER_ARN"):
            parameters = get_parameter(os.getenv("LOGIN_PARAMETER_ARN"))
            if parameters:
                os.environ["USER_ID"] = parameters.get("USER_ID")
                os.environ["PASSWORD"] = parameters.get("PASSWORD")
                os.environ["BIRTHDATE"] = parameters.get("BIRTHDATE")
            updated_settings = get_settings(
                user_id=os.getenv("USER_ID"), password=os.getenv("PASSWORD"), birthdate=os.getenv("BIRTHDATE")
            )
            self.user_id = updated_settings.user_id
            self.password = updated_settings.password
            self.birthdate = updated_settings.birthdate

    def scrape(self) -> str:
        """スクレイピングを実行する

        Returns:
            str: スクレイピング結果のHTMLソース

        Raises:
            ScrapingError: スクレイピングに失敗した場合
        """
        try:
            if not self.user_id or not self.password or not self.birthdate:
                raise ScrapingError("user_id, password, and birthdate must be set.")

            driver = get_chrome_driver()
            return scrape(self.user_id, self.password.get_secret_value(), self.birthdate, driver)
        except ScrapingError as e:
            key = "error_image.png"
            s3_uri = f"s3://{settings.s3_bucket_name}/{key}"
            logger.exception(f"An error occurred during the scraping process. Please check {s3_uri} for error details.")
            upload_file(
                bucket=settings.s3_bucket_name,
                key=key,
                file_path=e.error_image_path,
            )
            raise


class DcpOperationStatusExtractor:
    """確定拠出年金の運用状況を抽出するクラス"""

    def __init__(self) -> None:
        pass

    def is_tag_element(self, element: Any) -> TypeGuard[Tag]:
        """要素がタグ要素かどうかを判定する型ガード

        Args:
            element (Any): 判定する要素

        Returns:
            TypeGuard[Tag]: 要素がタグ要素であるかどうか
        """
        if isinstance(element, Tag):
            return True
        return False

    def is_tag_elements(self, elements: Any) -> TypeGuard[list[Tag]]:
        """要素がタグ要素のリストかどうかを判定する型ガード

        Args:
            elements (Any): 判定する要素

        Returns:
            TypeGuard[list[Tag]]: 要素がタグ要素のリストであるかどうか
        """
        if isinstance(elements, list) and all(isinstance(e, Tag) for e in elements):
            return True
        return False

    def extract(self, html_source: str) -> DcpAssetsInfo:
        """スクレイピング結果から資産情報を抽出する

        Args:
            html_source (str): スクレイピング結果のHTMLソース

        Returns:
            DcpAssetsInfo: 抽出した資産情報

        Raises:
            ExtractError: 抽出に失敗した場合
        """
        try:
            soup = BeautifulSoup(html_source, "html.parser")

            # 総評価額を取得
            total_assets = self._extract_total_assets(soup)

            # 商品別
            assets_each_product = self._extract_product_assets(soup)

            return DcpAssetsInfo(
                total=total_assets,
                products=assets_each_product,
            )

        except Exception:
            logger.exception("extract_assets error")
            # TODO: html_sourceをS3にアップロードする処理を追加する
            raise ExtractError("extract_assets error")

    def _extract_total_assets(self, soup: BeautifulSoup) -> DcpTotalAssets:
        """総評価額を抽出する

        Args:
            soup (BeautifulSoup): BeautifulSoupオブジェクト

        Returns:
            DcpTotalAssets: 抽出した総評価額情報
        """
        logger.info("_extract_total_assets start.")

        total = soup.find(class_="total")
        if not self.is_tag_element(total):
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
        if not self.is_tag_element(product_info):
            raise ElementTypeError("product_info is not a tag element")

        products = product_info.find_all(class_="infoDetailUnit_02 pc_mb30")
        if not self.is_tag_elements(products):
            raise ElementTypeError("products is not a tag element list")

        assets_each_product: Dict[str, DcpProductAssets] = {}
        for product in products:
            table_body = product.find("tbody")
            if not self.is_tag_element(table_body):
                raise ElementTypeError("table_body is not a tag element")

            table_rows = table_body.find_all("tr")
            if not self.is_tag_elements(table_rows):
                raise ElementTypeError("table_rows is not a tag element list")

            product_assets = DcpProductAssets(
                cumulative_acquisition_costs=table_rows[2].find_all("td")[-1].text,
                gains_or_losses=table_rows[5].find_all("td")[-1].text,
                asset_valuation=table_rows[2].find_all("td")[2].text,
            )

            product_info = product.find(class_="infoHdWrap00")
            if not self.is_tag_element(product_info):
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


class DcpOperationStatusTransformer:
    """確定拠出年金の運用状況を変換するクラス"""

    def __init__(self) -> None:
        pass

    def transform(self, assets_info: DcpAssetsInfo) -> DcpOpsIndicators:
        """資産情報を変換する

        Args:
            assets_info (DcpAssetsInfo): 資産情報

        Returns:
            DcpOpsIndicators: 運用指標情報
        """

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
        total_amount_at_60age_int = int(240000 * (((1 + actual_yield_rate) ** 26 - 1) / actual_yield_rate))
        total_amount_at_60age = f"{total_amount_at_60age_int:,.0f}円"

        # 計算した値で運用指標オブジェクトを作成
        operational_indicators = DcpOpsIndicators(
            operation_years=operation_years,
            actual_yield_rate=actual_yield_rate,
            expected_yield_rate=0.06,
            total_amount_at_60age=total_amount_at_60age,
        )
        logger.info("operational_indicators.", extra=operational_indicators.__dict__)

        return operational_indicators

    def yen_to_int(self, yen: str) -> int:
        """円表記の文字列を数値に変換する

        Args:
            yen (str): 円表記の文字列

        Returns:
            int: 数値

        Example:
            >>> yen = "1,234,567円"
            >>> transformer = DcpOperationStatusTransformer()
            >>> transformer.yen_to_int(yen)
            1234567
        """
        return int(yen.replace("円", "").replace(",", ""))

    def make_message(self, assets_info: DcpAssetsInfo, operational_indicators: DcpOpsIndicators) -> str:
        """通知用メッセージを作成する

        Args:
            assets_info (DcpAssetsInfo): 資産情報
            operational_indicators (DcpOpsIndicators): 運用指標情報

        Returns:
            str: 通知用メッセージ
        """
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


class DcpOperationStatusNotifier:
    """確定拠出年金の運用状況を通知するクラス"""

    def __init__(self) -> None:
        pass

    def notify(self, message: str) -> None:
        """通知用メッセージを作成する"""
        publish(
            topic_arn=settings.sns_topic_arn,
            message=message,
            subject="確定拠出年金 運用状況",
        )
