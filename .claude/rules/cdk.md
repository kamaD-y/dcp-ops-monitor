---
paths:
  - "{lib,bin,test}/**/*.ts"
---

# CDK（TypeScript）開発ガイドライン

## コーディング規約

### 一般原則

- 型定義を必須とする
- `any` の使用を避ける
- 関数は単一責任を持つ

---

## 命名規則

| 種別 | 規則 | 例 |
|------|------|-----|
| クラス・インターフェース | PascalCase | `DcpOpsMonitorStack` |
| 関数・変数 | camelCase | `errorBucket`, `webScrapingFunction` |
| 定数 | UPPER_SNAKE_CASE または camelCase | `LOG_LEVEL` |
