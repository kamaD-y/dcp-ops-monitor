from datetime import datetime, timedelta

import pytest
from src.domain.dcp_value_object import DcpAssetsInfo, DcpProductAssets, DcpTotalAssets, DcpOpsIndicators

@pytest.fixture
def valid_assets_info() -> DcpAssetsInfo:
    """テスト用のDcpAssetsInfoオブジェクトを生成する"""
    return DcpAssetsInfo(
        total=DcpTotalAssets(
            cumulative_contributions="900,000円", total_gains_or_losses="300,000円", total_asset_valuation="1,200,000円"
        ),
        products={
            "プロダクト_1": DcpProductAssets(
                cumulative_acquisition_costs="100,000円", gains_or_losses="11,111円", asset_valuation="111,111円"
            ),
            "プロダクト_2": DcpProductAssets(
                cumulative_acquisition_costs="200,000円", gains_or_losses="22,222円", asset_valuation="222,222円"
            ),
        },
    )


@pytest.fixture
def valid_ops_indicators() -> dict:
    """テスト用の運用指標を生成する"""
    return DcpOpsIndicators(
        operation_years=5.0,
        actual_yield_rate=0.05,
        expected_yield_rate=0.06,
        total_amount_at_60age="1,000,000円",
    )


@pytest.fixture
def dcp_operation_days() -> float:
    """運用年数を返す"""
    # 運用開始日: 2016/10/01
    operation_start_dt = datetime(2016, 10, 1)
    today = datetime.today()
    operation_days = (today - operation_start_dt) / timedelta(days=365)
    return round(operation_days, 2)
