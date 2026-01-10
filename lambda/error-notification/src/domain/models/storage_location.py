"""ストレージ上のオブジェクト位置モデル"""

from pydantic import BaseModel, field_validator


class StorageLocation(BaseModel):
    """ストレージ上のオブジェクト位置（S3非依存）

    S3固有の bucket/key ではなく、汎用的な container/path を使用
    """

    container: str  # バケット/コンテナ名
    path: str  # オブジェクトキー/パス

    @field_validator("container", "path")
    @classmethod
    def not_empty(cls, v: str) -> str:
        """空文字列チェック"""
        if not v or not v.strip():
            msg = "container と path は空文字列にできません"
            raise ValueError(msg)
        return v

    def __str__(self) -> str:
        """可読性の高い文字列表現"""
        return f"{self.container}/{self.path}"
