import json
import os

import pytest

from src.domain import AssetNotFound, DcpAssetInfo, DcpAssets
from tests.conftest import data_bucket_name
from tests.fixtures.mocks import MockAssetRepository, MockNotifier


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
            "商品B": DcpAssetInfo(
                cumulative_contributions=450_000,
                gains_or_losses=150_000,
                asset_valuation=600_000,
            ),
        },
    )


def test_main__e2e_with_mocks(sample_assets):
    """main 関数の E2E テスト（Mock を使用）

    資産取得→指標計算→通知送信の全フローが正常に完了することを確認する
    """
    # given
    from src.presentation.summary_notification_handler import main

    repo = MockAssetRepository(assets=sample_assets)
    notifier = MockNotifier()

    # when
    main(asset_repository=repo, notifier=notifier)

    # then
    assert repo.get_called
    assert notifier.notify_called
    assert len(notifier.messages_sent) == 1

    message = notifier.messages_sent[0]
    assert "確定拠出年金 運用状況通知Bot" in message.text
    assert "900,000円" in message.text
    assert "商品A" in message.text
    assert "商品B" in message.text
    assert "運用年数:" in message.text
    assert "想定受取額(60歳):" in message.text


def test_main__e2e_with_s3(local_stack_container, create_test_bucket, sample_assets):
    """main 関数の E2E テスト（S3 + Mock Notifier）

    S3 から実際に資産情報を取得し、通知が送信されることを確認する
    """
    # given
    from src.presentation.summary_notification_handler import main

    client = local_stack_container.get_client("s3")  # type: ignore (missing-argument)
    client.put_object(
        Bucket=data_bucket_name,
        Key="assets/2026/02/05.json",
        Body=sample_assets.model_dump_json().encode("utf-8"),
        ContentType="application/json",
    )

    notifier = MockNotifier()

    # when
    main(notifier=notifier)

    # then
    assert notifier.notify_called
    assert len(notifier.messages_sent) == 1
    assert "900,000円" in notifier.messages_sent[0].text

    # cleanup
    client.delete_object(Bucket=data_bucket_name, Key="assets/2026/02/05.json")


def test_main__asset_not_found_raises(local_stack_container, create_test_bucket):
    """S3 に資産情報がない場合 AssetNotFound が発生する"""
    # given
    from src.presentation.summary_notification_handler import main

    # assets/ を全削除
    client = local_stack_container.get_client("s3")  # type: ignore (missing-argument)
    response = client.list_objects_v2(Bucket=data_bucket_name, Prefix="assets/")
    for obj in response.get("Contents", []):
        client.delete_object(Bucket=data_bucket_name, Key=obj["Key"])

    notifier = MockNotifier()

    # when, then
    with pytest.raises(AssetNotFound):
        main(notifier=notifier)
