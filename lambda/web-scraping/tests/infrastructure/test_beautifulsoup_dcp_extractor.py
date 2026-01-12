from pathlib import Path

import pytest

from src.domain import AssetExtractionFailed
from src.infrastructure.beautifulsoup_dcp_extractor import BeautifulSoupDcpExtractor


class TestBeautifulSoupDcpExtractor:
    @pytest.fixture
    def extractor(self) -> BeautifulSoupDcpExtractor:
        """BeautifulSoupDcpExtractor のインスタンスを作成"""
        return BeautifulSoupDcpExtractor()

    @pytest.fixture
    def valid_assets_page(self) -> str:
        """有効な資産評価ページのHTMLを読み込む"""
        html_path = Path(__file__).parent.parent / "fixtures" / "html" / "valid_assets_page.html"
        return html_path.read_text()

    @pytest.fixture
    def invalid_assets_page(self) -> str:
        """無効な資産評価ページのHTMLを読み込む"""
        html_path = Path(__file__).parent.parent / "fixtures" / "html" / "invalid_assets_page.html"
        return html_path.read_text()

    def test_extract_success(self, extractor: BeautifulSoupDcpExtractor, valid_assets_page: str) -> None:
        """正常系: 有効なHTMLから正しく抽出できる"""
        result = extractor.extract(valid_assets_page)

        # 総評価額の検証
        assert result.total.cumulative_contributions == 900_000
        assert result.total.gains_or_losses == 300_000
        assert result.total.asset_valuation == 1_200_000

        # 商品別の検証
        assert "プロダクト_1" in result.products
        assert result.products["プロダクト_1"].cumulative_contributions == 100_000
        assert result.products["プロダクト_1"].gains_or_losses == 11_111
        assert result.products["プロダクト_1"].asset_valuation == 111_111

        assert "プロダクト_2" in result.products
        assert result.products["プロダクト_2"].cumulative_contributions == 200_000
        assert result.products["プロダクト_2"].gains_or_losses == 22_222
        assert result.products["プロダクト_2"].asset_valuation == 222_222

        assert "プロダクト_3" in result.products
        assert result.products["プロダクト_3"].cumulative_contributions == 300_000
        assert result.products["プロダクト_3"].gains_or_losses == 33_333
        assert result.products["プロダクト_3"].asset_valuation == 333_333

    def test_extract_failure_with_invalid_html(
        self, extractor: BeautifulSoupDcpExtractor, invalid_assets_page: str
    ) -> None:
        """異常系: 無効なHTMLでAssetExtractionFailedが発生"""
        with pytest.raises(AssetExtractionFailed) as exc_info:
            extractor.extract(invalid_assets_page)

        assert "資産情報の抽出に失敗しました" in str(exc_info.value)

    def test_extract_failure_with_empty_html(self, extractor: BeautifulSoupDcpExtractor) -> None:
        """異常系: 空のHTMLでAssetExtractionFailedが発生"""
        with pytest.raises(AssetExtractionFailed) as exc_info:
            extractor.extract("")

        assert "資産情報の抽出に失敗しました" in str(exc_info.value)

    def test_extract_with_custom_parser(self, valid_assets_page: str) -> None:
        """正常系: カスタムパーサーを指定できる"""
        extractor = BeautifulSoupDcpExtractor(parser="html.parser")
        result = extractor.extract(valid_assets_page)

        # 結果が正しく取得できることを確認
        assert result.total.asset_valuation == 1_200_000
