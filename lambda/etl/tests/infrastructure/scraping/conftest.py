from pathlib import Path
import pytest


@pytest.fixture
def valid_assets_page() -> str:
    """テスト用の正常なHTMLファイルを読み込む"""
    with open(Path(__file__).parents[2] / "fixtures/html/valid_assets_page.html") as f:
        assets_page = f.read()
    return assets_page


@pytest.fixture
def invalid_assets_page() -> str:
    """テスト用の不正なHTMLファイルを読み込む"""
    with open(Path(__file__).parents[2] / "fixtures/html/invalid_assets_page.html") as f:
        assets_page = f.read()
    return assets_page
