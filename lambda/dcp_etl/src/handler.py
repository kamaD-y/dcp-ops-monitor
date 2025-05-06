from src.application.dcp_ops import main
from src.settings.settings import get_logger

logger = get_logger()


@logger.inject_lambda_context
def handler(event: dict = None, context=None) -> str:
    """Lambda handler エントリーポイント"""
    try:
        main()
        return "Success"
    except Exception:
        raise
