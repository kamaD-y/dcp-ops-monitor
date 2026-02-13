from pydantic import BaseModel


class DcpAssetInfo(BaseModel):
    """確定拠出年金の資産評価を扱う値クラス

    Attributes:
        cumulative_contributions (int): 拠出金額累計
        gains_or_losses (int): 評価損益
        asset_valuation (int): 資産評価額
    """

    cumulative_contributions: int
    gains_or_losses: int
    asset_valuation: int
