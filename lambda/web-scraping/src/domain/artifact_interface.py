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
