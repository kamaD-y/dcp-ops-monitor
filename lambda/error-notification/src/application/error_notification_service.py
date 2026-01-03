"""エラー通知サービス"""

from src.config.settings import get_logger
from src.domain import (
    ErrorLogRecord,
    ILineNotifier,
    IS3Client,
    LineImageMessage,
    LineMessage,
    LineTextMessage,
    S3ImageDownloadError,
)

from .message_formatter import MessageFormatter

logger = get_logger()


class ErrorNotificationService:
    """エラー通知サービス"""

    def __init__(
        self,
        s3_client: IS3Client,
        line_notifier: ILineNotifier,
        message_formatter: MessageFormatter,
    ) -> None:
        """エラー通知サービスを初期化

        Args:
            s3_client: S3 クライアント
            line_notifier: LINE 通知クライアント
            message_formatter: メッセージフォーマッター
        """
        self.s3_client = s3_client
        self.line_notifier = line_notifier
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
        text_message = LineTextMessage(text=message_text)

        # メッセージリスト (テキスト + 画像)
        messages: list[LineMessage] = [text_message]

        # 最初のレコードにスクリーンショットがあれば画像メッセージ追加
        first_record = error_records[0]
        if first_record.has_screenshot():
            image_message = self._create_image_message(first_record, bucket_name)
            if image_message:
                messages.append(image_message)

        # LINE 送信
        self.line_notifier.send_messages(messages)
        logger.info("LINE 通知送信完了", message_count=len(messages))

    def _create_image_message(self, record: ErrorLogRecord, bucket_name: str) -> LineImageMessage | None:
        """画像メッセージを作成

        Args:
            record: エラーログレコード
            bucket_name: S3 バケット名

        Returns:
            LineImageMessage | None: 画像メッセージ (取得失敗時は None)
        """
        if not record.error_file_key:
            return None

        try:
            # S3 署名付き URL 生成 (有効期限: 1時間)
            image_url = self.s3_client.generate_presigned_url(bucket_name, record.error_file_key, expires_in=3600)

            return LineImageMessage(originalContentUrl=image_url, previewImageUrl=image_url)

        except S3ImageDownloadError as e:
            logger.warning("S3 署名付き URL の生成に失敗しました。テキストのみ送信します。", error=str(e))
            return None
