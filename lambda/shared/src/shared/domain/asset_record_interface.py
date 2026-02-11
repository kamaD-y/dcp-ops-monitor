from abc import ABC, abstractmethod

from shared.domain.asset_record_object import AssetRecord


class IAssetRecordRepository(ABC):
    @abstractmethod
    def save_daily_records(self, records: list[AssetRecord]) -> None:
        """日次の資産レコードを保存する

        冪等性を保証する。同一日付のレコードが既に存在する場合は
        既存レコードを削除してから保存する（upsert セマンティクス）。

        Raises:
            AssetRecordError: レコード保存失敗時
        """
