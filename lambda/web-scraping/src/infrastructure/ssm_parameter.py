from aws_lambda_powertools.utilities import parameters


def get_ssm_json_parameter(name: str, decrypt: bool = True) -> dict:
    """SSMパラメータストアからJSON形式のパラメータを取得する
    Args:
        name (str): パラメータ名
        decrypt (bool, optional): 暗号化されたパラメータを復号化するかどうか. Defaults to True.
    Returns:
        dict: 取得したパラメータ値
    """
    return parameters.get_parameter(name=name, decrypt=decrypt, transform="json")


def get_ssm_parameter(name: str, decrypt: bool = True) -> str:
    """SSMパラメータストアからパラメータを取得する

    Args:
        name (str): パラメータ名
        decrypt (bool, optional): 暗号化されたパラメータを復号化するかどうか. Defaults to True.

    Returns:
        str: 取得したパラメータ値
    """
    return parameters.get_parameter(name=name, decrypt=decrypt)
