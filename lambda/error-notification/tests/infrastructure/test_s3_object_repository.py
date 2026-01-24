"""S3ObjectRepository のテスト"""

from urllib.parse import parse_qs, unquote, urlparse

import pytest

from src.domain import StorageLocation
from src.infrastructure import S3ObjectRepository


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
        url = repository.generate_temporary_url(location, expires_in=7200)

        # then
        assert url is not None
        parsed_url = urlparse(url)
        assert bucket_name in parsed_url.path
        assert test_key in unquote(parsed_url.path)
        # 署名付きURLの検証 (LocalStackはv2署名、実AWSはv4署名を使用)
        q = parse_qs(parsed_url.query)
        assert ("Signature" in q) or ("X-Amz-Signature" in q)

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
        parsed_url = urlparse(url)
        assert bucket_name in parsed_url.path
        assert "not/exists.png" in unquote(parsed_url.path)
