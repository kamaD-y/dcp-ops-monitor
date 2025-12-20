from aws_lambda_powertools.utilities.typing import LambdaContext

from config.settings import get_logger
from presentation.dcp_ops_notification import main

logger = get_logger()


@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext) -> str:
    """Lambda handler エントリーポイント"""
    main()
    return "Success"
