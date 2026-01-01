"""error_notification_handler のテスト"""

from unittest.mock import Mock

import pytest
from aws_lambda_powertools.utilities.data_classes import CloudWatchLogsEvent

from src.domain import CloudWatchLogsParseError, ILineNotifier, LineNotificationError
from src.presentation import main
from tests.fixtures import create_cloudwatch_logs_event, create_error_log_message
from tests.fixtures.mocks import MockLineNotifier


class TestErrorNotificationHandlerMain:
    """main 関数のテスト"""

    def test_main__single_error_without_screenshot(self):
        """1件のエラー（スクリーンショット無し）でテキストメッセージのみ送信"""
        # given
        error_log = create_error_log_message(
            message="スクレイピングタイムアウト",
            error_file_key=None,
        )
        event_dict = create_cloudwatch_logs_event(log_messages=[error_log])
        event = CloudWatchLogsEvent(event_dict)
        mock_line_notifier = MockLineNotifier()

        # when
        main(event, line_notifier=mock_line_notifier)

        # then
        assert mock_line_notifier.send_messages_called is True
        assert len(mock_line_notifier.messages_sent) == 1
        assert mock_line_notifier.messages_sent[0].type == "text"
        assert "スクレイピングタイムアウト" in mock_line_notifier.messages_sent[0].text

    def test_main__multiple_errors(self):
        """複数のエラーログが正しくフォーマットされること"""
        # given
        error_logs = [
            create_error_log_message(message="エラー1"),
            create_error_log_message(message="エラー2"),
            create_error_log_message(message="エラー3"),
        ]
        event_dict = create_cloudwatch_logs_event(log_messages=error_logs)
        event = CloudWatchLogsEvent(event_dict)
        mock_line_notifier = MockLineNotifier()

        # when
        main(event, line_notifier=mock_line_notifier)

        # then
        assert mock_line_notifier.send_messages_called is True
        message_text = mock_line_notifier.messages_sent[0].text
        assert "エラー1" in message_text
        assert "エラー2" in message_text
        assert "エラー3" in message_text
        assert "🚨 エラー通知 (3件)" in message_text

    def test_main__no_error_logs(self):
        """エラーレコード0件で早期リターン"""
        # given
        event_dict = create_cloudwatch_logs_event(log_messages=[])
        event = CloudWatchLogsEvent(event_dict)
        mock_line_notifier = MockLineNotifier()

        # when
        main(event, line_notifier=mock_line_notifier)

        # then
        assert mock_line_notifier.send_messages_called is False

    def test_main__s3_download_error(self):
        """S3ダウンロード失敗時、テキストのみ送信"""
        # given
        error_log = create_error_log_message(
            error_file_key="errors/2025/01/01/not_exist.png"  # S3に存在しない
        )
        event_dict = create_cloudwatch_logs_event(log_messages=[error_log])
        event = CloudWatchLogsEvent(event_dict)
        mock_line_notifier = MockLineNotifier()

        # when
        main(event, line_notifier=mock_line_notifier)

        # then
        assert mock_line_notifier.send_messages_called is True
        # テキストメッセージのみ
        assert len(mock_line_notifier.messages_sent) == 1
        assert mock_line_notifier.messages_sent[0].type == "text"

    def test_main__upload_image_not_implemented(self, local_stack_container):
        """画像アップロード未実装（Stage 7）のため、スクリーンショット有りでもテキストのみ送信"""
        # given
        error_log = create_error_log_message(
            error_file_key="errors/2025/01/01/screenshot.png"
        )
        event_dict = create_cloudwatch_logs_event(log_messages=[error_log])
        event = CloudWatchLogsEvent(event_dict)

        # S3にダミー画像配置
        s3 = local_stack_container.get_client("s3")
        s3.put_object(
            Bucket="test-error-bucket",
            Key="errors/2025/01/01/screenshot.png",
            Body=b"dummy_image_data",
        )

        # upload_image_and_get_url()でNotImplementedError発生
        mock_line_notifier = MockLineNotifier(upload_should_fail=True)

        # when
        main(event, line_notifier=mock_line_notifier)

        # then
        assert mock_line_notifier.send_messages_called is True
        # S3ダウンロードは成功するが、upload_image_and_get_url()が未実装のためテキストのみ送信
        assert len(mock_line_notifier.messages_sent) == 1
        assert mock_line_notifier.messages_sent[0].type == "text"

    def test_main__cloudwatch_logs_parse_error(self):
        """CloudWatch Logsパースエラーが伝播すること"""
        # given
        # 不正なbase64データ
        invalid_event = CloudWatchLogsEvent({"awslogs": {"data": "invalid_base64"}})
        mock_line_notifier = MockLineNotifier()

        # when, then
        with pytest.raises(CloudWatchLogsParseError):
            main(invalid_event, line_notifier=mock_line_notifier)

    def test_main__line_notification_error(self):
        """LINE通知エラーが伝播すること"""
        # given
        error_log = create_error_log_message()
        event_dict = create_cloudwatch_logs_event(log_messages=[error_log])
        event = CloudWatchLogsEvent(event_dict)

        # LINE送信時にエラーを発生させるMock
        mock_line_notifier = Mock(spec=ILineNotifier)
        mock_line_notifier.send_messages.side_effect = LineNotificationError("Mock LINE error")

        # when, then
        with pytest.raises(LineNotificationError):
            main(event, line_notifier=mock_line_notifier)
