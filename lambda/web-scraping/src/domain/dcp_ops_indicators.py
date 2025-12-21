import dataclasses


@dataclasses.dataclass(frozen=True)
class DcpOpsIndicators:
    """確定拠出年金の運用指標を扱う値クラス

    Attributes:
        operation_years (float): 運用年数
        actual_yield_rate (float): 運用利回り
        expected_yield_rate (float): 目標利回り
        total_amount_at_60age (str): 想定受取額(60歳)
    """

    operation_years: float = dataclasses.field(default=0.0)
    actual_yield_rate: float = dataclasses.field(default=0.0)
    expected_yield_rate: float = dataclasses.field(default=0.06)
    total_amount_at_60age: str = dataclasses.field(default="0円")

    def __post_init__(self) -> None:
        """初期化後にtotal_amount_at_60ageの末尾に「円」が付いていることを確認する
        Raises:
            ValueError: 各フィールドの値が不正な場合
        """
        if not isinstance(self.total_amount_at_60age, str) or not self.total_amount_at_60age.endswith("円"):
            raise ValueError("total_amount_at_60age must be a string ending with '円'")
