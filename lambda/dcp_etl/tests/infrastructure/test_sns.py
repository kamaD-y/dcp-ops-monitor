import pytest
from testcontainers.localstack import LocalStackContainer


topic_name = "test-topic"
topic_arn = ""


@pytest.fixture(scope="module", autouse=True)
def setup(local_stack_container: LocalStackContainer) -> None:
    global topic_arn

    client = local_stack_container.get_client("sns", region_name="ap-northeast-1")
    topic_arn = client.create_topic(Name=topic_name)["TopicArn"]


def test_publish() -> None:
    """SNSトピックにメッセージを発行するテスト"""
    from src.infrastructure.aws import sns

    try:
        # when
        sns.publish(
            topic_arn=topic_arn,
            message="Test message",
            subject="Test Subject",
        )

        # then
        assert True
    except Exception as e:
        pytest.fail(f"Failed to publish message: {e}")