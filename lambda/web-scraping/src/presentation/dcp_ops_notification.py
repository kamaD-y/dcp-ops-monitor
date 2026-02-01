"""DCP 運用状況通知の Presentation 層"""

from typing import Optional

from src.application import NotificationService, WebScrapingService, to_operational_indicators
from src.config.settings import get_logger, get_settings
from src.domain import INotifier, IScraper, ScrapingParams
from src.infrastructure import (
    LineNotifier,
    S3ObjectRepository,
    SeleniumScraper,
    get_ssm_json_parameter,
)

settings = get_settings()
logger = get_logger()


def main(
    scraper: Optional[IScraper] = None,
    notifier: Optional[INotifier] = None,
) -> None:
    """メイン処理

    Args:
        scraper (Optional[IScraper]): スクレイパー（テスト時にMockを注入可能）
        notifier (Optional[INotifier]): 通知サービス（テスト時にMockを注入可能）

    Raises:
        ScrapingFailed: スクレイピングまたは資産情報抽出処理失敗時
        NotificationFailed: 通知送信失敗時
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

    try:
        web_scraping_service = WebScrapingService(
            scraper=scraper,
            object_repository=S3ObjectRepository(settings.error_bucket_name),
        )
        assets_info = web_scraping_service.scrape()

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
    except Exception:
        raise
