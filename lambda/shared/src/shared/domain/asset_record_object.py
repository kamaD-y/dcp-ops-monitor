from datetime import date

from pydantic import BaseModel

from shared.domain.asset_object import DcpAssetInfo


class AssetRecord(BaseModel):
    """商品別のフラットな資産レコード"""

    date: date
    product: str
    asset_valuation: int
    cumulative_contributions: int
    gains_or_losses: int

    @staticmethod
    def from_dcp_asset_products(
        target_date: date,
        products: dict[str, DcpAssetInfo],
    ) -> list["AssetRecord"]:
        """商品別 DcpAssetInfo から AssetRecord のリストを生成する"""
        return [
            AssetRecord(
                date=target_date,
                product=product_name,
                asset_valuation=info.asset_valuation,
                cumulative_contributions=info.cumulative_contributions,
                gains_or_losses=info.gains_or_losses,
            )
            for product_name, info in products.items()
        ]
