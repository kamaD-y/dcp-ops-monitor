"""サマリ通知サービス"""

from src.config.settings import get_logger
from src.domain import IAssetRepository, INotifier, NotificationMessage

from .indicators_calculator import calculate_indicators
from .message_formatter import format_summary_message

logger = get_logger()


class SummaryNotificationService:
    """サマリ通知サービス"""

    def __init__(
        self,
        asset_repository: IAssetRepository,
        notifier: INotifier,
    ) -> None:
        """サマリ通知サービスを初期化

        Args:
            asset_repository: 資産リポジトリ
            notifier: 通知クライアント
        """
        self.asset_repository = asset_repository
        self.notifier = notifier

    def send_summary(self) -> None:
        """サマリ通知を送信

        S3 から最新の資産情報を取得し、運用指標を計算してメッセージを生成・送信する。

        Raises:
            AssetNotFound: 資産情報が見つからない場合
            NotificationFailed: 通知送信失敗時
        """
        # 最新の資産情報を取得
        assets = self.asset_repository.get_latest_assets()
        total = assets.calculate_total()
        logger.info("資産情報を取得しました")

        # 運用指標を計算
        indicators = calculate_indicators(total)
        logger.info("運用指標を計算しました", indicators=indicators.model_dump())

        # メッセージをフォーマット
        message_text = format_summary_message(total, indicators)

        # 通知を送信
        notification_message = NotificationMessage(text=message_text)
        self.notifier.notify([notification_message])
        logger.info("サマリ通知を送信しました")
