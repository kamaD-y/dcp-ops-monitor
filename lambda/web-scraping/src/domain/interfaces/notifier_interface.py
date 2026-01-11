from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.models import DcpAssets, DcpOpsIndicators


class INotifier(ABC):
    """通知クラス(抽象クラス)"""

    @abstractmethod
    def create_message_by(self, assets_info: "DcpAssets", ops_indicators: "DcpOpsIndicators") -> str:
        pass

    @abstractmethod
    def send(self, message: str) -> bool:
        pass
