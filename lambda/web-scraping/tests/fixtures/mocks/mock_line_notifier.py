from typing import List

from src.domain import DcpAssets, DcpOpsIndicators, INotifier


class MockLineNotifier(INotifier):
    """LINE通知クラスのMock実装（E2Eテスト用）

    実際にAPIを呼び出さず、メソッド呼び出しを記録するMockオブジェクト
    """

    def __init__(self, url: str = "", token: str = "") -> None:
        """コンストラクタ

        Args:
            url (str): LINE Message API URL（使用しない）
            token (str): LINE Message API トークン（使用しない）
        """
        self.url = url
        self.token = token
        self.sent_messages: List[str] = []
        self.call_count = 0

    def send(self, message: str) -> bool:
        """メッセージ送信をシミュレート（実際には送信しない）

        Args:
            message (str): 送信するメッセージ

        Returns:
            bool: 常にTrue
        """
        self.sent_messages.append(message)
        self.call_count += 1
        print(f"[Mock] LINE message recorded (call #{self.call_count}, message_length={len(message)})")
        return True

    def create_message_by(self, assets_info: DcpAssets, ops_indicators: DcpOpsIndicators) -> str:
        """資産情報と運用指標からメッセージを生成（実装と同じロジック）

        Args:
            assets_info (DcpAssets): 資産情報
            ops_indicators (DcpOpsIndicators): 運用指標

        Returns:
            str: 生成されたメッセージ
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

    def get_last_sent_message(self) -> str:
        """最後に送信したメッセージを取得

        Returns:
            str: 最後に送信したメッセージ（送信履歴がない場合は空文字列）
        """
        return self.sent_messages[-1] if self.sent_messages else ""

    def get_all_sent_messages(self) -> List[str]:
        """すべての送信メッセージを取得

        Returns:
            List[str]: 送信メッセージのリスト
        """
        return self.sent_messages.copy()

    def reset(self) -> None:
        """Mock状態をリセット"""
        self.sent_messages = []
        self.call_count = 0
