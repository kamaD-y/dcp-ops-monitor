from abc import ABC, abstractmethod
from typing import Any

from .error_log_object import ErrorLogEvents


class IErrorLogEventsAdapter(ABC):
    """実際のエラーログから ErrorLogEvents への変換を行うインターフェース"""

    @abstractmethod
    def convert(self, raw_event: Any) -> ErrorLogEvents:
        """生のイベントデータを ErrorLogEvents に変換"""
