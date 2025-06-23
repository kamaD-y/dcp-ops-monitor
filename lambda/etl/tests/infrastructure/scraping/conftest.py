from datetime import datetime, timedelta

import pytest


@pytest.fixture
def valid_assets_page() -> str:
    """テスト用の正常なHTMLファイルを読み込む"""
    with open("tests/fixtures/html/valid_assets_page.html") as f:
        assets_page = f.read()
    return assets_page


@pytest.fixture
def invalid_assets_page() -> str:
    """テスト用の不正なHTMLファイルを読み込む"""
    with open("tests/fixtures/html/invalid_assets_page.html") as f:
        assets_page = f.read()
    return assets_page
