"""CloudWatch Logs パーサーインターフェース"""

from abc import ABC, abstractmethod

from aws_lambda_powertools.utilities.data_classes import CloudWatchLogsEvent

from .parsed_cloudwatch_logs_data import ParsedCloudWatchLogsData


class ICloudWatchLogsParser(ABC):
    """CloudWatch Logs パーサーインターフェース"""

    @abstractmethod
    def parse(self, event: CloudWatchLogsEvent) -> ParsedCloudWatchLogsData:
        """CloudWatch Logs イベントをパース

        Args:
            event: AWS Lambda Powertools の CloudWatchLogsEvent

        Returns:
            ParsedCloudWatchLogsData: パース済みデータ (エラーレコード + メタデータ)

        Raises:
            CloudWatchLogsParseError: パース失敗時
        """
        pass
