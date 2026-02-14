"""サマリ通知機能のカスタム例外定義"""

from typing import Self


class SummaryNotificationFailed(Exception):
    """サマリ通知機能のベース例外"""

    pass


class AssetNotFound(SummaryNotificationFailed):
    """資産情報が見つからない"""

    @classmethod
    def no_assets_in_spreadsheet(cls) -> Self:
        """スプレッドシートに資産情報が存在しない場合の例外を生成

        Returns:
            AssetNotFound: 生成された例外インスタンス
        """
        return cls("スプレッドシートに資産情報が見つかりません")


class NotificationFailed(SummaryNotificationFailed):
    """通知送信エラー"""

    @classmethod
    def during_request(cls) -> Self:
        """通知送信中にエラーが発生した場合の例外インスタンスを生成する名前付きコンストラクタ

        Returns:
            NotificationFailed: 生成された例外インスタンス
        """
        return cls("通知送信中にエラーが発生しました")

    @classmethod
    def before_request(cls) -> Self:
        """通知送信前にエラーが発生した場合の例外インスタンスを生成する名前付きコンストラクタ

        Returns:
            NotificationFailed: 生成された例外インスタンス
        """
        return cls("通知送信前にエラーが発生しました")
