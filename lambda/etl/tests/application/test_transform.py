import re
import pytest


def test_transform__valid_assets_info(valid_assets_info, operation_years) -> None:
    from src.application.transform import DcpOpsMonitorTransformer
    # given
    transformer = DcpOpsMonitorTransformer()

    # when
    operational_indicators = transformer.calculate_ops_indicators(valid_assets_info.total)

    # then
    # 運用年数が正しいこと
    assert operational_indicators.operation_years == operation_years
    # 0.0以上の浮動小数点であること
    assert operational_indicators.actual_yield_rate > 0.0
    # 0.06であること
    assert operational_indicators.expected_yield_rate == 0.06
    # 1円以上の金額であること
    actual_total_amount_at_60age = operational_indicators.total_amount_at_60age
    pattern = re.compile(r"^\d{1,3}(,\d{3})*円$")
    assert actual_total_amount_at_60age != "0円" and pattern.match(actual_total_amount_at_60age)


@pytest.mark.parametrize(
    "yen_str, expected",
    [
        ("円", ValueError),
        ("0.01円", ValueError),
        ("abc円", ValueError),
        ("0円", ZeroDivisionError)
    ],
)
def test_transform__invalid_assets_info(yen_str: str, expected: Exception) -> None:
    from src.application.transform import DcpOpsMonitorTransformer
    from src.domain.value_object import DcpAssetsInfo, DcpTotalAssets
    # given
    transformer = DcpOpsMonitorTransformer()
    # 不正なデータを設定
    invalid_total = DcpTotalAssets(
        cumulative_contributions=yen_str,
        total_gains_or_losses="300,000円",
        total_asset_valuation="1,200,000円",
    )
    invalid_assets_info = DcpAssetsInfo(
        total=invalid_total,
        products={},
    )

    # when, then
    with pytest.raises(expected):
        transformer.calculate_ops_indicators(invalid_assets_info.total)


def test_make_message__valid_args(valid_assets_info, valid_ops_indicators) -> None:
    from src.application.transform import DcpOpsMonitorTransformer
    # given
    transformer = DcpOpsMonitorTransformer()

    # when
    message = transformer.make_message(valid_assets_info, valid_ops_indicators)

    # then
    assert isinstance(message, str)
    assert message.startswith("確定拠出年金 運用状況通知Bot")
    assert "総評価" in message
    assert "商品別" in message
