import json
from datetime import datetime, timedelta

from src.domain.factory import NotificationDestinationsFactory
from src.infrastructure.aws import logs


class FailureCase:
    def __init__(self) -> None:
        self.time_from_minutes = 5

    def process_message(self, message: str) -> None:
        """失敗メッセージを処理し、通知を送信する

        Args:
            message (str): CloudWatch Alarm で受信したエラーメッセージの文字列形式
        """
        try:
            message_dict = self._parse_message(message)
            error_message = self._fetch_error_logs_from_cloudwatch_alarms(message_dict)

            notifications = NotificationDestinationsFactory.create()
            notifications.notify(error_message)
        except Exception as e:
            raise RuntimeError("Failed to process failure message.") from e

    def _parse_message(self, message: str) -> dict:
        """文字列型のメッセージを辞書形式に変換する

        Args:
            message (str): JSON形式の文字列メッセージ

        Returns:
            dict: 変換後の辞書形式メッセージ
        """
        try:
            return json.loads(message)
        except json.decoder.JSONDecodeError as e:
            raise ValueError("Invalid message format. Expected a JSON string.") from e

    def _fetch_error_logs_from_cloudwatch_alarms(self, message_dict: dict) -> str:
        """CloudWatch Alarm で受信したエラーメッセージから CloudWatch Logs のエラーログを取得する

        Args:
            message_dict (dict): CloudWatch Alarm で受信したエラーメッセージの辞書形式

        Returns:
            str: エラーログ
        """
        metric_filters = logs.describe_metric_filters(
            message_dict["Trigger"]["MetricName"], message_dict["Trigger"]["Namespace"]
        )

        time_to = datetime.strptime(message_dict["StateChangeTime"][:19], "%Y-%m-%dT%H:%M:%S") + timedelta(minutes=1)
        timestamp_to = int(time_to.timestamp() * 1000)
        time_from = time_to - timedelta(minutes=self.time_from_minutes)
        timestamp_from = int(time_from.timestamp() * 1000)

        log_events = logs.filter_log_events(
            metric_filters["metricFilters"][0]["logGroupName"],
            metric_filters["metricFilters"][0]["filterPattern"],
            timestamp_from,
            timestamp_to,
        )
        return log_events["events"][0]["message"]


class SuccessCase:
    def __init__(self) -> None:
        pass

    def process_message(self, message: str) -> None:
        """成功メッセージを処理し、通知を送信する

        Args:
            message (str): SNS で受信した成功メッセージの文字列形式
        """
        try:
            notifications = NotificationDestinationsFactory.create()
            notifications.notify(message)
        except Exception as e:
            raise RuntimeError("Failed to process success message.") from e
