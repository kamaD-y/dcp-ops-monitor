"""LINE メッセージモデル"""

from typing import Literal

from pydantic import BaseModel


class LineTextMessage(BaseModel):
    """LINE テキストメッセージ"""

    type: Literal["text"] = "text"
    text: str


class LineImageMessage(BaseModel):
    """LINE 画像メッセージ"""

    type: Literal["image"] = "image"
    originalContentUrl: str  # noqa: N815 (LINE API の仕様)
    previewImageUrl: str  # noqa: N815 (LINE API の仕様)


# Union 型で複数メッセージ対応
LineMessage = LineTextMessage | LineImageMessage
