"""Google Spreadsheet 資産リポジトリ実装"""

import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1
from shared.domain.asset_object import DcpAssetInfo

from src.config.settings import get_logger
from src.domain import AssetNotFound, DcpAssets, IAssetRepository

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
        4. DcpAssets に変換（total は全商品の合算）

        Returns:
            DcpAssets: 最新の資産情報

        Raises:
            AssetNotFound: 資産情報が見つからない場合
        """
        try:
            headers = self.worksheet.row_values(self.HEADER_ROW)
            date_col = headers.index("date") + 1
            date_values = self.worksheet.col_values(date_col)
            data_dates = date_values[self.HEADER_ROW :]

            if not data_dates:
                raise AssetNotFound.no_assets_in_spreadsheet()

            latest_date = max(data_dates)
            logger.info("最新の資産情報を取得します", extra={"date": latest_date})

            target_rows = [i + self.HEADER_ROW + 1 for i, d in enumerate(data_dates) if d == latest_date]

            num_cols = len(headers)
            ranges = [f"{rowcol_to_a1(row, 1)}:{rowcol_to_a1(row, num_cols)}" for row in target_rows]
            results = self.worksheet.batch_get(ranges)
            rows = [dict(zip(headers, row[0])) for row in results]

            return self._to_dcp_assets(rows)

        except AssetNotFound:
            raise
        except Exception as e:
            raise AssetNotFound(f"資産情報の取得に失敗しました: {e}") from e

    def _to_dcp_assets(self, rows: list[dict]) -> DcpAssets:
        """フラットレコードから DcpAssets を構築する（total は全商品の合算）"""
        products: dict[str, DcpAssetInfo] = {}
        total_contributions = 0
        total_gains = 0
        total_valuation = 0

        for row in rows:
            info = DcpAssetInfo(
                asset_valuation=int(row["asset_valuation"]),
                cumulative_contributions=int(row["cumulative_contributions"]),
                gains_or_losses=int(row["gains_or_losses"]),
            )
            products[row["product"]] = info
            total_contributions += info.cumulative_contributions
            total_gains += info.gains_or_losses
            total_valuation += info.asset_valuation

        total = DcpAssetInfo(
            cumulative_contributions=total_contributions,
            gains_or_losses=total_gains,
            asset_valuation=total_valuation,
        )
        return DcpAssets(total=total, products=products)
