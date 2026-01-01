"""S3 クライアントインターフェース"""

from abc import ABC, abstractmethod


class IS3Client(ABC):
    """S3 クライアントインターフェース"""

    @abstractmethod
    def download_object(self, bucket: str, key: str) -> bytes:
        """S3 からオブジェクトをダウンロード

        Args:
            bucket: バケット名
            key: オブジェクトキー

        Returns:
            bytes: ダウンロードされたオブジェクトのバイトデータ

        Raises:
            S3ImageDownloadError: ダウンロード失敗時
        """
        pass
