from typing import Optional

from application import NotificationService, WebScrapingService, to_operational_indicators
from config.settings import get_settings
from domain import IDcpScraper, INotifier, ScrapingParams
from infrastructure import LineNotifier, SeleniumDcpScraper, get_ssm_json_parameter

settings = get_settings()


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

    web_scraping_service = WebScrapingService(scraper=scraper)
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
