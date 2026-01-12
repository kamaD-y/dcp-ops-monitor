from datetime import datetime
from typing import Any, Dict, Optional, TypeGuard

from bs4 import BeautifulSoup
from bs4.element import Tag

from config.settings import get_logger
from src.domain import AssetExtractionError, DcpAssetInfo, DcpAssets, IDcpScraper, IS3Repository, ScrapingFailed

logger = get_logger()


class WebScrapingService:
    def __init__(self, scraper: IDcpScraper, s3_repository: IS3Repository) -> None:
        self.scraper: IDcpScraper = scraper
        self.s3_repository: IS3Repository = s3_repository

    def scrape(self) -> str:
        try:
            return self.scraper.fetch_asset_valuation_html()
        except ScrapingFailed as e:
            error_image_path = self.scraper.get_error_image_path()
            if not error_image_path:
                raise

            logger.info("スクレイピングエラー画像の S3 アップロード開始")
            key = f"files/{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            try:
                self.s3_repository.upload_file(
                    key=key,
                    file_path=error_image_path,
                )
            except Exception as upload_error:
                raise Exception("スクレイピングエラー画像の S3 アップロードに失敗しました。") from upload_error

            logger.info(
                "エラー画像を S3 にアップロードしました。",
                extra={"error_file_key": key},
            )
            # error_file_keyを設定して再raise
            e.error_file_key = key
            raise

    def extract_asset_valuation(self, html_source: str) -> DcpAssets:
        """HTML から資産情報を抽出する

        Returns:
            DcpAssets: 抽出した資産情報
        """
        try:
            soup = BeautifulSoup(html_source, "html.parser")

            logger.info("資産情報の抽出開始")
            # 総評価額を取得
            total_assets = self._extract_total_assets(soup)

            # 商品別
            assets_each_product = self._extract_product_assets(soup)

            logger.info("資産情報の抽出完了")
            return DcpAssets(
                total=total_assets,
                products=assets_each_product,
            )

        except Exception as e:
            logger.info("エラーになった資産情報 HTML ファイルの S3 アップロード開始")
            key = f"files/{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
            try:
                self.s3_repository.put_object(
                    key=key,
                    body=html_source,
                )
            except Exception as upload_error:
                logger.error(
                    "資産情報 HTML ファイルの S3 アップロードに失敗しました。",
                    exc_info=upload_error,
                )
            else:
                logger.info(
                    "資産情報 HTML ファイルを S3 にアップロードしました。",
                    extra={"error_file_key": key},
                )
            raise AssetExtractionError("資産情報の抽出に失敗しました。", error_file_key=key) from e

    def _extract_total_assets(self, soup: BeautifulSoup) -> DcpAssetInfo:
        """総評価額を抽出する

        Args:
            soup (BeautifulSoup): BeautifulSoup オブジェクト

        Returns:
            DcpAssetInfo: 抽出した総評価額情報
        """
        logger.info("総評価額の抽出開始")

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

    def _extract_product_assets(self, soup: BeautifulSoup) -> Dict[str, DcpAssetInfo]:
        """商品別の資産評価額を抽出する

        Args:
            soup (BeautifulSoup): BeautifulSoup オブジェクト

        Returns:
            Dict[str, DcpAssetInfo]: 商品別の資産評価額情報
        """
        logger.info("商品別の資産評価額の抽出開始")

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

            product_info = product.find(class_="infoHdWrap00")

            product_name = product_info.text.strip()
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
