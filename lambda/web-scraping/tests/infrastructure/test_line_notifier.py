"""LineNotifier のテスト"""

import json

import pytest
import requests


class TestLineNotifierNotify:
    """LineNotifier の notify メソッドのテスト"""

    def test_notify__single_text_message(self, mocker):
        """単一のテキストメッセージを正しく送信できること"""
        # given
        from src.domain import NotificationMessage
        from src.infrastructure.line_notifier import LineNotifier

        url = "https://api.line.me/v2/bot/message/push"
        token = "test-token-12345"

        mock_post = mocker.patch("requests.post")
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = '{"status":"ok"}'
        mock_post.return_value = mock_response

        notifier = LineNotifier(url=url, token=token)
        messages = [NotificationMessage(text="テストメッセージ")]

        # when
        notifier.notify(messages)

        # then
        expected_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        expected_payload = {"messages": [{"type": "text", "text": "テストメッセージ"}]}

        mock_post.assert_called_once_with(
            url,
            headers=expected_headers,
            data=json.dumps(expected_payload),
            timeout=30,
        )

    def test_notify__single_message_with_image(self, mocker):
        """画像付きメッセージを正しく送信できること"""
        # given
        from src.domain import NotificationMessage
        from src.infrastructure.line_notifier import LineNotifier

        url = "https://api.line.me/v2/bot/message/push"
        token = "test-token-12345"

        mock_post = mocker.patch("requests.post")
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = '{"status":"ok"}'
        mock_post.return_value = mock_response

        notifier = LineNotifier(url=url, token=token)
        messages = [NotificationMessage(text="エラーが発生しました", image_url="https://example.com/error.png")]

        # when
        notifier.notify(messages)

        # then
        expected_payload = {
            "messages": [
                {"type": "text", "text": "エラーが発生しました"},
                {
                    "type": "image",
                    "originalContentUrl": "https://example.com/error.png",
                    "previewImageUrl": "https://example.com/error.png",
                },
            ]
        }

        call_args = mock_post.call_args
        actual_payload = json.loads(call_args.kwargs["data"])
        assert actual_payload == expected_payload

    def test_notify__multiple_messages_batch_sending(self, mocker):
        """5件を超えるメッセージを分割送信できること"""
        # given
        from src.domain import NotificationMessage
        from src.infrastructure.line_notifier import LineNotifier

        url = "https://api.line.me/v2/bot/message/push"
        token = "test-token-12345"

        mock_post = mocker.patch("requests.post")
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = '{"status":"ok"}'
        mock_post.return_value = mock_response

        notifier = LineNotifier(url=url, token=token)
        # 6件のメッセージを作成（LINE APIの5件制限を超える）
        messages = [NotificationMessage(text=f"メッセージ{i}") for i in range(6)]

        # when
        notifier.notify(messages)

        # then
        # 2回に分けて送信されることを確認
        assert mock_post.call_count == 2

        # 1回目: 5件
        first_call_payload = json.loads(mock_post.call_args_list[0].kwargs["data"])
        assert len(first_call_payload["messages"]) == 5

        # 2回目: 1件
        second_call_payload = json.loads(mock_post.call_args_list[1].kwargs["data"])
        assert len(second_call_payload["messages"]) == 1

    def test_notify__http_error_raises_notification_failed(self, mocker):
        """HTTPエラー時に NotificationFailed 例外が発生すること"""
        # given
        from src.domain.exceptions import NotificationFailed
        from src.domain import NotificationMessage
        from src.infrastructure.line_notifier import LineNotifier

        url = "https://api.line.me/v2/bot/message/push"
        token = "test-token-12345"

        mock_post = mocker.patch("src.infrastructure.line_notifier.requests.post")
        mock_response = mocker.Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Bad Request")
        mock_post.return_value = mock_response

        notifier = LineNotifier(url=url, token=token)
        messages = [NotificationMessage(text="テスト")]

        # when / then
        with pytest.raises(NotificationFailed) as exc_info:
            notifier.notify(messages)

        assert "通知送信中にエラーが発生しました" in str(exc_info.value)

    def test_notify__unexpected_error_raises_notification_failed(self, mocker):
        """予期しないエラー時に NotificationFailed 例外が発生すること"""
        # given
        from src.domain.exceptions import NotificationFailed
        from src.domain import NotificationMessage
        from src.infrastructure.line_notifier import LineNotifier

        url = "https://api.line.me/v2/bot/message/push"
        token = "test-token-12345"

        notifier = LineNotifier(url=url, token=token)
        messages = [NotificationMessage(text="テスト")]

        # _convert_to_line_format でエラーが発生するようにモック
        mocker.patch.object(
            notifier,
            "_convert_to_line_format",
            side_effect=ValueError("Unexpected error"),
        )

        # when / then
        with pytest.raises(NotificationFailed) as exc_info:
            notifier.notify(messages)

        assert "通知送信前にエラーが発生しました" in str(exc_info.value)
