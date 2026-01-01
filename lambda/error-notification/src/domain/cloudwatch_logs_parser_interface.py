"""CloudWatch Logs パーサーインターフェース"""

from abc import ABC, abstractmethod

from aws_lambda_powertools.utilities.data_classes import CloudWatchLogsEvent

from .error_log_record import ErrorLogRecord


class ICloudWatchLogsParser(ABC):
    """CloudWatch Logs パーサーインターフェース"""

    @abstractmethod
    def parse(self, event: CloudWatchLogsEvent) -> list[ErrorLogRecord]:
        """CloudWatch Logs イベントをパース

        Args:
            event: AWS Lambda Powertools の CloudWatchLogsEvent

        Returns:
            list[ErrorLogRecord]: パースされたエラーログレコードリスト

        Raises:
            CloudWatchLogsParseError: パース失敗時
        """
        pass
