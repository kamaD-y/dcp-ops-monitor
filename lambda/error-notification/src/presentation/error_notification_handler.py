"""エラー通知ハンドラー"""

from aws_lambda_powertools.utilities.data_classes import CloudWatchLogsEvent

from src.application import ErrorNotificationService
from src.config.settings import get_logger, get_settings
from src.domain import ErrorLogEvents, INotifier, IObjectRepository
from src.infrastructure import (
    CloudWatchLogsAdapter,
    LineNotifier,
    S3ObjectRepository,
    get_ssm_json_parameter,
)

settings = get_settings()
logger = get_logger()


# TODO: プレゼンテーション層の Input で依存注入を削除する方向で検討
def main(
    event: CloudWatchLogsEvent,
    error_log_events: ErrorLogEvents | None = None,
    object_repository: IObjectRepository | None = None,
    notifier: INotifier | None = None,
) -> None:
    """メイン処理

    Args:
        event: CloudWatch Logs イベント (生の Lambda イベント)
        error_log_events: エラーログイベントデータ (テスト時に直接注入可能)
        object_repository: オブジェクトリポジトリ (テスト時に Mock 注入可能)
        notifier: 通知クライアント (テスト時に Mock 注入可能)
    """
    # error_log_events が指定されていない場合、Adapter で変換（URL生成も含む）
    if error_log_events is None:
        adapter = CloudWatchLogsAdapter()
        error_log_events = adapter.convert(event)

    # オブジェクトリポジトリが指定されていない場合のみ実装を使用
    if object_repository is None:
        object_repository = S3ObjectRepository()

    # 通知クライアントが指定されていない場合のみ実装を使用
    if notifier is None:
        line_message_parameter = get_ssm_json_parameter(name=settings.line_message_parameter_name, decrypt=True)
        notifier = LineNotifier(
            url=line_message_parameter["url"],
            token=line_message_parameter["token"],
        )

    # エラー通知サービス実行
    notification_service = ErrorNotificationService(object_repository, notifier)
    notification_service.send_error_notification(
        error_log_events,
        settings.error_bucket_name,
    )

    logger.info("エラー通知処理が完了しました", error_count=len(error_log_events.error_records))
