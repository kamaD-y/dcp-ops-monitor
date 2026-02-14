import pytest

from src.application import SummaryNotificationService
from src.domain import AssetNotFound, DcpAssetInfo, DcpAssets
from tests.fixtures.mocks import MockAssetRepository, MockNotifier


@pytest.fixture
def sample_assets() -> DcpAssets:
    """テスト用資産情報"""
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


class TestSummaryNotificationService:
    def test_send_summary__success(self, sample_assets):
        """正常にサマリ通知を送信できる"""
        # given
        repo = MockAssetRepository(assets=sample_assets)
        notifier = MockNotifier()
        service = SummaryNotificationService(asset_repository=repo, notifier=notifier)

        # when
        service.send_summary()

        # then
        assert repo.get_called
        assert notifier.notify_called
        assert len(notifier.messages_sent) == 1
        assert "確定拠出年金 運用状況通知Bot" in notifier.messages_sent[0].text
        assert "900,000円" in notifier.messages_sent[0].text

    def test_send_summary__asset_not_found_raises(self):
        """資産情報がない場合 AssetNotFound が発生する"""
        # given
        repo = MockAssetRepository(should_fail=True)
        notifier = MockNotifier()
        service = SummaryNotificationService(asset_repository=repo, notifier=notifier)

        # when, then
        with pytest.raises(AssetNotFound):
            service.send_summary()

        assert not notifier.notify_called

    def test_send_summary__message_contains_indicators(self, sample_assets):
        """送信メッセージに運用指標が含まれる"""
        # given
        repo = MockAssetRepository(assets=sample_assets)
        notifier = MockNotifier()
        service = SummaryNotificationService(asset_repository=repo, notifier=notifier)

        # when
        service.send_summary()

        # then
        message_text = notifier.messages_sent[0].text
        assert "運用年数:" in message_text
        assert "運用利回り:" in message_text
        assert "目標利回り: 0.06" in message_text
        assert "想定受取額(60歳):" in message_text
