from datetime import datetime, timedelta

from domain import DcpAssetInfo, DcpOpsIndicators


def yen_to_int(yen: str) -> int:
    return int(yen.replace("円", "").replace(",", ""))


def to_operational_indicators(total_assets: DcpAssetInfo) -> DcpOpsIndicators:
    # 運用年数の算出
    operation_years = calculate_year_diff(start_dt=datetime(2016, 10, 1), end_dt=datetime.today())

    # 年間利回りの算出
    actual_yield_rate = calculate_annual_operation_yield_rate(
        cumulative_contributions=total_assets.cumulative_contributions,
        gains_or_losses=total_assets.gains_or_losses,
        operation_years=operation_years,
    )

    # 60歳まで運用した場合の想定受取額の計算
    annual_reserve_amount = 12 * 20000  # 年間積立額: 24万円とする
    years_to_60age = calculate_year_diff(start_dt=datetime.today(), end_dt=datetime(2046, 10, 1))
    # NOTE: 計算式: 年間積立額 * (((1+利回り)**60歳までの年数 - 1) / 利回り)
    total_amount_at_60age_int = int(
        annual_reserve_amount * (((1 + actual_yield_rate) ** years_to_60age - 1) / actual_yield_rate)
    )
    # NOTE: 計算方法が正しいか分からないが、計算実行時点での資産評価額を加算する
    total_amount_at_60age_int += yen_to_int(total_assets.asset_valuation)
    total_amount_at_60age = f"{total_amount_at_60age_int:,.0f}円"

    # 計算した値で運用指標オブジェクトを作成
    operational_indicators = DcpOpsIndicators(
        operation_years=operation_years,
        actual_yield_rate=actual_yield_rate,
        expected_yield_rate=0.06,
        total_amount_at_60age=total_amount_at_60age,
    )

    return operational_indicators


def calculate_year_diff(start_dt: datetime, end_dt: datetime) -> float:
    """開始日と終了日から年数を算出する

    Args:
        start_dt (datetime): 開始日時
        end_dt (datetime): 終了日時

    Returns:
        float: 年数
    """
    operation_years = (end_dt - start_dt) / timedelta(days=365)
    operation_years = round(operation_years, 2)
    return operation_years


def calculate_annual_operation_yield_rate(
    cumulative_contributions: str, gains_or_losses: str, operation_years: float
) -> float:
    """拠出額累計、評価損益、運用年数から年間利回り率を算出する
    年間利回りの計算式: 利回り = 利益 / 拠出額 / 運用年数

    Args:
        cumulative_contributions (str): 拠出額累計
        gains_or_losses (str): 評価損益
        operation_years (float): 運用年数

    Returns:
        float: 年間利回り
    """
    try:
        # 年間利回りの計算式: 利回り = 利益 / 拠出額 / 運用年数
        actual_yield_rate = round(
            yen_to_int(gains_or_losses) / yen_to_int(cumulative_contributions) / operation_years, 3
        )
    except ValueError as e:
        raise
    except ZeroDivisionError:
        raise

    return actual_yield_rate
