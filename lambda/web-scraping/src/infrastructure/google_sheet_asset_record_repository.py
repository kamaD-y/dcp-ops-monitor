"""Google Spreadsheet を使った資産レコードリポジトリ実装"""

import gspread
from google.oauth2.service_account import Credentials
from shared.domain.asset_record_interface import IAssetRecordRepository
from shared.domain.asset_record_object import AssetRecord
from shared.domain.exceptions import AssetRecordError

from src.config.settings import get_logger

logger = get_logger()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class GoogleSheetAssetRecordRepository(IAssetRecordRepository):
    """Google Spreadsheet を使った IAssetRecordRepository 実装"""

    def __init__(self, spreadsheet_id: str, sheet_name: str, credentials: dict) -> None:
        """Google Spreadsheet クライアントを初期化

        Args:
            spreadsheet_id: スプレッドシートID
            sheet_name: シート名
            credentials: サービスアカウント認証情報
        """
        creds = Credentials.from_service_account_info(credentials, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(spreadsheet_id)
        self.worksheet = spreadsheet.worksheet(sheet_name)

    def save_daily_records(self, records: list[AssetRecord]) -> None:
        """日次の資産レコードをスプレッドシートに保存する

        冪等性の実現方法:
        1. シート内から対象日付の既存行を検索（date カラム一致）
        2. 既存行があれば削除
        3. 新しいレコードを末尾に追記

        Args:
            records: 保存する資産レコードのリスト

        Raises:
            AssetRecordError: レコード保存失敗時
        """
        if not records:
            return

        try:
            target_date = str(records[0].date)
            self._delete_existing_rows(target_date)
            self._append_records(records)
            logger.info("資産レコードを保存しました", extra={"date": target_date, "count": len(records)})
        except AssetRecordError:
            raise
        except Exception as e:
            raise AssetRecordError(f"資産レコードの保存に失敗しました: {e}") from e

    def _delete_existing_rows(self, target_date: str) -> None:
        """対象日付の既存行を削除する"""
        date_column = self.worksheet.col_values(1)
        rows_to_delete = [i + 1 for i, val in enumerate(date_column) if val == target_date]

        # 下の行から削除（インデックスがずれないように）
        for row_index in reversed(rows_to_delete):
            self.worksheet.delete_rows(row_index)

        if rows_to_delete:
            logger.info("既存行を削除しました", extra={"date": target_date, "count": len(rows_to_delete)})

    def _append_records(self, records: list[AssetRecord]) -> None:
        """レコードを末尾に追記する"""
        rows = [
            [
                str(record.date),
                record.product,
                record.asset_valuation,
                record.cumulative_contributions,
                record.gains_or_losses,
            ]
            for record in records
        ]
        self.worksheet.append_rows(rows, value_input_option="RAW")
