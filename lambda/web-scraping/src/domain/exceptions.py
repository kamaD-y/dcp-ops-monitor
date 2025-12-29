from typing import Optional


class ScrapingError(Exception):
    """スクレイピング処理のエラー

    Attributes:
        message (str): エラーメッセージ
        error_file_key (Optional[str]): エラー時のスクリーンショット画像のS3キー
    """

    def __init__(self, message: str, error_file_key: Optional[str] = None):
        super().__init__(message)
        self.error_file_key = error_file_key


class AssetExtractionError(Exception):
    """資産情報抽出処理のエラー

    Attributes:
        message (str): エラーメッセージ
        error_file_key (Optional[str]): エラー時のHTMLソース
    """

    def __init__(self, message: str, error_file_key: Optional[str] = None):
        super().__init__(message)
        self.error_file_key = error_file_key
