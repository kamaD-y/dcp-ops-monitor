import pytest
import boto3
from src.infrastructure.aws import ssm
from testcontainers.localstack import LocalStackContainer


parameter_name = "/test/parameter"
parameter_value = '{"USER_ID": "test-user", "PASSWORD": "test-password", "BIRTHDATE": "19800101"}'
parameter_arn = ""
endpoint_url = ""


@pytest.fixture(scope="module", autouse=True)
def setup() -> LocalStackContainer:
    """LocalStackのコンテナを起動し、SSMクライアントを取得する。
    パラメータを一つ作成し、テスト終了後にクリーンアップする。

    Returns:
        LocalStackContainer: LocalStackのコンテナ
    """
    global endpoint_url, parameter_arn

    with LocalStackContainer() as container:
        endpoint_url = container.get_url()
        client = container.get_client("ssm")
        client.put_parameter(
            Name=parameter_name,
            Value=parameter_value,
            Type="String",
            Overwrite=True
        )
        parameter_arn = f"arn:aws:ssm:{container.region_name}:000000000000:parameter{parameter_name}"
        yield container
        print("Cleaning up LocalStack container...")


@pytest.fixture(scope="module")
def ssm_client() -> boto3.client:
    """SSMクライアントを取得する。

    Returns:
        boto3.client: SSMクライアント
    """
    return ssm.get_client("ssm", endpoint_url=endpoint_url)


def test_get_parameter(ssm_client: boto3.client) -> None:
    """SSMパラメータストアからパラメータを取得するテスト"""
    try:
        # when
        parameters = ssm.get_parameter(parameter_name, client=ssm_client)
        
        # then
        assert parameters is not None
        assert "USER_ID" in parameters
        assert parameters["USER_ID"] == "test-user"
        assert "PASSWORD" in parameters
        assert parameters["PASSWORD"] == "test-password"
        assert "BIRTHDATE" in parameters
        assert parameters["BIRTHDATE"] == "19800101"
    except Exception as e:
        pytest.fail(f"Failed to get parameter: {e}")