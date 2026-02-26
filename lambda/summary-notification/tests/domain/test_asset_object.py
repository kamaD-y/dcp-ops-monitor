from src.domain import AssetEvaluation


class TestAssetEvaluation:
    def test_create__valid_values(self):
        """正常な値で AssetEvaluation を生成できる"""
        info = AssetEvaluation(
            cumulative_contributions=900_000,
            gains_or_losses=300_000,
            asset_valuation=1_200_000,
        )
        assert info.cumulative_contributions == 900_000
        assert info.gains_or_losses == 300_000
        assert info.asset_valuation == 1_200_000

    def test_create__negative_gains_or_losses(self):
        """評価損益がマイナスの場合も生成できる"""
        info = AssetEvaluation(
            cumulative_contributions=900_000,
            gains_or_losses=-100_000,
            asset_valuation=800_000,
        )
        assert info.gains_or_losses == -100_000

    def test_aggregate__sums_all_evaluations(self):
        """複数の AssetEvaluation を合算できる"""
        evaluations = [
            AssetEvaluation(
                cumulative_contributions=450_000,
                gains_or_losses=150_000,
                asset_valuation=600_000,
            ),
            AssetEvaluation(
                cumulative_contributions=450_000,
                gains_or_losses=150_000,
                asset_valuation=600_000,
            ),
        ]
        total = AssetEvaluation.aggregate(evaluations)
        assert total.cumulative_contributions == 900_000
        assert total.gains_or_losses == 300_000
        assert total.asset_valuation == 1_200_000

    def test_aggregate__empty_returns_zero(self):
        """空リストの場合に全フィールド 0 が返る"""
        total = AssetEvaluation.aggregate([])
        assert total.cumulative_contributions == 0
        assert total.gains_or_losses == 0
        assert total.asset_valuation == 0
