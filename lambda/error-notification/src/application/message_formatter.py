"""エラーメッセージのフォーマット"""

from src.domain import LogsEventData


def format_error_message(logs_event_data: LogsEventData) -> str:
    """エラーメッセージをフォーマット

    Args:
        logs_event_data: ログイベントデータ

    Returns:
        str: フォーマットされたメッセージ
    """
    error_records = logs_event_data.error_records

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

    # CloudWatch Logs リンク（URLが存在する場合のみ）
    if logs_event_data.logs_url:
        lines.append(f"📊 CloudWatch Logs: {logs_event_data.logs_url}")

    return "\n".join(lines)
