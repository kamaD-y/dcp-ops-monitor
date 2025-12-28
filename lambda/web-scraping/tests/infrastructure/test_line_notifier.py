import pytest


class TestLineNotifierCreateMessageBy:
    """LineNotifier の create_message_by メソッドのテスト"""

    def test_create_message_by__with_multiple_products(self):
        """複数の商品がある場合、正しいメッセージが生成されること"""
        # given
        from src.domain.dcp_assets import DcpAssetInfo, DcpAssets
        from src.domain.dcp_ops_indicators import DcpOpsIndicators
        from src.infrastructure.line_notifier import LineNotifier

        assets = DcpAssets(
            total=DcpAssetInfo(cumulative_contributions=1500000, gains_or_losses=300000, asset_valuation=1800000),
            products={
                "商品A": DcpAssetInfo(cumulative_contributions=300000, gains_or_losses=50000, asset_valuation=350000),
                "商品B": DcpAssetInfo(cumulative_contributions=700000, gains_or_losses=150000, asset_valuation=850000),
                "商品C": DcpAssetInfo(cumulative_contributions=500000, gains_or_losses=100000, asset_valuation=600000),
            },
        )

        indicators = DcpOpsIndicators(
            operation_years=7.0, actual_yield_rate=0.10, expected_yield_rate=0.06, total_amount_at_60age=8000000
        )

        notifier = LineNotifier(url="https://example.com", token="dummy-token")

        # when
        message = notifier.create_message_by(assets, indicators)

        # then
        expected = """確定拠出年金 運用状況通知Bot

総評価
拠出金額累計: 1,500,000円
評価損益: 300,000円
資産評価額: 1,800,000円

運用年数: 7.0年
運用利回り: 0.1
目標利回り: 0.06
想定受取額(60歳): 8,000,000円

商品別
商品A
取得価額累計: 300,000円
損益: 50,000円
資産評価額: 350,000円

商品B
取得価額累計: 700,000円
損益: 150,000円
資産評価額: 850,000円

商品C
取得価額累計: 500,000円
損益: 100,000円
資産評価額: 600,000円

"""
        assert message == expected

    def test_create_message_by__with_negative_gains(self):
        """評価損益がマイナスの場合、正しくメッセージが生成されること"""
        # given
        from src.domain.dcp_assets import DcpAssetInfo, DcpAssets
        from src.domain.dcp_ops_indicators import DcpOpsIndicators
        from src.infrastructure.line_notifier import LineNotifier

        assets = DcpAssets(
            total=DcpAssetInfo(cumulative_contributions=1000000, gains_or_losses=-100000, asset_valuation=900000),
            products={
                "商品A": DcpAssetInfo(cumulative_contributions=500000, gains_or_losses=-50000, asset_valuation=450000),
                "商品B": DcpAssetInfo(cumulative_contributions=500000, gains_or_losses=-50000, asset_valuation=450000),
            },
        )

        indicators = DcpOpsIndicators(
            operation_years=3.0, actual_yield_rate=-0.02, expected_yield_rate=0.06, total_amount_at_60age=2000000
        )

        notifier = LineNotifier(url="https://example.com", token="dummy-token")

        # when
        message = notifier.create_message_by(assets, indicators)

        # then
        expected = """確定拠出年金 運用状況通知Bot

総評価
拠出金額累計: 1,000,000円
評価損益: -100,000円
資産評価額: 900,000円

運用年数: 3.0年
運用利回り: -0.02
目標利回り: 0.06
想定受取額(60歳): 2,000,000円

商品別
商品A
取得価額累計: 500,000円
損益: -50,000円
資産評価額: 450,000円

商品B
取得価額累計: 500,000円
損益: -50,000円
資産評価額: 450,000円

"""
        assert message == expected


class TestLineNotifierSend:
    """LineNotifier の send メソッドのテスト"""

    def test_send__success(self, mocker):
        """メッセージが正しいパラメータでPOSTされること"""
        # given
        import json

        from src.infrastructure.line_notifier import LineNotifier

        url = "https://api.line.me/v2/bot/message/push"
        token = "test-token-12345"
        message = "テストメッセージ\n確定拠出年金の通知"

        mock_post = mocker.patch("requests.post")
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        notifier = LineNotifier(url=url, token=token)

        # when
        result = notifier.send(message)

        # then
        assert result is True

        # requests.post が正しいパラメータで呼び出されたことを確認
        expected_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        expected_payload = {"messages": [{"type": "text", "text": message}]}

        mock_post.assert_called_once_with(url, headers=expected_headers, data=json.dumps(expected_payload))
