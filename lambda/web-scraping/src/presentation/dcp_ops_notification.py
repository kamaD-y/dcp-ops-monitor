from typing import Optional

from application import NotificationService, WebScrapingService, to_operational_indicators
from config.settings import get_logger, get_settings
from domain import AssetExtractionError, IDcpScraper, INotifier, ScrapingError, ScrapingParams
from infrastructure import LineNotifier, S3Repository, SeleniumDcpScraper, get_ssm_json_parameter

settings = get_settings()
logger = get_logger()


def main(
    scraper: Optional[IDcpScraper] = None,
    notifier: Optional[INotifier] = None,
):
    """メイン処理

    Args:
        scraper (Optional[IDcpScraper]): スクレイパー（テスト時にMockを注入可能）
        notifier (Optional[INotifier]): 通知サービス（テスト時にMockを注入可能）
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
        scraper = SeleniumDcpScraper(user_agent=settings.user_agent, scraping_params=scraping_params)

    try:
        web_scraping_service = WebScrapingService(
            scraper=scraper, s3_repository=S3Repository(settings.error_bucket_name)
        )
        html_source = web_scraping_service.scrape()
        assets_info = web_scraping_service.extract_asset_valuation(html_source)

        operational_indicators = to_operational_indicators(total_assets=assets_info.total)

        # notifierが指定されていない場合のみ実装を使用
        if notifier is None:
            line_message_parameter = get_ssm_json_parameter(name=settings.line_message_parameter_name, decrypt=True)
            notifier = LineNotifier(
                url=line_message_parameter["url"],
                token=line_message_parameter["token"],
            )

        notification_service = NotificationService(notifier=notifier)
        notification_service.send_notification(assets_info, operational_indicators)

    except ScrapingError as e:
        logger.error(
            "スクレイピング処理でエラーが発生しました。",
            extra={"error_image_path": e.error_image_path},
        )
        raise
    except AssetExtractionError as e:
        logger.error(
            "資産情報の抽出でエラーが発生しました。",
            extra={"html_source_length": len(e.html_source) if e.html_source else 0},
        )
        raise
