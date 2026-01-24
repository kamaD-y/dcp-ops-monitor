from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel


class ErrorRecord(BaseModel):
    level: Literal["ERROR"]  # ログレベル (ERROR)
    location: str  # エラー発生箇所 (例: handler.handler:17)
    message: str  # エラーメッセージ本文
    service: str  # サービス名 (web-scraping)
    timestamp: datetime  # タイムスタンプ (UTC、例: "2025-12-31 16:30:00,123+0000")

    jst_timestamp: Optional[datetime] = None  # JST に変換されたタイムスタンプ
    has_screenshot: bool = False  # スクリーンショットの有無
    has_html: bool = False  # HTML ファイルの有無
    error_file_key: Optional[str] = None  # エラーオブジェクトのキー
    exception_name: Optional[str] = None  # 例外クラス名
    exception: Optional[str] = None  # スタックトレース

    def model_post_init(self, context: Any) -> None:
        """初期化後の追加フィールド設定"""
        self.jst_timestamp = self.timestamp.astimezone(timezone(timedelta(hours=9)))
        self.has_screenshot = self.error_file_key is not None and self.error_file_key.endswith(".png")
        self.has_html = self.error_file_key is not None and self.error_file_key.endswith(".html")


class ErrorLogEvents(BaseModel):
    error_records: list[ErrorRecord]
    logs_url: str | None = None  # 生ログの閲覧URL（オプション）
