import json
import os

import pytest

from src.domain import DcpAssetInfo, DcpAssets


def list_s3_objects(local_stack_container, prefix: str) -> list[str]:
    """指定されたプレフィックスのS3オブジェクトキーを取得する"""
    client = local_stack_container.get_client("s3")
    response = client.list_objects_v2(
        Bucket=os.environ["DATA_BUCKET_NAME"],
        Prefix=prefix,
    )
    return [obj["Key"] for obj in response.get("Contents", [])]


@pytest.fixture
def valid_assets() -> DcpAssets:
    """テスト用の正常な資産情報を生成する"""
    return DcpAssets(
        total=DcpAssetInfo(
            cumulative_contributions=900_000,
            gains_or_losses=300_000,
            asset_valuation=1_200_000,
        ),
        products={
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
        },
    )


def test_main_e2e_with_mocks(valid_assets, local_stack_container):
    """main関数のE2Eテスト（Mockを使用）

    エンドツーエンドで処理が正常に完了し、S3 に JSON が保存されることを確認する
    """
    # given
    from src.presentation.asset_collection_handler import main
    from tests.fixtures.mocks import MockSeleniumScraper

    scraper = MockSeleniumScraper(mock_assets=valid_assets)

    # when
    main(scraper=scraper)

    # then
    # スクレイピングが実行されたことを確認
    assert scraper.fetch_called is True

    # S3 バケットに JSON ファイルが保存されたことを確認
    object_keys = list_s3_objects(local_stack_container, "assets/")
    assert any(key.endswith(".json") for key in object_keys)

    # JSON の内容を確認
    json_key = next(key for key in object_keys if key.endswith(".json"))
    client = local_stack_container.get_client("s3")
    response = client.get_object(Bucket=os.environ["DATA_BUCKET_NAME"], Key=json_key)
    json_content = json.loads(response["Body"].read().decode("utf-8"))

    assert json_content["total"]["cumulative_contributions"] == 900_000
    assert json_content["total"]["gains_or_losses"] == 300_000
    assert json_content["total"]["asset_valuation"] == 1_200_000
    assert "プロダクト_1" in json_content["products"]
    assert "プロダクト_2" in json_content["products"]
    assert "プロダクト_3" in json_content["products"]


def test_main_e2e_with_scraping_error(local_stack_container):
    """スクレイピングエラー時のE2Eテスト

    スクレイピングが失敗した場合、例外が発生することを確認する
    また、エラー画像が S3 の errors/ プレフィックスにアップロードされることを確認する
    """
    # given
    from src.domain import ScrapingFailed
    from src.presentation.asset_collection_handler import main
    from tests.fixtures.mocks import MockSeleniumScraper

    scraper = MockSeleniumScraper(should_fail=True)

    # when, then
    with pytest.raises(ScrapingFailed) as exc_info:
        main(scraper=scraper)

    # エラーオブジェクトに error_screenshot_key が含まれることを確認
    assert exc_info.value.error_screenshot_key is not None
    assert exc_info.value.error_screenshot_key.startswith("errors/")

    # スクレイピングは試みられたが失敗したことを確認
    assert scraper.fetch_called is True

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
    from tests.fixtures.mocks import MockSeleniumScraper

    scraper = MockSeleniumScraper(should_fail_extraction=True)

    # when, then
    with pytest.raises(ScrapingFailed) as exc_info:
        main(scraper=scraper)

    # エラーオブジェクトに error_html_key が含まれることを確認
    assert exc_info.value.error_html_key is not None
    assert exc_info.value.error_html_key.startswith("errors/")

    # スクレイピングは実行されたことを確認
    assert scraper.fetch_called is True

    # S3 バケットにエラー HTML ファイルが存在することを確認
    object_keys = list_s3_objects(local_stack_container, "errors/")
    assert any(key.endswith(".html") for key in object_keys)
