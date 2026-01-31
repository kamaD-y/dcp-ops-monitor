from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from pydantic import BaseModel, computed_field, field_validator


class ErrorRecord(BaseModel):
    level: Literal["ERROR"]  # ログレベル (ERROR)
    location: str  # エラー発生箇所 (例: handler.handler:17)
    message: str  # エラーメッセージ本文
    service: str  # サービス名 (web-scraping)
    timestamp: datetime  # タイムスタンプ (UTC、例: "2025-12-31 16:30:00,123+0000")

    error_screenshot_key: str | None = None  # スクリーンショットの S3 キー
    error_html_key: str | None = None  # HTML ファイルの S3 キー
    exception_name: str | None = None  # 例外クラス名
    exception: str | None = None  # スタックトレース

    @field_validator("timestamp", mode="before")
    @classmethod
    def _parse_timestamp(cls, v: Any) -> datetime:
        if isinstance(v, datetime):
            return v if v.tzinfo is not None else v.replace(tzinfo=timezone.utc)
        if isinstance(v, str):
            ts = v.replace(",", ".")
            return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S.%f%z")
        raise TypeError("timestamp must be datetime or str")

    @computed_field
    @property
    def jst_timestamp(self) -> datetime:
        """JST に変換されたタイムスタンプ"""
        return self.timestamp.astimezone(timezone(timedelta(hours=9)))


class ErrorLogEvents(BaseModel):
    error_records: list[ErrorRecord]
    logs_url: str | None = None  # 生ログの閲覧URL（オプション）
