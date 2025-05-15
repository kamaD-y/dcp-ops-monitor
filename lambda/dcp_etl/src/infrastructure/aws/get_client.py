import boto3


def get_client(resource: str, endpoint_url: str | None = None) -> boto3.client:
    """boto3クライアントを取得する

    Returns:
        boto3.client: 指定したリソースのboto3クライアント
    """
    if endpoint_url:
        return boto3.client(resource, region_name="ap-northeast-1", endpoint_url=endpoint_url)
    return boto3.client(resource, region_name="ap-northeast-1")
