from aws_lambda_powertools.utilities.typing import LambdaContext

from src.config.settings import get_logger
from src.domain import ArtifactUploadError, ScrapingFailed
from src.presentation.asset_collection_handler import main

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
            extra={
                "error_screenshot_key": e.error_screenshot_key,
                "error_html_key": e.error_html_key,
            },
        )
        raise
    except ArtifactUploadError:
        logger.exception("資産情報の保存に失敗しました。")
        raise
    except Exception:
        logger.exception("予期せぬエラーが発生しました。")
        raise
