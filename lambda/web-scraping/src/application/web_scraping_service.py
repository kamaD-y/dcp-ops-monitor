from datetime import datetime

from src.config.settings import get_logger
from src.domain import (
    AssetExtractionFailed,
    DcpAssets,
    IDcpExtractor,
    IDcpScraper,
    IObjectRepository,
    ScrapingFailed,
)

logger = get_logger()


class WebScrapingService:
    def __init__(
        self,
        scraper: IDcpScraper,
        object_repository: IObjectRepository,
        dcp_extractor: IDcpExtractor,
    ) -> None:
        self.scraper: IDcpScraper = scraper
        self.object_repository: IObjectRepository = object_repository
        self.dcp_extractor: IDcpExtractor = dcp_extractor

    def scrape(self) -> str:
        try:
            return self.scraper.fetch_asset_valuation_html()
        except ScrapingFailed as e:
            error_image_path = self.scraper.get_error_image_path()
            if not error_image_path:
                raise

            logger.info("エラー画像のアップロード開始")
            key = f"files/{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            try:
                self.object_repository.upload_file(
                    key=key,
                    file_path=error_image_path,
                )
            except Exception as upload_error:
                raise Exception("エラー画像のアップロードに失敗しました。") from upload_error

            logger.info("エラー画像をアップロードしました。", extra={"error_file_key": key})
            # error_file_keyを設定して再raise
            e.error_file_key = key
            raise

    def extract_asset_valuation(self, html_source: str) -> DcpAssets:
        """HTML から資産情報を抽出する

        Args:
            html_source: HTML ソース文字列

        Returns:
            DcpAssets: 抽出した資産情報

        Raises:
            AssetExtractionFailed: 抽出に失敗した場合
        """
        try:
            return self.dcp_extractor.extract(html_source)
        except AssetExtractionFailed as e:
            logger.info("エラーになった資産情報 HTML ファイルの S3 アップロード開始")
            key = f"files/{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
            try:
                self.object_repository.put_object(
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
            # error_file_key を設定して再 raise
            e.error_file_key = key
            raise
