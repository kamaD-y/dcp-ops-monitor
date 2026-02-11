"""Domain レイヤー: モデル、インターフェース、例外"""

from .artifact_interface import IArtifactRepository
from .exceptions import (
    ArtifactUploadError,
    ScrapingFailed,
    WebScrapingFailed,
)
from .extraction_object import DcpAssetInfo, DcpAssets
from .scraping_interface import IScraper
from .scraping_object import ScrapingParams

__all__ = [
    # Models
    "DcpAssetInfo",
    "DcpAssets",
    "ScrapingParams",
    # Interfaces
    "IScraper",
    "IArtifactRepository",
    # Exceptions
    "ArtifactUploadError",
    "ScrapingFailed",
    "WebScrapingFailed",
]
