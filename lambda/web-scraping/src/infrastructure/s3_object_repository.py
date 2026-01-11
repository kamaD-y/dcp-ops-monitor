"""S3 オブジェクトリポジトリ実装"""

import os

import boto3

from config.settings import get_logger
from domain import IS3Repository

logger = get_logger()


class S3ObjectRepository(IS3Repository):
    """S3 オブジェクトリポジトリ実装"""

    def __init__(self, bucket: str) -> None:
        """S3 クライアントを初期化

        環境変数 ENV が "local" または "test" の場合、LocalStack の endpoint を使用

        Args:
            bucket: S3 バケット名
        """
        if os.environ.get("ENV") in ["local", "test"]:
            self.client = boto3.client("s3", endpoint_url=os.environ["LOCAL_STACK_CONTAINER_URL"])
        else:
            self.client = boto3.client("s3")
        self.bucket = bucket

    def upload_file(self, key: str, file_path: str) -> None:
        """S3バケットにファイルをアップロードする

        Args:
            key: S3オブジェクトのキー
            file_path: アップロードするファイルのパス

        Raises:
            Exception: S3 へのファイルアップロード失敗時
        """
        try:
            self.client.upload_file(file_path, self.bucket, key)
            logger.info("S3 へのファイルアップロード成功", bucket=self.bucket, key=key)
        except Exception as e:
            logger.error("S3 へのファイルアップロードに失敗しました", bucket=self.bucket, key=key, error=str(e))
            raise Exception("S3 へのファイルアップロードに失敗しました。") from e

    def put_object(self, key: str, body: str) -> None:
        """S3バケットにオブジェクトをアップロードする

        Args:
            key: S3オブジェクトのキー
            body: アップロードするオブジェクトの内容

        Raises:
            Exception: S3 へのオブジェクトアップロード失敗時
        """
        try:
            body_bytes = body.encode("utf-8")
            self.client.put_object(Bucket=self.bucket, Key=key, Body=body_bytes)
            logger.info("S3 へのオブジェクトアップロード成功", bucket=self.bucket, key=key)
        except Exception as e:
            logger.error("S3 へのオブジェクトアップロードに失敗しました", bucket=self.bucket, key=key, error=str(e))
            raise Exception("S3 へのオブジェクトアップロードに失敗しました。") from e
