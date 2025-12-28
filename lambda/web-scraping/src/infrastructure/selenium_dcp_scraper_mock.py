from typing import Optional

from domain import IDcpScraper, ScrapingParams


class MockSeleniumDcpScraper(IDcpScraper):
    """Selenium WebDriver のMock実装（E2Eテスト用）

    実際にブラウザを起動せず、事前に用意したHTMLを返すMockオブジェクト
    """

    def __init__(
        self,
        user_agent: str = "",
        scraping_params: Optional[ScrapingParams] = None,
        chrome_binary_location: str = "",
        chrome_driver_path: str = "",
        mock_html: Optional[str] = None,
        should_fail: bool = False,
    ) -> None:
        """コンストラクタ

        Args:
            user_agent (str): ユーザーエージェント（使用しない）
            scraping_params (Optional[ScrapingParams]): スクレイピングパラメータ（使用しない）
            chrome_binary_location (str): Chromeバイナリの場所（使用しない）
            chrome_driver_path (str): ChromeDriverのパス（使用しない）
            mock_html (Optional[str]): 返却するHTMLソース（指定しない場合はデフォルトHTML）
            should_fail (bool): Trueの場合、fetch_asset_valuation_htmlで例外を発生させる
        """
        self.user_agent = user_agent
        self.scraping_params = scraping_params
        self.chrome_binary_location = chrome_binary_location
        self.chrome_driver_path = chrome_driver_path
        self.mock_html = mock_html or self._get_default_html()
        self.should_fail = should_fail
        self.error_image_path: Optional[str] = None
        self.fetch_called = False

    def fetch_asset_valuation_html(self) -> str:
        """資産評価情報ページの HTML ソースを返す（Mock実装）

        Returns:
            str: 資産評価情報ページの HTML ソース

        Raises:
            Exception: should_fail=True の場合
        """
        self.fetch_called = True

        if self.should_fail:
            self.error_image_path = "/tmp/mock_error.png"
            print("[Mock] Scraping failed (simulated)")
            raise Exception("Mock scraping error")

        print(f"[Mock] Scraping succeeded (html_length={len(self.mock_html)})")
        return self.mock_html

    def get_error_image_path(self) -> Optional[str]:
        """エラー時のスクリーンショット画像のパスを返す

        Returns:
            Optional[str]: エラー時のスクリーンショット画像のパス
        """
        return self.error_image_path

    @staticmethod
    def _get_default_html() -> str:
        """デフォルトのHTMLを返す（テストフィクスチャから読み込む）

        Returns:
            str: テスト用のデフォルトHTML
        """
        import os

        # テストフィクスチャのHTMLファイルを読み込む
        fixture_path = os.path.join(os.path.dirname(__file__), "../../tests/fixtures/html/valid_assets_page.html")
        try:
            with open(fixture_path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            # ファイルが見つからない場合はシンプルなHTMLを返す（フォールバック）
            print(f"[Mock] Warning: Fixture file not found at {fixture_path}, using fallback HTML")
            return """<html><body class="cate01"><div class="dataArea">
<div class="total">
  <dl class="sum01 pc_mr15"><dt data-lang="jp">拠出金額累計</dt><dd>900,000円</dd></dl>
  <dl class="sum01 pc_mr15"><dt data-lang="jp">評価損益</dt><dd>300,000円</dd></dl>
  <dl class="sum02"><dt data-lang="jp">資産評価額</dt><dd>1,200,000円</dd></dl>
</div>
<div class="infoDetail" id="prodInfo">
  <div class="infoDetailUnit_02 pc_mb30">
    <div class="infoHdWrap">
      <dl class="infoHdDl00" data-lang="jp">
        <dt>商品名</dt>
        <dd class="infoHdWrap00">テスト商品</dd>
      </dl>
    </div>
    <div class="infoDataWrap_02 idw-prov01">
      <div class="tblDataList listStyle01">
        <table>
          <tbody>
            <tr>
            <td rowspan="3">1</td>
            <td>100,000円</td>
            <td>100,000円</td>
            <td>100,000円</td>
            </tr>
      <tr>
      <td>100,000円</td>
      <td>100,000円</td>
      <td>0円</td>
      </tr>
    </tbody></table></div></div>
  </div>
</div>
</div></body></html>"""
