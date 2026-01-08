"""S3ObjectRepository のテスト"""

import pytest

from src.domain import ObjectDownloadError, StorageLocation
from src.infrastructure import S3ObjectRepository


class TestS3ObjectRepositoryDownload:
    """S3ObjectRepository の download メソッドのテスト"""

    def test_download__success(self, s3_bucket):
        """オブジェクトが正常にダウンロードされること"""
        # given
        bucket_name, s3_client = s3_bucket("test-s3-object-repository-download")
        test_key = "test/sample.txt"
        test_content = b"test content"
        s3_client.put_object(Bucket=bucket_name, Key=test_key, Body=test_content)

        repository = S3ObjectRepository()
        location = StorageLocation(container=bucket_name, path=test_key)

        # when
        result = repository.download(location)

        # then
        assert result == test_content

    def test_download__object_not_found(self, s3_bucket):
        """存在しないオブジェクトで ObjectDownloadError が発生すること"""
        # given
        bucket_name, _ = s3_bucket("test-s3-object-repository-not-found")
        repository = S3ObjectRepository()
        location = StorageLocation(container=bucket_name, path="not/exists.txt")

        # when, then
        with pytest.raises(ObjectDownloadError) as exc_info:
            repository.download(location)

        assert "オブジェクトのダウンロードに失敗しました" in str(exc_info.value)

    def test_download__bucket_not_found(self):
        """存在しないバケットで ObjectDownloadError が発生すること"""
        # given
        repository = S3ObjectRepository()
        location = StorageLocation(container="not-exists-bucket", path="test.txt")

        # when, then
        with pytest.raises(ObjectDownloadError) as exc_info:
            repository.download(location)

        assert "オブジェクトのダウンロードに失敗しました" in str(exc_info.value)


class TestS3ObjectRepositoryGenerateTemporaryUrl:
    """S3ObjectRepository の generate_temporary_url メソッドのテスト"""

    def test_generate_temporary_url__success(self, s3_bucket):
        """署名付きURLが正常に生成されること"""
        # given
        bucket_name, s3_client = s3_bucket("test-s3-object-repository-url-success")
        test_key = "test/image.png"
        s3_client.put_object(Bucket=bucket_name, Key=test_key, Body=b"dummy image")

        repository = S3ObjectRepository()
        location = StorageLocation(container=bucket_name, path=test_key)

        # when
        url = repository.generate_temporary_url(location, expires_in=3600)

        # then
        assert url is not None
        assert bucket_name in url
        assert test_key in url
        # 署名付きURLの検証 (LocalStackはv2署名、実AWSはv4署名を使用)
        assert "Signature=" in url or "X-Amz-Signature" in url

    def test_generate_temporary_url__custom_expires_in(self, s3_bucket):
        """カスタム有効期限で URL が生成されること"""
        # given
        bucket_name, s3_client = s3_bucket("test-s3-object-repository-url-custom")
        test_key = "test/file.txt"
        s3_client.put_object(Bucket=bucket_name, Key=test_key, Body=b"test")

        repository = S3ObjectRepository()
        location = StorageLocation(container=bucket_name, path=test_key)

        # when
        url = repository.generate_temporary_url(location, expires_in=7200)

        # then
        assert url is not None
        assert "Signature=" in url or "X-Amz-Signature" in url

    def test_generate_temporary_url__object_not_exists(self, s3_bucket):
        """存在しないオブジェクトでも URL は生成されること (S3の仕様)"""
        # given
        # S3の署名付きURLは、オブジェクトの存在チェックをしないため、
        # 存在しないオブジェクトでもURLは生成される
        bucket_name, _ = s3_bucket("test-s3-object-repository-url-not-exists")
        repository = S3ObjectRepository()
        location = StorageLocation(container=bucket_name, path="not/exists.png")

        # when
        url = repository.generate_temporary_url(location, expires_in=3600)

        # then
        # URL自体は生成される (実際にアクセスすると404が返る)
        assert url is not None
        assert bucket_name in url
