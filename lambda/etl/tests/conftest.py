import os
import pytest
from testcontainers.localstack import LocalStackContainer


bucket_name = "test-bucket"


@pytest.fixture(scope="package", autouse=True)
def local_stack_container() -> LocalStackContainer:
    """LocalStackのコンテナを起動する

    Returns:
        LocalStackContainer: LocalStackのコンテナ
    """
    with LocalStackContainer(region_name="ap-northeast-1") as container:
        os.environ["LOCAL_STACK_CONTAINER_URL"] = container.get_url()
        os.environ["AWS_ACCESS_KEY_ID"] = "dummy"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "dummy"
        yield container
        print("Cleaning up LocalStack container...")


@pytest.fixture(scope="package", autouse=True)
def create_test_bucket(local_stack_container: LocalStackContainer) -> None:
    os.environ["error_bucket_name"] = bucket_name
    client = local_stack_container.get_client("s3")
    client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": local_stack_container.region_name})


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


@pytest.fixture
def valid_assets_info():
    """テスト用のDcpAssetsInfoオブジェクトを生成する"""
    from src.domain.dcp_value_object import DcpAssetsInfo, DcpProductAssets, DcpTotalAssets
    return DcpAssetsInfo(
        total=DcpTotalAssets(
            cumulative_contributions="900,000円", total_gains_or_losses="300,000円", total_asset_valuation="1,200,000円"
        ),
        products={
            "プロダクト_1": DcpProductAssets(
                cumulative_acquisition_costs="100,000円", gains_or_losses="11,111円", asset_valuation="111,111円"
            ),
            "プロダクト_2": DcpProductAssets(
                cumulative_acquisition_costs="200,000円", gains_or_losses="22,222円", asset_valuation="222,222円"
            ),
        },
    )


@pytest.fixture(scope="module")
def put_login_parameter(local_stack_container: LocalStackContainer) -> None:
    parameter_name="/test/parameter"
    parameter_value = '{"LOGIN_USER_ID": "test-user", "LOGIN_PASSWORD": "test-password", "LOGIN_BIRTHDATE": "19800101"}'

    client = local_stack_container.get_client("ssm")
    client.put_parameter(
        Name=parameter_name,
        Value=parameter_value,
        Type="String",
        Overwrite=True
    )
