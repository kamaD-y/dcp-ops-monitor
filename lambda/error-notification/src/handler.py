from aws_lambda_powertools.utilities.data_classes import CloudWatchLogsEvent, event_source
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.application.notification import send
from src.settings import get_logger

logger = get_logger()


@event_source(data_class=CloudWatchLogsEvent)
@logger.inject_lambda_context
def handler(event: CloudWatchLogsEvent, context: LambdaContext) -> str:
    """Lambda handler エントリーポイント"""
    logger.info("Received CloudWatch Logs event", event=event)
    for log_event in event.parse_logs_data().log_events:
        logger.info("Received CloudWatch Logs message", record=log_event)
        # send(log_event)
        logger.info("Processed CloudWatch Logs message successfully", record=log_event)
    return "Success"
