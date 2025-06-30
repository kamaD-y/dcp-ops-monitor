from domain.interface import ScraperInterface
from domain.value_object import DcpAssetsInfo, ScrapingParams
from infrastructure.aws.s3 import put_object, upload_file
from infrastructure.scraping.nrk_scraping import ExtractError, NRKScraper, ScrapingError
from settings import get_logger, get_settings

logger = get_logger()
settings = get_settings()


class DcpOpsMonitorExtractor:
    """確定拠出年金の運用状況を抽出するクラス

    このクラスは、スクレイピング結果から資産情報を抽出します。
    """

    def extract(self) -> DcpAssetsInfo:
        """スクレイピングを実行する

        Returns:
            str: スクレイピング結果のHTMLソース

        Raises:
            ScrapingError: スクレイピングに失敗した場合
        """
        login_params = {
            **({"user_id": settings.login_user_id} if settings.login_user_id else {}),
            **({"password": settings.login_password.get_secret_value()} if settings.login_password else {}),
            **({"birthdate": settings.login_birthdate} if settings.login_birthdate else {}),
            **({"parameter_name": settings.login_parameter_name} if settings.login_parameter_name else {}),
        }
        scraping_params = ScrapingParams(**login_params)
        scraper = NRKScraper(scraping_params.user_id, scraping_params.password, scraping_params.birthdate)
        self._scrape(scraper)
        assets = self._extract(scraper)
        return assets

    def _scrape(self, scraper: ScraperInterface) -> None:
        """スクレイピングを実行し、資産情報ページのHTMLソースを取得する

        Raises:
            ScrapingError: スクレイピングに失敗した場合
        """
        try:
            scraper.scrape(settings.start_url)
        except ScrapingError as e:
            if e.error_image_path:
                key = "error_image.png"
                s3_uri = f"s3://{settings.error_bucket_name}/{key}"
                upload_file(
                    bucket=settings.error_bucket_name,
                    key=key,
                    file_path=e.error_image_path,
                )
                logger.info(f"An error occurred during the scraping process. Please check {s3_uri} for error details.")
            raise

    def _extract(self, scraper: ScraperInterface) -> DcpAssetsInfo:
        """スクレイピング結果から資産情報を抽出する

        Args:
            html_source (str): スクレイピング結果のHTMLソース

        Returns:
            DcpAssetsInfo: 抽出した資産情報

        Raises:
            ExtractError: 抽出に失敗した場合
        """
        try:
            return scraper.extract()

        except ExtractError as e:
            logger.exception("An error occurred during the extracting process.")

            key = "error_html.html"
            s3_uri = f"s3://{settings.error_bucket_name}/{key}"
            body = scraper.page_source.encode("utf-8")
            put_object(
                bucket=settings.error_bucket_name,
                key=key,
                body=body,
            )
            logger.info(f"An error occurred during the extracting process. Please check {s3_uri} for error details.")
            raise
