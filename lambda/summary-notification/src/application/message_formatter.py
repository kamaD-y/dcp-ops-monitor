"""サマリ通知メッセージのフォーマット"""

from src.domain import DcpAssets, DcpOpsIndicators


def format_summary_message(assets: DcpAssets, indicators: DcpOpsIndicators) -> str:
    """資産情報と運用指標からサマリメッセージをフォーマット

    Args:
        assets: 資産情報
        indicators: 運用指標

    Returns:
        str: フォーマットされたメッセージ
    """
    message = "確定拠出年金 運用状況通知Bot\n\n"

    message += "総評価\n"
    message += f"拠出金額累計: {assets.total.cumulative_contributions:,}円\n"
    message += f"評価損益: {assets.total.gains_or_losses:,}円\n"
    message += f"資産評価額: {assets.total.asset_valuation:,}円\n"
    message += "\n"

    message += f"運用年数: {indicators.operation_years}年\n"
    message += f"運用利回り: {indicators.actual_yield_rate}\n"
    message += f"目標利回り: {indicators.expected_yield_rate}\n"
    message += f"想定受取額(60歳): {indicators.total_amount_at_60age:,}円\n"
    message += "\n"

    message += "商品別\n"
    for product_name, product_info in assets.products.items():
        message += f"{product_name}\n"
        message += f"取得価額累計: {product_info.cumulative_contributions:,}円\n"
        message += f"損益: {product_info.gains_or_losses:,}円\n"
        message += f"資産評価額: {product_info.asset_valuation:,}円\n"
        message += "\n"

    return message
