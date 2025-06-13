from abc import ABC, abstractmethod


class AbstractScraper(ABC):
    """スクレイピング抽象クラス"""

    @abstractmethod
    def scrape(self) -> bool:
        pass
