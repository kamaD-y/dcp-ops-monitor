"""ドメインインターフェース"""

from .notifier_interface import INotifier
from .object_repository_interface import IObjectRepository

__all__ = [
    "IObjectRepository",
    "INotifier",
]
