# Codex Rollout Logs

codex は `~/.codex/sessions/<YYYY>/<MM>/<DD>/rollout-<timestamp>-<uuid>.jsonl` に会話ログを自動保存する。

- 1 回の codex 起動 = 1 ファイル
- JSONL 形式（1 行 1 オブジェクト）
- kk と AI のメッセージ、ツール呼び出し、推論、トークンカウント等が時系列で記録される
- codex は自動削除しない。手動で消すまで残る

## LILIA への取り込み

```bash
./lilia archive-codex-logs session_006
```

`~/.codex/sessions/` から、cwd が LILIA リポと一致する rollout を探し、
`saves/session_006/archive/logs/<YYYY>/<MM>/<DD>/` へコピーする。

- 既存ファイルはスキップ（idempotent。何度実行しても安全）
- コピーしたファイルとスキップしたファイルの数を表示
- 必要な時だけ実行する opt-in コマンド。普段は何も自動でやらない

## 読み方

JSONL は 1 行 1 オブジェクト。`jq` で整形可能:

```bash
cat saves/session_006/archive/logs/2026/05/06/rollout-*.jsonl | jq 'select(.type == "event_msg" and (.payload.type == "user_message" or .payload.type == "agent_message"))'
```

主要なフィールド:

- `payload.event_msg.user_message`: kk の入力
- `payload.event_msg.agent_message`: AI の応答
- `payload.response_item.function_call`: ツール呼び出し（scene-tick など）
- `payload.response_item.reasoning`: AI の推論

## 容量

1 セッションあたり 200KB〜10MB 程度。1 年で数百 MB に達する可能性があるが、テキストデータのみなので Mac の SSD では問題ない。
気になる場合は手動で gzip 圧縮するか、古いファイルを削除する。

## 元データの場所

`~/.codex/sessions/` は codex 自身の管理下。LILIA は読み取りのみ行い、削除しない。
kk が容量管理したい場合は、その下を手動で削除すればよい。
