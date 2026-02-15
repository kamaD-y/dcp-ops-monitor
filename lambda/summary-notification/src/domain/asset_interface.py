from abc import ABC, abstractmethod
from datetime import date

from .asset_object import DcpAssets


class IAssetRepository(ABC):
    """資産リポジトリインターフェース"""

    @abstractmethod
    def get_latest_assets(self) -> DcpAssets:
        """最新の資産情報を取得

        Returns:
            DcpAssets: 最新の資産情報

        Raises:
            AssetRetrievalFailed: 資産情報が見つからない場合
        """
        pass

    @abstractmethod
    def get_weekly_assets(self) -> dict[date, DcpAssets]:
        """直近1週間の資産情報を日付別に取得

        Returns:
            dict[date, DcpAssets]: 日付 → 資産情報のマッピング
            データが存在しない日は含まない

        Raises:
            AssetRetrievalFailed: 資産情報が見つからない場合
        """
        pass
