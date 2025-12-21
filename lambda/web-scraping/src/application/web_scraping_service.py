from typing import Any, Dict, Optional, TypeGuard

from bs4 import BeautifulSoup
from bs4.element import Tag

from config.settings import get_logger
from domain import DcpAssetsInfo, DcpProductAssets, DcpTotalAssets, IDcpScraper
from infrastructure import SeleniumDcpScraper

logger = get_logger()


class WebScrapingService:
    def __init__(self, scraper: IDcpScraper) -> None:
        self.scraper: IDcpScraper = scraper

    def scrape(self) -> str:
        try:
            return self.scraper.fetch_asset_valuation_html()
        except Exception as e:
            error_image_path = self.scraper.get_error_image_path()
            if error_image_path:
                # S3 などにスクリーンショットを保存する処理をここに追加可能
                pass
            raise

    def extract_asset_valuation(self, html_source: str) -> DcpAssetsInfo:
        """HTML から資産情報を抽出する

        Returns:
            DcpAssetsInfo: 抽出した資産情報
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
            raise

    def _extract_total_assets(self, soup: BeautifulSoup) -> DcpTotalAssets:
        """総評価額を抽出する

        Args:
            soup (BeautifulSoup): BeautifulSoup オブジェクト

        Returns:
            DcpTotalAssets: 抽出した総評価額情報
        """
        logger.info("_extract_total_assets start.")

        total = soup.find(class_="total")

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
            soup (BeautifulSoup): BeautifulSoup オブジェクト

        Returns:
            Dict[str, DcpProductAssets]: 商品別の資産評価額情報
        """
        logger.info("_extract_product_assets start.")

        product_info = soup.find(id="prodInfo")

        products = product_info.find_all(class_="infoDetailUnit_02 pc_mb30")

        # 商品毎の資産評価額を取得する
        assets_each_product: Dict[str, DcpProductAssets] = {}
        for product in products:
            table_body = product.find("tbody")

            table_rows = table_body.find_all("tr")

            product_assets = DcpProductAssets(
                cumulative_acquisition_costs=table_rows[2].find_all("td")[-1].text,
                gains_or_losses=table_rows[5].find_all("td")[-1].text,
                asset_valuation=table_rows[2].find_all("td")[2].text,
            )

            product_info = product.find(class_="infoHdWrap00")

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
