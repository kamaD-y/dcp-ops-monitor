import json
import os
from typing import Any, Dict

import boto3

if os.environ.get("ENV") == "test":
    client = boto3.client("ssm", region_name="ap-northeast-1", endpoint_url=os.environ["LOCAL_STACK_CONTAINER_URL"])
else:
    client = boto3.client("ssm", region_name="ap-northeast-1")


def get_ssm_json_parameter(name: str, decrypt: bool = True) -> Dict[str, Any]:
    response = client.get_parameter(Name=name, WithDecryption=decrypt)
    parameters_json = response["Parameter"]["Value"]
    return json.loads(parameters_json)


def get_ssm_parameter(name: str, decrypt: bool = True) -> str:
    response = client.get_parameter(Name=name, WithDecryption=decrypt)
    return response["Parameter"]["Value"]
