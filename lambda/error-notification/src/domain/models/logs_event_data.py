"""CloudWatch Logs イベントデータのドメインモデル"""

from pydantic import BaseModel

from .error_log_record import ErrorLogRecord


class LogsEventData(BaseModel):
    """ログイベントから抽出したドメインデータ

    技術詳細に依存しない形でログイベント情報を保持する
    """

    error_records: list[ErrorLogRecord]  # エラーログレコードのリスト
    logs_url: str | None = None  # 生ログの閲覧URL（オプション）
