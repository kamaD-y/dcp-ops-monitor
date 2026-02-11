from shared.config.base_settings import BaseEnvSettings, get_logger  # noqa: F401


class EnvSettings(BaseEnvSettings):
    """スクレイピング関数の設定"""

    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )

    # Systems Manager Parameter Store のパラメータ名
    scraping_parameter_name: str


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
