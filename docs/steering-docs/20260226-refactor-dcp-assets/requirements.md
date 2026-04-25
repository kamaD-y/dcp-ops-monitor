# 要求定義: DcpAssets 廃止・AssetEvaluation への責務集約

## 背景

summary-notification の `DcpAssets` は `dict[str, AssetEvaluation]` の薄いラッパーであり、
実質的な追加ロジックは `calculate_total()` のみである。

また、インフラ層（`GoogleSheetAssetRepository`）が `_to_dcp_assets()` という
ドメインオブジェクト変換ロジックを持っており、責務が混在している。

## 目的

1. **DcpAssets の廃止**: summary-notification ローカルの `DcpAssets` クラスを廃止し、
   `dict[str, AssetEvaluation]` を直接使用する
2. **aggregate ロジックの集約**: `calculate_total()` 相当のロジックを
   `AssetEvaluation.aggregate()` として shared パッケージに集約する
3. **インフラ層の責務分離**: `GoogleSheetAssetRepository._to_dcp_assets()` を廃止し、
   インフラ層はデータ取得のみを担う形に整理する

## 要求内容

- `shared/domain/asset_object.py` に `AssetEvaluation.aggregate()` クラスメソッドを追加する
  - `Iterable[AssetEvaluation]` を受け取り、全フィールドを合算した単一の `AssetEvaluation` を返す
- `DcpAssets` クラスを廃止し、関連ファイルを削除・変更する
- `IAssetRepository` の戻り値型を `DcpAssets` から `dict[str, AssetEvaluation]` へ変更する
- `GoogleSheetAssetRepository` の変換ロジック (`_to_dcp_assets`) を
  `_to_products` に置き換え、`dict[str, AssetEvaluation]` を返すようにする
- `SummaryNotificationService` を新しい型に合わせて更新する
- テストを新しい設計に合わせて更新する

## 非機能要求

- 既存の振る舞いは変更しない（リファクタリングのみ）
- テストカバレッジを維持する
