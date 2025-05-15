import boto3
from settings.settings import get_logger

from .get_client import get_client

logger = get_logger()


def upload_file(bucket: str, key: str, file_path: str, client: boto3.client = None) -> None:
    """S3バケットにファイルをアップロードする

    Args:
        bucket (str): S3バケット名
        key (str): S3オブジェクトのキー
        file_path (str): アップロードするファイルのパス
        client (boto3.client): S3クライアント

    Returns:
        None
    """
    if not client:
        client = get_client("s3")

    try:
        client.upload_file(file_path, bucket, key)
        logger.info(f"File {file_path} uploaded to bucket {bucket} with key {key}")
    except Exception:
        logger.exception(f"Failed to upload file {file_path} to bucket {bucket}")
        raise
