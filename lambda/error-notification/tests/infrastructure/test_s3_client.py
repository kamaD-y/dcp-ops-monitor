"""S3Client のテスト"""

import os

import pytest

from src.domain import S3ImageDownloadError
from src.infrastructure import S3Client


class TestS3ClientDownloadObject:
    """S3Client の download_object メソッドのテスト"""

    def test_download_object__success(self, s3_bucket):
        """S3からのオブジェクトダウンロードが成功すること"""
        # given
        bucket_name, s3_local = s3_bucket("test-download-bucket")
        object_key = "test-image.png"
        content = b"fake image data"

        # オブジェクトを作成
        s3_local.put_object(Bucket=bucket_name, Key=object_key, Body=content)

        client = S3Client()

        # when
        result = client.download_object(bucket_name, object_key)

        # then
        assert result == content

    def test_download_object__object_not_found(self, s3_bucket):
        """存在しないオブジェクトをダウンロードしようとするとS3ImageDownloadErrorが発生すること"""
        # given
        bucket_name, _ = s3_bucket("test-download-error-bucket")
        object_key = "non-existent.png"

        client = S3Client()

        # when, then
        with pytest.raises(S3ImageDownloadError) as exc_info:
            client.download_object(bucket_name, object_key)

        assert "S3 からのオブジェクトダウンロードに失敗しました" in str(exc_info.value)


class TestS3ClientGeneratePresignedUrl:
    """S3Client の generate_presigned_url メソッドのテスト"""

    def test_generate_presigned_url__success(self, s3_bucket):
        """署名付きURLが正しく生成されること"""
        # given
        bucket_name, s3_local = s3_bucket("test-presigned-url-bucket")
        object_key = "test-image.png"
        content = b"fake image data"

        # オブジェクトを作成
        s3_local.put_object(Bucket=bucket_name, Key=object_key, Body=content)

        client = S3Client()

        # when
        url = client.generate_presigned_url(bucket_name, object_key, expires_in=3600)

        # then
        assert url is not None
        assert isinstance(url, str)
        assert bucket_name in url
        assert object_key in url
        # LocalStack の場合、URL に endpoint が含まれる
        if os.environ.get("ENV") in ["local", "test"]:
            assert os.environ["LOCAL_STACK_CONTAINER_URL"] in url

    def test_generate_presigned_url__custom_expiration(self, s3_bucket):
        """カスタム有効期限で署名付きURLが生成されること"""
        # given
        bucket_name, s3_local = s3_bucket("test-presigned-url-expiration-bucket")
        object_key = "test-image.png"
        content = b"fake image data"
        expires_in = 7200  # 2時間

        # オブジェクトを作成
        s3_local.put_object(Bucket=bucket_name, Key=object_key, Body=content)

        client = S3Client()

        # when
        url = client.generate_presigned_url(bucket_name, object_key, expires_in)

        # then
        assert url is not None
        assert isinstance(url, str)
        # URL に有効期限が含まれる（Expiresパラメータ）
        assert "Expires=" in url or "X-Amz-Expires=" in url
