from datetime import datetime

from shared.domain.asset_object import DcpAssetInfo

from src.config.settings import get_logger
from src.domain import (
    IArtifactRepository,
    IScraper,
    ScrapingFailed,
)

logger = get_logger()


class WebScrapingService:
    def __init__(
        self,
        scraper: IScraper,
        artifact_repository: IArtifactRepository,
    ) -> None:
        self.scraper: IScraper = scraper
        self.artifact_repository: IArtifactRepository = artifact_repository

    def scrape(self) -> dict[str, DcpAssetInfo]:
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
            key = f"errors/{timestamp}.png"
            self.artifact_repository.save_error_artifact(key=key, file_path=e.tmp_screenshot_path)
            logger.info("エラー画像をアップロードしました。", extra={"error_screenshot_key": key})
            e.error_screenshot_key = key

        if e.tmp_html_path:
            logger.info("エラーになった資産情報 HTML ファイルのアップロード開始")
            key = f"errors/{timestamp}.html"
            self.artifact_repository.save_error_artifact(key=key, file_path=e.tmp_html_path)
            logger.info("資産情報 HTML ファイルをアップロードしました。", extra={"error_html_key": key})
            e.error_html_key = key
