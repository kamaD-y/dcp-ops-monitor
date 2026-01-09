"""エラー通知サービス"""

from src.config.settings import get_logger
from src.domain import (
    ErrorLogRecord,
    INotifier,
    IObjectRepository,
    NotificationMessage,
    StorageLocation,
    TemporaryUrlGenerationError,
)

from .message_formatter import MessageFormatter

logger = get_logger()


class ErrorNotificationService:
    """エラー通知サービス"""

    def __init__(
        self,
        object_repository: IObjectRepository,
        notifier: INotifier,
        message_formatter: MessageFormatter,
    ) -> None:
        """エラー通知サービスを初期化

        Args:
            object_repository: オブジェクトリポジトリ
            notifier: 通知クライアント
            message_formatter: メッセージフォーマッター
        """
        self.object_repository = object_repository
        self.notifier = notifier
        self.message_formatter = message_formatter

    def send_error_notification(
        self,
        error_records: list[ErrorLogRecord],
        log_group: str,
        log_stream: str,
        bucket_name: str,
    ) -> None:
        """エラー通知を送信

        Args:
            error_records: エラーログレコードリスト
            log_group: CloudWatch Logs ロググループ名
            log_stream: CloudWatch Logs ログストリーム名
            bucket_name: S3 バケット名
        """
        if not error_records:
            logger.info("エラーレコードが0件のため、通知をスキップします")
            return

        # テキストメッセージ生成
        message_text = self.message_formatter.format_error_message(error_records, log_group, log_stream)

        # 画像URL取得 (最初のレコードにスクリーンショットがあれば)
        image_url = None
        first_record = error_records[0]
        if first_record.has_screenshot():
            image_url = self._get_image_url(first_record, bucket_name)

        # 通知メッセージ作成 (テキスト + 画像URL)
        notification_message = NotificationMessage(text=message_text, image_url=image_url)

        # 通知送信
        self.notifier.notify([notification_message])
        logger.info("通知送信完了")

    def _get_image_url(self, record: ErrorLogRecord, bucket_name: str) -> str | None:
        """画像URLを取得

        Args:
            record: エラーログレコード
            bucket_name: S3 バケット名

        Returns:
            str | None: 画像URL (取得失敗時は None)
        """
        if not record.error_file_key:
            return None

        try:
            # オブジェクトストレージの一時 URL 生成 (有効期限: 1時間)
            location = StorageLocation(container=bucket_name, path=record.error_file_key)
            image_url = self.object_repository.generate_temporary_url(location, expires_in=3600)
            return image_url

        except TemporaryUrlGenerationError as e:
            logger.warning("一時 URL の生成に失敗しました。テキストのみ送信します。", error=str(e))
            return None
