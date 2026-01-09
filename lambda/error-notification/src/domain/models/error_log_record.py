"""エラーログレコードモデル"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import BaseModel


class ErrorLogRecord(BaseModel):
    """エラーログレコード (Lambda Powertools JSON ログ形式)"""

    level: str  # ログレベル (ERROR)
    location: str  # エラー発生箇所 (例: handler.handler:17)
    message: str  # エラーメッセージ本文
    timestamp: str  # タイムスタンプ (UTC、例: "2025-12-31 16:30:00,123+0000")
    service: str  # サービス名 (web-scraping)
    error_file_key: Optional[str] = None  # エラーオブジェクトのキー
    exception_name: Optional[str] = None  # 例外クラス名
    exception: Optional[str] = None  # スタックトレース

    def get_jst_timestamp(self) -> datetime:
        """タイムスタンプを JST に変換

        Returns:
            datetime: JST に変換されたタイムスタンプ
        """
        # "2025-12-31 16:30:00,123+0000" → datetime (UTC)
        # カンマをドットに置換してパース
        timestamp_str = self.timestamp.replace(",", ".")
        dt_utc = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f%z")

        # JST に変換 (UTC+9)
        jst = timezone(timedelta(hours=9))
        return dt_utc.astimezone(jst)

    def has_screenshot(self) -> bool:
        """スクリーンショットが存在するか

        Returns:
            bool: スクリーンショットが存在する場合 True
        """
        return self.error_file_key is not None and self.error_file_key.endswith(".png")

    def has_html(self) -> bool:
        """HTML ファイルが存在するか

        Returns:
            bool: HTML ファイルが存在する場合 True
        """
        return self.error_file_key is not None and self.error_file_key.endswith(".html")
