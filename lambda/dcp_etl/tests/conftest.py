import os
import pytest
from testcontainers.localstack import LocalStackContainer


@pytest.fixture(scope="package", autouse=True)
def local_stack_container() -> LocalStackContainer:
    """LocalStackのコンテナを起動する

    Returns:
        LocalStackContainer: LocalStackのコンテナ
    """
    with LocalStackContainer(region_name="ap-northeast-1") as container:
        os.environ["LOCAL_STACK_CONTAINER_URL"] = container.get_url()
        yield container
        print("Cleaning up LocalStack container...")


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
