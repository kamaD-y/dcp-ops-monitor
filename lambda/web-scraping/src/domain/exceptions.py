from typing import Optional


class ScrapingError(Exception):
    """スクレイピング処理のエラー

    Attributes:
        message (str): エラーメッセージ
        error_image_path (Optional[str]): エラー時のスクリーンショット画像パス
    """

    def __init__(self, message: str, error_image_path: Optional[str] = None):
        super().__init__(message)
        self.error_image_path = error_image_path


class AssetExtractionError(Exception):
    """資産情報抽出処理のエラー

    Attributes:
        message (str): エラーメッセージ
        html_source (Optional[str]): エラー時のHTMLソース
    """

    def __init__(self, message: str, html_source: Optional[str] = None):
        super().__init__(message)
        self.html_source = html_source
