import boto3
from settings.settings import get_logger

from .get_client import get_client

logger = get_logger()


def publish(topic_arn: str, message: str, subject: str, client: boto3.client = None) -> None:
    """SNSトピックにメッセージを公開する

    Args:
        topic_arn (str): SNSトピックのARN
        message (str): 公開するメッセージ
        subject (str): メッセージの件名

    Returns:
        None
    """
    if not client:
        client = get_client("sns")

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
