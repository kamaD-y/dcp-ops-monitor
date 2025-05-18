import os
import pytest
from testcontainers.localstack import LocalStackContainer


bucket_name = "test-bucket"

@pytest.fixture(scope="module", autouse=True)
def setup(local_stack_container: LocalStackContainer) -> None:
    client = local_stack_container.get_client("s3")
    client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": local_stack_container.region_name})


def test_upload_file() -> None:
    """S3バケットにファイルをアップロードするテスト"""
    from src.infrastructure.aws import s3

    # given
    test_file_path = "test-file.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file.")

    try:
        # when
        s3.upload_file(bucket_name, "test-file-key", test_file_path)

        # then
        assert True
    except Exception as e:
        pytest.fail(f"Failed to upload file: {e}")
    finally:
        os.remove(test_file_path)
