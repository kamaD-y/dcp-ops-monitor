import pytest
import boto3
from src.infrastructure.aws import sns
from testcontainers.localstack import LocalStackContainer


topic_name = "test-topic"
topic_arn = ""
endpoint_url = ""


@pytest.fixture(scope="module", autouse=True)
def setup() -> LocalStackContainer:
    """LocalStackのコンテナを起動し、SNSクライアントを取得する。
    トピックを一つ作成し、テスト終了後にクリーンアップする。

    Returns:
        LocalStackContainer: LocalStackのコンテナ
    """
    global endpoint_url, topic_arn

    with LocalStackContainer() as container:
        endpoint_url = container.get_url()
        client = container.get_client("sns")
        response = client.create_topic(Name=topic_name)
        topic_arn = response["TopicArn"]
        yield container
        print("Cleaning up LocalStack container...")


@pytest.fixture(scope="module")
def sns_client() -> boto3.client:
    """SNSクライアントを取得する。

    Returns:
        boto3.client: SNSクライアント
    """
    return sns.get_client("sns", endpoint_url=endpoint_url)


def test_publish(sns_client: boto3.client) -> None:
    """SNSトピックにメッセージを発行するテスト"""
    try:
        # when
        sns.publish(
            topic_arn=topic_arn,
            message="Test message",
            subject="Test Subject",
            client=sns_client
        )
        # then
        assert True
    except Exception as e:
        pytest.fail(f"Failed to publish message: {e}")