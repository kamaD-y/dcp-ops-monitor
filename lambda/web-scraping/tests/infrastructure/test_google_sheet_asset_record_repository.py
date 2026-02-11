from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from shared.domain.asset_record_object import AssetRecord
from shared.domain.exceptions import AssetRecordError

from src.infrastructure.google_sheet_asset_record_repository import (
    GoogleSheetAssetRecordRepository,
)


@pytest.fixture
def mock_worksheet():
    return MagicMock()


@pytest.fixture
def repository(mock_worksheet):
    """認証をバイパスしてワークシートをモック注入したリポジトリ"""
    with (
        patch("src.infrastructure.google_sheet_asset_record_repository.Credentials") as mock_creds_cls,
        patch("src.infrastructure.google_sheet_asset_record_repository.gspread") as mock_gspread,
    ):
        mock_creds_cls.from_service_account_info.return_value = MagicMock()
        mock_client = MagicMock()
        mock_gspread.authorize.return_value = mock_client
        mock_spreadsheet = MagicMock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet

        repo = GoogleSheetAssetRecordRepository(
            spreadsheet_id="test-spreadsheet-id",
            sheet_name="test-sheet",
            credentials={"type": "service_account"},
        )
    return repo


@pytest.fixture
def sample_records():
    return [
        AssetRecord(
            date=date(2026, 2, 11),
            product="商品A",
            asset_valuation=110_000,
            cumulative_contributions=100_000,
            gains_or_losses=10_000,
        ),
        AssetRecord(
            date=date(2026, 2, 11),
            product="商品B",
            asset_valuation=220_000,
            cumulative_contributions=200_000,
            gains_or_losses=20_000,
        ),
    ]


class TestSaveDailyRecords:
    def test_save_daily_records__appends_rows(self, repository, mock_worksheet, sample_records):
        """レコードがスプレッドシートに追記される"""
        mock_worksheet.col_values.return_value = ["date", "2026-02-10"]

        repository.save_daily_records(sample_records)

        mock_worksheet.append_rows.assert_called_once_with(
            [
                ["2026-02-11", "商品A", 110_000, 100_000, 10_000],
                ["2026-02-11", "商品B", 220_000, 200_000, 20_000],
            ],
            value_input_option="RAW",
        )

    def test_save_daily_records__deletes_existing_rows_then_appends(self, repository, mock_worksheet, sample_records):
        """同一日付の既存行がある場合、削除してから追記する（冪等性）"""
        # date カラムにヘッダ + 既存データ（2行が対象日付に一致）
        mock_worksheet.col_values.return_value = [
            "date",
            "2026-02-10",
            "2026-02-11",
            "2026-02-11",
        ]

        repository.save_daily_records(sample_records)

        # 下の行から削除される（行番号 4, 3 の順）
        assert mock_worksheet.delete_rows.call_count == 2
        mock_worksheet.delete_rows.assert_any_call(4)
        mock_worksheet.delete_rows.assert_any_call(3)

        mock_worksheet.append_rows.assert_called_once()

    def test_save_daily_records__empty_records_does_nothing(self, repository, mock_worksheet):
        """空リストの場合、何も行わない"""
        repository.save_daily_records([])

        mock_worksheet.col_values.assert_not_called()
        mock_worksheet.append_rows.assert_not_called()

    def test_save_daily_records__api_error_raises_asset_record_error(self, repository, mock_worksheet, sample_records):
        """API エラー時に AssetRecordError が発生する"""
        mock_worksheet.col_values.side_effect = Exception("API Error")

        with pytest.raises(AssetRecordError, match="資産レコードの保存に失敗しました"):
            repository.save_daily_records(sample_records)
