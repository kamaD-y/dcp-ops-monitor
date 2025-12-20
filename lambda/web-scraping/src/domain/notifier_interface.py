from abc import ABC, abstractmethod

from .value_object import DcpAssetsInfo, DcpOpsIndicators


class INotifier(ABC):
    """通知クラス(抽象クラス)"""

    @abstractmethod
    def create_message_by(self, assets_info: DcpAssetsInfo, ops_indicators: DcpOpsIndicators) -> str:
        pass

    @abstractmethod
    def send(self, message: str) -> bool:
        pass
