from aws_lambda_powertools.utilities.data_classes import sns_event

from src.application.usecase import FailureNotification, SuccessNotification


def send(sns_message: sns_event.SNSMessage) -> None:
    """メイン処理"""
    if "FailureTopic" in sns_message.topic_arn:
        FailureNotification().send(sns_message.message)
        return
    SuccessNotification().send(sns_message.message)
