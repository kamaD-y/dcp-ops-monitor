"""S3 オブジェクトリポジトリ実装"""

import os

import boto3

from src.config.settings import get_logger
from src.domain import ArtifactUploadError, AssetStorageError, IObjectRepository

logger = get_logger()


class S3ObjectRepository(IObjectRepository):
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
            ArtifactUploadError: S3 へのファイルアップロード失敗時
        """
        try:
            self.client.upload_file(file_path, self.bucket, key)
            logger.info("S3 へのファイルアップロード成功", bucket=self.bucket, key=key)
        except Exception as e:
            raise ArtifactUploadError(
                f"S3 へのファイルアップロードに失敗しました。bucket={self.bucket}, key={key}"
            ) from e

    def put_json(self, key: str, json_str: str) -> None:
        """JSON 文字列を S3 に保存する

        Args:
            key: S3オブジェクトのキー
            json_str: JSON 文字列

        Raises:
            AssetStorageError: S3 への JSON 保存失敗時
        """
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json_str.encode("utf-8"),
                ContentType="application/json",
            )
            logger.info("JSON の S3 保存成功", bucket=self.bucket, key=key)
        except Exception as e:
            raise AssetStorageError(f"JSON の S3 保存に失敗しました。bucket={self.bucket}, key={key}") from e
