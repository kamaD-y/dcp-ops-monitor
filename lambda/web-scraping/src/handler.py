from aws_lambda_powertools.utilities.typing import LambdaContext

from config.settings import get_logger
from domain import AssetExtractionFailed, ScrapingFailed
from presentation.dcp_ops_notification import main

logger = get_logger()


@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext) -> str | None:
    """Lambda handler エントリーポイント"""
    try:
        main()
        return "Success"
    except ScrapingFailed as e:
        logger.exception(
            "スクレイピング処理でエラーが発生しました。",
            extra={"error_file_key": e.error_file_key},
        )
        raise
    except AssetExtractionFailed as e:
        logger.exception(
            "資産情報の抽出でエラーが発生しました。",
            extra={"error_file_key": e.error_file_key},
        )
        raise
    except Exception as e:
        logger.exception("予期せぬエラーが発生しました。")
        raise
