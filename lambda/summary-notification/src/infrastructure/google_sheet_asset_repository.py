"""Google Spreadsheet 資産リポジトリ実装"""

from datetime import date, timedelta

import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1
from shared.domain.asset_object import DcpAssetInfo

from src.config.settings import get_logger
from src.domain import AssetRetrievalFailed, DcpAssets, IAssetRepository

logger = get_logger()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


class GoogleSheetAssetRepository(IAssetRepository):
    """Google Spreadsheet から資産情報を取得するリポジトリ"""

    HEADER_ROW = 1

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

    def get_latest_assets(self) -> DcpAssets:
        """最新日付の資産レコードを取得し DcpAssets に変換する

        1. ヘッダー行から列構成を取得
        2. date 列のみ取得し、最新日付と該当行番号を特定
        3. 該当行のデータのみ取得
        4. DcpAssets に変換

        Returns:
            DcpAssets: 最新の資産情報

        Raises:
            AssetRetrievalFailed: 資産情報が見つからない場合
        """
        try:
            headers = self.worksheet.row_values(self.HEADER_ROW)
            date_col = headers.index("date") + 1
            date_values = self.worksheet.col_values(date_col)
            data_dates = date_values[self.HEADER_ROW :]

            if not data_dates:
                raise AssetRetrievalFailed.no_assets_in_spreadsheet()

            latest_date = max(data_dates)
            logger.info("最新の資産情報を取得します", extra={"date": latest_date})

            target_rows = [i + self.HEADER_ROW + 1 for i, d in enumerate(data_dates) if d == latest_date]

            num_cols = len(headers)
            ranges = [f"{rowcol_to_a1(row, 1)}:{rowcol_to_a1(row, num_cols)}" for row in target_rows]
            results = self.worksheet.batch_get(ranges)
            rows = [dict(zip(headers, row[0])) for row in results if row and row[0]]

            return self._to_dcp_assets(rows)

        except AssetRetrievalFailed:
            raise
        except Exception as e:
            raise AssetRetrievalFailed.during_fetching() from e

    def get_weekly_assets(self) -> dict[date, DcpAssets]:
        """直近カレンダー7日分の資産情報を日付別に取得する

        Returns:
            dict[date, DcpAssets]: 日付 → 資産情報のマッピング
        """
        try:
            headers = self.worksheet.row_values(self.HEADER_ROW)
            date_col = headers.index("date") + 1
            date_values = self.worksheet.col_values(date_col)
            data_dates = date_values[self.HEADER_ROW :]

            if not data_dates:
                raise AssetRetrievalFailed.no_assets_in_spreadsheet()

            latest_date = max(data_dates)
            latest_dt = date.fromisoformat(latest_date)
            cutoff_dt = latest_dt - timedelta(days=7)

            target_dates = {d for d in data_dates if date.fromisoformat(d) > cutoff_dt}

            result: dict[date, DcpAssets] = {}
            num_cols = len(headers)
            for target_date in target_dates:
                target_rows = [i + self.HEADER_ROW + 1 for i, d in enumerate(data_dates) if d == target_date]
                ranges = [f"{rowcol_to_a1(row, 1)}:{rowcol_to_a1(row, num_cols)}" for row in target_rows]
                results = self.worksheet.batch_get(ranges)
                rows = [dict(zip(headers, row[0])) for row in results if row and row[0]]
                result[date.fromisoformat(target_date)] = self._to_dcp_assets(rows)

            return result

        except AssetRetrievalFailed:
            raise
        except Exception as e:
            raise AssetRetrievalFailed.during_fetching() from e

    def _to_dcp_assets(self, rows: list[dict]) -> DcpAssets:
        """フラットレコードから DcpAssets を構築する"""
        products: dict[str, DcpAssetInfo] = {}

        for row in rows:
            info = DcpAssetInfo(
                asset_valuation=int(row["asset_valuation"]),
                cumulative_contributions=int(row["cumulative_contributions"]),
                gains_or_losses=int(row["gains_or_losses"]),
            )
            products[row["product"]] = info

        return DcpAssets(products=products)
