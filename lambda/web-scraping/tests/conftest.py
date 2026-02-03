import os

import pytest
from testcontainers.localstack import LocalStackContainer

bucket_name = "test-bucket"


@pytest.fixture
def valid_assets_page() -> str:
    """テスト用の正常なHTMLファイルを読み込む"""
    with open("tests/fixtures/html/valid_assets_page.html") as f:
        assets_page = f.read()
    return assets_page


@pytest.fixture
def invalid_assets_page() -> str:
    """テスト用の不正なHTMLファイルを読み込む"""
    with open("tests/fixtures/html/invalid_assets_page.html") as f:
        assets_page = f.read()
    return assets_page


@pytest.fixture(scope="package", autouse=True)
def local_stack_container() -> LocalStackContainer:  # type: ignore (invalid-return-type)
    """LocalStackのコンテナを起動する

    Returns:
        LocalStackContainer: LocalStackのコンテナ
    """
    with LocalStackContainer(region_name="ap-northeast-1") as container:
        os.environ["LOCAL_STACK_CONTAINER_URL"] = container.get_url()
        os.environ["AWS_ACCESS_KEY_ID"] = "dummy"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "dummy"
        yield container
        print("Cleaning up LocalStack container...")


@pytest.fixture(scope="package", autouse=True)
def create_test_bucket(local_stack_container: LocalStackContainer) -> None:
    os.environ["data_bucket_name"] = bucket_name
    client = local_stack_container.get_client("s3")  # type: ignore (missing-argument)
    client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": local_stack_container.region_name},
    )
