"""CloudWatch Logs イベントデータのドメインモデル"""

from pydantic import BaseModel

from ..error_log_record import ErrorLogRecord


class LogsEventData(BaseModel):
    """CloudWatch Logs イベントから抽出したドメインデータ

    CloudWatchLogsEvent から AWS固有の詳細を排除し、
    ビジネスロジックに必要な情報のみを保持する
    """

    error_records: list[ErrorLogRecord]  # エラーログレコードのリスト
    log_group: str  # ロググループ名
    log_stream: str  # ログストリーム名
