import os
import pytest

from bs4.element import Tag


def test_scrape__get_parameter_called_when_login_parameter_arn_set(mocker) -> None:
    # given
    from src.infrastructure.scraping.nrk_scraping import NRKScraper
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


def test_scrape__get_parameter_not_called_when_login_parameter_arn_not_set(mocker) -> None:
    # given
    from src.infrastructure.scraping.nrk_scraping import NRKScraper
    os.environ.pop("LOGIN_PARAMETER_ARN", None)
    mock_get_parameter = mocker.patch("src.infrastructure.aws.ssm.get_parameter")
    mock_driver = mocker.Mock()

    # when
    NRKScraper(user_id="test", password="test", birthdate="20200101", driver=mock_driver)

    # then
    mock_get_parameter.assert_not_called()


def test_extract__valid_assets_page(valid_assets_page: str, mocker) -> None:
    from src.infrastructure.scraping.nrk_scraping import NRKScraper
    # given
    scraper = NRKScraper(user_id="test", password="test", birthdate="20200101", driver=mocker.Mock())
    scraper.page_source = valid_assets_page


    # when
    assets_info = scraper.extract()

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
    from src.infrastructure.scraping.nrk_scraping import NRKScraper, ExtractError
    # given
    scraper = NRKScraper(user_id="test", password="test", birthdate="20200101", driver=mocker.Mock())
    scraper.page_source = invalid_assets_page

    # when, then
    with pytest.raises(ExtractError):
        scraper.extract()


def test_is_tag_element__tag(mocker) -> None:
    from src.infrastructure.scraping.nrk_scraping import NRKScraper
    # given
    scraper = NRKScraper(user_id="test", password="test", birthdate="20200101", driver=mocker.Mock())

    # when
    tag = Tag(name="div")

    # then
    assert scraper._is_tag_element(tag) is True


def test_is_tag_element__not_tag(mocker) -> None:
    from src.infrastructure.scraping.nrk_scraping import NRKScraper
    # given
    scraper = NRKScraper(user_id="test", password="test", birthdate="20200101", driver=mocker.Mock())

    # when
    not_tag = "not a tag"

    # then
    assert scraper._is_tag_element(not_tag) is False

