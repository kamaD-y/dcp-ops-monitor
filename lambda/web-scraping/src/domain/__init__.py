"""Domain レイヤー: モデル、インターフェース、例外"""

from shared.domain.asset_object import DcpAssetInfo

from .artifact_interface import IArtifactRepository
from .exceptions import (
    ArtifactUploadError,
    ScrapingFailed,
    WebScrapingFailed,
)
from .scraping_interface import IScraper
from .scraping_object import ScrapingParams

__all__ = [
    # Models
    "DcpAssetInfo",
    "ScrapingParams",
    # Interfaces
    "IScraper",
    "IArtifactRepository",
    # Exceptions
    "ArtifactUploadError",
    "ScrapingFailed",
    "WebScrapingFailed",
]
