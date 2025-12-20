from abc import ABC, abstractmethod


class IDcpScraper(ABC):
    """スクレイピングドライバー抽象クラス"""

    @abstractmethod
    def __init__(self) -> None:
        """コンストラクタ"""
        pass

    @abstractmethod
    def fetch_asset_valuation_html(self, start_url: str) -> str:
        """資産評価情報ページの HTML ソースを取得するメソッド

        Args:
            start_url (str): スクレイピングを開始する URL

        Returns:
            str: 資産評価情報ページの HTML ソース
        """
        pass
