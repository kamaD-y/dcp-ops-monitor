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
        try:
            url = self.client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires_in,
            )
            return url
        except Exception as e:
            msg = f"S3 署名付き URL の生成に失敗しました (bucket={bucket}, key={key}): {e}"
            raise S3ImageDownloadError(msg) from e
