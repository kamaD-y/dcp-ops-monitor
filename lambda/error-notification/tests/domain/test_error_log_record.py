"""ErrorLogRecord のテスト"""

from datetime import timedelta, timezone

from src.domain import ErrorLogRecord


class TestErrorLogRecordGetJstTimestamp:
    """ErrorLogRecord の get_jst_timestamp メソッドのテスト"""

    def test_get_jst_timestamp__valid_utc(self):
        """有効なUTCタイムスタンプがJSTに正しく変換されること"""
        # given
        record = ErrorLogRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp="2025-01-01 00:00:00,123+0000",
            service="web-scraping",
        )

        # when
        result = record.get_jst_timestamp()

        # then
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 9  # UTC 0時 → JST 9時
        assert result.minute == 0
        assert result.second == 0
        assert result.microsecond == 123000
        assert result.tzinfo == timezone(timedelta(hours=9))

    def test_get_jst_timestamp__year_boundary(self):
        """年境界（UTC年末→JST新年）が正しく変換されること"""
        # given
        record = ErrorLogRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp="2024-12-31 20:00:00,000+0000",
            service="web-scraping",
        )

        # when
        result = record.get_jst_timestamp()

        # then
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 5


class TestErrorLogRecordHasScreenshot:
    """ErrorLogRecord の has_screenshot メソッドのテスト"""

    def test_has_screenshot__png_file(self):
        """.png拡張子の場合、Trueが返されること"""
        # given
        record = ErrorLogRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp="2025-01-01 00:00:00,000+0000",
            service="web-scraping",
            error_file_key="errors/2025/01/01/error.png",
        )

        # when
        result = record.has_screenshot()

        # then
        assert result is True

    def test_has_screenshot__html_file(self):
        """.html拡張子の場合、Falseが返されること"""
        # given
        record = ErrorLogRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp="2025-01-01 00:00:00,000+0000",
            service="web-scraping",
            error_file_key="errors/2025/01/01/page.html",
        )

        # when
        result = record.has_screenshot()

        # then
        assert result is False

    def test_has_screenshot__no_extension(self):
        """拡張子なしの場合、Falseが返されること"""
        # given
        record = ErrorLogRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp="2025-01-01 00:00:00,000+0000",
            service="web-scraping",
            error_file_key="errors/2025/01/01/error",
        )

        # when
        result = record.has_screenshot()

        # then
        assert result is False

    def test_has_screenshot__none_value(self):
        """error_file_keyがNoneの場合、Falseが返されること"""
        # given
        record = ErrorLogRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp="2025-01-01 00:00:00,000+0000",
            service="web-scraping",
            error_file_key=None,
        )

        # when
        result = record.has_screenshot()

        # then
        assert result is False


class TestErrorLogRecordHasHtml:
    """ErrorLogRecord の has_html メソッドのテスト"""

    def test_has_html__html_file(self):
        """.html拡張子の場合、Trueが返されること"""
        # given
        record = ErrorLogRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp="2025-01-01 00:00:00,000+0000",
            service="web-scraping",
            error_file_key="errors/2025/01/01/page.html",
        )

        # when
        result = record.has_html()

        # then
        assert result is True

    def test_has_html__png_file(self):
        """.png拡張子の場合、Falseが返されること"""
        # given
        record = ErrorLogRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp="2025-01-01 00:00:00,000+0000",
            service="web-scraping",
            error_file_key="errors/2025/01/01/error.png",
        )

        # when
        result = record.has_html()

        # then
        assert result is False

    def test_has_html__no_extension(self):
        """拡張子なしの場合、Falseが返されること"""
        # given
        record = ErrorLogRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp="2025-01-01 00:00:00,000+0000",
            service="web-scraping",
            error_file_key="errors/2025/01/01/file",
        )

        # when
        result = record.has_html()

        # then
        assert result is False

    def test_has_html__none_value(self):
        """error_file_keyがNoneの場合、Falseが返されること"""
        # given
        record = ErrorLogRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp="2025-01-01 00:00:00,000+0000",
            service="web-scraping",
            error_file_key=None,
        )

        # when
        result = record.has_html()

        # then
        assert result is False
