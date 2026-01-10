"""エラーメッセージのフォーマット"""

from src.domain import ErrorLogRecord


class MessageFormatter:
    """エラーメッセージフォーマッター"""

    def format_error_message(
        self,
        error_records: list[ErrorLogRecord],
        log_group: str,
        log_stream: str,
    ) -> str:
        """エラーメッセージをフォーマット

        Args:
            error_records: エラーログレコードリスト
            log_group: CloudWatch Logs ロググループ名
            log_stream: CloudWatch Logs ログストリーム名

        Returns:
            str: フォーマットされたメッセージ
        """
        if not error_records:
            return "エラーログがありませんでした。"

        # ヘッダー
        lines = [f"🚨 エラー通知 ({len(error_records)}件)"]
        lines.append("")

        # 各エラーレコード
        for i, record in enumerate(error_records, 1):
            jst_time = record.get_jst_timestamp()
            timestamp_str = jst_time.strftime("%Y-%m-%d %H:%M:%S")

            lines.append(f"【エラー {i}】")
            lines.append(f"時刻: {timestamp_str} (JST)")
            lines.append(f"サービス: {record.service}")
            lines.append(f"場所: {record.location}")
            lines.append(f"メッセージ: {record.message}")

            if record.exception_name:
                lines.append(f"例外: {record.exception_name}")

            if record.error_file_key:
                lines.append(f"ファイル: {record.error_file_key}")

            lines.append("")

        # CloudWatch Logs リンク
        cloudwatch_url = self._generate_cloudwatch_logs_url(log_group, log_stream)
        lines.append(f"📊 CloudWatch Logs: {cloudwatch_url}")

        return "\n".join(lines)

    def _generate_cloudwatch_logs_url(self, log_group: str, log_stream: str) -> str:
        """CloudWatch Logs URL を生成

        Args:
            log_group: ロググループ名
            log_stream: ログストリーム名

        Returns:
            str: CloudWatch Logs URL
        """
        region = "ap-northeast-1"
        # URL エンコードが必要な文字列は urllib.parse.quote で処理
        from urllib.parse import quote

        log_group_encoded = quote(log_group, safe="")
        log_stream_encoded = quote(log_stream, safe="")

        url = (
            f"https://{region}.console.aws.amazon.com/cloudwatch/home?"
            f"region={region}#logsV2:log-groups/log-group/{log_group_encoded}/"
            f"log-events/{log_stream_encoded}"
        )

        return url
