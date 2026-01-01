"""LINE 通知インターフェース"""

from abc import ABC, abstractmethod

from .line_message import LineMessage


class ILineNotifier(ABC):
    """LINE 通知インターフェース"""

    @abstractmethod
    def send_messages(self, messages: list[LineMessage]) -> None:
        """LINE メッセージを送信

        Args:
            messages: 送信するメッセージリスト

        Raises:
            LineNotificationError: 送信失敗時
        """
        pass

    @abstractmethod
    def upload_image_and_get_url(self, image_data: bytes) -> str:
        """画像をアップロードして URL を取得

        Args:
            image_data: 画像のバイトデータ

        Returns:
            str: アップロードされた画像の URL

        Raises:
            NotImplementedError: 初期実装では未実装
        """
        pass
