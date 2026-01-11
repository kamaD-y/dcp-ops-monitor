"""message_formatter のテスト"""

from src.application.message_formatter import format_error_message
from src.domain import ErrorLogRecord, LogsEventData


class TestFormatErrorMessage:
    """format_error_message 関数のテスト"""

    def test_format_error_message__single_error_with_url(self):
        """1件のエラーを正しくフォーマット（URL付き）"""
        # given
        error_record = ErrorLogRecord(
            level="ERROR",
            location="handler:17",
            message="テストエラー",
            timestamp="2025-01-01 00:00:00,000+0000",
            service="test-service",
        )
        logs_event_data = LogsEventData(
            error_records=[error_record],
            logs_url="https://ap-northeast-1.console.aws.amazon.com/cloudwatch/home",
        )

        # when
        result = format_error_message(logs_event_data)

        # then
        assert "🚨 エラー通知 (1件)" in result
        assert "テストエラー" in result
        assert "test-service" in result
        assert "📊 CloudWatch Logs:" in result
        assert logs_event_data.logs_url in result # type: ignore (unsupported operator)

    def test_format_error_message__no_url(self):
        """URLなしの場合はリンクを表示しない"""
        # given
        error_record = ErrorLogRecord(
            level="ERROR",
            location="handler:17",
            message="テストエラー",
            timestamp="2025-01-01 00:00:00,000+0000",
            service="test-service",
        )
        logs_event_data = LogsEventData(
            error_records=[error_record],
            logs_url=None,
        )

        # when
        result = format_error_message(logs_event_data)

        # then
        assert "🚨 エラー通知 (1件)" in result
        assert "テストエラー" in result
        assert "📊 CloudWatch Logs:" not in result

    def test_format_error_message__empty_list(self):
        """エラーレコードが空の場合"""
        # given
        logs_event_data = LogsEventData(
            error_records=[],
        )

        # when
        result = format_error_message(logs_event_data)

        # then
        assert "エラーログがありませんでした" in result

    def test_format_error_message__multiple_errors(self):
        """複数エラーの場合、全てフォーマットされる"""
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
                location="handler:25",
                message="エラー2",
                timestamp="2025-01-01 00:00:01,000+0000",
                service="test-service",
                exception_name="ValueError",
            ),
        ]
        logs_event_data = LogsEventData(
            error_records=error_records,
        )

        # when
        result = format_error_message(logs_event_data)

        # then
        assert "🚨 エラー通知 (2件)" in result
        assert "エラー1" in result
        assert "エラー2" in result
        assert "ValueError" in result
