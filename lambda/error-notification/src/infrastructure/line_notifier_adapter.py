"""LINE 通知アダプター"""

from src.config.settings import get_logger
from src.domain import INotifier, NotificationError, NotificationMessage

from .line_notifier import LineNotifier

logger = get_logger()


class LineNotifierAdapter(INotifier):
    """LINE 通知アダプター

    汎用的な NotificationMessage を LINE 固有のメッセージ形式に変換
    """

    def __init__(self, url: str, token: str) -> None:
        """LINE 通知アダプターを初期化

        Args:
            url: LINE Messaging API URL
            token: LINE アクセストークン
        """
        self.line_notifier = LineNotifier(url=url, token=token)

    def notify(self, messages: list[NotificationMessage]) -> None:
        """通知を送信

        Args:
            messages: 通知メッセージリスト

        Raises:
            NotificationError: 通知送信失敗時
        """
        try:
            # NotificationMessage を LINE メッセージ形式に変換
            line_messages = self._convert_to_line_format(messages)
            # LINE API 経由で送信
            self.line_notifier.send_messages(line_messages)
        except Exception as e:
            msg = f"通知の送信に失敗しました: {e}"
            raise NotificationError(msg) from e

    def _convert_to_line_format(self, messages: list[NotificationMessage]) -> list[dict]:
        """NotificationMessage を LINE メッセージ形式に変換

        Args:
            messages: 通知メッセージリスト

        Returns:
            list[dict]: LINE メッセージ形式のリスト
        """
        result = []
        for msg in messages:
            # テキストメッセージを追加
            result.append({"type": "text", "text": msg.text})

            # 画像URLがあれば画像メッセージを追加
            if msg.image_url:
                result.append(
                    {
                        "type": "image",
                        "originalContentUrl": msg.image_url,
                        "previewImageUrl": msg.image_url,
                    }
                )

        return result
