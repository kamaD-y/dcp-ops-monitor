import pytest
from src.domain.dcp_value_object import DcpOpsIndicators, DcpProductAssets, DcpTotalAssets

"""
DcpTotalAssetsのテスト
"""


def test_dcp_total_assets__valid_parameters() -> None:
    """DcpTotalAssetsのパラメータが正しい場合のテスト"""
    try:
        DcpTotalAssets(
            cumulative_contributions="900,000円",
            total_gains_or_losses="300,000円",
            total_asset_valuation="1,200,000円",
        )
    except ValueError:
        pytest.fail("DcpTotalAssets raised ValueError unexpectedly!")


@pytest.mark.parametrize(
    "cumulative_contributions, total_gains_or_losses, total_asset_valuation",
    [
        ("900,000", "300,000", "1,200,000"),  # 円のない文字列
    ],
)
def test_dcp_total_assets__invalid_parameters(
    cumulative_contributions: str,
    total_gains_or_losses: str,
    total_asset_valuation: str,
) -> None:
    """DcpTotalAssetsのパラメータが不正な場合のテスト"""

    with pytest.raises(ValueError):
        DcpTotalAssets(
            cumulative_contributions=cumulative_contributions,
            total_gains_or_losses=total_gains_or_losses,
            total_asset_valuation=total_asset_valuation,
        )


"""
DcpProductAssetsのテスト
"""


def test_dcp_product_assets__valid_parameters() -> None:
    """DcpProductAssetsのパラメータが正しい場合のテスト"""
    try:
        DcpProductAssets(
            cumulative_acquisition_costs="100,000円",
            gains_or_losses="11,111円",
            asset_valuation="111,111円",
        )
    except ValueError:
        pytest.fail("DcpProductAssets raised ValueError unexpectedly!")


@pytest.mark.parametrize(
    "cumulative_acquisition_costs, gains_or_losses, asset_valuation",
    [
        ("100,000", "11,111", "111,111"),  # 円のない文字列
    ],
)
def test_dcp_product_assets__invalid_parameters(
    cumulative_acquisition_costs: str,
    gains_or_losses: str,
    asset_valuation: str,
) -> None:
    """DcpProductAssetsのパラメータが不正な場合のテスト"""

    with pytest.raises(ValueError):
        DcpProductAssets(
            cumulative_acquisition_costs=cumulative_acquisition_costs,
            gains_or_losses=gains_or_losses,
            asset_valuation=asset_valuation,
        )


"""
DcpOpsIndicatorsのテスト
"""


def test_dcp_ops_indicators__valid_parameters() -> None:
    """DcpOpsIndicatorsのパラメータが正しい場合のテスト"""
    try:
        DcpOpsIndicators(
            operation_years=5.0,
            actual_yield_rate=0.05,
            expected_yield_rate=0.06,
            total_amount_at_60age="1,500,000円",
        )
    except ValueError:
        pytest.fail("DcpOpsIndicators raised ValueError unexpectedly!")


@pytest.mark.parametrize(
    "operation_years, actual_yield_rate, expected_yield_rate, total_amount_at_60age",
    [
        (5.0, 0.05, 0.06, "1,500,000"),  # 円のない文字列
    ],
)
def test_dcp_ops_indicators__invalid_parameters(
    operation_years: float,
    actual_yield_rate: float,
    expected_yield_rate: float,
    total_amount_at_60age: str,
) -> None:
    """DcpOpsIndicatorsのパラメータが不正な場合のテスト"""

    with pytest.raises(ValueError):
        DcpOpsIndicators(
            operation_years=operation_years,
            actual_yield_rate=actual_yield_rate,
            expected_yield_rate=expected_yield_rate,
            total_amount_at_60age=total_amount_at_60age,
        )
