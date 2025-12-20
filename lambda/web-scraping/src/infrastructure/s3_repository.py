import os

import boto3

from config.settings import get_logger
from domain import IS3Repository

logger = get_logger()


class S3Repository(IS3Repository):
    def __init__(self) -> None:
        self.client = (
            boto3.client("s3")
            if os.environ.get("ENV") != "test"
            else boto3.client("s3", endpoint_url=os.environ["LOCAL_STACK_CONTAINER_URL"])
        )

    def upload_file(self, bucket: str, key: str, file_path: str) -> None:
        try:
            self.client.upload_file(file_path, bucket, key)
        except Exception:
            logger.exception(f"Failed to upload file {file_path} to bucket {bucket}")
            raise

    def put_object(self, bucket: str, key: str, body: str) -> None:
        try:
            body_bytes = body.encode("utf-8")
            self.client.put_object(Bucket=bucket, Key=key, Body=body_bytes)
        except Exception:
            logger.exception(f"Failed to upload object with key {key} to bucket {bucket}")
            raise
