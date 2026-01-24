"""CloudWatch Logs アダプター"""

import json
from urllib.parse import quote

from aws_lambda_powertools.utilities.data_classes import CloudWatchLogsEvent

from src.config.settings import get_logger
from src.domain import ErrorLogEvents, ErrorRecord, IErrorLogEventsAdapter, LogsParseFailed

logger = get_logger()


class CloudWatchLogsAdapter(IErrorLogEventsAdapter):
    """CloudWatch Logs イベントをドメインモデルに変換するアダプター

    AWS固有の CloudWatchLogsEvent 型をドメイン独自の ErrorLogEvents に変換し、
    ドメイン層への技術詳細の侵入を防ぐ
    """

    REGION = "ap-northeast-1"  # CloudWatch Logs リージョン（定数）

    def convert(self, raw_event: CloudWatchLogsEvent) -> ErrorLogEvents:
        """CloudWatchLogsEvent を ErrorLogEvents に変換

        Args:
            raw_event: CloudWatchLogsEvent（CloudWatch Logs イベント）

        Returns:
            ErrorLogEvents: エラーログイベントデータ

        Raises:
            LogsParseFailed: イベントのパースに失敗した場合
        """
        try:
            decoded_data = raw_event.parse_logs_data()

            error_records: list[ErrorRecord] = []
            for log_event in decoded_data.log_events:
                log_data = json.loads(log_event.message)
                if log_data.get("level") == "ERROR":
                    error_records.append(ErrorRecord(**log_data))

        except Exception as e:
            raise LogsParseFailed() from e

        logs_url = None
        try:
            logs_url = self.generate_logs_url(
                decoded_data.log_group,
                decoded_data.log_stream,
            )
        except Exception as e:
            # URL生成に失敗しても処理継続
            logger.warning("CloudWatch Logs URL の生成に失敗しました", error=str(e))

        return ErrorLogEvents(
            error_records=error_records,
            logs_url=logs_url,
        )

    def generate_logs_url(self, log_group: str, log_stream: str) -> str:
        """CloudWatch Logs コンソールURLを生成

        Args:
            log_group: ロググループ名
            log_stream: ログストリーム名

        Returns:
            str: CloudWatch Logs URL
        """
        log_group_encoded = quote(log_group, safe="")
        log_stream_encoded = quote(log_stream, safe="")

        url = (
            f"https://{self.REGION}.console.aws.amazon.com/cloudwatch/home?"
            f"region={self.REGION}#logsV2:log-groups/log-group/{log_group_encoded}/"
            f"log-events/{log_stream_encoded}"
        )

        return url
