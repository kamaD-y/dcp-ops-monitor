from datetime import date

from src.application import format_summary_message
from src.domain import DcpAssetInfo, DcpOpsIndicators


class TestFormatSummaryMessage:
    def test_format_summary_message__contains_header(self):
        """メッセージにヘッダーが含まれる"""
        total = DcpAssetInfo(cumulative_contributions=900_000, gains_or_losses=300_000, asset_valuation=1_200_000)
        indicators = DcpOpsIndicators(
            operation_years=9.34,
            actual_yield_rate=0.036,
            total_amount_at_60age=15_000_000,
        )

        result = format_summary_message(total, indicators, [])

        assert "確定拠出年金 運用状況通知Bot" in result

    def test_format_summary_message__contains_total_assets(self):
        """メッセージに総評価が含まれる"""
        total = DcpAssetInfo(cumulative_contributions=900_000, gains_or_losses=300_000, asset_valuation=1_200_000)
        indicators = DcpOpsIndicators(
            operation_years=9.34,
            actual_yield_rate=0.036,
            total_amount_at_60age=15_000_000,
        )

        result = format_summary_message(total, indicators, [])

        assert "拠出金額累計: 900,000円" in result
        assert "評価損益: 300,000円" in result
        assert "資産評価額: 1,200,000円" in result

    def test_format_summary_message__contains_indicators(self):
        """メッセージに運用指標が含まれる"""
        total = DcpAssetInfo(cumulative_contributions=900_000, gains_or_losses=300_000, asset_valuation=1_200_000)
        indicators = DcpOpsIndicators(
            operation_years=9.34,
            actual_yield_rate=0.036,
            total_amount_at_60age=15_000_000,
        )

        result = format_summary_message(total, indicators, [])

        assert "運用年数: 9.34年" in result
        assert "運用利回り: 0.036" in result
        assert "想定受取額(60歳): 15,000,000円" in result

    def test_format_summary_message__contains_weekly_valuations(self):
        """メッセージに資産評価額推移が含まれる"""
        total = DcpAssetInfo(cumulative_contributions=900_000, gains_or_losses=300_000, asset_valuation=1_200_000)
        indicators = DcpOpsIndicators(
            operation_years=9.34,
            actual_yield_rate=0.036,
            total_amount_at_60age=15_000_000,
        )
        weekly_valuations = [
            (date(2026, 2, 14), 1_200_000, 5_000),
            (date(2026, 2, 13), 1_195_000, -2_000),
            (date(2026, 2, 12), 1_197_000, None),
        ]

        result = format_summary_message(total, indicators, weekly_valuations)

        assert "資産評価額推移（直近1週間）" in result
        assert "2026-02-14: 1,200,000円 +5,000円" in result
        assert "2026-02-13: 1,195,000円 -2,000円" in result
        assert "2026-02-12: 1,197,000円 -" in result

    def test_format_summary_message__empty_weekly_valuations(self):
        """週次データが空の場合、推移セクションが表示されない"""
        total = DcpAssetInfo(cumulative_contributions=900_000, gains_or_losses=300_000, asset_valuation=1_200_000)
        indicators = DcpOpsIndicators(
            operation_years=9.34,
            actual_yield_rate=0.036,
            total_amount_at_60age=15_000_000,
        )

        result = format_summary_message(total, indicators, [])

        assert "資産評価額推移" not in result
