import os

import pytest
from shared.domain.asset_object import DcpAssetInfo


def list_s3_objects(local_stack_container, prefix: str) -> list[str]:
    """指定されたプレフィックスのS3オブジェクトキーを取得する"""
    client = local_stack_container.get_client("s3")
    response = client.list_objects_v2(
        Bucket=os.environ["DATA_BUCKET_NAME"],
        Prefix=prefix,
    )
    return [obj["Key"] for obj in response.get("Contents", [])]


@pytest.fixture
def valid_products() -> dict[str, DcpAssetInfo]:
    """テスト用の正常な商品別資産情報を生成する"""
    return {
        "プロダクト_1": DcpAssetInfo(
            cumulative_contributions=100_000,
            gains_or_losses=11_111,
            asset_valuation=111_111,
        ),
        "プロダクト_2": DcpAssetInfo(
            cumulative_contributions=200_000,
            gains_or_losses=22_222,
            asset_valuation=222_222,
        ),
        "プロダクト_3": DcpAssetInfo(
            cumulative_contributions=300_000,
            gains_or_losses=33_333,
            asset_valuation=333_333,
        ),
    }


def test_main_e2e_with_mocks(valid_products):
    """main関数のE2Eテスト（Mockを使用）

    エンドツーエンドで処理が正常に完了することを確認する
    """
    # given
    from src.presentation.asset_collection_handler import main
    from tests.fixtures.mocks import MockAssetRecordRepository, MockSeleniumScraper

    scraper = MockSeleniumScraper(mock_products=valid_products)
    asset_record_repo = MockAssetRecordRepository()

    # when
    main(scraper=scraper, asset_record_repository=asset_record_repo)

    # then
    assert scraper.fetch_called is True
    assert len(asset_record_repo.saved_records) == 3
    product_names = {r.product for r in asset_record_repo.saved_records}
    assert product_names == {"プロダクト_1", "プロダクト_2", "プロダクト_3"}


def test_main_e2e_with_scraping_error(local_stack_container):
    """スクレイピングエラー時のE2Eテスト

    スクレイピングが失敗した場合、例外が発生することを確認する
    また、エラー画像が S3 の errors/ プレフィックスにアップロードされることを確認する
    """
    # given
    from src.domain import ScrapingFailed
    from src.presentation.asset_collection_handler import main
    from tests.fixtures.mocks import MockAssetRecordRepository, MockSeleniumScraper

    scraper = MockSeleniumScraper(should_fail=True)
    asset_record_repo = MockAssetRecordRepository()

    # when, then
    with pytest.raises(ScrapingFailed) as exc_info:
        main(scraper=scraper, asset_record_repository=asset_record_repo)

    # エラーオブジェクトに error_screenshot_key が含まれることを確認
    assert exc_info.value.error_screenshot_key is not None
    assert exc_info.value.error_screenshot_key.startswith("errors/")

    # スクレイピングは試みられたが失敗したことを確認
    assert scraper.fetch_called is True

    # レコード保存は呼ばれていないことを確認
    assert len(asset_record_repo.saved_records) == 0

    # S3 バケットにエラー画像ファイルが存在することを確認
    object_keys = list_s3_objects(local_stack_container, "errors/")
    assert any(key.endswith(".png") for key in object_keys)


def test_main_e2e_with_extraction_error(local_stack_container):
    """抽出エラー時のE2Eテスト

    資産情報の抽出に失敗した場合、例外が発生することを確認する
    また、エラー HTML ファイルが S3 の errors/ プレフィックスにアップロードされることを確認する
    """
    # given
    from src.domain import ScrapingFailed
    from src.presentation.asset_collection_handler import main
    from tests.fixtures.mocks import MockAssetRecordRepository, MockSeleniumScraper

    scraper = MockSeleniumScraper(should_fail_extraction=True)
    asset_record_repo = MockAssetRecordRepository()

    # when, then
    with pytest.raises(ScrapingFailed) as exc_info:
        main(scraper=scraper, asset_record_repository=asset_record_repo)

    # エラーオブジェクトに error_html_key が含まれることを確認
    assert exc_info.value.error_html_key is not None
    assert exc_info.value.error_html_key.startswith("errors/")

    # スクレイピングは実行されたことを確認
    assert scraper.fetch_called is True

    # レコード保存は呼ばれていないことを確認
    assert len(asset_record_repo.saved_records) == 0

    # S3 バケットにエラー HTML ファイルが存在することを確認
    object_keys = list_s3_objects(local_stack_container, "errors/")
    assert any(key.endswith(".html") for key in object_keys)
