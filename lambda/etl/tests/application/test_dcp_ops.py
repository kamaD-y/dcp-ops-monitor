import pytest
from pytest_mock import MockerFixture


def test_main__success(mocker: MockerFixture, valid_assets_info) -> None:
    """main()が正常に動作することを確認するテスト"""
    from src.application.etl import main
    # given
    mock_extractor = mocker.patch("src.application.etl.DcpOpsMonitorExtractor")
    mock_extractor.return_value.extract.return_value = valid_assets_info
    mock_notify = mocker.patch("src.application.etl.DcpOperationStatusNotifier.notify")

    # when, then
    try:
        main()
    except Exception:
        pytest.fail("main() raised an exception")

    mock_extractor.return_value.extract.assert_called_once()
    mock_notify.assert_called_once()


def test_main__failed(mocker: MockerFixture) -> None:
    """main()がエラー発生時に異常終了することを確認するテスト"""
    from src.application.etl import main
    # given
    mock_extractor = mocker.patch("src.application.etl.DcpOpsMonitorExtractor")
    mock_extractor.return_value.extract.side_effect = Exception("Test error")

    # when, then
    with pytest.raises(Exception):
        main()
