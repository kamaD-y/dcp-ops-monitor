from src.domain import DcpOpsIndicators


class TestDcpOpsIndicators:
    def test_create__valid_values(self):
        """正常な値で DcpOpsIndicators を生成できる"""
        indicators = DcpOpsIndicators(
            operation_years=9.34,
            actual_yield_rate=0.036,
            total_amount_at_60age=15_000_000,
        )
        assert indicators.operation_years == 9.34
        assert indicators.actual_yield_rate == 0.036
        assert indicators.total_amount_at_60age == 15_000_000

    def test_create__zero_yield_rate(self):
        """利回りが 0 の場合も生成できる"""
        indicators = DcpOpsIndicators(
            operation_years=1.0,
            actual_yield_rate=0.0,
            total_amount_at_60age=0,
        )
        assert indicators.actual_yield_rate == 0.0

    def test_create__negative_yield_rate(self):
        """利回りがマイナスの場合も生成できる"""
        indicators = DcpOpsIndicators(
            operation_years=5.0,
            actual_yield_rate=-0.02,
            total_amount_at_60age=5_000_000,
        )
        assert indicators.actual_yield_rate == -0.02
