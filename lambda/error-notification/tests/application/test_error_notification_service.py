"""error_notification_service のテスト"""

import os

from src.application import ErrorNotificationService
from src.domain import ErrorLogRecord, LogsEventData
from src.infrastructure import S3ObjectRepository
from tests.fixtures.mocks import MockNotifier


class TestErrorNotificationService:
    """ErrorNotificationService のテスト"""

    def test_send_error_notification__with_logs_event_data(self):
        """LogsEventDataを渡して通知送信"""
        # Arrange
        error_record = ErrorLogRecord(
            level="ERROR",
            location="handler:17",
            message="テストエラー",
            timestamp="2025-01-01 00:00:00,000+0000",
            service="test-service",
        )
        logs_event_data = LogsEventData(
            error_records=[error_record],
            logs_url="https://console.aws.amazon.com/cloudwatch/home",
        )

        mock_repo = S3ObjectRepository()  # 使用しないが必要
        mock_notifier = MockNotifier()
        service = ErrorNotificationService(mock_repo, mock_notifier)

        # Act
        service.send_error_notification(logs_event_data, "test-bucket")

        # Assert
        assert mock_notifier.notify_called is True
        assert len(mock_notifier.messages_sent) == 1
        message = mock_notifier.messages_sent[0]
        assert "テストエラー" in message.text
        assert "https://console.aws.amazon.com/cloudwatch/home" in message.text

    def test_send_error_notification__empty_records(self):
        """エラーレコードが空の場合は通知しない"""
        # Arrange
        logs_event_data = LogsEventData(
            error_records=[],
        )

        mock_repo = S3ObjectRepository()
        mock_notifier = MockNotifier()
        service = ErrorNotificationService(mock_repo, mock_notifier)

        # Act
        service.send_error_notification(logs_event_data, "test-bucket")

        # Assert
        assert mock_notifier.notify_called is False

    def test_send_error_notification__with_screenshot(self, local_stack_container):
        """スクリーンショット付きエラーで画像URL付き通知送信"""
        # Arrange
        bucket_name = os.environ["ERROR_BUCKET_NAME"]
        object_key = "errors/test.png"

        # LocalStack S3にオブジェクトを作成
        s3 = local_stack_container.get_client("s3")
        s3.put_object(Bucket=bucket_name, Key=object_key, Body=b"fake image")

        error_record = ErrorLogRecord(
            level="ERROR",
            location="handler:17",
            message="テストエラー",
            timestamp="2025-01-01 00:00:00,000+0000",
            service="test-service",
            error_file_key=object_key,
        )
        logs_event_data = LogsEventData(
            error_records=[error_record],
        )

        repo = S3ObjectRepository()
        mock_notifier = MockNotifier()
        service = ErrorNotificationService(repo, mock_notifier)

        # Act
        service.send_error_notification(logs_event_data, bucket_name)

        # Assert
        assert mock_notifier.notify_called is True
        message = mock_notifier.messages_sent[0]
        assert message.image_url is not None
        assert object_key in message.image_url
