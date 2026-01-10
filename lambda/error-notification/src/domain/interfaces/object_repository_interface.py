"""オブジェクトリポジトリインターフェース"""

from abc import ABC, abstractmethod

from ..models import StorageLocation


class IObjectRepository(ABC):
    """オブジェクトストレージリポジトリインターフェース"""

    @abstractmethod
    def generate_temporary_url(self, location: StorageLocation, expires_in: int = 3600) -> str:
        """一時アクセス URL を生成

        Args:
            location: ストレージ上の位置
            expires_in: URL の有効期限 (秒)、デフォルトは 3600秒 (1時間)

        Returns:
            str: 一時アクセス URL

        Raises:
            TemporaryUrlGenerationError: URL 生成失敗時
        """
        pass
