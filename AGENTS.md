# AGENTS

このファイルは、CodexがLILIAで作業する時に最初に読む入口です。
詳細な正本一覧、現在地、優先順位、archive候補は `PROJECT_CONTROL.md` を読む。

## 1. 最初に読むファイル

作業開始時は、まず以下を読む。

- `PROJECT_CONTROL.md`
- `docs/CORE_CONCEPT.md`

その後は `PROJECT_CONTROL.md` の「作業別の読み方」に従い、作業に必要な正本だけ読む。
毎回すべてのdocsを総読みしない。

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

## 4. 採用 / 不採用方針

採用するもの:

- MIRAからは `core / voice / state / relationship / memory / beliefs` の人格構造を採用する。
- inner-galgeからは、キャラ中心の会話体験、hotsetによる再開時の温度維持、Markdown運用を採用する。
- LIRIAからは、session構造、event_card、保存再開、archiveの考え方を採用する。

初期MVPで採用しないもの:

- MIRAのproxy / web research / bench系
- inner-galgeのharem名称、複数キャラ前提
- LIRIAのcase_engine、villain_engine、重いorganization運用、漫画化、AI Harness
- 巨大なprompt分割
- 壮大な事件や組織圧

## 5. 更新ルール

- 正本一覧と役割分担は `PROJECT_CONTROL.md` を優先する。
- βまでのタスク状態を変えたら `RELEASE_WBS.md` を更新する。
- 主要な設計判断をしたら `docs/HANDOFF.md` を更新する。
- 新しいprompt、session構造、採用元、不採用方針、次タスクが変わったら `docs/HANDOFF.md` に反映する。
- マイルストーンが進んだら `docs/ROADMAP.md` と `docs/HANDOFF.md` を更新する。
- 実装順やMVP境界を変えたら `docs/ROADMAP.md` に理由を短く残す。
- `docs/HANDOFF.md` は直近作業・次タスク・引き継ぎに絞り、長期実装順は `docs/ROADMAP.md` を正本にする。
- `STATUS_DASHBOARD.html` は人間用ビューであり、正本ではない。Markdown正本をHTMLに置き換えない。

## 6. Codex作業ルール

- 実装指示にないファイルを勝手に変更しない。
- 既存ファイルの削除や移動をしない。
- 変更後は `git diff --stat` と `git status --short` を報告する。
- 可能なら作業単位ごとにcommitする。
- Markdown中心で、人間が読んで把握しやすい構造を優先する。
