from aws_lambda_powertools.utilities.data_classes import sns_event

from src.domain.usecase import FailureCase, SuccessCase


def main(sns_message: sns_event.SNSMessage) -> None:
    """メイン処理"""
    if "FailureTopic" in sns_message.topic_arn:
        FailureCase().process_message(sns_message.message)
        return
    SuccessCase().process_message(sns_message.message)
