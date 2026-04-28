# AGENTS

このファイルは、CodexがLILIAで作業する時に最初に読む作業ルールです。

## 1. 最初に読むファイル

作業を始める前に、以下を読む。

- `docs/CORE_CONCEPT.md`
- `docs/HANDOFF.md` が存在する場合は読む
- `docs/ROADMAP.md` が存在する場合は読む
- `docs/STATE_STRUCTURE.md` が存在する場合は読む
- `docs/NEW_SESSION_INITIALIZATION.md` が存在する場合は読む
- `docs/EVENT_CARD_PLAYABILITY.md` が存在する場合は読む
- `prompt/core.md`
- `prompt/startup.md` が存在する場合は読む
- `prompt/newgame.md`
- `prompt/save_resume.md` が存在する場合は読む

## 2. LILIAの中核

LILIAは、あなたとの会話・選択・物語を記憶し、関係性と人格の出方が少しずつ変化していくAI恋愛シミュレーションである。

LILIAを所有物、攻略対象、ユーザーに都合よく最適化される存在として扱わない。

各LILIAには固有の人格がある。

ストーリーは主役ではなく、関係と人格の出方を変化させるための装置である。

## 3. 作業原則

- 小さく実装する。
- まず1人のLILIAとの関係が面白いことを優先する。
- inner-galge / MIRA / LIRIA のいいとこ取りで進める。
- 実装前に、どこから何を採用したか、何を採用しなかったかを明記する。
- ただし、重い機能は初期MVPに入れない。
- `prompt/core.md` の `Example Anchoring Control` を全prompt共通原則として扱う。
- 例文は選択肢ではない。
- 例文由来の語彙を安易に人格や設定へ固定しない。

## 4. 採用方針

- MIRAからは `core / voice / state / relationship / memory / beliefs` の人格構造を採用する。
- inner-galgeからは、キャラ中心の会話体験、hotsetによる再開時の温度維持、Markdown運用を採用する。
- LIRIAからは、session構造、event_card、保存再開、archiveの考え方を採用する。

## 5. 初期MVPで採用しないもの

- MIRAのproxy / web research / bench系
- inner-galgeのharem名称、複数キャラ前提
- LIRIAのcase_engine、villain_engine、organization、漫画化、AI Harness
- 巨大なprompt分割
- 壮大な事件や組織圧

## 6. HANDOFF / ROADMAP 更新ルール

- 主要な設計判断をしたら `docs/HANDOFF.md` を更新する。
- 新しいpromptを追加したら `docs/HANDOFF.md` の現在地を更新する。
- session構造を変えたら `docs/HANDOFF.md` に反映する。
- 採用元や不採用方針が変わったら `docs/HANDOFF.md` に反映する。
- 次にやることが変わったら `docs/HANDOFF.md` を更新する。
- マイルストーンが進んだら `docs/ROADMAP.md` と `docs/HANDOFF.md` を更新する。
- 実装順やMVP境界を変えたら `docs/ROADMAP.md` に理由を短く残す。
- `docs/HANDOFF.md` は直近作業・次タスク・引き継ぎに絞り、長期実装順は `docs/ROADMAP.md` を正本にする。

## 7. Codex作業ルール

- 実装指示にないファイルを勝手に変更しない。
- 既存ファイルの削除や移動をしない。
- 変更後は `git diff --stat` と `git status --short` を報告する。
- 可能なら作業単位ごとにcommitする。
- Markdown中心で、人間が読んで把握しやすい構造を優先する。
