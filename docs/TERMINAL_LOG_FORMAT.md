# Terminal Log Format

`./lilia codex-new` と `./lilia codex-resume` の起動時、ターミナルが自動録音される。

## 保存先

```text
saves/<session>/archive/logs/<YYYY>/<YYYYMMDD_HHMMSS>.log
```

1 回の codex 起動 = 1 ファイル。

## 内容

`script` コマンドによる録音なので、以下が含まれる：

- kk の入力テキスト
- LILIA / GM AI の応答
- `./lilia scene-tick` などの内部コマンド出力
- ANSI エスケープシーケンス（色、カーソル移動）
- システムメッセージ（codex の "Worked for X seconds" 等）

掃除はしない。検証・振り返り用途として保管するため、ゴミも含めてそのまま残す。

## 読み方

ANSI エスケープを除去して読みたい場合：

```bash
cat saves/session_006/archive/logs/2026/20260506_143458.log | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' | less
```

または `cat -v` で可視化、`col -b` でバックスペース除去、など標準 Unix ツールで処理できる。

## 録音をオフにする

```bash
./lilia codex-resume session_006 --no-record
./lilia codex-new session_006 --no-record
```

## 容量

文字データのみなので軽量。1 ファイル数 KB〜数十 KB。1 年分でも数十 MB 程度。
