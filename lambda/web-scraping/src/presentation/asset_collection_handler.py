"""資産情報収集の Presentation 層"""

from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from shared.domain.asset_record_interface import IAssetRecordRepository
from shared.domain.asset_record_object import AssetRecord

from src.application import WebScrapingService
from src.config.settings import get_logger, get_settings
from src.domain import IScraper, ScrapingParams
from src.infrastructure import (
    GoogleSheetAssetRecordRepository,
    S3ArtifactRepository,
    SeleniumScraper,
    get_ssm_json_parameter,
)

settings = get_settings()
logger = get_logger()


def main(
    scraper: Optional[IScraper] = None,
    asset_record_repository: Optional[IAssetRecordRepository] = None,
) -> None:
    """メイン処理

    Args:
        scraper (Optional[IScraper]): スクレイパー（テスト時にMockを注入可能）
        asset_record_repository (Optional[IAssetRecordRepository]): 資産レコードリポジトリ（テスト時にMockを注入可能）

    Raises:
        ScrapingFailed: スクレイピングまたは資産情報抽出処理失敗時
        ArtifactUploadError: エラーアーティファクトの S3 保存失敗時
        AssetRecordError: 資産レコードの保存失敗時
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

    if asset_record_repository is None:
        spreadsheet_param = get_ssm_json_parameter(name=settings.spreadsheet_parameter_name, decrypt=True)
        asset_record_repository = GoogleSheetAssetRecordRepository(
            spreadsheet_id=spreadsheet_param["spreadsheet_id"],
            sheet_name=spreadsheet_param["sheet_name"],
            credentials=spreadsheet_param["credentials"],
        )

    artifact_repository = S3ArtifactRepository(settings.data_bucket_name)

    web_scraping_service = WebScrapingService(
        scraper=scraper,
        artifact_repository=artifact_repository,
    )
    products = web_scraping_service.scrape()

    today = datetime.now(ZoneInfo("Asia/Tokyo")).date()
    records = AssetRecord.from_dcp_asset_products(target_date=today, products=products)
    asset_record_repository.save_daily_records(records)
