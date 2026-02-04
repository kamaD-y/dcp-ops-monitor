"""SSM Parameter Store からパラメータを取得"""

import json
import os
from typing import Any

import boto3


def _get_client():
    """SSM クライアントを取得（遅延初期化）"""
    if os.environ.get("ENV") in ["local", "test"]:
        return boto3.client("ssm", region_name="ap-northeast-1", endpoint_url=os.environ["LOCAL_STACK_CONTAINER_URL"])
    return boto3.client("ssm", region_name="ap-northeast-1")


def get_ssm_json_parameter(name: str, decrypt: bool = True) -> dict[str, Any]:  # noqa: FBT001, FBT002
    """SSM Parameter Store から JSON パラメータを取得

    Args:
        name: パラメータ名
        decrypt: 復号化するかどうか (デフォルト: True)

    Returns:
        dict[str, Any]: JSON パラメータの辞書
    """
    client = _get_client()
    response = client.get_parameter(Name=name, WithDecryption=decrypt)
    parameters_json = response["Parameter"]["Value"]
    return json.loads(parameters_json)
