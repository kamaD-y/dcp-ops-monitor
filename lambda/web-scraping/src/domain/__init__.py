"""Domain レイヤー: モデル、インターフェース、例外"""

from shared.domain.asset_object import AssetEvaluation
from shared.domain.asset_record_interface import IAssetRecordRepository
from shared.domain.asset_record_object import AssetRecord
from shared.domain.exceptions import AssetRecordError

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
    "AssetEvaluation",
    "ScrapingParams",
    "AssetRecord",
    # Interfaces
    "IScraper",
    "IArtifactRepository",
    "IAssetRecordRepository",
    # Exceptions
    "ArtifactUploadError",
    "ScrapingFailed",
    "WebScrapingFailed",
    "AssetRecordError",
]
