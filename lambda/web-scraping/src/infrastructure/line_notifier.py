import json

import requests

from config.settings import get_logger
from domain import DcpAssetsInfo, DcpOpsIndicators, INotifier

logger = get_logger()


class LineNotifierError(Exception):
    pass


class LineNotifier(INotifier):
    """LINE通知クラス"""

    def __init__(self, url: str, token: str):
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        }

    def send(self, message: str) -> bool:
        messages = [{"type": "text", "text": message}]
        payload = {"messages": messages}
        try:
            r = requests.post(self.url, headers=self.headers, data=json.dumps(payload))
            r.raise_for_status()
            logger.info("LINE message api send success", result=r)
            return True
        except Exception as e:
            raise LineNotifierError("LINE message api send failed") from e

    def create_message_by(self, assets_info: DcpAssetsInfo, ops_indicators: DcpOpsIndicators) -> str:
        message = "確定拠出年金 運用状況通知Bot\n\n"
        message += "総評価\n"
        message += f"拠出金額累計: {assets_info.total.cumulative_contributions}\n"
        message += f"評価損益: {assets_info.total.total_gains_or_losses}\n"
        message += f"資産評価額: {assets_info.total.total_asset_valuation}\n"
        message += "\n"
        message += f"運用年数: {ops_indicators.operation_years}年\n"
        message += f"運用利回り: {ops_indicators.actual_yield_rate}\n"
        message += "目標利回り: 0.06\n"
        message += f"想定受取額(60歳): {ops_indicators.total_amount_at_60age}\n"
        message += "\n"

        message += "商品別\n"
        for p_name, p_v in assets_info.products.items():
            message += f"{p_name}\n"
            message += f"取得価額累計: {p_v.cumulative_acquisition_costs}\n"
            message += f"損益: {p_v.gains_or_losses}\n"
            message += f"資産評価額: {p_v.asset_valuation}\n"
            message += "\n"

        return message
