from typing import Any, Optional

from aws_lambda_powertools import Logger
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_logger(logger: Logger = Logger()) -> Logger:
    """Loggerのインスタンスを取得する

    Args:
        logger (Logger, optional): Loggerのインスタンス. Defaults to Logger().

    Returns:
        Logger: Loggerのインスタンス
    """
    return logger


class NotificationSettings(BaseSettings):
    """スクレイピング関数の設定"""

    # 共通設定
    log_level: str = Field(default="INFO")

    line_message_api_url: str = Field(default="https://api.line.me/v2/bot/message/broadcast")
    line_message_api_token: Optional[SecretStr] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# TODO: Anyを具体的な型への置き換えを検討
def get_settings(
    settings_instance: NotificationSettings = NotificationSettings(), **kwargs: Any
) -> NotificationSettings:
    """設定インスタンスを取得する

    Args:
        settings_instance (NotificationSettings, optional): 設定インスタンス. Defaults to NotificationSettings().
        **kwargs (Any): その他のキーワード引数

    Returns:
        NotificationSettings: 設定インスタンス
    """
    if kwargs:
        settings_instance = NotificationSettings(**kwargs)
    return settings_instance
