"""通知メッセージモデル"""

from pydantic import BaseModel


class NotificationMessage(BaseModel):
    """通知メッセージ（LINE非依存）

    LINE固有の構造ではなく、汎用的なメッセージモデル
    """

    text: str  # メッセージテキスト
    image_url: str | None = None  # 画像URL（オプション）
