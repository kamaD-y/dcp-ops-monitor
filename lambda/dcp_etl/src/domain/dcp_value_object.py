import dataclasses
from typing import Dict

from pydantic.dataclasses import dataclass


@dataclass
class DcpAssetsInfoTotal:
    cumulative_contributions: str = dataclasses.field(default="0円", metadata={"description": "拠出金額累計"})
    total_gains_or_losses: str = dataclasses.field(default="0円", metadata={"description": "評価損益"})
    total_asset_valuation: str = dataclasses.field(default="0円", metadata={"description": "資産評価額"})


@dataclass
class DcpAssetsInfoProduct:
    cumulative_acquisition_costs: str = dataclasses.field(default="0円", metadata={"description": "取得価額累計"})
    gains_or_losses: str = dataclasses.field(default="0円", metadata={"description": "評価損益"})
    asset_valuation: str = dataclasses.field(default="0円", metadata={"description": "資産評価額"})


@dataclass
class DcpAssetsInfo:
    total: DcpAssetsInfoTotal = dataclasses.field(
        default_factory=DcpAssetsInfoTotal, metadata={"description": "総評価"}
    )
    products: Dict[str, DcpAssetsInfoProduct] = dataclasses.field(
        default_factory=dict, metadata={"description": "商品別"}
    )


@dataclass
class DcpOpsIndicators:
    operation_years: float = dataclasses.field(default=0.0, metadata={"description": "運用年数"})
    actual_yield_rate: float = dataclasses.field(default=0.0, metadata={"description": "運用利回り"})
    expected_yield_rate: float = dataclasses.field(default=0.06, metadata={"description": "目標利回り"})
    total_amount_at_60age: str = dataclasses.field(default="0円", metadata={"description": "想定受取額(60歳)"})
