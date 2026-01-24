"""ErrorRecord のテスト"""

from datetime import datetime, timezone

from src.domain import ErrorRecord


class TestErrorRecordTimestamp:
    """ErrorRecord の timestamp プロパティのテスト"""

    def test_timestamp__utc_datetime(self):
        """UTCのdatetimeオブジェクトが正しく設定されること"""
        # given
        utc_time = datetime(2025, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
        record = ErrorRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp=utc_time,
            service="web-scraping",
        )

        # then
        assert record.timestamp == utc_time

    def test_timestamp__string(self):
        """文字列のタイムスタンプが正しくUTCのdatetimeオブジェクトに変換されること"""
        # given
        timestamp_str = "2025-01-01 00:00:00,000+0000"
        record = ErrorRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp=timestamp_str,  # type: ignore[invalid-argument-type] BaseModel により自動変換できる為
            service="web-scraping",
        )

        # then
        expected_utc_time = datetime(2025, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
        assert record.timestamp == expected_utc_time


class TestErrorRecordJstTimestamp:
    """ErrorRecord の jst_timestamp プロパティのテスト"""

    def test_jst_timestamp__year_boundary(self):
        """年境界（UTC年末→JST新年）が正しく変換されること"""
        # given
        record = ErrorRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp="2024-12-31 20:00:00,000+0000",  # type: ignore[invalid-argument-type] BaseModel により自動変換できる為
            service="web-scraping",
        )

        # then
        result = record.jst_timestamp
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 5


class TestErrorRecordHasScreenshot:
    """ErrorRecord の has_screenshot プロパティのテスト"""

    def test_has_screenshot__png_file(self):
        """.png拡張子の場合、Trueが返されること"""
        # given
        utc_time = datetime(2025, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
        record = ErrorRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp=utc_time,
            service="web-scraping",
            error_file_key="errors/2025/01/01/error.png",
        )

        # then
        assert record.has_screenshot is True

    def test_has_screenshot__html_file(self):
        """.html拡張子の場合、Falseが返されること"""
        # given
        utc_time = datetime(2025, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
        record = ErrorRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp=utc_time,
            service="web-scraping",
            error_file_key="errors/2025/01/01/page.html",
        )

        # then
        assert record.has_screenshot is False

    def test_has_screenshot__no_extension(self):
        """拡張子なしの場合、Falseが返されること"""
        # given
        utc_time = datetime(2025, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
        record = ErrorRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp=utc_time,
            service="web-scraping",
            error_file_key="errors/2025/01/01/error",
        )

        # then
        assert record.has_screenshot is False

    def test_has_screenshot__none_value(self):
        """error_file_keyがNoneの場合、Falseが返されること"""
        # given
        utc_time = datetime(2025, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
        record = ErrorRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp=utc_time,
            service="web-scraping",
            error_file_key=None,
        )

        # then
        assert record.has_screenshot is False


class TestErrorRecordHasHtml:
    """ErrorRecord の has_html プロパティのテスト"""

    def test_has_html__html_file(self):
        """.html拡張子の場合、Trueが返されること"""
        # given
        utc_time = datetime(2025, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
        record = ErrorRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp=utc_time,
            service="web-scraping",
            error_file_key="errors/2025/01/01/page.html",
        )

        # then
        assert record.has_html is True

    def test_has_html__png_file(self):
        """.png拡張子の場合、Falseが返されること"""
        # given
        utc_time = datetime(2025, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
        record = ErrorRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp=utc_time,
            service="web-scraping",
            error_file_key="errors/2025/01/01/error.png",
        )

        # then
        assert record.has_html is False

    def test_has_html__no_extension(self):
        """拡張子なしの場合、Falseが返されること"""
        # given
        utc_time = datetime(2025, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
        record = ErrorRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp=utc_time,
            service="web-scraping",
            error_file_key="errors/2025/01/01/file",
        )

        # then
        assert record.has_html is False

    def test_has_html__none_value(self):
        """error_file_keyがNoneの場合、Falseが返されること"""
        # given
        utc_time = datetime(2025, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
        record = ErrorRecord(
            level="ERROR",
            location="handler.handler:17",
            message="エラー",
            timestamp=utc_time,
            service="web-scraping",
            error_file_key=None,
        )

        # then
        assert record.has_html is False
