import json

import pytest
import requests


class TestLineNotifierNotify:
    """LineNotifier の notify メソッドのテスト"""

    def test_notify__single_message_without_image(self, mocker):
        """画像なしの単一メッセージが正しく送信されること"""
        # given
        from src.domain import NotificationMessage
        from src.infrastructure.line_notifier import LineNotifier

        url = "https://api.line.me/v2/bot/message/push"
        token = "test-token-12345"

        mock_post = mocker.patch("requests.post")
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = "success"
        mock_post.return_value = mock_response

        notifier = LineNotifier(url=url, token=token)
        messages = [NotificationMessage(text="テストメッセージ", image_url=None)]

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
        """画像付きの単一メッセージが正しく送信されること"""
        # given
        from src.domain import NotificationMessage
        from src.infrastructure.line_notifier import LineNotifier

        url = "https://api.line.me/v2/bot/message/push"
        token = "test-token-12345"

        mock_post = mocker.patch("requests.post")
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = "success"
        mock_post.return_value = mock_response

        notifier = LineNotifier(url=url, token=token)
        messages = [
            NotificationMessage(
                text="エラーが発生しました",
                image_url="https://example.com/screenshot.png",
            )
        ]

        # when
        notifier.notify(messages)

        # then
        expected_payload = {
            "messages": [
                {"type": "text", "text": "エラーが発生しました"},
                {
                    "type": "image",
                    "originalContentUrl": "https://example.com/screenshot.png",
                    "previewImageUrl": "https://example.com/screenshot.png",
                },
            ]
        }

        mock_post.assert_called_once()
        actual_call = mock_post.call_args
        actual_payload = json.loads(actual_call[1]["data"])
        assert actual_payload == expected_payload

    def test_notify__split_messages_exceeding_limit(self, mocker):
        """5件を超えるメッセージが分割送信されること"""
        # given
        from src.domain import NotificationMessage
        from src.infrastructure.line_notifier import LineNotifier

        url = "https://api.line.me/v2/bot/message/push"
        token = "test-token-12345"

        mock_post = mocker.patch("requests.post")
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = "success"
        mock_post.return_value = mock_response

        notifier = LineNotifier(url=url, token=token)
        # 7件のメッセージ（テキストのみなのでLINEメッセージも7件）
        messages = [
            NotificationMessage(text=f"メッセージ{i}", image_url=None)
            for i in range(1, 8)
        ]

        # when
        notifier.notify(messages)

        # then
        # 7件のメッセージは5件+2件の2回に分割される
        assert mock_post.call_count == 2

        # 1回目のリクエスト（5件）
        first_call = mock_post.call_args_list[0]
        first_payload = json.loads(first_call[1]["data"])
        assert len(first_payload["messages"]) == 5
        assert first_payload["messages"][0] == {"type": "text", "text": "メッセージ1"}
        assert first_payload["messages"][4] == {"type": "text", "text": "メッセージ5"}

        # 2回目のリクエスト（2件）
        second_call = mock_post.call_args_list[1]
        second_payload = json.loads(second_call[1]["data"])
        assert len(second_payload["messages"]) == 2
        assert second_payload["messages"][0] == {"type": "text", "text": "メッセージ6"}
        assert second_payload["messages"][1] == {"type": "text", "text": "メッセージ7"}

    def test_notify__http_error(self, mocker):
        """HTTPエラーが NotificationError に変換されること"""
        # given
        from src.domain import NotificationError, NotificationMessage
        from src.infrastructure.line_notifier import LineNotifier

        url = "https://api.line.me/v2/bot/message/push"
        token = "test-token-12345"

        mock_post = mocker.patch("requests.post")
        mock_response = mocker.Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Bad Request")
        mock_post.return_value = mock_response

        notifier = LineNotifier(url=url, token=token)
        messages = [NotificationMessage(text="テストメッセージ", image_url=None)]

        # when/then
        with pytest.raises(NotificationError) as exc_info:
            notifier.notify(messages)

        assert "LINE Message API への送信失敗" in str(exc_info.value)

    def test_notify__unexpected_error(self, mocker):
        """予期しないエラーが NotificationError に変換されること"""
        # given
        from src.domain import NotificationError, NotificationMessage
        from src.infrastructure.line_notifier import LineNotifier

        url = "https://api.line.me/v2/bot/message/push"
        token = "test-token-12345"

        notifier = LineNotifier(url=url, token=token)
        messages = [NotificationMessage(text="テストメッセージ", image_url=None)]

        # _convert_to_line_format でエラーが発生するようにモック
        mocker.patch.object(
            notifier,
            "_convert_to_line_format",
            side_effect=ValueError("Unexpected error"),
        )

        # when/then
        with pytest.raises(NotificationError) as exc_info:
            notifier.notify(messages)

        assert "通知の送信に失敗しました" in str(exc_info.value)
        assert "Unexpected error" in str(exc_info.value)
