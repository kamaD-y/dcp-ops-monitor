from abc import ABC, abstractmethod


class AbstractScraper(ABC):
    """スクレイピング抽象クラス"""

    @abstractmethod
    def scrape(self, start_url: str) -> str:
        """スクレイピング実行メソッド

        Args:
            start_url (str): スクレイピングを開始するURL

        Returns:
            str: スクレイピング結果のHTMLソース
        """
        pass
