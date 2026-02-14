"""サマリ通知メッセージのフォーマット"""

from src.domain import DcpAssetInfo, DcpOpsIndicators


def format_summary_message(total: DcpAssetInfo, indicators: DcpOpsIndicators) -> str:
    """資産情報と運用指標からサマリメッセージをフォーマット

    Args:
        total: 全商品合計の資産情報
        indicators: 運用指標

    Returns:
        str: フォーマットされたメッセージ
    """
    message = "確定拠出年金 運用状況通知Bot\n\n"

    message += "総評価\n"
    message += f"拠出金額累計: {total.cumulative_contributions:,}円\n"
    message += f"評価損益: {total.gains_or_losses:,}円\n"
    message += f"資産評価額: {total.asset_valuation:,}円\n"
    message += "\n"

    message += f"運用年数: {indicators.operation_years}年\n"
    message += f"運用利回り: {indicators.actual_yield_rate}\n"
    message += f"目標利回り: {indicators.expected_yield_rate}\n"
    message += f"想定受取額(60歳): {indicators.total_amount_at_60age:,}円\n"
    message += "\n"

    return message
