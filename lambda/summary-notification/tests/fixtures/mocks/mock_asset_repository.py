"""テスト用 Mock Asset Repository"""

from datetime import date

from src.domain import AssetEvaluation, AssetRetrievalFailed, IAssetRepository


class MockAssetRepository(IAssetRepository):
    """テスト用 Mock 資産リポジトリ

    get_latest_assets() / get_weekly_assets() の呼び出しを記録し、テストで検証可能にする
    """

    def __init__(
        self,
        assets: dict[str, AssetEvaluation] | None = None,
        weekly_assets: dict[date, dict[str, AssetEvaluation]] | None = None,
        should_fail: bool = False,
    ) -> None:
        self.assets = assets
        self.weekly_assets = weekly_assets or {}
        self.should_fail = should_fail
        self.get_called = False

    def get_latest_assets(self) -> dict[str, AssetEvaluation]:
        self.get_called = True
        if self.should_fail:
            raise AssetRetrievalFailed.no_assets_in_spreadsheet()
        if self.assets is None:
            raise AssetRetrievalFailed.no_assets_in_spreadsheet()
        return self.assets

    def get_weekly_assets(self) -> dict[date, dict[str, AssetEvaluation]]:
        return self.weekly_assets
