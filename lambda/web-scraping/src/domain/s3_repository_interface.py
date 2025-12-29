from abc import ABC, abstractmethod


class IS3Repository(ABC):
    """S3リポジトリ抽象クラス"""

    def __init__(self, bucket: str) -> None:
        """コンストラクタ"""
        pass

    @abstractmethod
    def upload_file(self, key: str, file_path: str) -> None:
        """S3バケットにファイルをアップロードする
        Args:
            key (str): S3オブジェクトのキー
            file_path (str): アップロードするファイルのパス
        Returns:
            None
        """
        pass

    @abstractmethod
    def put_object(self, key: str, body: str) -> None:
        """S3バケットにオブジェクトをアップロードする

        Args:
            key (str): S3オブジェクトのキー
            body (str): アップロードするオブジェクトの内容

        Returns:
            None
        """
        pass
