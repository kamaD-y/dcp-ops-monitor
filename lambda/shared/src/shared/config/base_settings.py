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


class BaseEnvSettings(BaseSettings):
    """共通設定の基底クラス"""

    powertools_log_level: str = "INFO"

    # データ保存用 S3 バケット名
    data_bucket_name: str

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
