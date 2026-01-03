"""テスト用共通 fixture"""

import os

import pytest
from testcontainers.localstack import LocalStackContainer

error_bucket_name = "test-error-bucket"


@pytest.fixture(scope="package", autouse=True)
def local_stack_container() -> LocalStackContainer:  # type: ignore (invalid-return-type)
    """LocalStack のコンテナを起動する

    Returns:
        LocalStackContainer: LocalStack のコンテナ
    """
    with LocalStackContainer(region_name="ap-northeast-1") as container:
        os.environ["LOCAL_STACK_CONTAINER_URL"] = container.get_url()
        os.environ["AWS_ACCESS_KEY_ID"] = "dummy"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "dummy"
        os.environ["ENV"] = "test"
        yield container
        print("Cleaning up LocalStack container...")


@pytest.fixture(scope="package", autouse=True)
def create_test_bucket(local_stack_container: LocalStackContainer) -> None:
    """S3 テストバケットを作成"""
    os.environ["ERROR_BUCKET_NAME"] = error_bucket_name
    client = local_stack_container.get_client("s3")  # type: ignore (missing-argument)
    client.create_bucket(
        Bucket=error_bucket_name,
        CreateBucketConfiguration={"LocationConstraint": local_stack_container.region_name},
    )


@pytest.fixture
def s3_bucket(local_stack_container: LocalStackContainer):
    """テスト用S3バケットを作成し、テスト終了後に削除するファクトリ

    Returns:
        function: バケット名を引数に取り、(bucket_name, s3_client) を返す関数
    """
    created_buckets = []

    def _create_bucket(bucket_name: str):
        """指定されたバケット名でS3バケットを作成

        Args:
            bucket_name: 作成するバケット名

        Returns:
            tuple[str, object]: (bucket_name, s3_client)
        """
        client = local_stack_container.get_client("s3")  # type: ignore (missing-argument)

        # バケット作成
        client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": local_stack_container.region_name},
        )
        created_buckets.append(bucket_name)

        return bucket_name, client

    yield _create_bucket

    # テスト終了後、作成したすべてのバケットをクリーンアップ
    client = local_stack_container.get_client("s3")  # type: ignore (missing-argument)
    for bucket_name in created_buckets:
        try:
            # バケット内のすべてのオブジェクトを取得して削除
            response = client.list_objects_v2(Bucket=bucket_name)
            if "Contents" in response:
                for obj in response["Contents"]:
                    client.delete_object(Bucket=bucket_name, Key=obj["Key"])

            # バケットを削除
            client.delete_bucket(Bucket=bucket_name)
        except Exception:
            # クリーンアップ失敗は無視（LocalStackが終了すれば自動削除される）
            pass
