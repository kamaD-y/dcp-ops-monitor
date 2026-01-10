"""CloudWatch Logs イベントデータのドメインモデル"""

from pydantic import BaseModel

from .error_log_record import ErrorLogRecord


class LogsEventData(BaseModel):
    """CloudWatch Logs イベントから抽出したドメインデータ

    CloudWatchLogsEvent から AWS固有の詳細を排除し、
    ビジネスロジックに必要な情報のみを保持する
    """

    error_records: list[ErrorLogRecord]  # エラーログレコードのリスト
    log_group: str  # ロググループ名（後方互換性のため維持、後で削除予定）
    log_stream: str  # ログストリーム名（後方互換性のため維持、後で削除予定）
    logs_url: str | None = None  # 生ログの閲覧URL（オプション）
