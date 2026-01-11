"""エラー通知サービス"""

from src.config.settings import get_logger
from src.domain import (
    CouldNotGenerateTemporaryUrl,
    ErrorLogRecord,
    INotifier,
    IObjectRepository,
    LogsEventData,
    NotificationMessage,
    StorageLocation,
)

from .message_formatter import format_error_message

logger = get_logger()


class ErrorNotificationService:
    """エラー通知サービス"""

    def __init__(
        self,
        object_repository: IObjectRepository,
        notifier: INotifier,
    ) -> None:
        """エラー通知サービスを初期化

        Args:
            object_repository: オブジェクトリポジトリ
            notifier: 通知クライアント
        """
        self.object_repository = object_repository
        self.notifier = notifier

    def send_error_notification(
        self,
        logs_event_data: LogsEventData,
        bucket_name: str,
    ) -> None:
        """エラー通知を送信

        Args:
            logs_event_data: ログイベントデータ
            bucket_name: S3 バケット名
        """
        error_records = logs_event_data.error_records

        if not error_records:
            logger.info("エラーレコードが0件のため、通知をスキップします")
            return

        # テキストメッセージ生成
        message_text = format_error_message(logs_event_data)

        # NOTE: エラーが複数件同時に発生する想定をしておらず、最初のレコードのスクリーンショットのみを確認している
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

        except CouldNotGenerateTemporaryUrl as e:
            logger.warning("一時 URL の生成に失敗しました。テキストのみ送信します。", error=str(e))
            return None
