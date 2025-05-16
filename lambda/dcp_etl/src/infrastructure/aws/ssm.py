import json
from typing import Any, Dict

import boto3
from settings.settings import get_logger

from .get_client import get_client

logger = get_logger()


def get_parameter(parameter_arn: str, client: boto3.client = None) -> Dict[str, Any]:
    """Parameter Storeから設定を読み込む

    Args:
        parameter_arn (str): Parameter StoreのARN

    Returns:
        Dict[str, Any]: 読み込んだパラメータ、失敗時は空辞書
    """
    if not client:
        client = get_client("s3")

    try:
        response = client.get_parameter(Name=parameter_arn)
        parameters_json = response["Parameter"]["Value"]
        return json.loads(parameters_json)
    except Exception:
        # エラーログ記録などが必要な場合はここで行う
        logger.error(f"Failed to get parameter {parameter_arn}", exc_info=True)
        return {}
