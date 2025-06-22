import os


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
