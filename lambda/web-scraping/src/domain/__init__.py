"""Domain レイヤー: モデル、インターフェース、例外"""

from .exceptions import (
    AssetExtractionFailed,
    NotificationFailed,
    ScrapingFailed,
    WebScrapingFailed,
)
from .interfaces import IDcpScraper, INotifier, IObjectRepository
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
    "IObjectRepository",
    # Exceptions
    "AssetExtractionFailed",
    "NotificationFailed",
    "ScrapingFailed",
    "WebScrapingFailed",
]
