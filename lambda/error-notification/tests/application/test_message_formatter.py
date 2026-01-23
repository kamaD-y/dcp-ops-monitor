"""message_formatter のテスト"""

from datetime import datetime, timezone

from src.application.message_formatter import format_error_message
from src.domain import ErrorLogEvents, ErrorRecord


class TestFormatErrorMessage:
    """format_error_message 関数のテスト"""

    def test_format_error_message__single_error_with_url(self):
        """1件のエラーを正しくフォーマット（URL付き）"""
        # given
        error_record = ErrorRecord(
            level="ERROR",
            location="handler:17",
            message="テストエラー",
            timestamp="2025-01-01 00:00:00,000+0000", # type: ignore[invalid-argument-type] BaseModel により自動変換できる為
            service="test-service",
        )
        error_log_events = ErrorLogEvents(
            error_records=[error_record],
            logs_url="https://ap-northeast-1.console.aws.amazon.com/cloudwatch/home",
        )

        # when
        result = format_error_message(error_log_events)

        # then
        assert "🚨 エラー通知 (1件)" in result
        assert "テストエラー" in result
        assert "test-service" in result
        assert "📊 CloudWatch Logs:" in result
        assert error_log_events.logs_url in result  # type: ignore (unsupported operator)

    def test_format_error_message__no_url(self):
        """URLなしの場合はリンクを表示しない"""
        # given
        error_record = ErrorRecord(
            level="ERROR",
            location="handler:17",
            message="テストエラー",
            timestamp="2025-01-01 00:00:00,000+0000", # type: ignore[invalid-argument-type] BaseModel により自動変換できる為
            service="test-service",
        )
        error_log_events = ErrorLogEvents(
            error_records=[error_record],
            logs_url=None,
        )

        # when
        result = format_error_message(error_log_events)

        # then
        assert "🚨 エラー通知 (1件)" in result
        assert "テストエラー" in result
        assert "📊 CloudWatch Logs:" not in result

    def test_format_error_message__empty_list(self):
        """エラーレコードが空の場合"""
        # given
        error_log_events = ErrorLogEvents(
            error_records=[],
        )

        # when
        result = format_error_message(error_log_events)

        # then
        assert "エラーログがありませんでした" in result

    def test_format_error_message__multiple_errors(self):
        """複数エラーの場合、全てフォーマットされる"""
        # given
        error_records = [
            ErrorRecord(
                level="ERROR",
                location="handler:17",
                message="エラー1",
                timestamp="2025-01-01 00:00:00,000+0000", # type: ignore[invalid-argument-type] BaseModel により自動変換できる為
                service="test-service",
            ),
            ErrorRecord(
                level="ERROR",
                location="handler:25",
                message="エラー2",
                timestamp="2025-01-01 00:00:01,000+0000", # type: ignore[invalid-argument-type] BaseModel により自動変換できる為
                service="test-service",
                exception_name="ValueError",
            ),
        ]
        error_log_events = ErrorLogEvents(
            error_records=error_records,
        )

        # when
        result = format_error_message(error_log_events)

        # then
        assert "🚨 エラー通知 (2件)" in result
        assert "エラー1" in result
        assert "エラー2" in result
        assert "ValueError" in result
