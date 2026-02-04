"""Lambda handler エントリーポイント"""

from aws_lambda_powertools.utilities.typing import LambdaContext

from src.config.settings import get_logger
from src.domain import SummaryNotificationFailed
from src.presentation import main

logger = get_logger()


@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext) -> str | None:
    """Lambda handler エントリーポイント

    Args:
        event: Lambda イベント（EventBridge から空の dict）
        context: Lambda コンテキスト

    Returns:
        str | None: 成功時は "Success"
    """
    try:
        main()
        return "Success"
    except SummaryNotificationFailed:
        logger.exception("サマリ通知処理に失敗しました")
        raise
    except Exception:
        logger.exception("予期せぬエラーが発生しました")
        raise
