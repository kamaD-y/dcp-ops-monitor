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
