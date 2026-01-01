"""エラー通知ハンドラー"""

from aws_lambda_powertools.utilities.data_classes import CloudWatchLogsEvent

from src.application import ErrorNotificationService, MessageFormatter
from src.config.settings import get_logger, get_settings
from src.domain import ICloudWatchLogsParser, ILineNotifier, IS3Client
from src.infrastructure import CloudWatchLogsParser, LineNotifier, S3Client, get_ssm_json_parameter

settings = get_settings()
logger = get_logger()


def main(
    event: CloudWatchLogsEvent,
    parser: ICloudWatchLogsParser | None = None,
    s3_client: IS3Client | None = None,
    line_notifier: ILineNotifier | None = None,
) -> None:
    """メイン処理

    Args:
        event: CloudWatch Logs イベント
        parser: CloudWatch Logs パーサー (テスト時に Mock 注入可能)
        s3_client: S3 クライアント (テスト時に Mock 注入可能)
        line_notifier: LINE 通知クライアント (テスト時に Mock 注入可能)
    """
    # parser が指定されていない場合のみ実装を使用
    if parser is None:
        parser = CloudWatchLogsParser()

    # S3 クライアントが指定されていない場合のみ実装を使用
    if s3_client is None:
        s3_client = S3Client()

    # LINE 通知が指定されていない場合のみ実装を使用
    if line_notifier is None:
        line_message_parameter = get_ssm_json_parameter(name=settings.line_message_parameter_name, decrypt=True)
        line_notifier = LineNotifier(
            url=line_message_parameter["url"],
            token=line_message_parameter["token"],
        )

    # CloudWatch Logs イベントパース
    error_records = parser.parse(event)

    # log_group と log_stream を取得
    decoded_data = event.parse_logs_data()
    log_group = decoded_data.log_group
    log_stream = decoded_data.log_stream

    # エラー通知サービス実行
    message_formatter = MessageFormatter()
    notification_service = ErrorNotificationService(s3_client, line_notifier, message_formatter)
    notification_service.send_error_notification(
        error_records,
        log_group,
        log_stream,
        settings.error_bucket_name,
    )

    logger.info("エラー通知処理が完了しました", error_count=len(error_records))
