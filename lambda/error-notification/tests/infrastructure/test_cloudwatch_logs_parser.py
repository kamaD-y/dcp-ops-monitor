"""CloudWatchLogsParser のテスト"""

import base64
import gzip
import json

import pytest
from aws_lambda_powertools.utilities.data_classes import CloudWatchLogsEvent

from src.domain import CloudWatchLogsParseError, ErrorLogRecord
from src.infrastructure import CloudWatchLogsParser
from tests.fixtures import create_cloudwatch_logs_event, create_error_log_message


class TestCloudWatchLogsParserParse:
    """CloudWatchLogsParser の parse メソッドのテスト"""

    def test_parse__single_error_log(self):
        """1件のERRORログが正しくパースされること"""
        # given
        error_log = create_error_log_message(
            level="ERROR",
            location="handler.handler:17",
            message="スクレイピング失敗",
            timestamp="2025-01-01 00:00:00,123+0000",
            service="web-scraping",
            error_file_key="errors/2025/01/01/error.png",
            exception_name="TimeoutException",
            exception="Traceback (most recent call last)...",
        )
        event_dict = create_cloudwatch_logs_event(log_messages=[error_log])
        event = CloudWatchLogsEvent(event_dict)

        parser = CloudWatchLogsParser()

        # when
        result = parser.parse(event)

        # then
        assert len(result) == 1
        record = result[0]
        assert isinstance(record, ErrorLogRecord)
        assert record.level == "ERROR"
        assert record.location == "handler.handler:17"
        assert record.message == "スクレイピング失敗"
        assert record.timestamp == "2025-01-01 00:00:00,123+0000"
        assert record.service == "web-scraping"
        assert record.error_file_key == "errors/2025/01/01/error.png"
        assert record.exception_name == "TimeoutException"
        assert record.exception == "Traceback (most recent call last)..."

    def test_parse__multiple_error_logs(self):
        """複数のERRORログが正しくパースされること"""
        # given
        error_logs = [
            create_error_log_message(message="エラー1", timestamp="2025-01-01 00:00:00,000+0000"),
            create_error_log_message(message="エラー2", timestamp="2025-01-01 00:00:01,000+0000"),
            create_error_log_message(message="エラー3", timestamp="2025-01-01 00:00:02,000+0000"),
        ]
        event_dict = create_cloudwatch_logs_event(log_messages=error_logs)
        event = CloudWatchLogsEvent(event_dict)

        parser = CloudWatchLogsParser()

        # when
        result = parser.parse(event)

        # then
        assert len(result) == 3
        assert result[0].message == "エラー1"
        assert result[1].message == "エラー2"
        assert result[2].message == "エラー3"

    def test_parse__ignore_non_error_logs(self):
        """ERROR以外のログレベルは無視されること"""
        # given
        logs = [
            create_error_log_message(level="INFO", message="情報ログ"),
            create_error_log_message(level="WARNING", message="警告ログ"),
            create_error_log_message(level="ERROR", message="エラーログ"),
        ]
        event_dict = create_cloudwatch_logs_event(log_messages=logs)
        event = CloudWatchLogsEvent(event_dict)

        parser = CloudWatchLogsParser()

        # when
        result = parser.parse(event)

        # then
        assert len(result) == 1
        assert result[0].level == "ERROR"
        assert result[0].message == "エラーログ"

    def test_parse__empty_event(self):
        """ログが0件の場合、空のリストが返されること"""
        # given
        event_dict = create_cloudwatch_logs_event(log_messages=[])
        event = CloudWatchLogsEvent(event_dict)

        parser = CloudWatchLogsParser()

        # when
        result = parser.parse(event)

        # then
        assert result == []

    def test_parse__invalid_json(self):
        """不正なJSON文字列でCloudWatchLogsParseErrorがraiseされること"""
        # given
        # 手動で不正なJSONを含むイベントを作成
        logs_data = {
            "messageType": "DATA_MESSAGE",
            "owner": "123456789012",
            "logGroup": "/aws/lambda/test-function",
            "logStream": "2025/01/01/[$LATEST]abcdef",
            "subscriptionFilters": ["test-filter"],
            "logEvents": [
                {
                    "id": "0",
                    "timestamp": 1704067200000,
                    "message": "{invalid json",  # 不正なJSON
                }
            ],
        }
        json_str = json.dumps(logs_data)
        compressed = gzip.compress(json_str.encode("utf-8"))
        encoded = base64.b64encode(compressed).decode("utf-8")
        event_dict = {"awslogs": {"data": encoded}}
        event = CloudWatchLogsEvent(event_dict)

        parser = CloudWatchLogsParser()

        # when, then
        with pytest.raises(CloudWatchLogsParseError) as exc_info:
            parser.parse(event)

        assert "ログイベントのパースに失敗しました" in str(exc_info.value)

    def test_parse__invalid_pydantic_validation(self):
        """Pydanticバリデーションエラー時にCloudWatchLogsParseErrorがraiseされること"""
        # given
        # 必須フィールド (timestamp) が欠落
        invalid_log = {
            "level": "ERROR",
            "location": "handler.handler:17",
            "message": "エラー",
            # "timestamp": "2025-01-01 00:00:00,000+0000",  # 必須フィールドが欠落
            "service": "web-scraping",
        }
        event_dict = create_cloudwatch_logs_event(log_messages=[invalid_log])
        event = CloudWatchLogsEvent(event_dict)

        parser = CloudWatchLogsParser()

        # when, then
        with pytest.raises(CloudWatchLogsParseError) as exc_info:
            parser.parse(event)

        assert "ログイベントのパースに失敗しました" in str(exc_info.value)
