from datetime import datetime

from src.application import calculate_indicators
from src.application.indicators_calculator import (
    calculate_annual_yield_rate,
    calculate_total_amount_at_60age,
    calculate_year_diff,
)
from src.domain import DcpAssetInfo


class TestCalculateYearDiff:
    def test_calculate_year_diff__one_year(self):
        """1年差を正しく計算できる"""
        result = calculate_year_diff(
            start_dt=datetime(2016, 10, 1),
            end_dt=datetime(2017, 10, 1),
        )
        assert result == 1.0

    def test_calculate_year_diff__fractional_years(self):
        """端数年数を正しく計算できる"""
        result = calculate_year_diff(
            start_dt=datetime(2016, 10, 1),
            end_dt=datetime(2026, 2, 5),
        )
        assert result > 9.0
        assert result < 10.0


class TestCalculateAnnualYieldRate:
    def test_calculate_annual_yield_rate__positive(self):
        """正のリターンの利回りを計算できる"""
        result = calculate_annual_yield_rate(
            cumulative_contributions=1_000_000,
            gains_or_losses=300_000,
            operation_years=10.0,
        )
        assert result == 0.03

    def test_calculate_annual_yield_rate__negative(self):
        """負のリターンの利回りを計算できる"""
        result = calculate_annual_yield_rate(
            cumulative_contributions=1_000_000,
            gains_or_losses=-100_000,
            operation_years=5.0,
        )
        assert result == -0.02


class TestCalculateTotalAmountAt60age:
    def test_calculate_total_amount_at_60age__positive_yield(self):
        """正の利回りで想定受取額を計算できる"""
        result = calculate_total_amount_at_60age(
            yield_rate=0.03,
            asset_valuation=1_200_000,
            today=datetime(2026, 2, 5),
        )
        assert result > 1_200_000  # 積立分 + 現在の資産
        assert isinstance(result, int)


class TestCalculateIndicators:
    def test_calculate_indicators__returns_valid_indicators(self):
        """正常な資産情報から運用指標を計算できる"""
        total_assets = DcpAssetInfo(
            cumulative_contributions=900_000,
            gains_or_losses=300_000,
            asset_valuation=1_200_000,
        )
        today = datetime(2026, 2, 5)

        result = calculate_indicators(total_assets, today=today)

        assert result.operation_years > 9.0
        assert result.actual_yield_rate > 0
        assert result.total_amount_at_60age > 1_200_000
        assert isinstance(result.total_amount_at_60age, int)
