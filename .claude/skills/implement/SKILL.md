---
name: implement
description: 計画フェーズで作成された task-list.md に基づき、TDD で実装 → レビュー → 修正のフィードバックループを回しつつ実装を進める。implementer / reviewer サブエージェントを協調させてタスク単位で完了させる。新機能追加・バグ修正等のコード実装を行う段階で使用する。/plan で計画を立て終わったあとに使用する。
---

# /implement

`task-list.md` の各タスクを、`implementer` と `reviewer` のフィードバックループで実装する。

## 引数

- ステアリングディレクトリのパス、または `task-list.md` のパス
- 省略時はユーザーに確認

## 制御フロー

```
task_list = read(task-list.md)
for task in task_list:
    1. implementer サブエージェントを起動（mode=initial、対象タスクを渡す）
    2. for loop in 1..3:
         reviewer サブエージェントを起動（変更 diff を渡す）
         if blocker = 0:
             break
         implementer サブエージェントを起動（mode=fix、blocker指摘を渡す）
    3. if blocker > 0（3 回ループしても残る）:
         ユーザーに介入要請して中断
    4. else:
         コミット作成（メイン Claude が `git commit` を実行）
         major / minor 指摘があれば警告ログとしてユーザーに通知
    5. 次のタスクへ
全タスク完了後、ユーザーに完了報告
```

## メイン Claude の責務

- task-list.md の読み込みと進捗管理
- 各サブエージェントの起動と入出力受け渡し
- ループ回数の管理（上限 3 回）
- `git add` / `git commit` の実行
- ユーザーへの通知（タスク完了、警告、ループ上限到達）

## サブエージェントに委譲する責務

- 実装の詳細手順 → `implementer` エージェント定義を単一情報源
- レビューの観点・severity 区分 → `reviewer` エージェント定義を単一情報源

このファイルでは詳細を重複させない。

## コミットメッセージ

`implementer` が返した想定コミットメッセージ（Conventional Commits 形式）を使う。妥当性を簡易確認のうえメイン Claude が `git commit` する。

## 中断条件

- 3 回ループしても blocker が残った場合
- ユーザーが明示的に中断を指示した場合
- pre-commit フック（lefthook）でテストが失敗した場合 — フックを `--no-verify` でバイパスしない
