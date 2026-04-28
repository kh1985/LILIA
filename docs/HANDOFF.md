# LILIA Handoff

このファイルは、別のGPTセッションでLILIA開発を再開する時に最初に読ませる引き継ぎ文書です。

## 1. LILIAとは

LILIAは、あなたとの会話・選択・物語を記憶し、関係性と人格の出方が少しずつ変化していくAI恋愛シミュレーションです。

## 2. 現在の決定事項

- 名前は LILIA。
- LILIAは「ヒロイン」「キャラ」「パートナー」ではなく、LILIAというAI上の人格・関係存在として扱う。
- 短いコピーは「あなたとの記憶で、関係が育つ。」
- ストーリーは主役ではなく、関係と人格の出方を変化させる装置として扱う。
- 最初は1人のLILIAとの関係が面白いことを優先する。

## 3. 現在の実装状況

- `docs/CORE_CONCEPT.md` を作成済み。
- `templates/session/` を作成済み。
- `prompt/core.md` を作成済み。
- `prompt/core.md` に `Example Anchoring Control` を追加済み。
- `prompt/newgame.md` を作成または更新済み。
- `prompt/save_resume.md` は作成済みで、保存・再開promptとしてレビュー済み/コミット待ち。

prompt内の `current/...`、`lilia/main/...`、`story/...`、`archive/...` は、生成されたセッションルートからの相対パスとして扱う。テンプレート上では `templates/session/` 配下に対応する。

## 4. 採用元

- MIRA: 人格構造 `core / voice / state / relationship / memory / beliefs`
- inner-galge: キャラ中心、hotset、Markdown運用
- LIRIA: session構造、event_card、save/resume、archive

## 5. 採用しないもの

- proxy / web research / bench
- harem名称
- 複数キャラ前提
- case_engine / villain_engine / organization
- 漫画化 / AI Harness
- 巨大prompt分割

## 6. 次にやること

- `prompt/save_resume.md` をレビューし、`prompt/core.md` / `prompt/newgame.md` との整合性を確認する。
- `AGENTS.md`、`docs/HANDOFF.md`、`prompt/save_resume.md` を意図した単位でコミットする。
- その後、最小起動フローを考える。
- さらに後で export 機能を設計する。

## 7. 今後の判断基準

- 1人のLILIAとの関係が面白くなるか。
- LILIAの人格の核を壊していないか。
- ユーザーに迎合しすぎていないか。
- 記憶が次回の会話温度に効いているか。
- ストーリーが事件処理ではなく関係変化に効いているか。
- 例文やテンプレに引っ張られていないか。

## 8. HANDOFF更新ルール

- このファイルは開発の引き継ぎ正本である。
- 設計判断、prompt追加、session構造変更、採用方針変更、次タスク変更があったら更新する。
- 別GPTセッションで再開する時は、まずこのファイルを読ませる。
