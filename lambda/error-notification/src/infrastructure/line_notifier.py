"""LINE 通知実装"""

import json

import requests

from src.config.settings import get_logger
from src.domain import ILineNotifier, LineMessage, LineNotificationError

logger = get_logger()


class LineNotifier(ILineNotifier):
    """LINE 通知実装"""

    def __init__(self, url: str, token: str) -> None:
        """LINE 通知クライアントを初期化

        Args:
            url: LINE Messaging API の URL
            token: LINE Messaging API のアクセストークン
        """
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

    def send_messages(self, messages: list[LineMessage]) -> None:
        """LINE メッセージを送信

        Args:
            messages: 送信するメッセージリスト

        Raises:
            LineNotificationError: 送信失敗時
        """
        try:
            # Pydantic モデルを辞書に変換
            message_dicts = [msg.model_dump() for msg in messages]
            payload = {"messages": message_dicts}

            response = requests.post(
                self.url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30,
            )
            response.raise_for_status()

            logger.info("LINE Message API への送信成功", response=response.text)

        except requests.exceptions.RequestException as e:
            msg = f"LINE Message API への送信失敗: {e}"
            raise LineNotificationError(msg) from e
