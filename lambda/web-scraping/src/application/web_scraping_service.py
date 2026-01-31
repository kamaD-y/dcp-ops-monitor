from datetime import datetime

from src.config.settings import get_logger
from src.domain import (
    DcpAssets,
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
    ) -> None:
        self.scraper: IDcpScraper = scraper
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

        if e.screenshot_path:
            logger.info("エラー画像のアップロード開始")
            key = f"files/{timestamp}.png"
            try:
                self.object_repository.upload_file(
                    key=key,
                    file_path=e.screenshot_path,
                )
            except Exception as upload_error:
                raise Exception("エラー画像のアップロードに失敗しました。") from upload_error

            logger.info("エラー画像をアップロードしました。", extra={"error_file_key": key})
            e.error_file_key = key

        if e.html_source:
            logger.info("エラーになった資産情報 HTML ファイルのアップロード開始")
            key = f"files/{timestamp}.html"
            try:
                self.object_repository.put_object(
                    key=key,
                    body=e.html_source,
                )
            except Exception as upload_error:
                raise Exception("資産情報 HTML ファイルのアップロードに失敗しました。") from upload_error

            logger.info("資産情報 HTML ファイルをアップロードしました。", extra={"error_file_key": key})
            e.error_file_key = key
