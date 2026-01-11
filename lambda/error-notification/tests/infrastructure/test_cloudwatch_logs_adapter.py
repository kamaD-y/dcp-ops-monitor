"""CloudWatchLogsAdapter のテスト"""

import gzip
import json
from base64 import b64encode

import pytest
from aws_lambda_powertools.utilities.data_classes import CloudWatchLogsEvent

from src.domain import ErrorLogRecord, LogsEventData, LogsParseFailed
from src.infrastructure.cloudwatch_logs_adapter import CloudWatchLogsAdapter


def create_cloudwatch_logs_event(log_events: list[dict], log_group: str, log_stream: str) -> CloudWatchLogsEvent:
    """テスト用の CloudWatchLogsEvent を作成

    Args:
        log_events: ログイベントのリスト
        log_group: ロググループ名
        log_stream: ログストリーム名

    Returns:
        CloudWatchLogsEvent
    """
    # CloudWatch Logs のペイロード構造
    payload = {
        "messageType": "DATA_MESSAGE",
        "owner": "123456789012",
        "logGroup": log_group,
        "logStream": log_stream,
        "subscriptionFilters": ["test-filter"],
        "logEvents": [
            {"id": str(i), "timestamp": 1000 * i, "message": json.dumps(msg)} for i, msg in enumerate(log_events)
        ],
    }

    # gzip 圧縮してBase64エンコード
    compressed = gzip.compress(json.dumps(payload).encode("utf-8"))
    encoded = b64encode(compressed).decode("utf-8")

    # CloudWatch Logs イベント形式
    event = {"awslogs": {"data": encoded}}

    return CloudWatchLogsEvent(event)


class TestCloudWatchLogsAdapter:
    """CloudWatchLogsAdapter のテストケース"""

    def test_convert__success(self):
        """正常系: ERROR レベルのログのみ抽出される"""
        # Arrange
        log_events = [
            {
                "level": "ERROR",
                "location": "handler:17",
                "message": "エラー1",
                "timestamp": "2025-01-01 00:00:00,000+0000",
                "service": "test-service",
                "error_file_key": "error1.png",
            },
            {
                "level": "INFO",
                "location": "handler:20",
                "message": "情報ログ",
                "timestamp": "2025-01-01 00:00:01,000+0000",
                "service": "test-service",
            },
            {
                "level": "ERROR",
                "location": "handler:25",
                "message": "エラー2",
                "timestamp": "2025-01-01 00:00:02,000+0000",
                "service": "test-service",
                "error_file_key": "error2.png",
            },
        ]
        event = create_cloudwatch_logs_event(
            log_events=log_events,
            log_group="/aws/lambda/test-function",
            log_stream="2025/01/01/[$LATEST]test",
        )
        adapter = CloudWatchLogsAdapter()

        # Act
        result = adapter.convert(event)

        # Assert
        assert isinstance(result, LogsEventData)
        assert len(result.error_records) == 2
        assert result.error_records[0].message == "エラー1"
        assert result.error_records[1].message == "エラー2"
        assert result.logs_url is not None
        assert "ap-northeast-1" in result.logs_url
        assert "console.aws.amazon.com/cloudwatch/home" in result.logs_url

    def test_convert__no_error_logs(self):
        """正常系: ERROR レベルのログがない場合"""
        # Arrange
        log_events = [
            {"level": "INFO", "message": "情報ログ"},
            {"level": "DEBUG", "message": "デバッグログ"},
        ]
        event = create_cloudwatch_logs_event(
            log_events=log_events,
            log_group="/aws/lambda/test-function",
            log_stream="2025/01/01/[$LATEST]test",
        )
        adapter = CloudWatchLogsAdapter()

        # Act
        result = adapter.convert(event)

        # Assert
        assert isinstance(result, LogsEventData)
        assert len(result.error_records) == 0
        assert result.logs_url is not None

    def test_convert__invalid_json_in_message(self):
        """正常系: JSON パース失敗時は該当ログをスキップ"""
        # Arrange
        log_events = [
            {
                "level": "ERROR",
                "location": "handler:17",
                "message": "エラー1",
                "timestamp": "2025-01-01 00:00:00,000+0000",
                "service": "test-service",
                "error_file_key": "error1.png",
            },
            "not a valid json",  # 不正なJSON
            {
                "level": "ERROR",
                "location": "handler:25",
                "message": "エラー2",
                "timestamp": "2025-01-01 00:00:02,000+0000",
                "service": "test-service",
                "error_file_key": "error2.png",
            },
        ]
        event_dict = {
            "messageType": "DATA_MESSAGE",
            "owner": "123456789012",
            "logGroup": "/aws/lambda/test-function",
            "logStream": "2025/01/01/[$LATEST]test",
            "subscriptionFilters": ["test-filter"],
            "logEvents": [
                {"id": "0", "timestamp": 0, "message": json.dumps(log_events[0])},
                {"id": "1", "timestamp": 1000, "message": log_events[1]},  # 不正なJSON
                {"id": "2", "timestamp": 2000, "message": json.dumps(log_events[2])},
            ],
        }

        compressed = gzip.compress(json.dumps(event_dict).encode("utf-8"))
        encoded = b64encode(compressed).decode("utf-8")
        invalid_event = CloudWatchLogsEvent({"awslogs": {"data": encoded}})

        adapter = CloudWatchLogsAdapter()

        # Act
        # Act & Assert
        with pytest.raises(LogsParseFailed) as exc_info:
            adapter.convert(invalid_event)

        assert "ログイベントのパースに失敗しました" in str(exc_info.value)

    def test_convert__invalid_event_structure(self):
        """異常系: CloudWatch Logs イベントの構造が不正"""
        # Arrange
        invalid_event = CloudWatchLogsEvent({"invalid": "structure"})
        adapter = CloudWatchLogsAdapter()

        # Act & Assert
        with pytest.raises(LogsParseFailed) as exc_info:
            adapter.convert(invalid_event)

        assert "ログイベントのパースに失敗しました" in str(exc_info.value)

    def test_generate_logs_url__success(self):
        """正常系: CloudWatch Logs URL を正しく生成"""
        # Arrange
        adapter = CloudWatchLogsAdapter()
        log_group = "/aws/lambda/test-function"
        log_stream = "2025/01/01/[$LATEST]test"

        # Act
        url = adapter.generate_logs_url(log_group, log_stream)

        # Assert
        assert "ap-northeast-1" in url
        assert "console.aws.amazon.com/cloudwatch/home" in url
        assert "%2Faws%2Flambda%2Ftest-function" in url  # URL エンコードされたlog_group
        assert "2025%2F01%2F01%2F%5B%24LATEST%5Dtest" in url  # URL エンコードされたlog_stream
