from abc import ABC, abstractmethod
from typing import Optional


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

    @abstractmethod
    def get_error_image_path(self) -> Optional[str]:
        """エラー時のスクリーンショット画像のパスを取得するメソッド

        Returns:
            Optional[str]: エラー時のスクリーンショット画像のパス
        """
        pass
