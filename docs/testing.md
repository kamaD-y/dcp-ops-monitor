## テスト戦略

- **LocalStack使用**: TestContainers を使用して実環境に近いテスト環境を構築
- **Mock最小限の原則**: 外部APIのみMockを使用し、AWS サービスは LocalStack で実行
- **カバレッジ要件**: 60%以上
