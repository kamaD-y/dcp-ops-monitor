from datetime import datetime, timedelta

from domain.dcp_value_object import DcpAssetsInfo, DcpOpsIndicators, DcpTotalAssets
from settings.settings import get_logger, get_settings

logger = get_logger()
settings = get_settings()


class DcpOpsMonitorTransformer:
    """確定拠出年金の運用状況を変換するクラス"""

    def calculate_ops_indicators(self, total_assets: DcpTotalAssets) -> DcpOpsIndicators:
        """総資産評価情報から運用指標を算出する

        Args:
            total_assets (DcpTotalAssets): 資産情報

        Returns:
            DcpOpsIndicators: 運用指標情報
        """
        logger.info("calculate_ops_indicators start.", extra=total_assets.__dict__)

        # 運用年数の算出
        today = datetime.today()
        operation_start_dt = datetime(2016, 10, 1)  # 運用開始日: 2016/10/01
        operation_years = (today - operation_start_dt) / timedelta(days=365)
        operation_years = round(operation_years, 2)

        # 年間利回りの算出
        cumulative_contributions = self._yen_to_int(total_assets.cumulative_contributions)
        total_gains_or_losses = self._yen_to_int(total_assets.total_gains_or_losses)
        try:
            # 年間利回りの計算式: 利回り = 利益 / 拠出額 / 運用年数
            actual_yield_rate = round(total_gains_or_losses / cumulative_contributions / operation_years, 3)
        except ZeroDivisionError:
            logger.error("ZeroDivisionError: Error in yield calculation.", extra=total_assets.__dict__)
            raise

        # 60歳まで運用した場合の想定受取額, 60歳までの運用年数: 26年とする
        # 計算式: 24万(年積立額) * (((1+利回り)**年数26年 - 1) / 利回り)
        total_amount_at_60age_int = int(240000 * (((1 + actual_yield_rate) ** 26 - 1) / actual_yield_rate))
        total_amount_at_60age = f"{total_amount_at_60age_int:,.0f}円"

        # 計算した値で運用指標オブジェクトを作成
        operational_indicators = DcpOpsIndicators(
            operation_years=operation_years,
            actual_yield_rate=actual_yield_rate,
            expected_yield_rate=0.06,
            total_amount_at_60age=total_amount_at_60age,
        )
        logger.info("calculate_ops_indicators end.", extra=operational_indicators.__dict__)

        return operational_indicators

    def _yen_to_int(self, yen: str) -> int:
        """円表記の文字列を数値に変換する

        Args:
            yen (str): 円表記の文字列

        Returns:
            int: 数値

        Example:
            >>> yen = "1,234,567円"
            >>> transformer = DcpOpsMonitorTransformer()
            >>> transformer._yen_to_int(yen)
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
