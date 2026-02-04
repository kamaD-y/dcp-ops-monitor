import json

import pytest

from src.domain import AssetNotFound, DcpAssetInfo, DcpAssets
from src.infrastructure import S3AssetRepository
from tests.conftest import data_bucket_name


@pytest.fixture
def sample_assets() -> DcpAssets:
    """テスト用の資産情報"""
    return DcpAssets(
        total=DcpAssetInfo(
            cumulative_contributions=900_000,
            gains_or_losses=300_000,
            asset_valuation=1_200_000,
        ),
        products={
            "商品A": DcpAssetInfo(
                cumulative_contributions=450_000,
                gains_or_losses=150_000,
                asset_valuation=600_000,
            ),
        },
    )


def _put_asset_json(local_stack_container, key: str, assets: DcpAssets) -> None:
    """S3 にテスト用 JSON を配置"""
    client = local_stack_container.get_client("s3")  # type: ignore (missing-argument)
    client.put_object(
        Bucket=data_bucket_name,
        Key=key,
        Body=assets.model_dump_json().encode("utf-8"),
        ContentType="application/json",
    )


def _cleanup_assets(local_stack_container) -> None:
    """S3 の assets/ プレフィックスを全削除"""
    client = local_stack_container.get_client("s3")  # type: ignore (missing-argument)
    response = client.list_objects_v2(Bucket=data_bucket_name, Prefix="assets/")
    for obj in response.get("Contents", []):
        client.delete_object(Bucket=data_bucket_name, Key=obj["Key"])


class TestS3AssetRepository:
    def test_get_latest_assets__returns_latest_file(self, local_stack_container, create_test_bucket, sample_assets):
        """最新の資産情報 JSON を正しく取得できる"""
        # given
        _put_asset_json(local_stack_container, "assets/2026/01/01.json", sample_assets)

        newer_assets = DcpAssets(
            total=DcpAssetInfo(
                cumulative_contributions=1_000_000,
                gains_or_losses=400_000,
                asset_valuation=1_400_000,
            ),
            products={},
        )
        _put_asset_json(local_stack_container, "assets/2026/02/01.json", newer_assets)

        repo = S3AssetRepository(bucket=data_bucket_name)

        # when
        result = repo.get_latest_assets()

        # then
        assert result.total.cumulative_contributions == 1_000_000
        assert result.total.asset_valuation == 1_400_000

        # cleanup
        _cleanup_assets(local_stack_container)

    def test_get_latest_assets__empty_bucket_raises_asset_not_found(self, local_stack_container, create_test_bucket):
        """S3 に資産情報がない場合 AssetNotFound が発生する"""
        # given
        _cleanup_assets(local_stack_container)
        repo = S3AssetRepository(bucket=data_bucket_name)

        # when, then
        with pytest.raises(AssetNotFound):
            repo.get_latest_assets()

    def test_get_latest_assets__json_deserialization(self, local_stack_container, create_test_bucket, sample_assets):
        """JSON から DcpAssets へのデシリアライズが正しく行われる"""
        # given
        _put_asset_json(local_stack_container, "assets/2026/01/15.json", sample_assets)
        repo = S3AssetRepository(bucket=data_bucket_name)

        # when
        result = repo.get_latest_assets()

        # then
        assert result.total.cumulative_contributions == 900_000
        assert result.total.gains_or_losses == 300_000
        assert result.total.asset_valuation == 1_200_000
        assert "商品A" in result.products
        assert result.products["商品A"].asset_valuation == 600_000

        # cleanup
        _cleanup_assets(local_stack_container)
