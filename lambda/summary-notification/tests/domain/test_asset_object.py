from src.domain import DcpAssetInfo, DcpAssets


class TestDcpAssetInfo:
    def test_create__valid_values(self):
        """正常な値で DcpAssetInfo を生成できる"""
        info = DcpAssetInfo(
            cumulative_contributions=900_000,
            gains_or_losses=300_000,
            asset_valuation=1_200_000,
        )
        assert info.cumulative_contributions == 900_000
        assert info.gains_or_losses == 300_000
        assert info.asset_valuation == 1_200_000

    def test_create__negative_gains_or_losses(self):
        """評価損益がマイナスの場合も生成できる"""
        info = DcpAssetInfo(
            cumulative_contributions=900_000,
            gains_or_losses=-100_000,
            asset_valuation=800_000,
        )
        assert info.gains_or_losses == -100_000


class TestDcpAssets:
    def test_create__with_products(self):
        """商品別資産情報を含む DcpAssets を生成できる"""
        assets = DcpAssets(
            products={
                "商品A": DcpAssetInfo(
                    cumulative_contributions=450_000,
                    gains_or_losses=150_000,
                    asset_valuation=600_000,
                ),
                "商品B": DcpAssetInfo(
                    cumulative_contributions=450_000,
                    gains_or_losses=150_000,
                    asset_valuation=600_000,
                ),
            },
        )
        assert len(assets.products) == 2
        assert "商品A" in assets.products
        assert "商品B" in assets.products

    def test_create__empty_products(self):
        """商品なしの DcpAssets を生成できる"""
        assets = DcpAssets(products={})
        assert len(assets.products) == 0

    def test_calculate_total__sums_all_products(self):
        """calculate_total で全商品の合計が算出される"""
        assets = DcpAssets(
            products={
                "商品A": DcpAssetInfo(
                    cumulative_contributions=450_000,
                    gains_or_losses=150_000,
                    asset_valuation=600_000,
                ),
                "商品B": DcpAssetInfo(
                    cumulative_contributions=450_000,
                    gains_or_losses=150_000,
                    asset_valuation=600_000,
                ),
            },
        )
        total = assets.calculate_total()
        assert total.cumulative_contributions == 900_000
        assert total.gains_or_losses == 300_000
        assert total.asset_valuation == 1_200_000

    def test_calculate_total__empty_products(self):
        """商品なしの場合 calculate_total は全て0を返す"""
        assets = DcpAssets(products={})
        total = assets.calculate_total()
        assert total.cumulative_contributions == 0
        assert total.gains_or_losses == 0
        assert total.asset_valuation == 0

    def test_serialization__json_round_trip(self):
        """JSON シリアライズ・デシリアライズが正常に動作する"""
        original = DcpAssets(
            products={
                "商品A": DcpAssetInfo(
                    cumulative_contributions=900_000,
                    gains_or_losses=300_000,
                    asset_valuation=1_200_000,
                ),
            },
        )
        json_str = original.model_dump_json()
        restored = DcpAssets.model_validate_json(json_str)
        assert restored == original
