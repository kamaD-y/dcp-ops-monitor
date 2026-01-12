"""Domain レイヤー - Interfaces: ビジネスロジックのインターフェース定義"""

from .dcp_extractor_interface import IDcpExtractor
from .dcp_scraper_interface import IDcpScraper
from .notifier_interface import INotifier
from .object_repository_interface import IObjectRepository

__all__ = [
    "IDcpExtractor",
    "IDcpScraper",
    "INotifier",
    "IObjectRepository",
]
