"""CloudWatch Logs アダプター"""

import json

from aws_lambda_powertools.utilities.data_classes import CloudWatchLogsEvent

from src.config.settings import get_logger
from src.domain import ErrorLogRecord, LogsEventData, LogsParseError

logger = get_logger()


class CloudWatchLogsAdapter:
    """CloudWatch Logs イベントをドメインモデルに変換するアダプター

    AWS固有の CloudWatchLogsEvent 型をドメイン独自の LogsEventData に変換し、
    ドメイン層への技術詳細の侵入を防ぐ
    """

    def convert(self, event: CloudWatchLogsEvent) -> LogsEventData:
        """CloudWatchLogsEvent を LogsEventData に変換

        Args:
            event: CloudWatch Logs イベント

        Returns:
            LogsEventData: ドメインモデル

        Raises:
            LogsParseError: イベントのパースに失敗した場合
        """
        try:
            # CloudWatch Logs イベントをデコード
            decoded_data = event.parse_logs_data()

            # ERROR レベルのログのみ抽出
            error_records = []
            for log_event in decoded_data.log_events:
                try:
                    log_data = json.loads(log_event.message)
                    if log_data.get("level") == "ERROR":
                        error_records.append(ErrorLogRecord(**log_data))
                except (json.JSONDecodeError, TypeError, ValueError) as e:
                    logger.warning(f"ログメッセージのパースに失敗しました: {e}")
                    continue

            # LogsEventData を生成
            return LogsEventData(
                error_records=error_records,
                log_group=decoded_data.log_group,
                log_stream=decoded_data.log_stream,
            )

        except Exception as e:
            msg = f"CloudWatch Logs イベントの変換に失敗しました: {e}"
            raise LogsParseError(msg) from e
