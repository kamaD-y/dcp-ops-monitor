from pydantic import BaseModel


class DcpOpsIndicators(BaseModel):
    """運用指標を扱う値クラス

    Attributes:
        operation_years (float): 運用年数
        actual_yield_rate (float): 運用利回り
        total_amount_at_60age (int): 想定受取額（60歳）
    """

    operation_years: float
    actual_yield_rate: float
    total_amount_at_60age: int
