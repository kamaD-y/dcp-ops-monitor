import os
import re

import pytest
from bs4.element import Tag
from pytest_mock import MockerFixture

"""
Scraperのテスト
"""


def test_scrape__get_parameter_called_when_login_parameter_arn_set(mocker: MockerFixture) -> None:
    # given
    from src.infrastructure.scraping.dcp_scraping import NRKScraper
    os.environ["LOGIN_PARAMETER_ARN"] = "arn:aws:ssm:us-east-1:123456789012:parameter/test"
    mock_get_parameter = mocker.patch("src.infrastructure.aws.ssm.get_parameter")
    mock_get_parameter.return_value = {
        "LOGIN_USER_ID": "dummy_user_id",
        "LOGIN_PASSWORD": "dummy_password",
        "LOGIN_BIRTHDATE": "20200101",
    }
    mock_driver = mocker.Mock()

    # when
    scraper = NRKScraper(user_id="dummy_user_id", password="dummy_password", birthdate="20200101", driver=mock_driver)

    # then
    assert scraper.user_id == "dummy_user_id"
    assert scraper.password == "dummy_password"
    assert scraper.birthdate == "20200101"


def test_scrape__get_parameter_not_called_when_login_parameter_arn_not_set(mocker: MockerFixture) -> None:
    # given
    from src.infrastructure.scraping.dcp_scraping import NRKScraper
    os.environ.pop("LOGIN_PARAMETER_ARN", None)
    mock_get_parameter = mocker.patch("src.infrastructure.aws.ssm.get_parameter")
    mock_driver = mocker.Mock()

    # when
    NRKScraper(user_id="test", password="test", birthdate="20200101", driver=mock_driver)

    # then
    mock_get_parameter.assert_not_called()


"""
Extractorのテスト
"""


def test_extract__valid_assets_page(valid_assets_page: str, mocker) -> None:
    from src.domain.extraction import DcpOpsMonitorExtractor
    # given
    mocker.patch.object(DcpOpsMonitorExtractor, "_scrape", return_value=valid_assets_page)
    extractor = DcpOpsMonitorExtractor()

    # when
    assets_info = extractor.extract()

    # then
    assert assets_info.total.cumulative_contributions == "900,000円"
    assert assets_info.total.total_gains_or_losses == "300,000円"
    assert assets_info.total.total_asset_valuation == "1,200,000円"

    assert assets_info.products["プロダクト_1"].cumulative_acquisition_costs == "100,000円"
    assert assets_info.products["プロダクト_1"].gains_or_losses == "11,111円"
    assert assets_info.products["プロダクト_1"].asset_valuation == "111,111円"

    assert assets_info.products["プロダクト_2"].cumulative_acquisition_costs == "200,000円"
    assert assets_info.products["プロダクト_2"].gains_or_losses == "22,222円"
    assert assets_info.products["プロダクト_2"].asset_valuation == "222,222円"


def test_extract__invalid_assets_page(invalid_assets_page: str, mocker) -> None:
    from src.domain.extraction import DcpOpsMonitorExtractor, ExtractError
    # given
    mocker.patch.object(DcpOpsMonitorExtractor, "__init__", return_value=None)
    mocker.patch.object(DcpOpsMonitorExtractor, "_scrape", return_value=invalid_assets_page)
    extractor = DcpOpsMonitorExtractor()

    # when, then
    with pytest.raises(ExtractError):
        extractor.extract()


def test_is_tag_element__tag(mocker) -> None:
    from src.domain.extraction import DcpOpsMonitorExtractor
    # given
    mocker.patch.object(DcpOpsMonitorExtractor, "__init__", return_value=None)
    extractor = DcpOpsMonitorExtractor()

    # when
    tag = Tag(name="div")

    # then
    assert extractor._is_tag_element(tag) is True


def test_is_tag_element__not_tag(mocker) -> None:
    from src.domain.extraction import DcpOpsMonitorExtractor
    # given
    mocker.patch.object(DcpOpsMonitorExtractor, "__init__", return_value=None)
    extractor = DcpOpsMonitorExtractor()

    # when
    not_tag = "not a tag"

    # then
    assert extractor._is_tag_element(not_tag) is False


"""
Transformerのテスト
"""


def test_transform__valid_assets_info(valid_assets_info, dcp_operation_days) -> None:
    from src.domain.transform import DcpOpsMonitorTransformer
    # given
    transformer = DcpOpsMonitorTransformer()

    # when
    operational_indicators = transformer.calculate_ops_indicators(valid_assets_info.total)

    # then
    # 運用年数が正しいこと
    assert operational_indicators.operation_years == dcp_operation_days
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
    from src.domain.transform import DcpOpsMonitorTransformer
    from src.domain.dcp_value_object import DcpAssetsInfo, DcpTotalAssets
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
    from src.domain.transform import DcpOpsMonitorTransformer
    # given
    transformer = DcpOpsMonitorTransformer()

    # when
    message = transformer.make_message(valid_assets_info, valid_ops_indicators)

    # then
    assert isinstance(message, str)
    assert message.startswith("確定拠出年金 運用状況通知Bot")
    assert "総評価" in message
    assert "商品別" in message
