# 要求内容: ドメインインターフェースの表記揺れ修正

## 背景

web-scraping Lambda の `storage_interface.py` / `IObjectRepository` が、機能設計書の命名規則（`{domain}_interface.py`：ドメイン知識単位）に反してインフラ寄りの命名になっている。

他の3つのインターフェースはすべてドメイン観点で命名されており、表記揺れが生じている。

| Lambda | ファイル名 | クラス名 | 命名観点 |
|--------|-----------|---------|---------|
| web-scraping | `scraping_interface.py` | `IScraper` | ドメイン |
| web-scraping | **`storage_interface.py`** | **`IObjectRepository`** | **インフラ** |
| summary-notification | `asset_interface.py` | `IAssetRepository` | ドメイン |
| summary-notification | `notification_interface.py` | `INotifier` | ドメイン |

## 問題点

1. **ファイル名**: `storage_interface` はインフラ概念（ストレージ）であり、ドメイン知識単位の命名規則に違反
2. **クラス名**: `IObjectRepository` は汎用的すぎて、ドメインの意図（何を保存するのか）が不明確
3. **メソッド名**: `upload_file`, `put_json` は S3 操作の薄いラッパーで、`IAssetRepository.get_latest_assets()` と比べてドメインの意図が弱い

## 要求

- ファイル名、クラス名、メソッド名をドメイン観点の命名に統一する
- 機能設計書（`docs/functional-design.md`）のインターフェース記述も合わせて更新する
- 既存テストが引き続きパスすることを確認する

## スコープ

- **対象**: web-scraping Lambda 内の `IObjectRepository` 関連の命名修正
- **対象外**: インターフェースの責務変更、メソッドシグネチャの変更、shared パッケージへの移動
