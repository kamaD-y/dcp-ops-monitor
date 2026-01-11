"""S3 オブジェクトリポジトリ実装"""

import os

import boto3

from src.domain import CouldNotGenerateTemporaryUrl, IObjectRepository, StorageLocation


class S3ObjectRepository(IObjectRepository):
    """S3 オブジェクトリポジトリ実装"""

    def __init__(self) -> None:
        """S3 クライアントを初期化

        環境変数 ENV が "local" または "test" の場合、LocalStack の endpoint を使用
        """
        if os.environ.get("ENV") in ["local", "test"]:
            self.client = boto3.client("s3", endpoint_url=os.environ["LOCAL_STACK_CONTAINER_URL"])
        else:
            self.client = boto3.client("s3")

    def generate_temporary_url(self, location: StorageLocation, expires_in: int = 3600) -> str:
        """一時アクセス URL を生成

        Args:
            location: ストレージ上の位置
            expires_in: URL の有効期限 (秒)、デフォルトは 3600秒 (1時間)

        Returns:
            str: 一時アクセス URL

        Raises:
            CouldNotGenerateTemporaryUrl: URL 生成失敗時
        """
        try:
            url = self.client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": location.container, "Key": location.path},
                ExpiresIn=expires_in,
            )
            return url
        except Exception as e:
            raise CouldNotGenerateTemporaryUrl.from_location(str(location)) from e
