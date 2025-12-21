import dataclasses


@dataclasses.dataclass(frozen=True)
class DcpAssetInfo:
    """確定拠出年金の資産評価を扱う値クラス

    Attributes:
        cumulative_contributions (str): 拠出金額累計
        gains_or_losses (str): 評価損益
        asset_valuation (str): 資産評価額
    """

    cumulative_contributions: str = dataclasses.field(default="0円")
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


@dataclasses.dataclass(frozen=True)
class DcpAssets:
    total: DcpAssetInfo
    products: dict[str, DcpAssetInfo]
