from pydantic import BaseModel
from shared.domain.asset_object import AssetEvaluation


class DcpAssets(BaseModel):
    """資産情報（商品別）"""

    products: dict[str, AssetEvaluation]

    def calculate_total(self) -> AssetEvaluation:
        """全商品の合計を算出する"""
        return AssetEvaluation(
            cumulative_contributions=sum(p.cumulative_contributions for p in self.products.values()),
            gains_or_losses=sum(p.gains_or_losses for p in self.products.values()),
            asset_valuation=sum(p.asset_valuation for p in self.products.values()),
        )
