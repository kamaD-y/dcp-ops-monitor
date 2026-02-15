from datetime import date

import pytest

from src.application import SummaryNotificationService
from src.domain import AssetRetrievalFailed, DcpAssetInfo, DcpAssets
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


def _make_weekly_assets() -> dict[date, DcpAssets]:
    """テスト用の週次資産データを生成"""
    return {
        date(2026, 2, 12): DcpAssets(
            products={
                "商品A": DcpAssetInfo(
                    cumulative_contributions=450_000,
                    gains_or_losses=147_000,
                    asset_valuation=597_000,
                ),
            },
        ),
        date(2026, 2, 13): DcpAssets(
            products={
                "商品A": DcpAssetInfo(
                    cumulative_contributions=450_000,
                    gains_or_losses=145_000,
                    asset_valuation=595_000,
                ),
            },
        ),
        date(2026, 2, 14): DcpAssets(
            products={
                "商品A": DcpAssetInfo(
                    cumulative_contributions=450_000,
                    gains_or_losses=150_000,
                    asset_valuation=600_000,
                ),
            },
        ),
    }


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
        """資産情報がない場合 AssetRetrievalFailed が発生する"""
        # given
        repo = MockAssetRepository(should_fail=True)
        notifier = MockNotifier()
        service = SummaryNotificationService(asset_repository=repo, notifier=notifier)

        # when, then
        with pytest.raises(AssetRetrievalFailed):
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
        assert "想定受取額(60歳):" in message_text

    def test_send_summary__message_contains_weekly_valuations(self, sample_assets):
        """送信メッセージに資産評価額推移が含まれる"""
        # given
        weekly_assets = _make_weekly_assets()
        repo = MockAssetRepository(assets=sample_assets, weekly_assets=weekly_assets)
        notifier = MockNotifier()
        service = SummaryNotificationService(asset_repository=repo, notifier=notifier)

        # when
        service.send_summary()

        # then
        message_text = notifier.messages_sent[0].text
        assert "資産評価額推移（直近1週間）" in message_text
        assert "2026-02-14: 600,000円 +5,000円" in message_text
        assert "2026-02-13: 595,000円 -2,000円" in message_text
        assert "2026-02-12: 597,000円 -" in message_text


class TestCalculateWeeklyValuations:
    def test_calculate_weekly_valuations__returns_descending_order(self):
        """新しい日付順で返される"""
        weekly_assets = _make_weekly_assets()

        result = SummaryNotificationService._calculate_weekly_valuations(weekly_assets)

        assert result[0] == (date(2026, 2, 14), 600_000, 5_000)
        assert result[1] == (date(2026, 2, 13), 595_000, -2_000)
        assert result[2] == (date(2026, 2, 12), 597_000, None)

    def test_calculate_weekly_valuations__empty_returns_empty(self):
        """空の場合は空リストを返す"""
        result = SummaryNotificationService._calculate_weekly_valuations({})

        assert result == []

    def test_calculate_weekly_valuations__single_day(self):
        """1日分のデータの場合、前日比はNone"""
        weekly_assets = {
            date(2026, 2, 14): DcpAssets(
                products={
                    "商品A": DcpAssetInfo(
                        cumulative_contributions=450_000,
                        gains_or_losses=150_000,
                        asset_valuation=600_000,
                    ),
                },
            ),
        }

        result = SummaryNotificationService._calculate_weekly_valuations(weekly_assets)

        assert result == [(date(2026, 2, 14), 600_000, None)]
