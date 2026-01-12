"""Domain レイヤー - Interfaces: ビジネスロジックのインターフェース定義"""

from .dcp_scraper_interface import IDcpScraper
from .notifier_interface import INotifier
from .object_repository_interface import IObjectRepository

__all__ = [
    "IDcpScraper",
    "INotifier",
    "IObjectRepository",
]
