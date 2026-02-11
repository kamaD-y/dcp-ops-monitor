from datetime import date

from shared.domain.asset_object import DcpAssetInfo
from shared.domain.asset_record_object import AssetRecord


class TestAssetRecord:
    def test_create__valid_fields(self):
        """AssetRecord が正しいフィールドで生成される"""
        record = AssetRecord(
            date=date(2026, 2, 11),
            product="テスト商品",
            asset_valuation=100_000,
            cumulative_contributions=80_000,
            gains_or_losses=20_000,
        )

        assert record.date == date(2026, 2, 11)
        assert record.product == "テスト商品"
        assert record.asset_valuation == 100_000
        assert record.cumulative_contributions == 80_000
        assert record.gains_or_losses == 20_000


class TestFromDcpAssetProducts:
    def test_from_dcp_asset_products__single_product(self):
        """単一商品から AssetRecord リストを生成できる"""
        products = {
            "商品A": DcpAssetInfo(
                cumulative_contributions=100_000,
                gains_or_losses=10_000,
                asset_valuation=110_000,
            ),
        }

        records = AssetRecord.from_dcp_asset_products(
            target_date=date(2026, 2, 11),
            products=products,
        )

        assert len(records) == 1
        assert records[0].date == date(2026, 2, 11)
        assert records[0].product == "商品A"
        assert records[0].asset_valuation == 110_000
        assert records[0].cumulative_contributions == 100_000
        assert records[0].gains_or_losses == 10_000

    def test_from_dcp_asset_products__multiple_products(self):
        """複数商品から AssetRecord リストを生成できる"""
        products = {
            "商品A": DcpAssetInfo(
                cumulative_contributions=100_000,
                gains_or_losses=10_000,
                asset_valuation=110_000,
            ),
            "商品B": DcpAssetInfo(
                cumulative_contributions=200_000,
                gains_or_losses=20_000,
                asset_valuation=220_000,
            ),
            "商品C": DcpAssetInfo(
                cumulative_contributions=300_000,
                gains_or_losses=-5_000,
                asset_valuation=295_000,
            ),
        }

        records = AssetRecord.from_dcp_asset_products(
            target_date=date(2026, 1, 15),
            products=products,
        )

        assert len(records) == 3
        product_names = {r.product for r in records}
        assert product_names == {"商品A", "商品B", "商品C"}

        # 全レコードが同一日付を持つ
        assert all(r.date == date(2026, 1, 15) for r in records)

    def test_from_dcp_asset_products__empty_products(self):
        """空の商品辞書から空リストが返される"""
        records = AssetRecord.from_dcp_asset_products(
            target_date=date(2026, 2, 11),
            products={},
        )

        assert records == []
