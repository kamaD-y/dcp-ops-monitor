import os

import boto3

from config.settings import get_logger
from domain import IS3Repository

logger = get_logger()


class S3Repository(IS3Repository):
    def __init__(self, bucket: str) -> None:
        self.client = (
            boto3.client("s3")
            if os.environ.get("ENV") not in ["local", "test"]
            else boto3.client("s3", endpoint_url=os.environ["LOCAL_STACK_CONTAINER_URL"])
        )
        self.bucket = bucket

    def upload_file(self, key: str, file_path: str) -> None:
        try:
            self.client.upload_file(file_path, self.bucket, key)
        except Exception as e:
            raise Exception("S3 へのファイルアップロードに失敗しました。") from e

    def put_object(self, key: str, body: str) -> None:
        try:
            body_bytes = body.encode("utf-8")
            self.client.put_object(Bucket=self.bucket, Key=key, Body=body_bytes)
        except Exception as e:
            raise Exception("S3 へのオブジェクトアップロードに失敗しました。") from e
