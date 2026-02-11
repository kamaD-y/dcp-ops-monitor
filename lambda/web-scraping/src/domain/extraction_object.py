from shared.domain.asset_object import DcpAssetInfo as BaseDcpAssetInfo


class DcpAssetInfo(BaseDcpAssetInfo):
    """HTML パース機能付き DcpAssetInfo"""

    @classmethod
    def from_html_strings(
        cls,
        cumulative_contributions_str: str,
        gains_or_losses_str: str,
        asset_valuation_str: str,
    ) -> "DcpAssetInfo":
        """HTML から取得した文字列から DcpAssetInfo を生成

        Args:
            cumulative_contributions_str: 拠出金額累計の文字列（例: "1,234,567円"）
            gains_or_losses_str: 評価損益の文字列
            asset_valuation_str: 資産評価額の文字列

        Returns:
            DcpAssetInfo: 変換済みの資産情報
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


__all__ = ["DcpAssetInfo"]
