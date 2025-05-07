from typing import Any, Dict, Optional

from aws_lambda_powertools import Logger
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_logger(logger: Logger = Logger()) -> Logger:
    """Loggerのインスタンスを取得する"""
    return logger


class ScrapingSettings(BaseSettings):
    """スクレイピング関数の設定"""

    # 共通設定
    log_level: str = Field(default="INFO")

    # スクレイピング関連設定
    login_url: str = Field(default="https://www.nrkn.co.jp/rk/login.html")
    user_id: Optional[str] = None
    password: Optional[SecretStr] = None
    birthdate: Optional[str] = None
    user_agent: str = Field(
        default=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        )
    )

    # Parameter Store関連設定
    login_parameter_arn: Optional[str] = None

    # SNS関連設定
    sns_topic_arn: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# TODO: Anyを具体的な型への置き換えを検討
def get_settings(settings_instance: ScrapingSettings = ScrapingSettings(), **kwargs: Any) -> ScrapingSettings:
    """
    設定インスタンスを取得する
    初回呼び出し時にParameter Storeからの設定読み込みも行う
    """
    if kwargs:
        settings_instance = ScrapingSettings(**kwargs)
    return settings_instance
