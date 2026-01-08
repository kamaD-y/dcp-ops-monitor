"""エラー通知ハンドラー"""

from aws_lambda_powertools.utilities.data_classes import CloudWatchLogsEvent

from src.application import ErrorNotificationService, MessageFormatter
from src.config.settings import get_logger, get_settings
from src.domain import ICloudWatchLogsParser, INotifier, IObjectRepository
from src.infrastructure import (
    CloudWatchLogsParser,
    LineNotifierAdapter,
    S3ObjectRepository,
    get_ssm_json_parameter,
)

settings = get_settings()
logger = get_logger()


def main(
    event: CloudWatchLogsEvent,
    parser: ICloudWatchLogsParser | None = None,
    object_repository: IObjectRepository | None = None,
    notifier: INotifier | None = None,
) -> None:
    """メイン処理

    Args:
        event: CloudWatch Logs イベント
        parser: CloudWatch Logs パーサー (テスト時に Mock 注入可能)
        object_repository: オブジェクトリポジトリ (テスト時に Mock 注入可能)
        notifier: 通知クライアント (テスト時に Mock 注入可能)
    """
    # parser が指定されていない場合のみ実装を使用
    if parser is None:
        parser = CloudWatchLogsParser()

    # オブジェクトリポジトリが指定されていない場合のみ実装を使用
    if object_repository is None:
        object_repository = S3ObjectRepository()

    # 通知クライアントが指定されていない場合のみ実装を使用
    if notifier is None:
        line_message_parameter = get_ssm_json_parameter(name=settings.line_message_parameter_name, decrypt=True)
        notifier = LineNotifierAdapter(
            url=line_message_parameter["url"],
            token=line_message_parameter["token"],
        )

    # CloudWatch Logs イベントパース
    parsed_data = parser.parse(event)
    error_records = parsed_data.error_records
    log_group = parsed_data.log_group
    log_stream = parsed_data.log_stream

    # エラー通知サービス実行
    message_formatter = MessageFormatter()
    notification_service = ErrorNotificationService(object_repository, notifier, message_formatter)
    notification_service.send_error_notification(
        error_records,
        log_group,
        log_stream,
        settings.error_bucket_name,
    )

    logger.info("エラー通知処理が完了しました", error_count=len(error_records))
