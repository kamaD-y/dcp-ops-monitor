"""オブジェクトリポジトリインターフェース"""

from abc import ABC, abstractmethod

from ..models import StorageLocation


class IObjectRepository(ABC):
    """オブジェクトストレージリポジトリインターフェース（S3非依存）"""

    @abstractmethod
    def download(self, location: StorageLocation) -> bytes:
        """オブジェクトをダウンロード

        Args:
            location: ストレージ上の位置

        Returns:
            bytes: ダウンロードされたオブジェクトのバイトデータ

        Raises:
            ObjectDownloadError: ダウンロード失敗時
        """
        pass

    @abstractmethod
    def generate_temporary_url(self, location: StorageLocation, expires_in: int = 3600) -> str:
        """一時アクセス URL を生成

        Args:
            location: ストレージ上の位置
            expires_in: URL の有効期限 (秒)、デフォルトは 3600秒 (1時間)

        Returns:
            str: 一時アクセス URL

        Raises:
            ObjectDownloadError: URL 生成失敗時
        """
        pass
