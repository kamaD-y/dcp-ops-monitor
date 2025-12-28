import pytest


def test_main_e2e_with_mocks(valid_assets_page):
    """main関数のE2Eテスト（Mockを使用）

    エンドツーエンドで処理が正常に完了することを確認する
    """
    # given
    import os

    from src.infrastructure.line_notifier_mock import MockLineNotifier
    from src.infrastructure.selenium_dcp_scraper_mock import MockSeleniumDcpScraper
    from src.presentation.dcp_ops_notification import main

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
    assert "確定拠出年金 運用状況通知Bot" in sent_message
    assert "総評価" in sent_message
    assert "拠出金額累計:" in sent_message
    assert "評価損益:" in sent_message
    assert "資産評価額:" in sent_message
    assert "運用年数:" in sent_message
    assert "運用利回り:" in sent_message
    assert "想定受取額(60歳):" in sent_message
    assert "商品別" in sent_message
    assert "プロダクト_1" in sent_message
    assert "プロダクト_2" in sent_message


def test_main_e2e_with_scraping_error():
    """スクレイピングエラー時のE2Eテスト

    スクレイピングが失敗した場合、例外が発生することを確認する
    """
    # given
    from src.infrastructure.line_notifier_mock import MockLineNotifier
    from src.infrastructure.selenium_dcp_scraper_mock import MockSeleniumDcpScraper
    from src.presentation.dcp_ops_notification import main

    scraper = MockSeleniumDcpScraper(should_fail=True)
    notifier = MockLineNotifier()

    # when, then
    with pytest.raises(Exception, match="Mock scraping error"):
        main(scraper=scraper, notifier=notifier)

    # スクレイピングは試みられたが失敗したことを確認
    assert scraper.fetch_called is True

    # 通知は送信されていないことを確認
    assert notifier.call_count == 0


def test_main_e2e_with_invalid_html(invalid_assets_page):
    """不正なHTMLでのE2Eテスト

    必要な要素が欠けているHTMLの場合、パースエラーが発生することを確認する
    """
    # given
    import os

    from src.infrastructure.line_notifier_mock import MockLineNotifier
    from src.infrastructure.selenium_dcp_scraper_mock import MockSeleniumDcpScraper
    from src.presentation.dcp_ops_notification import main

    scraper = MockSeleniumDcpScraper(mock_html=invalid_assets_page)
    notifier = MockLineNotifier()

    # when, then
    # HTMLパースエラーが発生することを確認
    with pytest.raises(Exception):
        main(scraper=scraper, notifier=notifier)

    # スクレイピングは実行されたことを確認
    assert scraper.fetch_called is True

    # 通知は送信されていないことを確認（パースエラーで処理が中断）
    assert notifier.call_count == 0
