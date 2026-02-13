from pydantic import BaseModel
from shared.domain.asset_object import DcpAssetInfo


class DcpAssets(BaseModel):
    """資産情報（総評価 + 商品別）"""

    total: DcpAssetInfo
    products: dict[str, DcpAssetInfo]
