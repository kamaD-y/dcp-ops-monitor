"""パース済み CloudWatch Logs データモデル"""

from pydantic import BaseModel

from .error_log_record import ErrorLogRecord


class ParsedCloudWatchLogsData(BaseModel):
    """パース済み CloudWatch Logs データ

    CloudWatchLogsParser.parse() の戻り値として使用し、
    エラーレコードとメタデータをまとめて返す
    """

    error_records: list[ErrorLogRecord]
    log_group: str
    log_stream: str
