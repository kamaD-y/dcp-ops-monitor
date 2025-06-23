from abc import ABC, abstractmethod

from domain.value_object import DcpAssetsInfo


class ScraperInterface(ABC):
    """スクレイピング抽象クラス"""

    @abstractmethod
    def __init__(self) -> None:
        """コンストラクタ"""
        self.page_source = ""  # スクレイピング結果のHTMLソース
        pass

    @abstractmethod
    def scrape(self, start_url: str) -> str:
        """スクレイピング実行メソッド

        Args:
            start_url (str): スクレイピングを開始するURL

        Returns:
            str: スクレイピング結果のHTMLソース
        """
        pass

    @abstractmethod
    def extract(self, html_source: str) -> DcpAssetsInfo:
        """スクレイピング結果から資産情報を抽出するメソッド

        Args:
            html_source (str): スクレイピング結果のHTMLソース

        Returns:
            DcpAssetsInfo: 抽出した資産情報
        """
        pass
