"""CloudWatch Logs Event のモックデータ生成"""

import base64
import gzip
import json
from typing import Any


def create_cloudwatch_logs_event(
    log_group: str = "/aws/lambda/test-function",
    log_stream: str = "2025/01/01/[$LATEST]abcdef1234567890",
    log_messages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """CloudWatch Logs Event を生成

    AWS Lambda Powertools の CloudWatchLogsEvent にパース可能な形式

    Args:
        log_group: ロググループ名
        log_stream: ログストリーム名
        log_messages: ログメッセージリスト (各要素は Lambda Powertools JSON 形式)

    Returns:
        dict: CloudWatch Logs Event (base64 + gzip 圧縮済み)
    """
    if log_messages is None:
        log_messages = []

    # CloudWatch Logs の内部形式
    log_events = []
    for idx, msg in enumerate(log_messages):
        log_events.append({
            "id": str(idx),
            "timestamp": 1735689600000 + idx * 1000,  # 2025-01-01 00:00:00 UTC
            "message": json.dumps(msg, ensure_ascii=False),
        })

    logs_data = {
        "messageType": "DATA_MESSAGE",
        "owner": "123456789012",
        "logGroup": log_group,
        "logStream": log_stream,
        "subscriptionFilters": ["test-filter"],
        "logEvents": log_events,
    }

    # JSON → gzip → base64 (AWS Lambda が受け取る形式)
    json_str = json.dumps(logs_data, ensure_ascii=False)
    compressed = gzip.compress(json_str.encode("utf-8"))
    encoded = base64.b64encode(compressed).decode("utf-8")

    return {"awslogs": {"data": encoded}}


def create_error_log_message(
    level: str = "ERROR",
    location: str = "handler.handler:17",
    message: str = "テストエラーメッセージ",
    timestamp: str = "2025-01-01 00:00:00,123+0000",
    service: str = "web-scraping",
    error_file_key: str | None = None,
    exception_name: str | None = None,
    exception: str | None = None,
) -> dict[str, Any]:
    """Lambda Powertools JSON ログ形式のエラーメッセージを生成

    Returns:
        dict: ErrorLogRecord にパース可能な辞書
    """
    log = {
        "level": level,
        "location": location,
        "message": message,
        "timestamp": timestamp,
        "service": service,
    }

    if error_file_key is not None:
        log["error_file_key"] = error_file_key
    if exception_name is not None:
        log["exception_name"] = exception_name
    if exception is not None:
        log["exception"] = exception

    return log
