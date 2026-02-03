"""Domain レイヤー: モデル、インターフェース、例外"""

from .exceptions import (
    ArtifactUploadError,
    ScrapingFailed,
    WebScrapingFailed,
)
from .extraction_object import DcpAssetInfo, DcpAssets
from .scraping_interface import IScraper
from .scraping_object import ScrapingParams
from .storage_interface import IObjectRepository

__all__ = [
    # Models
    "DcpAssetInfo",
    "DcpAssets",
    "ScrapingParams",
    # Interfaces
    "IScraper",
    "IObjectRepository",
    # Exceptions
    "ArtifactUploadError",
    "ScrapingFailed",
    "WebScrapingFailed",
]
