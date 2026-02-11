from abc import ABC, abstractmethod


class IArtifactRepository(ABC):
    """アーティファクトリポジトリ抽象クラス"""

    def __init__(self, bucket: str) -> None:
        """コンストラクタ"""
        pass

    @abstractmethod
    def save_error_artifact(self, key: str, file_path: str) -> None:
        """エラーアーティファクトを保存する
        Args:
            key (str): オブジェクトのキー
            file_path (str): 保存するファイルのパス
        Raises:
            ArtifactUploadError: 保存失敗時
        """
        pass

    @abstractmethod
    def save_assets(self, key: str, json_str: str) -> None:
        """資産情報を JSON として保存する
        Args:
            key (str): オブジェクトのキー
            json_str (str): JSON 文字列
        Raises:
            ArtifactUploadError: 保存失敗時
        """
        pass
