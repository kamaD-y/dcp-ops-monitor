import dataclasses
from typing import Dict

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class DcpTotalAssets:
    """確定拠出年金の総資産評価を扱う値クラス

    Attributes:
        cumulative_contributions (str): 拠出金額累計
        total_gains_or_losses (str): 評価損益
        total_asset_valuation (str): 資産評価額
    """

    cumulative_contributions: str = dataclasses.field(default="0円")
    total_gains_or_losses: str = dataclasses.field(default="0円")
    total_asset_valuation: str = dataclasses.field(default="0円")

    def __post_init__(self) -> None:
        """初期化後に各フィールドの末尾に「円」が付いていることを確認する
        Raises:
            ValueError: 各フィールドの値が不正な場合
        """
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, str) or not value.endswith("円"):
                raise ValueError(f"{field.name} must be a string ending with '円'")


@dataclass(frozen=True)
class DcpProductAssets:
    """確定拠出年金の商品毎の資産評価を扱う値クラス

    Attributes:
        cumulative_acquisition_costs (str): 取得価額累計
        gains_or_losses (str): 評価損益
        asset_valuation (str): 資産評価額
    """

    cumulative_acquisition_costs: str = dataclasses.field(default="0円")
    gains_or_losses: str = dataclasses.field(default="0円")
    asset_valuation: str = dataclasses.field(default="0円")

    def __post_init__(self) -> None:
        """初期化後に各フィールドの末尾に「円」が付いていることを確認する

        Raises:
            ValueError: 各フィールドの値が不正な場合
        """
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, str) or not value.endswith("円"):
                raise ValueError(f"{field.name} must be a string ending with '円'")


@dataclass(frozen=True)
class DcpAssetsInfo:
    """確定拠出年金の資産評価を扱う値クラス

    Attributes:
        total (DcpAssetsInfoTotal): 総資産評価情報
        products (Dict[str, DcpAssetsInfoProduct]): 商品別の資産評価情報
    """

    total: DcpTotalAssets = dataclasses.field(default_factory=DcpTotalAssets)
    products: Dict[str, DcpProductAssets] = dataclasses.field(default_factory=dict)


@dataclass(frozen=True)
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
