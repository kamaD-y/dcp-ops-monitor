from aws_lambda_powertools.utilities.data_classes import SNSEvent, event_source
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.application.notification import send
from src.config.settings import get_logger

logger = get_logger()


@event_source(data_class=SNSEvent)
@logger.inject_lambda_context
def handler(event: SNSEvent, context: LambdaContext) -> str:
    """Lambda handler エントリーポイント"""
    for record in event.records:
        logger.info("Received SNS message", record=record)
        send(record.sns)
        logger.info("Processed SNS message successfully", record=record)
    return "Success"
