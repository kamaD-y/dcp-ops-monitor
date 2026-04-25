# タスクリスト: SummaryNotification 通知メッセージ整理

## Commit 1: DcpAssets から total を削除し calculate_total() を追加

Domain モデルの変更とそれに依存する全レイヤーの追従。

- [ ] `DcpAssets` から `total` フィールドを削除、`calculate_total()` メソッドを追加
- [ ] `GoogleSheetAssetRepository._to_dcp_assets()` から total 算出ロジックを削除
- [ ] `SummaryNotificationService.send_summary()` で `calculate_total()` を使用するよう変更
- [ ] `message_formatter` の引数を `assets: DcpAssets` → `total: DcpAssetInfo` に変更（表示内容は据え置き）
- [ ] 全テストの `DcpAssets` 生成箇所から `total=...` を削除
- [ ] テスト実行で全テストが通ることを確認

## Commit 2: DcpOpsIndicators から expected_yield_rate を削除

- [ ] `DcpOpsIndicators` から `expected_yield_rate` フィールドを削除
- [ ] `indicators_calculator.py` から `EXPECTED_YIELD_RATE` 定数と戻り値への設定を削除
- [ ] `message_formatter` から目標利回り行を削除
- [ ] 関連テストを更新
- [ ] テスト実行で全テストが通ることを確認

## Commit 3: IAssetRepository に get_weekly_assets() を追加し資産評価額推移を実装

- [ ] `IAssetRepository` に `get_weekly_assets()` メソッドを追加
- [ ] `GoogleSheetAssetRepository` に `get_weekly_assets()` を実装
- [ ] `MockAssetRepository` に `get_weekly_assets()` を実装
- [ ] `SummaryNotificationService` に `_calculate_weekly_valuations()` を追加、`send_summary()` に統合
- [ ] `message_formatter` に資産評価額推移セクションを追加、商品別セクションを削除
- [ ] 関連テストを追加・更新
- [ ] テスト実行で全テストが通ることを確認

## Commit 4: docs/functional-design.md を更新

- [ ] データモデル定義（DcpAssets、DcpOpsIndicators）を更新
- [ ] インターフェース設計（IAssetRepository）を更新
- [ ] サマリ通知機能のシーケンス図を更新
