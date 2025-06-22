import pytest
from bs4.element import Tag


def test_extract__valid_assets_page(valid_assets_page: str, mocker) -> None:
    from src.application.extraction import DcpOpsMonitorExtractor
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
    from src.application.extraction import DcpOpsMonitorExtractor, ExtractError
    # given
    mocker.patch.object(DcpOpsMonitorExtractor, "__init__", return_value=None)
    mocker.patch.object(DcpOpsMonitorExtractor, "_scrape", return_value=invalid_assets_page)
    extractor = DcpOpsMonitorExtractor()

    # when, then
    with pytest.raises(ExtractError):
        extractor.extract()


def test_is_tag_element__tag(mocker) -> None:
    from src.application.extraction import DcpOpsMonitorExtractor
    # given
    mocker.patch.object(DcpOpsMonitorExtractor, "__init__", return_value=None)
    extractor = DcpOpsMonitorExtractor()

    # when
    tag = Tag(name="div")

    # then
    assert extractor._is_tag_element(tag) is True


def test_is_tag_element__not_tag(mocker) -> None:
    from src.application.extraction import DcpOpsMonitorExtractor
    # given
    mocker.patch.object(DcpOpsMonitorExtractor, "__init__", return_value=None)
    extractor = DcpOpsMonitorExtractor()

    # when
    not_tag = "not a tag"

    # then
    assert extractor._is_tag_element(not_tag) is False

