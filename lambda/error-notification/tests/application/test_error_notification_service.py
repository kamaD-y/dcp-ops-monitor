"""error_notification_service のテスト"""

import os

from src.application import ErrorNotificationService
from src.domain import ErrorLogEvents, ErrorRecord
from src.infrastructure import S3ObjectRepository
from tests.fixtures.mocks import MockNotifier


class TestErrorNotificationService:
    """ErrorNotificationService のテスト"""

    def test_send_error_notification__with_error_log_events(self):
        """ErrorLogEventsを渡して通知送信"""
        # given
        error_record = ErrorRecord(
            level="ERROR",
            location="handler:17",
            message="テストエラー",
            timestamp="2025-01-01 00:00:00,000+0000",  # type: ignore[invalid-argument-type] BaseModel により自動変換できる為
            service="test-service",
        )
        error_log_events = ErrorLogEvents(
            error_records=[error_record],
            logs_url="https://console.aws.amazon.com/cloudwatch/home",
        )

        mock_repo = S3ObjectRepository()  # 使用しないが必要
        mock_notifier = MockNotifier()
        service = ErrorNotificationService(mock_repo, mock_notifier)

        # when
        service.send_error_notification(error_log_events, "test-bucket")

        # then
        assert mock_notifier.notify_called is True
        assert len(mock_notifier.messages_sent) == 1
        message = mock_notifier.messages_sent[0]
        assert "テストエラー" in message.text
        assert "https://console.aws.amazon.com/cloudwatch/home" in message.text

    def test_send_error_notification__empty_records(self):
        """エラーレコードが空の場合は通知しない"""
        # given
        error_log_events = ErrorLogEvents(
            error_records=[],
        )

        mock_repo = S3ObjectRepository()
        mock_notifier = MockNotifier()
        service = ErrorNotificationService(mock_repo, mock_notifier)

        # when
        service.send_error_notification(error_log_events, "test-bucket")

        # then
        assert mock_notifier.notify_called is False

    def test_send_error_notification__with_screenshot(self, local_stack_container):
        """スクリーンショット付きエラーで画像URL付き通知送信"""
        # given
        bucket_name = os.environ["ERROR_BUCKET_NAME"]
        object_key = "errors/test.png"

        # LocalStack S3にオブジェクトを作成
        s3 = local_stack_container.get_client("s3")
        s3.put_object(Bucket=bucket_name, Key=object_key, Body=b"fake image")

        error_record = ErrorRecord(
            level="ERROR",
            location="handler:17",
            message="テストエラー",
            timestamp="2025-01-01 00:00:00,000+0000",  # type: ignore[invalid-argument-type] BaseModel により自動変換できる為
            service="test-service",
            error_screenshot_key=object_key,
        )
        error_log_events = ErrorLogEvents(
            error_records=[error_record],
        )

        repo = S3ObjectRepository()
        mock_notifier = MockNotifier()
        service = ErrorNotificationService(repo, mock_notifier)

        # when
        service.send_error_notification(error_log_events, bucket_name)

        # then
        assert mock_notifier.notify_called is True
        message = mock_notifier.messages_sent[0]
        assert message.image_url is not None
        assert object_key in message.image_url
