from shared.domain.asset_record_interface import IAssetRecordRepository
from shared.domain.asset_record_object import AssetRecord


class MockAssetRecordRepository(IAssetRecordRepository):
    """IAssetRecordRepository の Mock 実装（E2E テスト用）"""

    def __init__(self) -> None:
        self.saved_records: list[AssetRecord] = []

    def save_daily_records(self, records: list[AssetRecord]) -> None:
        self.saved_records.extend(records)
