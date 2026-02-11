"""S3 アーティファクトリポジトリ実装"""

import os

import boto3

from src.config.settings import get_logger
from src.domain import ArtifactUploadError, IArtifactRepository

logger = get_logger()


class S3ArtifactRepository(IArtifactRepository):
    """S3 アーティファクトリポジトリ実装"""

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

    def save_error_artifact(self, key: str, file_path: str) -> None:
        """エラーアーティファクトを S3 に保存する

        Args:
            key: S3オブジェクトのキー
            file_path: 保存するファイルのパス

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
