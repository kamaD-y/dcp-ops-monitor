import pytest
import requests_mock as rm

from src.domain import NotificationFailed, NotificationMessage
from src.infrastructure import LineNotifier

LINE_API_URL = "https://api.line.me/v2/bot/message/push"
LINE_TOKEN = "test-token"


@pytest.fixture
def notifier() -> LineNotifier:
    """テスト用 LINE 通知アダプター"""
    return LineNotifier(url=LINE_API_URL, token=LINE_TOKEN)


class TestLineNotifier:
    def test_notify__sends_text_message(self, notifier, requests_mock):
        """テキストメッセージを正常に送信できる"""
        # given
        requests_mock.post(LINE_API_URL, json={}, status_code=200)
        messages = [NotificationMessage(text="テストメッセージ")]

        # when
        notifier.notify(messages)

        # then
        assert requests_mock.called
        sent_body = requests_mock.last_request.json()
        assert len(sent_body["messages"]) == 1
        assert sent_body["messages"][0]["type"] == "text"
        assert sent_body["messages"][0]["text"] == "テストメッセージ"

    def test_notify__sends_text_with_image(self, notifier, requests_mock):
        """テキスト + 画像メッセージを送信できる"""
        # given
        requests_mock.post(LINE_API_URL, json={}, status_code=200)
        messages = [NotificationMessage(text="テスト", image_url="https://example.com/image.png")]

        # when
        notifier.notify(messages)

        # then
        sent_body = requests_mock.last_request.json()
        assert len(sent_body["messages"]) == 2
        assert sent_body["messages"][0]["type"] == "text"
        assert sent_body["messages"][1]["type"] == "image"
        assert sent_body["messages"][1]["originalContentUrl"] == "https://example.com/image.png"

    def test_notify__api_error_raises_notification_failed(self, notifier, requests_mock):
        """API エラー時に NotificationFailed が発生する"""
        # given
        requests_mock.post(LINE_API_URL, status_code=500)
        messages = [NotificationMessage(text="テスト")]

        # when, then
        with pytest.raises(NotificationFailed):
            notifier.notify(messages)

    def test_notify__authorization_header(self, notifier, requests_mock):
        """Authorization ヘッダーが正しく設定される"""
        # given
        requests_mock.post(LINE_API_URL, json={}, status_code=200)
        messages = [NotificationMessage(text="テスト")]

        # when
        notifier.notify(messages)

        # then
        auth_header = requests_mock.last_request.headers["Authorization"]
        assert auth_header == f"Bearer {LINE_TOKEN}"
