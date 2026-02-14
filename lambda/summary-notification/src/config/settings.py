from shared.config.base_settings import BaseEnvSettings, get_logger  # noqa: F401


class EnvSettings(BaseEnvSettings):
    """サマリ通知関数の設定"""

    # Systems Manager Parameter Store のパラメータ名
    line_message_parameter_name: str
    spreadsheet_parameter_name: str


def get_settings(settings_instance: EnvSettings | None = None) -> EnvSettings:
    """設定インスタンスを取得する

    Args:
        settings_instance (EnvSettings | None, optional): 設定インスタンス. Defaults to None.

    Returns:
        EnvSettings: 設定インスタンス
    """
    if settings_instance is None:
        settings_instance = EnvSettings()
    return settings_instance
