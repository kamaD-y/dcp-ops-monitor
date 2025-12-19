from infrastructure.aws.sns import publish
from settings import get_logger, get_settings

logger = get_logger()
settings = get_settings()


class DcpOpsMonitorNotifier:
    """確定拠出年金の運用状況を通知するクラス"""

    def notify(self, message: str) -> None:
        """通知用メッセージを作成する"""
        publish(
            topic_arn=settings.sns_topic_arn,
            message=message,
            subject="確定拠出年金 運用状況",
        )
