from abc import ABC, abstractmethod


class IS3Repository(ABC):
    """S3リポジトリ抽象クラス"""

    @abstractmethod
    def __init__(self) -> None:
        """コンストラクタ"""
        pass

    @abstractmethod
    def upload_file(self, bucket: str, key: str, file_path: str) -> None:
        """S3バケットにファイルをアップロードする
        Args:
            bucket (str): S3バケット名
            key (str): S3オブジェクトのキー
            file_path (str): アップロードするファイルのパス
        Returns:
            None
        """
        pass

    @abstractmethod
    def put_object(self, bucket: str, key: str, body: str) -> None:
        """S3バケットにオブジェクトをアップロードする

        Args:
            bucket (str): S3バケット名
            key (str): S3オブジェクトのキー
            body (str): アップロードするオブジェクトの内容

        Returns:
            None
        """
        pass
