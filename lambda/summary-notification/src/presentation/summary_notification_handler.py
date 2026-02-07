"""サマリ通知ハンドラー"""

from src.application import SummaryNotificationService
from src.config.settings import get_logger, get_settings
from src.domain import IAssetRepository, INotifier
from src.infrastructure import (
    LineNotifier,
    S3AssetRepository,
    get_ssm_json_parameter,
)

settings = get_settings()
logger = get_logger()


def main(
    asset_repository: IAssetRepository | None = None,
    notifier: INotifier | None = None,
) -> None:
    """メイン処理

    Args:
        asset_repository: 資産リポジトリ (テスト時に Mock 注入可能)
        notifier: 通知クライアント (テスト時に Mock 注入可能)
    """
    # 資産リポジトリが指定されていない場合のみ実装を使用
    if asset_repository is None:
        asset_repository = S3AssetRepository(bucket=settings.data_bucket_name)

    # 通知クライアントが指定されていない場合のみ実装を使用
    if notifier is None:
        line_message_parameter = get_ssm_json_parameter(name=settings.line_message_parameter_name, decrypt=True)
        notifier = LineNotifier(
            url=line_message_parameter["url"],
            token=line_message_parameter["token"],
        )

    # サマリ通知サービス実行
    service = SummaryNotificationService(asset_repository=asset_repository, notifier=notifier)
    service.send_summary()

    logger.info("サマリ通知処理が完了しました")
