import dataclasses
from typing import Dict

from pydantic.dataclasses import dataclass


@dataclass
class ScrapingParams:
    """Web ページ スクレイピング用のパラメータを扱う値クラス"""

    login_user_id: str = dataclasses.field(default="")
    login_password: str = dataclasses.field(default="")
    login_birthdate: str = dataclasses.field(default="")

    start_url: str = dataclasses.field(default="")
