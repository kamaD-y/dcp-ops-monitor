"""message_formatter のテスト"""

from src.application.message_formatter import format_error_message
from src.domain import ErrorLogRecord, LogsEventData


class TestFormatErrorMessage:
    """format_error_message 関数のテスト"""

    def test_format_error_message__single_error_with_url(self):
        """1件のエラーを正しくフォーマット（URL付き）"""
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
            log_group="/aws/lambda/test-function",
            log_stream="2025/01/01/[$LATEST]test",
            logs_url="https://ap-northeast-1.console.aws.amazon.com/cloudwatch/home",
        )

        # Act
        result = format_error_message(logs_event_data)

        # Assert
        assert "🚨 エラー通知 (1件)" in result
        assert "テストエラー" in result
        assert "test-service" in result
        assert "📊 CloudWatch Logs:" in result
        assert logs_event_data.logs_url in result

    def test_format_error_message__no_url(self):
        """URLなしの場合はリンクを表示しない"""
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
            log_group="/aws/lambda/test-function",
            log_stream="2025/01/01/[$LATEST]test",
            logs_url=None,
        )

        # Act
        result = format_error_message(logs_event_data)

        # Assert
        assert "🚨 エラー通知 (1件)" in result
        assert "テストエラー" in result
        assert "📊 CloudWatch Logs:" not in result

    def test_format_error_message__empty_list(self):
        """エラーレコードが空の場合"""
        # Arrange
        logs_event_data = LogsEventData(
            error_records=[],
            log_group="/aws/lambda/test-function",
            log_stream="2025/01/01/[$LATEST]test",
        )

        # Act
        result = format_error_message(logs_event_data)

        # Assert
        assert "エラーログがありませんでした" in result

    def test_format_error_message__multiple_errors(self):
        """複数エラーの場合、全てフォーマットされる"""
        # Arrange
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
                location="handler:25",
                message="エラー2",
                timestamp="2025-01-01 00:00:01,000+0000",
                service="test-service",
                exception_name="ValueError",
            ),
        ]
        logs_event_data = LogsEventData(
            error_records=error_records,
            log_group="/aws/lambda/test-function",
            log_stream="2025/01/01/[$LATEST]test",
        )

        # Act
        result = format_error_message(logs_event_data)

        # Assert
        assert "🚨 エラー通知 (2件)" in result
        assert "エラー1" in result
        assert "エラー2" in result
        assert "ValueError" in result
