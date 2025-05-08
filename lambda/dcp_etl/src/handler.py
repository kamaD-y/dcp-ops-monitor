from application.dcp_ops import main
from aws_lambda_powertools.utilities.typing import LambdaContext
from settings.settings import get_logger

logger = get_logger()


@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext) -> str:
    """Lambda handler エントリーポイント"""
    try:
        main()
        return "Success"
    except Exception:
        raise
