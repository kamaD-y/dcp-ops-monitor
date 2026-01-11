"""Lambda handler エントリーポイント"""

from aws_lambda_powertools.utilities.data_classes import CloudWatchLogsEvent, event_source
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.config.settings import get_logger
from src.domain import ErrorNotificationFailed
from src.presentation import main

logger = get_logger()


@event_source(data_class=CloudWatchLogsEvent)
@logger.inject_lambda_context
def handler(event: CloudWatchLogsEvent, context: LambdaContext) -> str | None:
    """Lambda handler エントリーポイント

    Args:
        event: CloudWatch Logs イベント
        context: Lambda コンテキスト

    Returns:
        str | None: 成功時は "Success"
    """
    try:
        main(event)
        return "Success"
    except ErrorNotificationFailed:
        logger.exception("エラー通知処理に失敗しました")
        raise
    except Exception:
        logger.exception("予期せぬエラーが発生しました")
        raise
