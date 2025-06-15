import json

import requests

from src.domain.interface import Notification, NotificationError
from src.settings.settings import get_logger

logger = get_logger()


class LineNotification(Notification):
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
            raise NotificationError("LINE message api send failed") from e
