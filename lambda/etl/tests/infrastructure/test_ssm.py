import pytest
from testcontainers.localstack import LocalStackContainer


parameter_name = "/test/parameter"
parameter_value = '{"LOGIN_USER_ID": "test-user", "LOGIN_PASSWORD": "test-password", "LOGIN_BIRTHDATE": "19800101"}'


@pytest.fixture(scope="module", autouse=True)
def setup(local_stack_container: LocalStackContainer) -> None:
    client = local_stack_container.get_client("ssm")
    client.put_parameter(
        Name=parameter_name,
        Value=parameter_value,
        Type="String",
        Overwrite=True
    )


def test_get_parameter() -> None:
    """SSMパラメータストアからパラメータを取得するテスト"""
    from src.infrastructure.aws import ssm
    try:
        # when
        parameters = ssm.get_parameter(parameter_name)
        
        # then
        assert parameters is not None
        assert "LOGIN_USER_ID" in parameters
        assert parameters["LOGIN_USER_ID"] == "test-user"
        assert "LOGIN_PASSWORD" in parameters
        assert parameters["LOGIN_PASSWORD"] == "test-password"
        assert "LOGIN_BIRTHDATE" in parameters
        assert parameters["LOGIN_BIRTHDATE"] == "19800101"
    except Exception as e:
        pytest.fail(f"Failed to get parameter: {e}")
