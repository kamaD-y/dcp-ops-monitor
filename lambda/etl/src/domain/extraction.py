from typing import Any, Dict, TypeGuard

from bs4 import BeautifulSoup
from bs4.element import Tag

from domain.dcp_value_object import DcpAssetsInfo, DcpProductAssets, DcpTotalAssets, ScrapingParams
from infrastructure.aws.s3 import put_object, upload_file
from infrastructure.scraping.dcp_scraping import NRKScraper, ScrapingError
from settings.settings import get_logger, get_settings

logger = get_logger()
settings = get_settings()


class ExtractError(Exception):
    pass


class ElementTypeError(ExtractError):
    pass


class DcpOpsMonitorExtractor:
    """確定拠出年金の運用状況を抽出するクラス

    このクラスは、スクレイピング結果から資産情報を抽出します。
    """

    def __init__(self) -> None:
        self.scraping_params = ScrapingParams(
            settings.login_user_id,
            settings.login_password.get_secret_value() if settings.login_password else "",
            settings.login_birthdate,
        )

    def extract(self) -> DcpAssetsInfo:
        """スクレイピングを実行し、資産情報を抽出する

        Returns:
            DcpAssetsInfo: 抽出した資産情報
        """
        html_source = self._scrape()
        return self._extract(html_source)

    def _scrape(self) -> str:
        """スクレイピングを実行する

        Returns:
            str: スクレイピング結果のHTMLソース

        Raises:
            ScrapingError: スクレイピングに失敗した場合
        """
        try:
            return NRKScraper(**self.scraping_params.__dict__).scrape(settings.start_url)
        except ScrapingError as e:
            if e.error_image_path:
                key = "error_image.png"
                s3_uri = f"s3://{settings.error_bucket_name}/{key}"
                upload_file(
                    bucket=settings.error_bucket_name,
                    key=key,
                    file_path=e.error_image_path,
                )
                logger.info(f"An error occurred during the scraping process. Please check {s3_uri} for error details.")
            raise

    def _extract(self, html_source: str) -> DcpAssetsInfo:
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

        except Exception as e:
            logger.exception("An error occurred during the extracting process.")

            key = "error_html.html"
            s3_uri = f"s3://{settings.error_bucket_name}/{key}"
            body = html_source.encode("utf-8")
            put_object(
                bucket=settings.error_bucket_name,
                key=key,
                body=body,
            )
            logger.info(f"An error occurred during the extracting process. Please check {s3_uri} for error details.")

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
