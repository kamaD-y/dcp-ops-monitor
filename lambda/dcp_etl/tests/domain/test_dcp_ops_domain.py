import os
import re

import pytest
from bs4.element import Tag
from pytest_mock import MockerFixture
from src.domain.dcp_ops_domain import (
    DcpOperationsStatusScraper,
    DcpOperationStatusExtractor,
    DcpOperationStatusTransformer,
    ExtractError,
)
from src.domain.dcp_value_object import DcpAssetsInfo, DcpOpsIndicators

"""
Scraperのテスト
"""


def test_scrape__get_parameter_called_when_login_parameter_arn_set(mocker: MockerFixture) -> None:
    # given
    os.environ["LOGIN_PARAMETER_ARN"] = "arn:aws:ssm:us-east-1:123456789012:parameter/test"
    mock_get_parameter = mocker.patch("src.domain.dcp_ops_domain.get_parameter")
    mock_get_parameter.return_value = {
        "USER_ID": "dummy_user_id",
        "PASSWORD": "dummy_password",
        "BIRTHDATE": "20200101",
    }

    # when
    scraper = DcpOperationsStatusScraper()

    # then
    mock_get_parameter.assert_called_once_with("arn:aws:ssm:us-east-1:123456789012:parameter/test")
    assert scraper.user_id == "dummy_user_id"
    assert scraper.password.get_secret_value() == "dummy_password"
    assert scraper.birthdate == "20200101"


def test_scrape__get_parameter_not_called_when_login_parameter_arn_not_set(mocker: MockerFixture) -> None:
    # given
    os.environ.pop("LOGIN_PARAMETER_ARN", None)
    mock_get_parameter = mocker.patch("src.domain.dcp_ops_domain.get_parameter")

    # when
    DcpOperationsStatusScraper()

    # then
    mock_get_parameter.assert_not_called()


"""
Extractorのテスト
"""


def test_extract__valid_assets_page(valid_assets_page: str) -> None:
    # given
    extractor = DcpOperationStatusExtractor()

    # when
    assets_info = extractor.extract(valid_assets_page)

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


def test_extract__invalid_assets_page(invalid_assets_page: str) -> None:
    # given
    extractor = DcpOperationStatusExtractor()

    # when, then
    with pytest.raises(ExtractError):
        extractor.extract(invalid_assets_page)


def test_is_tag_element__tag() -> None:
    # given
    extractor = DcpOperationStatusExtractor()

    # when
    tag = Tag(name="div")

    # then
    assert extractor.is_tag_element(tag) is True


def test_is_tag_element__not_tag() -> None:
    # given
    extractor = DcpOperationStatusExtractor()

    # when
    not_tag = "not a tag"

    # then
    assert extractor.is_tag_element(not_tag) is False


"""
Transformerのテスト
"""


def test_transform__valid_assets_info(valid_assets_info: DcpAssetsInfo, dcp_operation_days: int) -> None:
    # given
    transformer = DcpOperationStatusTransformer()

    # when
    operational_indicators = transformer.transform(valid_assets_info)

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
        ("999,999,999", 999999999),
        ("999,999,999円", 999999999),
        ("0円", 0),
        ("100円", 100),
        ("1,000,000円", 1000000),
        ("1000000円", 1000000),
        ("-1,234,567円", -1234567),
    ],
)
def test_yen_to_int__valid_str(yen_str: str, expected: int) -> None:
    # given
    transformer = DcpOperationStatusTransformer()

    # when
    result = transformer.yen_to_int(yen_str)

    # then
    assert result == expected


@pytest.mark.parametrize(
    "yen_str",
    [
        "",
        "0.01円",
        "abc円",
    ],
)
def test_yen_to_int__invalid_str(yen_str: str) -> None:
    # given
    transformer = DcpOperationStatusTransformer()

    # when, then
    with pytest.raises(ValueError):
        transformer.yen_to_int(yen_str)


def test_make_message__valid_args(valid_assets_info: DcpAssetsInfo, valid_ops_indicators: DcpOpsIndicators) -> None:
    # given
    transformer = DcpOperationStatusTransformer()

    # when
    message = transformer.make_message(valid_assets_info, valid_ops_indicators)

    # then
    assert isinstance(message, str)
    assert message.startswith("確定拠出年金 運用状況通知Bot")
    assert "総評価" in message
    assert "商品別" in message
