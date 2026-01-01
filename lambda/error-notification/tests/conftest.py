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
