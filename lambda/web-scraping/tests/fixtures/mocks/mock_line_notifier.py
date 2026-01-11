"""LINE 通知クラスの Mock 実装"""

from src.domain import INotifier, NotificationMessage


class MockLineNotifier(INotifier):
    """LINE 通知クラスの Mock 実装（E2Eテスト用）

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
        self.sent_messages: list[NotificationMessage] = []
        self.call_count = 0

    def notify(self, messages: list[NotificationMessage]) -> None:
        """通知を送信（実際には送信せず記録のみ）

        Args:
            messages: 通知メッセージリスト
        """
        self.sent_messages.extend(messages)
        self.call_count += 1
        print(f"[Mock] LINE message recorded (call #{self.call_count}, messages={len(messages)})")

    def get_last_sent_message(self) -> NotificationMessage | None:
        """最後に送信したメッセージを取得

        Returns:
            NotificationMessage | None: 最後に送信したメッセージ（送信履歴がない場合は None）
        """
        return self.sent_messages[-1] if self.sent_messages else None

    def get_all_sent_messages(self) -> list[NotificationMessage]:
        """すべての送信メッセージを取得

        Returns:
            list[NotificationMessage]: 送信メッセージのリスト
        """
        return self.sent_messages.copy()

    def reset(self) -> None:
        """Mock状態をリセット"""
        self.sent_messages = []
        self.call_count = 0
