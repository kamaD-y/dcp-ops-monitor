from aws_lambda_powertools.utilities.data_classes import SNSEvent, event_source
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.application.dcp_ops_app import main
from src.settings.settings import get_logger

logger = get_logger()


@event_source(data_class=SNSEvent)
@logger.inject_lambda_context
def handler(event: SNSEvent, context: LambdaContext) -> str:
    """Lambda handler エントリーポイント"""
    for record in event.records:
        main(record.sns.message)
    return "Success"
