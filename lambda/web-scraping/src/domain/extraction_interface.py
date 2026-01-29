from abc import ABC, abstractmethod

from .extraction_object import DcpAssets


class IDcpExtractor(ABC):
    """DCP 資産抽出インターフェース

    HTML から DCP 資産情報を抽出する抽象インターフェース。
    """

    @abstractmethod
    def extract(self, html: str) -> DcpAssets:
        """HTML から DCP 資産情報を抽出

        Args:
            html: HTML ソース文字列

        Returns:
            DcpAssets: 抽出された資産情報

        Raises:
            AssetExtractionFailed: 抽出に失敗した場合
        """
        pass
