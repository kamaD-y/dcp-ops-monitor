"""error_notification_handler のテスト"""

from unittest.mock import Mock

import pytest
from aws_lambda_powertools.utilities.data_classes import CloudWatchLogsEvent

from src.domain import ErrorLogRecord, INotifier, LogsEventData, LogsParseError, NotificationFailed
from src.presentation import main
from tests.fixtures.mocks import MockNotifier


class TestErrorNotificationHandlerMain:
    """main 関数のテスト"""

    def test_main__single_error_without_screenshot(self):
        """1件のエラー（スクリーンショット無し）でテキストメッセージのみ送信"""
        # given
        error_record = ErrorLogRecord(
            level="ERROR",
            location="handler:17",
            message="スクレイピングタイムアウト",
            timestamp="2025-01-01 00:00:00,000+0000",
            service="test-service",
            error_file_key=None,
        )
        logs_event_data = LogsEventData(
            error_records=[error_record],
        )
        event = CloudWatchLogsEvent({"awslogs": {"data": "dummy"}})
        mock_notifier = MockNotifier()

        # when
        main(event, logs_event_data=logs_event_data, notifier=mock_notifier)

        # then
        assert mock_notifier.notify_called is True
        assert len(mock_notifier.messages_sent) == 1
        message = mock_notifier.messages_sent[0]
        assert "スクレイピングタイムアウト" in message.text
        assert message.image_url is None

    def test_main__multiple_errors(self):
        """複数のエラーログが正しくフォーマットされること"""
        # given
        error_records = [
            ErrorLogRecord(
                level="ERROR",
                location="handler:17",
                message="エラー1",
                timestamp="2025-01-01 00:00:00,000+0000",
                service="test-service",
            ),
            ErrorLogRecord(
                level="ERROR",
                location="handler:20",
                message="エラー2",
                timestamp="2025-01-01 00:00:01,000+0000",
                service="test-service",
            ),
            ErrorLogRecord(
                level="ERROR",
                location="handler:25",
                message="エラー3",
                timestamp="2025-01-01 00:00:02,000+0000",
                service="test-service",
            ),
        ]
        logs_event_data = LogsEventData(
            error_records=error_records,
        )
        event = CloudWatchLogsEvent({"awslogs": {"data": "dummy"}})
        mock_notifier = MockNotifier()

        # when
        main(event, logs_event_data=logs_event_data, notifier=mock_notifier)

        # then
        assert mock_notifier.notify_called is True
        message = mock_notifier.messages_sent[0]
        assert "エラー1" in message.text
        assert "エラー2" in message.text
        assert "エラー3" in message.text
        assert "🚨 エラー通知 (3件)" in message.text

    def test_main__no_error_logs(self):
        """エラーレコード0件で早期リターン"""
        # given
        logs_event_data = LogsEventData(
            error_records=[],
        )
        event = CloudWatchLogsEvent({"awslogs": {"data": "dummy"}})
        mock_notifier = MockNotifier()

        # when
        main(event, logs_event_data=logs_event_data, notifier=mock_notifier)

        # then
        assert mock_notifier.notify_called is False

    def test_main__with_screenshot_url_generation(self):
        """スクリーンショット有り（実ファイル無し）でも署名付きURL生成により画像URL付きメッセージ送信"""
        # given
        # NOTE: generate_presigned_url はオブジェクトの存在チェックをしないため、
        #       実際にS3にファイルが無くてもURL生成は成功する
        error_record = ErrorLogRecord(
            level="ERROR",
            location="handler:17",
            message="エラー",
            timestamp="2025-01-01 00:00:00,000+0000",
            service="test-service",
            error_file_key="errors/2025/01/01/screenshot.png",
        )
        logs_event_data = LogsEventData(
            error_records=[error_record],
        )
        event = CloudWatchLogsEvent({"awslogs": {"data": "dummy"}})
        mock_notifier = MockNotifier()

        # when
        main(event, logs_event_data=logs_event_data, notifier=mock_notifier)

        # then
        assert mock_notifier.notify_called is True
        # テキスト + 画像URLを含む1つのメッセージ
        assert len(mock_notifier.messages_sent) == 1
        message = mock_notifier.messages_sent[0]
        assert message.image_url is not None
        assert "screenshot.png" in message.image_url

    def test_main__with_screenshot(self, local_stack_container):
        """スクリーンショット有りでテキスト + 画像URLを送信"""
        # given
        import os

        # ERROR_BUCKET_NAME 環境変数で指定されたバケットを使用
        bucket_name = os.environ["ERROR_BUCKET_NAME"]
        object_key = "errors/2025/01/01/screenshot.png"
        content = b"fake screenshot data"

        # S3にスクリーンショットを作成
        s3_local = local_stack_container.get_client("s3")  # type: ignore
        s3_local.put_object(Bucket=bucket_name, Key=object_key, Body=content)

        error_record = ErrorLogRecord(
            level="ERROR",
            location="handler:17",
            message="エラー",
            timestamp="2025-01-01 00:00:00,000+0000",
            service="test-service",
            error_file_key=object_key,
        )
        logs_event_data = LogsEventData(
            error_records=[error_record],
        )
        event = CloudWatchLogsEvent({"awslogs": {"data": "dummy"}})
        mock_notifier = MockNotifier()

        # when
        main(event, logs_event_data=logs_event_data, notifier=mock_notifier)

        # then
        assert mock_notifier.notify_called is True
        # テキスト + 画像URLを含む1つのメッセージ
        assert len(mock_notifier.messages_sent) == 1
        message = mock_notifier.messages_sent[0]
        assert message.image_url is not None
        assert bucket_name in message.image_url
        assert object_key in message.image_url

    def test_main__cloudwatch_logs_parse_error(self):
        """CloudWatch Logsパースエラーが伝播すること"""
        # given
        # 不正なbase64データ
        invalid_event = CloudWatchLogsEvent({"awslogs": {"data": "invalid_base64"}})
        mock_notifier = MockNotifier()

        # when, then
        # logs_event_data が None の場合、Adapter が呼ばれて LogsParseError が発生
        with pytest.raises(LogsParseError):
            main(invalid_event, notifier=mock_notifier)

    def test_main__notification_error(self):
        """通知送信エラーが伝播すること"""
        # given
        error_record = ErrorLogRecord(
            level="ERROR",
            location="handler:17",
            message="エラー",
            timestamp="2025-01-01 00:00:00,000+0000",
            service="test-service",
        )
        logs_event_data = LogsEventData(
            error_records=[error_record],
        )
        event = CloudWatchLogsEvent({"awslogs": {"data": "dummy"}})

        # 通知送信時にエラーを発生させるMock
        mock_notifier = Mock(spec=INotifier)
        mock_notifier.notify.side_effect = NotificationFailed("Mock notification error")

        # when, then
        with pytest.raises(NotificationFailed):
            main(event, logs_event_data=logs_event_data, notifier=mock_notifier)
