"""Domain レイヤー: モデル、インターフェース、例外"""

from .exceptions import (
    AssetExtractionFailed,
    NotificationFailed,
    ScrapingFailed,
    WebScrapingFailed,
)
from .extraction_interface import IDcpExtractor
from .extraction_object import DcpAssetInfo, DcpAssets, DcpOpsIndicators
from .notification_interface import INotifier
from .notification_object import NotificationMessage
from .scraping_interface import IDcpScraper
from .scraping_object import ScrapingParams
from .storage_interface import IObjectRepository

__all__ = [
    # Models
    "DcpAssetInfo",
    "DcpAssets",
    "DcpOpsIndicators",
    "NotificationMessage",
    "ScrapingParams",
    # Interfaces
    "IDcpExtractor",
    "IDcpScraper",
    "INotifier",
    "IObjectRepository",
    # Exceptions
    "AssetExtractionFailed",
    "NotificationFailed",
    "ScrapingFailed",
    "WebScrapingFailed",
]
