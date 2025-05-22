import os

import boto3
from settings.settings import get_logger

logger = get_logger()

if os.environ.get("ENV") == "test":
    client = boto3.client("sns", region_name="ap-northeast-1", endpoint_url=os.environ["LOCAL_STACK_CONTAINER_URL"])
else:
    client = boto3.client("sns", region_name="ap-northeast-1")


def publish(topic_arn: str, message: str, subject: str) -> None:
    """SNSトピックにメッセージを公開する

    Args:
        topic_arn (str): SNSトピックのARN
        message (str): 公開するメッセージ
        subject (str): メッセージの件名

    Returns:
        None
    """
    try:
        response = client.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=subject,
        )
        logger.info(f"Message sent to topic {topic_arn}", response=response)
    except Exception:
        logger.error(f"Failed to send message to topic {topic_arn}", exc_info=True)
        raise
