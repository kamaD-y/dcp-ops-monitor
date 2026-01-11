"""Domain レイヤー - Interfaces: ビジネスロジックのインターフェース定義"""

from .dcp_scraper_interface import IDcpScraper
from .notifier_interface import INotifier
from .s3_repository_interface import IS3Repository

__all__ = [
    "IDcpScraper",
    "INotifier",
    "IS3Repository",
]
