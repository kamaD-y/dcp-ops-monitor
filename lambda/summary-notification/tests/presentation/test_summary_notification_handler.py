import pytest

from src.domain import AssetRetrievalFailed, DcpAssetInfo, DcpAssets
from tests.fixtures.mocks import MockAssetRepository, MockNotifier


@pytest.fixture
def sample_assets() -> DcpAssets:
    """テスト用の資産情報"""
    return DcpAssets(
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
    assert "運用年数:" in message.text
    assert "想定受取額(60歳):" in message.text


def test_main__asset_not_found_raises():
    """資産情報が見つからない場合 AssetRetrievalFailed が発生する"""
    # given
    from src.presentation.summary_notification_handler import main

    repo = MockAssetRepository(should_fail=True)
    notifier = MockNotifier()

    # when, then
    with pytest.raises(AssetRetrievalFailed):
        main(asset_repository=repo, notifier=notifier)
