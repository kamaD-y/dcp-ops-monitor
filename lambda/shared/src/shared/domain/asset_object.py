from collections.abc import Iterable

from pydantic import BaseModel


class AssetEvaluation(BaseModel):
    """確定拠出年金の資産評価を扱う値クラス

    Attributes:
        cumulative_contributions (int): 拠出金額累計
        gains_or_losses (int): 評価損益
        asset_valuation (int): 資産評価額
    """

    cumulative_contributions: int
    gains_or_losses: int
    asset_valuation: int

    @classmethod
    def aggregate(cls, evaluations: Iterable["AssetEvaluation"]) -> "AssetEvaluation":
        """複数の AssetEvaluation を合算して単一の AssetEvaluation を生成する"""
        items = list(evaluations)
        return cls(
            cumulative_contributions=sum(e.cumulative_contributions for e in items),
            gains_or_losses=sum(e.gains_or_losses for e in items),
            asset_valuation=sum(e.asset_valuation for e in items),
        )

    @classmethod
    def from_html_strings(
        cls,
        cumulative_contributions_str: str,
        gains_or_losses_str: str,
        asset_valuation_str: str,
    ) -> "AssetEvaluation":
        """HTML から取得した文字列から AssetEvaluation を生成

        Args:
            cumulative_contributions_str: 拠出金額累計の文字列（例: "1,234,567円"）
            gains_or_losses_str: 評価損益の文字列
            asset_valuation_str: 資産評価額の文字列

        Returns:
            AssetEvaluation: 変換済みの資産情報
        """
        return cls(
            cumulative_contributions=cls._parse_yen_amount(cumulative_contributions_str),
            gains_or_losses=cls._parse_yen_amount(gains_or_losses_str),
            asset_valuation=cls._parse_yen_amount(asset_valuation_str),
        )

    @staticmethod
    def _parse_yen_amount(yen_str: str) -> int:
        """円表記の文字列を整数に変換

        Args:
            yen_str: 円表記の文字列（例: "1,234,567円"）

        Returns:
            int: 整数値
        """
        # カンマ、円記号、空白を除去
        cleaned = yen_str.replace(",", "").replace("円", "").replace(" ", "").strip()

        # 全角数字を半角に変換
        cleaned = cleaned.translate(str.maketrans("０１２３４５６７８９", "0123456789"))

        # マイナス記号の処理（全角・半角対応）
        cleaned = cleaned.replace("−", "-").replace("ー", "-").replace("－", "-")

        return int(cleaned)
