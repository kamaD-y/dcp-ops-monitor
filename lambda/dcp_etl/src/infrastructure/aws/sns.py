import boto3

from src.settings.settings import get_logger

logger = get_logger()
sns_client = boto3.client("sns", region_name="ap-northeast-1")


def publish(topic_arn: str, message: str, subject: str) -> None:
    """SNSトピックにメッセージを公開する"""
    try:
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=subject,
        )
        logger.info(f"Message sent to topic {topic_arn}", response=response)
    except Exception:
        logger.error(f"Failed to send message to topic {topic_arn}", exc_info=True)
        raise
