import os
import pytest
import boto3
from src.infrastructure.aws import s3
from testcontainers.localstack import LocalStackContainer


bucket_name = "test-bucket"
endpoint_url = ""


@pytest.fixture(scope="module", autouse=True)
def setup() -> LocalStackContainer:
    """LocalStackのコンテナを起動し、S3クライアントを取得する。
    バケットを一つ作成し、テスト終了後にクリーンアップする。

    Returns:
        LocalStackContainer: LocalStackのコンテナ
    """
    global endpoint_url

    with LocalStackContainer() as container:
        endpoint_url = container.get_url()
        client = container.get_client("s3")
        client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": container.region_name})
        yield container
        print("Cleaning up LocalStack container...")


@pytest.fixture(scope="module")
def s3_client() -> boto3.client:
    """S3クライアントを取得する。

    Returns:
        boto3.client: S3クライアント
    """
    return s3.get_client("s3", endpoint_url=endpoint_url)


def test_upload_file(s3_client: boto3.client) -> None:
    """S3バケットにファイルをアップロードするテスト"""
    # given
    test_file_path = "test-file.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file.")

    try:
        # when
        s3.upload_file(bucket_name, "test-file-key", test_file_path, s3_client)
        # then
        assert True
    except Exception as e:
        pytest.fail(f"Failed to upload file: {e}")
    finally:
        os.remove(test_file_path)
