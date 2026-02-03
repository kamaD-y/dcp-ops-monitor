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

    @abstractmethod
    def put_json(self, key: str, json_str: str) -> None:
        """JSON 文字列をオブジェクトとして保存する
        Args:
            key (str): オブジェクトのキー
            json_str (str): JSON 文字列
        Raises:
            AssetStorageError: 保存失敗時
        """
        pass
