"""エラーメッセージのフォーマット"""

from src.domain import ErrorLogEvents


def format_error_message(error_log_events: ErrorLogEvents) -> str:
    """エラーメッセージをフォーマット

    Args:
        error_log_events: エラーログイベントデータ

    Returns:
        str: フォーマットされたメッセージ
    """
    error_records = error_log_events.error_records

    if not error_records:
        return "エラーログがありませんでした。"

    # ヘッダー
    lines = [f"🚨 エラー通知 ({len(error_records)}件)"]
    lines.append("")

    # 各エラーレコード
    for i, record in enumerate(error_records, 1):
        timestamp_str = record.jst_timestamp.strftime("%Y-%m-%d %H:%M:%S")

        lines.append(f"【エラー {i}】")
        lines.append(f"時刻: {timestamp_str} (JST)")
        lines.append(f"サービス: {record.service}")
        lines.append(f"場所: {record.location}")
        lines.append(f"メッセージ: {record.message}")

        if record.exception_name:
            lines.append(f"例外: {record.exception_name}")

        if record.error_screenshot_key:
            lines.append(f"スクリーンショット: {record.error_screenshot_key}")

        if record.error_html_key:
            lines.append(f"HTML: {record.error_html_key}")

        lines.append("")

    # CloudWatch Logs リンク（URLが存在する場合のみ）
    if error_log_events.logs_url:
        lines.append(f"📊 CloudWatch Logs: {error_log_events.logs_url}")

    return "\n".join(lines)
