"""S3 資産リポジトリ実装"""

import json
import os

import boto3

from src.config.settings import get_logger
from src.domain import AssetNotFound, DcpAssets, IAssetRepository

logger = get_logger()


class S3AssetRepository(IAssetRepository):
    """S3 から資産情報を取得するリポジトリ"""

    def __init__(self, bucket: str) -> None:
        """S3 クライアントを初期化

        Args:
            bucket: S3 バケット名
        """
        if os.environ.get("ENV") in ["local", "test"]:
            self.client = boto3.client("s3", endpoint_url=os.environ["LOCAL_STACK_CONTAINER_URL"])
        else:
            self.client = boto3.client("s3")
        self.bucket = bucket

    def get_latest_assets(self) -> DcpAssets:
        """S3 から最新の資産情報を取得

        assets/ プレフィックス配下の最新の JSON ファイルを取得する。

        Returns:
            DcpAssets: 最新の資産情報

        Raises:
            AssetNotFound: 資産情報が見つからない場合
        """
        try:
            paginator = self.client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket, Prefix="assets/")
            contents = [obj for page in pages for obj in page.get("Contents", [])]
            if not contents:
                raise AssetNotFound.no_assets_in_bucket()

            # キー名でソートし最新を取得（assets/{YYYY}/{MM}/{DD}.json）
            latest = sorted(contents, key=lambda obj: obj["Key"], reverse=True)[0]
            latest_key = latest["Key"]

            logger.info("最新の資産情報を取得します", key=latest_key)

            obj = self.client.get_object(Bucket=self.bucket, Key=latest_key)
            json_content = json.loads(obj["Body"].read().decode("utf-8"))

            return DcpAssets.model_validate(json_content)

        except AssetNotFound:
            raise
        except Exception as e:
            raise AssetNotFound(f"資産情報の取得に失敗しました: {e}") from e
