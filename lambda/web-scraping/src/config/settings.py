from aws_lambda_powertools import Logger
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_logger(logger: Logger | None = None) -> Logger:
    """Logger のインスタンスを取得する

    Args:
        logger (Logger | None, optional): Logger のインスタンス. Defaults to None.

    Returns:
        Logger: Logger のインスタンス
    """
    if logger is None:
        logger = Logger()
    return logger


class EnvSettings(BaseSettings):
    """スクレイピング関数の設定"""

    powertools_log_level: str = "INFO"

    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )

    # Systems Manager Parameter Store のパラメータ名
    scraping_parameter_name: str

    # データ保存用 S3 バケット名
    data_bucket_name: str

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


def get_settings(settings_instance: EnvSettings | None = None) -> EnvSettings:
    """設定インスタンスを取得する

    Args:
        settings_instance (EnvSettings | None, optional): 設定インスタンス. Defaults to None.

    Returns:
        EnvSettings: 設定インスタンス
    """
    if settings_instance is None:
        settings_instance = EnvSettings()  # type: ignore (missing-argument)
    return settings_instance
