import pytest
from pytest_mock import MockerFixture


def test_main__success(mocker: MockerFixture, valid_assets_page: str) -> None:
    """main()が正常に動作することを確認するテスト"""
    from src.application.dcp_ops import main
    # given
    mock_scraper = mocker.patch("src.application.dcp_ops.DcpOperationsStatusScraper")
    mock_scraper.return_value.scrape.return_value = valid_assets_page
    mock_notify = mocker.patch("src.application.dcp_ops.DcpOperationStatusNotifier.notify")

    # when, then
    try:
        main()
    except Exception:
        pytest.fail("main() raised an exception")

    mock_scraper.return_value.scrape.assert_called_once()
    mock_notify.assert_called_once()


def test_main__failed(mocker: MockerFixture, invalid_assets_page: str) -> None:
    """main()がエラー発生時に異常終了することを確認するテスト"""
    from src.application.dcp_ops import main
    # given
    mock_scraper = mocker.patch("src.application.dcp_ops.DcpOperationsStatusScraper")
    mock_scraper.return_value.scrape.return_value = invalid_assets_page

    # when, then
    with pytest.raises(Exception):
        main()
