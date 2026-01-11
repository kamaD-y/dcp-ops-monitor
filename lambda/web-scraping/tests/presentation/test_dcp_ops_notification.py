import os
import pytest


def test_main_e2e_with_mocks(valid_assets_page):
    """main関数のE2Eテスト（Mockを使用）

    エンドツーエンドで処理が正常に完了することを確認する
    """
    # given
    from tests.fixtures.mocks import MockLineNotifier, MockSeleniumDcpScraper
    from presentation.dcp_ops_notification import main # type: ignore (import-error)

    scraper = MockSeleniumDcpScraper(mock_html=valid_assets_page)
    notifier = MockLineNotifier()

    # when
    main(scraper=scraper, notifier=notifier)

    # then
    # スクレイピングが実行されたことを確認
    assert scraper.fetch_called is True

    # 通知が1回送信されたことを確認
    assert notifier.call_count == 1

    # 送信されたメッセージの内容を確認
    sent_message = notifier.get_last_sent_message()
    assert sent_message is not None
    assert "確定拠出年金 運用状況通知Bot" in sent_message.text
    assert "総評価" in sent_message.text
    assert "拠出金額累計:" in sent_message.text
    assert "評価損益:" in sent_message.text
    assert "資産評価額:" in sent_message.text
    assert "運用年数:" in sent_message.text
    assert "運用利回り:" in sent_message.text
    assert "想定受取額(60歳):" in sent_message.text
    assert "商品別" in sent_message.text
    assert "プロダクト_1" in sent_message.text
    assert "プロダクト_2" in sent_message.text


def test_main_e2e_with_scraping_error(valid_assets_page, local_stack_container):
    """スクレイピングエラー時のE2Eテスト

    スクレイピングが失敗した場合、例外が発生することを確認する
    また、エラー画像がS3にアップロードされることを確認する
    """
    # given
    from domain import ScrapingError # type: ignore (import-error)
    from presentation.dcp_ops_notification import main # type: ignore (import-error)
    from tests.fixtures.mocks import MockLineNotifier, MockSeleniumDcpScraper

    scraper = MockSeleniumDcpScraper(mock_html=valid_assets_page, should_fail=True)
    notifier = MockLineNotifier()

    # when, then
    with pytest.raises(ScrapingError) as exc_info:
        main(scraper=scraper, notifier=notifier)

    # エラーオブジェクトにerror_file_keyが含まれることを確認
    assert exc_info.value.error_file_key is not None

    # スクレイピングは試みられたが失敗したことを確認
    assert scraper.fetch_called is True

    # 通知は送信されていないことを確認
    assert notifier.call_count == 0

    # S3 バケットにエラー画像ファイルが存在することを確認
    client = local_stack_container.get_client("s3")  # type: ignore (missing-argument)
    response = client.list_objects_v2(Bucket=os.environ["error_bucket_name"])
    object_keys = [obj["Key"] for obj in response.get("Contents", [])]
    assert any(key.endswith(".png") for key in object_keys)


def test_main_e2e_with_invalid_html(invalid_assets_page, local_stack_container):
    """不正なHTMLでのE2Eテスト

    必要な要素が欠けているHTMLの場合、パースエラーが発生することを確認する
    また、エラー HTML ファイルがS3にアップロードされることを確認する
    """
    # given
    from domain import AssetExtractionError # type: ignore (import-error)
    from presentation.dcp_ops_notification import main # type: ignore (import-error)
    from tests.fixtures.mocks import MockLineNotifier, MockSeleniumDcpScraper

    scraper = MockSeleniumDcpScraper(mock_html=invalid_assets_page)
    notifier = MockLineNotifier()

    # when, then
    # HTMLパースエラーが発生することを確認
    with pytest.raises(AssetExtractionError) as exc_info:
        main(scraper=scraper, notifier=notifier)

    # エラーオブジェクトにerror_file_keyが含まれることを確認
    assert exc_info.value.error_file_key is not None

    # スクレイピングは実行されたことを確認
    assert scraper.fetch_called is True

    # 通知は送信されていないことを確認（パースエラーで処理が中断）
    assert notifier.call_count == 0

    # S3 バケットにエラー HTML ファイルが存在することを確認
    client = local_stack_container.get_client("s3")  # type: ignore (missing-argument)
    response = client.list_objects_v2(Bucket=os.environ["error_bucket_name"])
    object_keys = [obj["Key"] for obj in response.get("Contents", [])]
    assert any(key.endswith(".html") for key in object_keys)
