from datetime import datetime, timedelta

from config.settings import get_logger, get_settings
from domain.value_object import DcpAssetsInfo, DcpOpsIndicators, DcpTotalAssets

logger = get_logger()
settings = get_settings()


class DcpOpsMonitorTransformer:
    """確定拠出年金の運用状況を変換するクラス"""

    def to_operational_indicators(self, total_assets: DcpTotalAssets) -> DcpOpsIndicators:
        """総資産評価情報から運用指標へ変換する

        Args:
            total_assets (DcpTotalAssets): 総資産情報

        Returns:
            DcpOpsIndicators: 運用指標情報
        """
        logger.info("to_operational_indicators start.", extra=total_assets.__dict__)

        # 運用年数の算出
        operation_years = self.calculate_year_diff(start_dt=datetime(2016, 10, 1), end_dt=datetime.today())

        # 年間利回りの算出
        actual_yield_rate = self.calculate_annual_operation_yield_rate(
            cumulative_contributions=total_assets.cumulative_contributions,
            gains_or_losses=total_assets.total_gains_or_losses,
            operation_years=operation_years,
        )

        # 60歳まで運用した場合の想定受取額の計算
        annual_reserve_amount = 12 * 20000  # 年間積立額: 24万円とする
        years_to_60age = self.calculate_year_diff(start_dt=datetime.today(), end_dt=datetime(2046, 10, 1))
        # NOTE: 計算式: 年間積立額 * (((1+利回り)**60歳までの年数 - 1) / 利回り)
        total_amount_at_60age_int = int(
            annual_reserve_amount * (((1 + actual_yield_rate) ** years_to_60age - 1) / actual_yield_rate)
        )
        # NOTE: 計算方法が正しいか分からないが、計算実行時点での資産評価額を加算する
        total_amount_at_60age_int += self._yen_to_int(total_assets.total_asset_valuation)
        total_amount_at_60age = f"{total_amount_at_60age_int:,.0f}円"

        # 計算した値で運用指標オブジェクトを作成
        operational_indicators = DcpOpsIndicators(
            operation_years=operation_years,
            actual_yield_rate=actual_yield_rate,
            expected_yield_rate=0.06,
            total_amount_at_60age=total_amount_at_60age,
        )
        logger.info("to_operational_indicators end.", extra=operational_indicators.__dict__)

        return operational_indicators

    def calculate_year_diff(self, start_dt: datetime, end_dt: datetime) -> float:
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
        self, cumulative_contributions: str, gains_or_losses: str, operation_years: float
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
                self._yen_to_int(gains_or_losses) / self._yen_to_int(cumulative_contributions) / operation_years, 3
            )
        except ValueError as e:
            logger.error(
                f"ValueError: {e} in yield calculation.",
                extra={"cumulative_contributions": cumulative_contributions, "gains_or_losses": gains_or_losses},
            )
            raise
        except ZeroDivisionError:
            logger.error(
                "ZeroDivisionError: Error in yield calculation.",
                extra={"cumulative_contributions": cumulative_contributions, "gains_or_losses": gains_or_losses},
            )
            raise

        return actual_yield_rate

    def _yen_to_int(self, yen: str) -> int:
        """円表記の文字列を数値に変換する

        Args:
            yen (str): 円表記の文字列

        Returns:
            int: 数値

        Example:
            >>> self._yen_to_int("1,234,567円")
            1234567
        """
        return int(yen.replace("円", "").replace(",", ""))

    def make_message(self, assets_info: DcpAssetsInfo, operational_indicators: DcpOpsIndicators) -> str:
        """通知用メッセージを作成する

        Args:
            assets_info (DcpAssetsInfo): 資産情報
            operational_indicators (DcpOpsIndicators): 運用指標情報

        Returns:
            str: 通知用メッセージ
        """
        message = "確定拠出年金 運用状況通知Bot\n\n"
        message += "総評価\n"
        message += f"拠出金額累計: {assets_info.total.cumulative_contributions}\n"
        message += f"評価損益: {assets_info.total.total_gains_or_losses}\n"
        message += f"資産評価額: {assets_info.total.total_asset_valuation}\n"
        message += "\n"
        message += f"運用年数: {operational_indicators.operation_years}年\n"
        message += f"運用利回り: {operational_indicators.actual_yield_rate}\n"
        message += "目標利回り: 0.06\n"
        message += f"想定受取額(60歳): {operational_indicators.total_amount_at_60age}\n"
        message += "\n"

        message += "商品別\n"
        for p_name, p_v in assets_info.products.items():
            message += f"{p_name}\n"
            message += f"取得価額累計: {p_v.cumulative_acquisition_costs}\n"
            message += f"損益: {p_v.gains_or_losses}\n"
            message += f"資産評価額: {p_v.asset_valuation}\n"
            message += "\n"

        return message
