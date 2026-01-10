"""エラー通知ハンドラー"""

from aws_lambda_powertools.utilities.data_classes import CloudWatchLogsEvent

from src.application import ErrorNotificationService
from src.config.settings import get_logger, get_settings
from src.domain import INotifier, IObjectRepository, LogsEventData
from src.infrastructure import (
    CloudWatchLogsAdapter,
    LineNotifier,
    S3ObjectRepository,
    get_ssm_json_parameter,
)

settings = get_settings()
logger = get_logger()


def main(
    event: CloudWatchLogsEvent,
    logs_event_data: LogsEventData | None = None,
    object_repository: IObjectRepository | None = None,
    notifier: INotifier | None = None,
) -> None:
    """メイン処理

    Args:
        event: CloudWatch Logs イベント (handler.py境界でのAWS型)
        logs_event_data: ログイベントデータ (テスト時に直接注入可能)
        object_repository: オブジェクトリポジトリ (テスト時に Mock 注入可能)
        notifier: 通知クライアント (テスト時に Mock 注入可能)
    """
    # logs_event_data が指定されていない場合、Adapter で変換
    if logs_event_data is None:
        adapter = CloudWatchLogsAdapter()
        logs_event_data = adapter.convert(event)

        # CloudWatch Logs URL を生成して設定
        try:
            logs_url = adapter.generate_logs_url(
                logs_event_data.log_group,
                logs_event_data.log_stream,
            )
            # Pydanticモデルなので再代入で新しいインスタンス作成
            logs_event_data = LogsEventData(
                error_records=logs_event_data.error_records,
                log_group=logs_event_data.log_group,
                log_stream=logs_event_data.log_stream,
                logs_url=logs_url,
            )
        except Exception as e:
            # URL生成失敗時はログを出して続行（URLなしで通知）
            logger.warning("CloudWatch Logs URL の生成に失敗しました", error=str(e))

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
        logs_event_data,
        settings.error_bucket_name,
    )

    logger.info("エラー通知処理が完了しました", error_count=len(logs_event_data.error_records))
