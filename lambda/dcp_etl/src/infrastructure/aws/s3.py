import os

import boto3
from settings.settings import get_logger

logger = get_logger()

if os.environ.get("ENV") == "test":
    client = boto3.client("s3", endpoint_url=os.environ["LOCAL_STACK_CONTAINER_URL"])
else:
    client = boto3.client("s3")


def upload_file(bucket: str, key: str, file_path: str) -> None:
    """S3バケットにファイルをアップロードする

    Args:
        bucket (str): S3バケット名
        key (str): S3オブジェクトのキー
        file_path (str): アップロードするファイルのパス

    Returns:
        None
    """
    try:
        client.upload_file(file_path, bucket, key)
        logger.info(f"File {file_path} uploaded to bucket {bucket} with key {key}")
    except Exception:
        logger.exception(f"Failed to upload file {file_path} to bucket {bucket}")
        raise


def put_object(bucket: str, key: str, body: str) -> None:
    """S3バケットにオブジェクトをアップロードする

    Args:
        bucket (str): S3バケット名
        key (str): S3オブジェクトのキー
        body (str): アップロードするオブジェクトの内容

    Returns:
        None
    """
    try:
        client.put_object(Bucket=bucket, Key=key, Body=body)
        logger.info(f"Object with key {key} uploaded to bucket {bucket}")
    except Exception:
        logger.exception(f"Failed to upload object with key {key} to bucket {bucket}")
        raise
