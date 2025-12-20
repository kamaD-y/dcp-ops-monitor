import dataclasses
from typing import Dict

from pydantic.dataclasses import dataclass


@dataclass
class LoginParams:
    """Web ページログイン用のパラメータを扱う値クラス"""

    user_id: str = dataclasses.field(default="")
    password: str = dataclasses.field(default="")
    birthdate: str = dataclasses.field(default="")
