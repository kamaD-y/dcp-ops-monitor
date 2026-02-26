from abc import ABC, abstractmethod
from datetime import date

from shared.domain.asset_object import AssetEvaluation


class IAssetRepository(ABC):
    """資産リポジトリインターフェース"""

    @abstractmethod
    def get_latest_assets(self) -> dict[str, AssetEvaluation]:
        """最新の資産情報を取得

        Returns:
            dict[str, AssetEvaluation]: 商品名 → 資産評価情報のマッピング

        Raises:
            AssetRetrievalFailed: 資産情報が見つからない場合
        """
        pass

    @abstractmethod
    def get_weekly_assets(self) -> dict[date, dict[str, AssetEvaluation]]:
        """直近1週間の資産情報を日付別に取得

        Returns:
            dict[date, dict[str, AssetEvaluation]]: 日付 → 資産情報のマッピング
            データが存在しない日は含まない

        Raises:
            AssetRetrievalFailed: 資産情報が見つからない場合
        """
        pass
