from datetime import datetime, timedelta

import pytest


@pytest.fixture
def valid_ops_indicators():
    """テスト用の運用指標を生成する"""
    from src.domain.dcp_value_object import DcpOpsIndicators

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
