"""運用指標の計算"""

from datetime import datetime, timedelta

from src.domain import DcpAssetInfo, DcpOpsIndicators

# 固定パラメータ
OPERATION_START_DATE = datetime(2016, 10, 1)
RETIREMENT_DATE = datetime(2046, 10, 1)
ANNUAL_CONTRIBUTION = 240_000  # 年間積立額: 24万円
EXPECTED_YIELD_RATE = 0.06  # 目標利回り


def calculate_year_diff(start_dt: datetime, end_dt: datetime) -> float:
    """開始日と終了日から年数を算出する

    Args:
        start_dt: 開始日時
        end_dt: 終了日時

    Returns:
        float: 年数（小数点以下2桁）
    """
    operation_years = (end_dt - start_dt) / timedelta(days=365)
    return round(operation_years, 2)


def calculate_annual_yield_rate(
    cumulative_contributions: int,
    gains_or_losses: int,
    operation_years: float,
) -> float:
    """年間運用利回りを算出する

    計算式: 利回り = 評価損益 / 拠出金額累計 / 運用年数

    Args:
        cumulative_contributions: 拠出金額累計
        gains_or_losses: 評価損益
        operation_years: 運用年数

    Returns:
        float: 年間利回り（小数点以下3桁）
    """
    return round(gains_or_losses / cumulative_contributions / operation_years, 3)


def calculate_total_amount_at_60age(
    yield_rate: float,
    asset_valuation: int,
    today: datetime,
) -> int:
    """60歳時点の想定受取額を算出する

    計算式: 年間積立額 × (((1 + 利回り)^60歳までの年数 - 1) / 利回り) + 現在の資産評価額

    Args:
        yield_rate: 運用利回り
        asset_valuation: 現在の資産評価額
        today: 現在日

    Returns:
        int: 想定受取額
    """
    years_to_60age = calculate_year_diff(start_dt=today, end_dt=RETIREMENT_DATE)
    total = int(ANNUAL_CONTRIBUTION * (((1 + yield_rate) ** years_to_60age - 1) / yield_rate))
    total += asset_valuation
    return total


def calculate_indicators(total_assets: DcpAssetInfo, today: datetime | None = None) -> DcpOpsIndicators:
    """資産情報から運用指標を計算する

    Args:
        total_assets: 総資産情報
        today: 現在日（テスト用に注入可能、デフォルトは現在日時）

    Returns:
        DcpOpsIndicators: 運用指標
    """
    if today is None:
        today = datetime.now()

    operation_years = calculate_year_diff(start_dt=OPERATION_START_DATE, end_dt=today)

    actual_yield_rate = calculate_annual_yield_rate(
        cumulative_contributions=total_assets.cumulative_contributions,
        gains_or_losses=total_assets.gains_or_losses,
        operation_years=operation_years,
    )

    total_amount_at_60age = calculate_total_amount_at_60age(
        yield_rate=actual_yield_rate,
        asset_valuation=total_assets.asset_valuation,
        today=today,
    )

    return DcpOpsIndicators(
        operation_years=operation_years,
        actual_yield_rate=actual_yield_rate,
        expected_yield_rate=EXPECTED_YIELD_RATE,
        total_amount_at_60age=total_amount_at_60age,
    )
