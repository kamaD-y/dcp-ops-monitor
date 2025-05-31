def handler(event: dict, context: dict) -> bool:
    """Lambda handler エントリーポイント"""
    print("event: ", event)
    print("context: ", context)

    return True
