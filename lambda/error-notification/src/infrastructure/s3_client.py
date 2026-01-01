"""S3 クライアント実装"""

import os

import boto3

from src.domain import IS3Client, S3ImageDownloadError


class S3Client(IS3Client):
    """S3 クライアント実装"""

    def __init__(self) -> None:
        """S3 クライアントを初期化

        環境変数 ENV が "local" または "test" の場合、LocalStack の endpoint を使用
        """
        if os.environ.get("ENV") in ["local", "test"]:
            self.client = boto3.client("s3", endpoint_url=os.environ["LOCAL_STACK_CONTAINER_URL"])
        else:
            self.client = boto3.client("s3")

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
        try:
            response = self.client.get_object(Bucket=bucket, Key=key)
            return response["Body"].read()
        except Exception as e:
            msg = f"S3 からのオブジェクトダウンロードに失敗しました (bucket={bucket}, key={key}): {e}"
            raise S3ImageDownloadError(msg) from e
