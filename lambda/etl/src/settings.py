from typing import Any, Optional

from aws_lambda_powertools import Logger
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_logger(logger: Logger = Logger()) -> Logger:
    """Loggerのインスタンスを取得する

    Args:
        logger (Logger, optional): Loggerのインスタンス. Defaults to Logger().

    Returns:
        Logger: Loggerのインスタンス
    """
    return logger


class ScrapingSettings(BaseSettings):
    """スクレイピング関数の設定"""

    # 共通設定
    log_level: str = "INFO"

    # スクレイピング関連設定
    start_url: str
    login_user_id: Optional[str] = None
    login_password: Optional[SecretStr] = None
    login_birthdate: Optional[str] = None
    login_parameter_name: Optional[str] = None
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )

    # エラー関連設定
    error_bucket_name: str

    # 通知関連設定
    sns_topic_arn: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# TODO: Anyを具体的な型への置き換えを検討
def get_settings(settings_instance: ScrapingSettings = ScrapingSettings(), **kwargs: Any) -> ScrapingSettings:
    """設定インスタンスを取得する

    Args:
        settings_instance (ScrapingSettings, optional): 設定インスタンス. Defaults to ScrapingSettings().
        **kwargs (Any): その他のキーワード引数

    Returns:
        ScrapingSettings: 設定インスタンス
    """
    if kwargs:
        settings_instance = ScrapingSettings(**kwargs)
    return settings_instance
