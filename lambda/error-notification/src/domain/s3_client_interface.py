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

    @abstractmethod
    def generate_presigned_url(self, bucket: str, key: str, expires_in: int = 3600) -> str:
        """S3 オブジェクトの署名付き URL を生成

        Args:
            bucket: バケット名
            key: オブジェクトキー
            expires_in: URL の有効期限 (秒)、デフォルトは 3600秒 (1時間)

        Returns:
            str: 署名付き URL

        Raises:
            S3ImageDownloadError: URL 生成失敗時
        """
        pass
