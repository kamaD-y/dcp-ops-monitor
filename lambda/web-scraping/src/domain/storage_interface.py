from abc import ABC, abstractmethod


class IObjectRepository(ABC):
    """オブジェクトリポジトリ抽象クラス"""

    def __init__(self, bucket: str) -> None:
        """コンストラクタ"""
        pass

    @abstractmethod
    def upload_file(self, key: str, file_path: str) -> None:
        """オブジェクトストレージにファイルをアップロードする
        Args:
            key (str): オブジェクトのキー
            file_path (str): アップロードするファイルのパス
        Raises:
            ArtifactUploadError: アップロード失敗時
        """
        pass
