from abc import ABC, abstractmethod

from shared.domain.asset_object import DcpAssets


class IAssetRepository(ABC):
    """資産リポジトリインターフェース"""

    @abstractmethod
    def get_latest_assets(self) -> DcpAssets:
        """最新の資産情報を取得

        Returns:
            DcpAssets: 最新の資産情報

        Raises:
            AssetNotFound: 資産情報が見つからない場合
        """
        pass
