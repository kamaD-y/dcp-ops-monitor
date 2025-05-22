import os
import pytest

bucket_name = "test-bucket"


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


def test_put_object() -> None:
    """S3バケットにオブジェクトをアップロードするテスト"""
    from src.infrastructure.aws import s3

    # given
    test_object_key = "test-object-key"
    test_object_body = "This is a test object."

    try:
        # when
        s3.put_object(bucket_name, test_object_key, test_object_body)

        # then
        assert True
    except Exception as e:
        pytest.fail(f"Failed to put object: {e}")
