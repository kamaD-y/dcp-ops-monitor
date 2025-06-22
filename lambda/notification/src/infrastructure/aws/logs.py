import os

import boto3
from mypy_boto3_logs.type_defs import DescribeMetricFiltersResponseTypeDef, FilterLogEventsResponseTypeDef

from src.config.settings import get_logger

logger = get_logger()

if os.environ.get("ENV") == "test":
    client = boto3.client("logs", endpoint_url=os.environ["LOCAL_STACK_CONTAINER_URL"])
else:
    client = boto3.client("logs")


def describe_metric_filters(metric_name: str, metric_namespace: str) -> DescribeMetricFiltersResponseTypeDef:
    """CloudWatch Logsのメトリックフィルターを取得する

    Args:
        metric_name (str): メトリック名
        metric_namespace (str): メトリックの名前空間

    Returns:
        DescribeMetricFiltersResponseTypeDef: メトリックフィルターのレスポンス
    """
    try:
        response: DescribeMetricFiltersResponseTypeDef = client.describe_metric_filters(
            metricName=metric_name, metricNamespace=metric_namespace
        )
        logger.info(f"Metric filters for {metric_name} in {metric_namespace}.", response=response)
        if len(response["metricFilters"]) == 0:
            raise ValueError("No metric filters found matching the provided metric name and namespace.")
        return response
    except Exception as e:
        logger.exception(f"Failed to describe metric filters for {metric_name} in {metric_namespace}: {e}")
        raise


def filter_log_events(
    log_group_name: str, filter_pattern: str, start_time: int, end_time: int
) -> FilterLogEventsResponseTypeDef:
    """CloudWatch Logsのログイベントをフィルタリングする

    Args:
        log_group_name (str): ロググループ名
        filter_pattern (str): フィルターパターン
        start_time (int): 開始時間（UNIXタイムスタンプ）
        end_time (int): 終了時間（UNIXタイムスタンプ）

    Returns:
        FilterLogEventsResponseTypeDef: フィルタリングされたログイベントのレスポンス
    """
    try:
        response: FilterLogEventsResponseTypeDef = client.filter_log_events(
            logGroupName=log_group_name, filterPattern=filter_pattern, startTime=start_time, endTime=end_time, limit=1
        )
        logger.info(
            "Filtered log events.",
            log_group_name=log_group_name,
            filter_pattern=filter_pattern,
            start_time=start_time,
            end_time=end_time,
            response=response,
        )
        if len(response["events"]) == 0:
            raise ValueError("No log events found matching the provided filter pattern and time range.")
        return response
    except Exception as e:
        logger.exception(f"Failed to filter log events in {log_group_name}: {e}")
        raise
