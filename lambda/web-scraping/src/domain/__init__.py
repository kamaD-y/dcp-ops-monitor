"""Domain レイヤー: モデル、インターフェース、例外"""

from .exceptions import (
    AssetExtractionError,
    NotificationFailed,
    ScrapingFailed,
    WebScrapingFailed,
)
from .interfaces import IDcpScraper, INotifier, IS3Repository
from .models import (
    DcpAssetInfo,
    DcpAssets,
    DcpOpsIndicators,
    NotificationMessage,
    ScrapingParams,
)

__all__ = [
    # Models
    "DcpAssetInfo",
    "DcpAssets",
    "DcpOpsIndicators",
    "NotificationMessage",
    "ScrapingParams",
    # Interfaces
    "IDcpScraper",
    "INotifier",
    "IS3Repository",
    # Exceptions
    "AssetExtractionError",
    "NotificationFailed",
    "ScrapingFailed",
    "WebScrapingFailed",
]
