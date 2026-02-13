from abc import ABC, abstractmethod

from shared.domain.asset_object import DcpAssetInfo


class IScraper(ABC):
    """スクレイピングドライバー抽象クラス"""

    def __init__(self) -> None:
        """コンストラクタ"""
        pass

    @abstractmethod
    def fetch_asset_valuation(self) -> dict[str, DcpAssetInfo]:
        """資産評価情報を取得するメソッド

        ページ遷移（ログイン → 資産評価ページ → ログアウト）と
        要素抽出を一括で行う。

        Returns:
            dict[str, DcpAssetInfo]: 商品別の資産評価情報

        Raises:
            ScrapingFailed: スクレイピングまたは資産情報抽出に失敗した場合
        """
        pass
