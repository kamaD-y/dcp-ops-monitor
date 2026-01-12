from typing import Dict

from bs4 import BeautifulSoup

from config.settings import get_logger
from src.domain import AssetExtractionFailed, DcpAssetInfo, DcpAssets, IDcpExtractor

logger = get_logger()


class BeautifulSoupDcpExtractor(IDcpExtractor):
    """BeautifulSoup を使用した DCP 資産抽出実装"""

    def __init__(self, parser: str = "html.parser") -> None:
        """コンストラクタ

        Args:
            parser: BeautifulSoup で使用するパーサー (デフォルト: "html.parser")
        """
        self.parser = parser

    def extract(self, html: str) -> DcpAssets:
        """HTML から DCP 資産情報を抽出

        Args:
            html: HTML ソース文字列

        Returns:
            DcpAssets: 抽出された資産情報

        Raises:
            AssetExtractionFailed: 抽出に失敗した場合
        """
        try:
            logger.info("資産情報の抽出開始")

            # 総評価額を抽出
            total_assets = self._extract_total_assets(html)

            # 商品別資産を抽出
            products_assets = self._extract_product_assets(html)

            logger.info("資産情報の抽出完了")
            return DcpAssets(total=total_assets, products=products_assets)
        except Exception as e:
            raise AssetExtractionFailed("資産情報の抽出に失敗しました。") from e

    def _extract_total_assets(self, html: str) -> DcpAssetInfo:
        """総評価額を抽出

        Args:
            html: HTML ソース文字列

        Returns:
            DcpAssetInfo: 総評価額情報
        """
        logger.info("総評価額の抽出開始")

        soup = BeautifulSoup(html, self.parser)
        total = soup.find(class_="total")

        total_assets = DcpAssetInfo.from_html_strings(
            cumulative_contributions_str=total.find_all("dd")[0].text,
            gains_or_losses_str=total.find_all("dd")[1].text,
            asset_valuation_str=total.find_all("dd")[2].text,
        )

        logger.info(
            "総評価額の抽出完了",
            extra=total_assets.__dict__,
        )
        return total_assets

    def _extract_product_assets(self, html: str) -> Dict[str, DcpAssetInfo]:
        """商品別資産を抽出

        Args:
            html: HTML ソース文字列

        Returns:
            Dict[str, DcpAssetInfo]: 商品別資産情報
        """
        logger.info("商品別の資産評価額の抽出開始")

        soup = BeautifulSoup(html, self.parser)
        product_info = soup.find(id="prodInfo")

        products = product_info.find_all(class_="infoDetailUnit_02 pc_mb30")

        # 商品毎の資産評価額を取得する
        assets_each_product: Dict[str, DcpAssetInfo] = {}
        for product in products:
            table_body = product.find("tbody")

            table_rows = table_body.find_all("tr")

            product_assets = DcpAssetInfo.from_html_strings(
                cumulative_contributions_str=table_rows[2].find_all("td")[-1].text,
                gains_or_losses_str=table_rows[5].find_all("td")[-1].text,
                asset_valuation_str=table_rows[2].find_all("td")[2].text,
            )

            product_info_elem = product.find(class_="infoHdWrap00")

            product_name = product_info_elem.text.strip()
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
