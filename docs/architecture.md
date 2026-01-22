## アーキテクチャ

### ディレクトリ構成
各 Lambda はクリーンアーキテクチャに基づいた 4 層構造で実装されています。

```
lambda/{feature}/
├── src/
│   ├── handler.py              # Lambda エントリーポイント
│   ├── config/
│   │   └── settings.py         # 環境設定管理
│   ├── presentation/
│   │   └── *.py                # Lambda イベント処理、依存性注入
│   ├── application/
│   │   └── *.py                # ビジネスロジック
│   ├── domain/
│   │   ├── *.py                # ドメインモデル
│   │   └── *_interface.py      # インターフェース定義
│   └── infrastructure/
│       └── *.py                # AWS サービス実装、外部 API 連携
├── tests/
│   ├── conftest.py             # pytest 設定
│   ├── presentation/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   └── fixtures/
├── pyproject.toml
├── uv.lock
└── README.md
```

### 各レイヤーの責務

- **Presentation**: Lambda イベント受け取り、依存性注入、レスポンス返却
- **Application**: 複数のドメインモデルを組み合わせた業務ロジック実行
- **Domain**: ビジネスルールとモデル定義（外部依存なし）
- **Infrastructure**: AWS サービスや外部 API との連携
