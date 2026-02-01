from datetime import datetime

from src.config.settings import get_logger
from src.domain import (
    DcpAssets,
    IObjectRepository,
    IScraper,
    ScrapingFailed,
)

logger = get_logger()


class WebScrapingService:
    def __init__(
        self,
        scraper: IScraper,
        object_repository: IObjectRepository,
    ) -> None:
        self.scraper: IScraper = scraper
        self.object_repository: IObjectRepository = object_repository

    def scrape(self) -> DcpAssets:
        try:
            return self.scraper.fetch_asset_valuation()
        except ScrapingFailed as e:
            self._upload_error_artifacts(e)
            raise

    def _upload_error_artifacts(self, e: ScrapingFailed) -> None:
        """エラーアーティファクトを S3 にアップロードする"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        if e.tmp_screenshot_path:
            logger.info("エラー画像のアップロード開始")
            key = f"files/{timestamp}.png"
            self.object_repository.upload_file(key=key, file_path=e.tmp_screenshot_path)
            logger.info("エラー画像をアップロードしました。", extra={"error_screenshot_key": key})
            e.error_screenshot_key = key

        if e.tmp_html_path:
            logger.info("エラーになった資産情報 HTML ファイルのアップロード開始")
            key = f"files/{timestamp}.html"
            self.object_repository.upload_file(key=key, file_path=e.tmp_html_path)
            logger.info("資産情報 HTML ファイルをアップロードしました。", extra={"error_html_key": key})
            e.error_html_key = key
