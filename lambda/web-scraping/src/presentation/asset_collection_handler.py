"""資産情報収集の Presentation 層"""

from typing import Optional

from src.application import WebScrapingService
from src.config.settings import get_logger, get_settings
from src.domain import IScraper, ScrapingParams
from src.infrastructure import (
    S3ArtifactRepository,
    SeleniumScraper,
    get_ssm_json_parameter,
)

settings = get_settings()
logger = get_logger()


def main(
    scraper: Optional[IScraper] = None,
) -> None:
    """メイン処理

    Args:
        scraper (Optional[IScraper]): スクレイパー（テスト時にMockを注入可能）

    Raises:
        ScrapingFailed: スクレイピングまたは資産情報抽出処理失敗時
        ArtifactUploadError: エラーアーティファクトの S3 保存失敗時
    """
    # scraperが指定されていない場合のみ実装を使用
    if scraper is None:
        scraping_parameter = get_ssm_json_parameter(name=settings.scraping_parameter_name, decrypt=True)
        scraping_params = ScrapingParams(
            login_user_id=scraping_parameter["login_user_id"],
            login_password=scraping_parameter["login_password"],
            login_birthdate=scraping_parameter["login_birthdate"],
            start_url=scraping_parameter["start_url"],
        )
        scraper = SeleniumScraper(user_agent=settings.user_agent, scraping_params=scraping_params)

    artifact_repository = S3ArtifactRepository(settings.data_bucket_name)

    web_scraping_service = WebScrapingService(
        scraper=scraper,
        artifact_repository=artifact_repository,
    )
    web_scraping_service.scrape()
