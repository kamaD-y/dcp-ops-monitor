from pydantic import BaseModel


class ScrapingParams(BaseModel):
    """Web ページ スクレイピング用のパラメータを扱う値クラス"""

    login_user_id: str
    login_password: str
    login_birthdate: str

    start_url: str
