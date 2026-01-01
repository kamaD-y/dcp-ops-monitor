"""CloudWatch Logs パーサー実装"""

import json

from aws_lambda_powertools.utilities.data_classes import CloudWatchLogsEvent

from src.domain import CloudWatchLogsParseError, ErrorLogRecord, ICloudWatchLogsParser


class CloudWatchLogsParser(ICloudWatchLogsParser):
    """CloudWatch Logs パーサー実装"""

    def parse(self, event: CloudWatchLogsEvent) -> list[ErrorLogRecord]:
        """CloudWatch Logs イベントをパース

        Args:
            event: AWS Lambda Powertools の CloudWatchLogsEvent

        Returns:
            list[ErrorLogRecord]: パースされたエラーログレコードリスト

        Raises:
            CloudWatchLogsParseError: パース失敗時
        """
        try:
            # AWS Lambda Powertools の parse_logs_data() で自動デコード・解凍
            decoded_data = event.parse_logs_data()

            error_records: list[ErrorLogRecord] = []

            for log_event in decoded_data.log_events:
                try:
                    # JSON 文字列をパース
                    log_message = json.loads(log_event.message)

                    # ERROR レベルのログのみ抽出
                    if log_message.get("level") == "ERROR":
                        # Pydantic モデルで検証
                        error_record = ErrorLogRecord(**log_message)
                        error_records.append(error_record)

                except (json.JSONDecodeError, ValueError) as e:
                    msg = f"ログイベントのパースに失敗しました: {e}"
                    raise CloudWatchLogsParseError(msg) from e

            return error_records

        except Exception as e:
            if isinstance(e, CloudWatchLogsParseError):
                raise
            msg = f"CloudWatch Logs イベントの解析に失敗しました: {e}"
            raise CloudWatchLogsParseError(msg) from e
