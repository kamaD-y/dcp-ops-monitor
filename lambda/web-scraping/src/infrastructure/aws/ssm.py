import json
import os
from typing import Any, Dict

import boto3

from config.settings import get_logger

logger = get_logger()

if os.environ.get("ENV") == "test":
    client = boto3.client("ssm", region_name="ap-northeast-1", endpoint_url=os.environ["LOCAL_STACK_CONTAINER_URL"])
else:
    client = boto3.client("ssm", region_name="ap-northeast-1")


def get_parameter(parameter_name: str) -> Dict[str, Any]:
    """Parameter Storeから設定を読み込む

    Args:
        parameter_name (str): Parameter Storeのパラメータ名

    Returns:
        Dict[str, Any]: 読み込んだパラメータ、失敗時は空辞書
    """
    try:
        response = client.get_parameter(Name=parameter_name, WithDecryption=True)
        logger.info(f"Successfully retrieved parameter {parameter_name}", response=response)
        parameters_json = response["Parameter"]["Value"]
        return json.loads(parameters_json)
    except Exception:
        # エラーログ記録などが必要な場合はここで行う
        logger.error(f"Failed to get parameter {parameter_name}", exc_info=True)
        return {}
