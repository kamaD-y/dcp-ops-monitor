from src.application import format_summary_message
from src.domain import DcpAssetInfo, DcpAssets, DcpOpsIndicators


class TestFormatSummaryMessage:
    def test_format_summary_message__contains_header(self):
        """メッセージにヘッダーが含まれる"""
        assets = DcpAssets(
            total=DcpAssetInfo(cumulative_contributions=900_000, gains_or_losses=300_000, asset_valuation=1_200_000),
            products={},
        )
        indicators = DcpOpsIndicators(
            operation_years=9.34,
            actual_yield_rate=0.036,
            expected_yield_rate=0.06,
            total_amount_at_60age=15_000_000,
        )

        result = format_summary_message(assets, indicators)

        assert "確定拠出年金 運用状況通知Bot" in result

    def test_format_summary_message__contains_total_assets(self):
        """メッセージに総評価が含まれる"""
        assets = DcpAssets(
            total=DcpAssetInfo(cumulative_contributions=900_000, gains_or_losses=300_000, asset_valuation=1_200_000),
            products={},
        )
        indicators = DcpOpsIndicators(
            operation_years=9.34,
            actual_yield_rate=0.036,
            expected_yield_rate=0.06,
            total_amount_at_60age=15_000_000,
        )

        result = format_summary_message(assets, indicators)

        assert "拠出金額累計: 900,000円" in result
        assert "評価損益: 300,000円" in result
        assert "資産評価額: 1,200,000円" in result

    def test_format_summary_message__contains_indicators(self):
        """メッセージに運用指標が含まれる"""
        assets = DcpAssets(
            total=DcpAssetInfo(cumulative_contributions=900_000, gains_or_losses=300_000, asset_valuation=1_200_000),
            products={},
        )
        indicators = DcpOpsIndicators(
            operation_years=9.34,
            actual_yield_rate=0.036,
            expected_yield_rate=0.06,
            total_amount_at_60age=15_000_000,
        )

        result = format_summary_message(assets, indicators)

        assert "運用年数: 9.34年" in result
        assert "運用利回り: 0.036" in result
        assert "目標利回り: 0.06" in result
        assert "想定受取額(60歳): 15,000,000円" in result

    def test_format_summary_message__contains_products(self):
        """メッセージに商品別情報が含まれる"""
        assets = DcpAssets(
            total=DcpAssetInfo(cumulative_contributions=900_000, gains_or_losses=300_000, asset_valuation=1_200_000),
            products={
                "商品A": DcpAssetInfo(
                    cumulative_contributions=450_000, gains_or_losses=150_000, asset_valuation=600_000
                ),
                "商品B": DcpAssetInfo(
                    cumulative_contributions=450_000, gains_or_losses=150_000, asset_valuation=600_000
                ),
            },
        )
        indicators = DcpOpsIndicators(
            operation_years=9.34,
            actual_yield_rate=0.036,
            expected_yield_rate=0.06,
            total_amount_at_60age=15_000_000,
        )

        result = format_summary_message(assets, indicators)

        assert "商品別" in result
        assert "商品A" in result
        assert "商品B" in result
        assert "取得価額累計: 450,000円" in result
        assert "損益: 150,000円" in result
