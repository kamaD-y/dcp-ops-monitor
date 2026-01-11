"""DCP運用状況メッセージのフォーマット"""

from domain import DcpAssets, DcpOpsIndicators


def format_dcp_ops_message(assets_info: DcpAssets, ops_indicators: DcpOpsIndicators) -> str:
    """DCP運用状況メッセージをフォーマット

    Args:
        assets_info: 資産情報
        ops_indicators: 運用指標

    Returns:
        str: フォーマットされたメッセージ
    """
    message = "確定拠出年金 運用状況通知Bot\n\n"
    message += "総評価\n"
    message += f"拠出金額累計: {assets_info.total.cumulative_contributions:,.0f}円\n"
    message += f"評価損益: {assets_info.total.gains_or_losses:,.0f}円\n"
    message += f"資産評価額: {assets_info.total.asset_valuation:,.0f}円\n"
    message += "\n"
    message += f"運用年数: {ops_indicators.operation_years}年\n"
    message += f"運用利回り: {ops_indicators.actual_yield_rate}\n"
    message += "目標利回り: 0.06\n"
    message += f"想定受取額(60歳): {ops_indicators.total_amount_at_60age:,.0f}円\n"
    message += "\n"

    message += "商品別\n"
    for p_name, p_v in assets_info.products.items():
        message += f"{p_name}\n"
        message += f"取得価額累計: {p_v.cumulative_contributions:,.0f}円\n"
        message += f"損益: {p_v.gains_or_losses:,.0f}円\n"
        message += f"資産評価額: {p_v.asset_valuation:,.0f}円\n"
        message += "\n"

    return message
