# LILIA Document Deduplication Plan

この文書は、Phase 3-A のドキュメント重複整理計画である。
今回は既存文書の削除、移動、大幅短縮、コード変更はしない。

目的は、`PROJECT_CONTROL.md` / `docs/HANDOFF.md` / `docs/ROADMAP.md` / `docs/release/*` / `STATUS_DASHBOARD.html` に重複している本文を洗い出し、Phase 3-B 以降で安全に短縮する順番を決めることである。

## 0. 採用 / 不採用

採用するもの:

- `PROJECT_CONTROL.md` を、人間とCodexが最初に読む司令塔として維持する。
- `docs/HANDOFF.md` は直近作業の引き継ぎに絞る。
- `docs/ROADMAP.md` は長期実装順、wave履歴、MVP境界、保留判断に寄せる。
- `docs/release/RELEASE_WBS.md` はタスク表、status、priority、done criteria の正本にする。
- `docs/release/COMMERCIALIZATION_ROADMAP.md` は商用化方針、MVP境界、Go / No-Go、画像・安全方針の正本にする。
- `docs/archive/IMPLEMENTATION_HISTORY.md` は実装履歴アーカイブとして維持する。
- `STATUS_DASHBOARD.html` は人間用ビューとして扱い、Markdown正本を置き換えない。

採用しないもの:

- 今回の Phase 3-A では既存本文を削らない。
- 正本docsを整理目的だけでarchive扱いしない。
- prompt / generator / validator / tests から参照される仕様docsを短縮対象にしない。
- `STATUS_DASHBOARD.html` を正本化しない。

## 1. 現在の役割分担

| File | 現在の役割 | Phase 3で守る境界 |
|---|---|---|
| `PROJECT_CONTROL.md` | 最初に読む現在地・司令塔。現在地、優先順位、正本一覧、読み方、archive候補を置く。 | 詳細仕様や長い履歴を増やさない。要約と導線に限定する。 |
| `docs/HANDOFF.md` | 直近作業の引き継ぎ。次タスク、直近の注意、再開時に必要な差分を置く。 | 古いwave履歴や巨大な実装済み一覧を持ちすぎない。 |
| `docs/ROADMAP.md` | 長期実装履歴、wave履歴、MVP境界、保留判断の正本。 | 現在地と次タスクの運用情報は `PROJECT_CONTROL.md` / `docs/HANDOFF.md` へ寄せる。 |
| `docs/release/RELEASE_WBS.md` | βまでの作業表。ID、Task、Status、Priority、Done Criteriaを管理する。 | 方針説明を増やしすぎず、タスク表と完了条件に集中する。 |
| `docs/release/COMMERCIALIZATION_ROADMAP.md` | 商用化方針、MVP境界、Phase Plan、Go / No-Go、画像戦略、安全原則の正本。 | WBSのstatus表を重複させない。商用判断の理由と条件に集中する。 |
| `docs/archive/IMPLEMENTATION_HISTORY.md` | 実装履歴アーカイブ。完了済みwaveと実装済み内容の台帳。 | 現在ステータス、次タスク、商用判断をここに増やさない。 |
| `STATUS_DASHBOARD.html` | 人間用ビュー。現在地、P0残タスク、正本リンク、WBS snapshotを視覚化する。 | 正本ではない。Dashboard更新だけでタスク状態更新扱いにしない。 |

## 2. 重複マトリクス

| 内容 | 重複しているファイル | 正本にすべきファイル | 他ファイルでの扱い | Phase 3-B以降の対応案 | リスク |
|---|---|---|---|---|---|
| 現在地 | `PROJECT_CONTROL.md`, `docs/HANDOFF.md`, `docs/ROADMAP.md`, `STATUS_DASHBOARD.html`, `docs/archive/IMPLEMENTATION_HISTORY.md` | `PROJECT_CONTROL.md` | HANDOFFは直近差分だけ。ROADMAPは長期文脈。Dashboardはsnapshot。Historyは過去台帳。 | Phase 3-BでHANDOFFの「現在の実装状況」を短縮。Phase 3-CでROADMAPのCurrent Positionを長期観点に寄せる。 | 現在地を削りすぎると再開時の把握が遅くなる。 |
| 実装済みwave | `docs/HANDOFF.md`, `docs/ROADMAP.md`, `docs/archive/IMPLEMENTATION_HISTORY.md`, `STATUS_DASHBOARD.html` | `docs/archive/IMPLEMENTATION_HISTORY.md` と `docs/ROADMAP.md` | HANDOFFは最新数件だけ。Dashboardは主要waveの可視化のみ。 | HANDOFFのWave 4〜11詳細を履歴側へ逃がす。ROADMAPはwave索引とMVP境界を残し、細かい履歴はHistory参照へ寄せる。 | 履歴を消すと「なぜそうしたか」が失われるため、移動ではなく要約とリンクにする。 |
| β前P0 | `PROJECT_CONTROL.md`, `docs/release/RELEASE_WBS.md`, `docs/release/COMMERCIALIZATION_ROADMAP.md`, `docs/ROADMAP.md`, `STATUS_DASHBOARD.html`, `docs/archive/IMPLEMENTATION_HISTORY.md` | `docs/release/RELEASE_WBS.md` | PROJECT_CONTROLは優先順の要約。Commercializationは商用条件。ROADMAPはMVP境界。Dashboardは見える化。Historyは過去の格上げ記録。 | Phase 3-Dでrelease docsの役割を整理し、WBSは表、Commercializationは方針、PROJECT_CONTROLは要約に分ける。 | WBS上todoでも仕様文書には定義済みの項目があるため、仕様doneと実装doneの混同に注意。 |
| Three Hook Spine | `PROJECT_CONTROL.md`, `docs/HANDOFF.md`, `docs/ROADMAP.md`, `docs/release/RELEASE_WBS.md`, `docs/release/COMMERCIALIZATION_ROADMAP.md`, `docs/testing/AI_PLAYTEST_PLAN.md`, `STATUS_DASHBOARD.html`, `docs/archive/IMPLEMENTATION_HISTORY.md` | 仕様方針: `docs/release/COMMERCIALIZATION_ROADMAP.md`; タスク状態: `docs/release/RELEASE_WBS.md`; Play品質: `docs/specs/PLAY_MODE_SPEC.md` | PROJECT_CONTROLは優先順だけ。HANDOFFは直近の実装注意だけ。ROADMAPはMVP境界。AI Playtestは検証観点。DashboardはP0地図。 | Phase 3-DでCommercializationの詳細とWBSのIDを対応付ける。HANDOFFは「次にHOOK-001から」程度に短縮する。 | どれか1つに統合すると、方針・タスク・検証観点が混ざる。 |
| Arc Closure / Story Continuation | `PROJECT_CONTROL.md`, `docs/ROADMAP.md`, `docs/release/RELEASE_WBS.md`, `docs/release/COMMERCIALIZATION_ROADMAP.md`, `docs/specs/PLAY_MODE_SPEC.md`, `docs/testing/AI_PLAYTEST_PLAN.md`, `STATUS_DASHBOARD.html`, `docs/archive/IMPLEMENTATION_HISTORY.md` | Arc Closure仕様: `docs/specs/PLAY_MODE_SPEC.md`; Story Continuation方針: `docs/release/COMMERCIALIZATION_ROADMAP.md`; タスク状態: `docs/release/RELEASE_WBS.md`; Judge項目: `docs/testing/AI_PLAYTEST_PLAN.md` | PROJECT_CONTROLは優先順。ROADMAPはMVP境界と保留判断。DashboardはP0地図。 | Phase 3-Dでrelease docsの重複説明を整理。Phase 3-CでROADMAPの長い保留説明を正本リンク中心にする。 | Play品質仕様を削るとprompt / Judgeとズレる。仕様正本は短縮対象にしない。 |
| AI Playtest | `PROJECT_CONTROL.md`, `docs/HANDOFF.md`, `docs/ROADMAP.md`, `docs/release/RELEASE_WBS.md`, `docs/release/COMMERCIALIZATION_ROADMAP.md`, `docs/testing/AI_PLAYTEST_PLAN.md`, `STATUS_DASHBOARD.html` | `docs/testing/AI_PLAYTEST_PLAN.md` | WBSはAI-001〜AI-008の状態。Commercializationは商用βで必要な理由。PROJECT_CONTROLは優先順。Dashboardは次タスク表示。 | HANDOFFから古いAI Playtest説明を削り、AI planへのリンクにする。WBSはstatus棚卸しで仕様done / 実装todoを分ける。 | AI-001 / AI-002は仕様済みだがWBSはtodo。勝手にdoneへ変えない。 |
| WebUI / Security / Image | `PROJECT_CONTROL.md`, `docs/release/RELEASE_WBS.md`, `docs/release/COMMERCIALIZATION_ROADMAP.md`, `STATUS_DASHBOARD.html`, `docs/archive/IMPLEMENTATION_HISTORY.md` | 商用方針: `docs/release/COMMERCIALIZATION_ROADMAP.md`; タスク状態: `docs/release/RELEASE_WBS.md` | PROJECT_CONTROLは未到達領域の要約。DashboardはP0カテゴリ表示。Historyはcommercialization gapとして記録。 | Phase 3-DでCommercializationのSafety/Image方針を残し、Dashboardは短い見出しとリンクにする。 | SecurityはWebUI前P0なので、Dashboardから見えなくしすぎない。 |
| Go / No-Go | `docs/release/COMMERCIALIZATION_ROADMAP.md`, `STATUS_DASHBOARD.html`, `PROJECT_CONTROL.md`, `docs/release/RELEASE_WBS.md` | `docs/release/COMMERCIALIZATION_ROADMAP.md` | Dashboardは抜粋ビュー。PROJECT_CONTROLはβ優先順。WBSはREL-003のdone criteria。 | DashboardのGo / No-Goは短い抜粋に維持。WBSには判定タスクだけ置く。 | Dashboardの抜粋が古くなるリスク。正本リンクを必ず残す。 |
| 次にやること | `PROJECT_CONTROL.md`, `docs/HANDOFF.md`, `docs/ROADMAP.md`, `STATUS_DASHBOARD.html` | `PROJECT_CONTROL.md` と `docs/HANDOFF.md` | PROJECT_CONTROLは優先順。HANDOFFは次セッションで実行する具体作業。ROADMAPは長期候補。Dashboardは人間向け優先タスク。 | Phase 3-BでHANDOFFの「次にやること」を現在のP0実行に合わせる。Phase 3-CでROADMAPの古いNext Taskを履歴化または削る計画を作る。 | ROADMAPの古いNext Taskが残るとCodexが旧waveへ戻る。 |
| 正本ファイル一覧 | `PROJECT_CONTROL.md`, `docs/ROADMAP.md`, `STATUS_DASHBOARD.html`, `AGENTS.md`, `docs/DOCUMENT_REORGANIZATION_PLAN.md` | `PROJECT_CONTROL.md` | AGENTSは入口だけ。ROADMAP冒頭は長期関連の正本リンク。Dashboardは見取り図。Reorganization planはPhase 2-A履歴。 | PROJECT_CONTROLを正本一覧の中心にし、他ファイルは必要な範囲だけリンクする。 | 正本一覧を複数箇所で詳細化すると、移動後にズレる。 |

## 3. 削ってよい候補

### `docs/HANDOFF.md`

- 長い実装履歴一覧は `docs/ROADMAP.md` / `docs/archive/IMPLEMENTATION_HISTORY.md` に寄せる候補。
- Wave 4〜11の詳細セクションは、Phase 3-Bで「履歴は `docs/archive/IMPLEMENTATION_HISTORY.md` を参照」に短縮する候補。
- `## 3. 現在の実装状況` は、直近作業に必要なものだけ残す候補。
- 古い「次のWave候補」は、現在のP0優先順とズレるため削減候補。

### `docs/ROADMAP.md`

- `## 5. Next Task` は古いWave 16に寄っているため、現在の次タスクは `PROJECT_CONTROL.md` / `docs/HANDOFF.md` へ寄せる候補。
- 完了済みWaveの長い本文は、ROADMAPでは索引化し、詳細は `docs/archive/IMPLEMENTATION_HISTORY.md` に寄せる候補。
- `Current Position` は長期観点に絞り、β前P0の詳細は `docs/release/RELEASE_WBS.md` へ寄せる候補。

### `docs/archive/IMPLEMENTATION_HISTORY.md`

- archiveとして維持するが、普段の導線からは外す候補。
- `Known Remaining Technical Items` / `Commercialization Gap` は、現在タスク管理ではなく過去の棚卸しとして扱う。
- Pending詳細は `docs/ROADMAP.md` や `docs/release/RELEASE_WBS.md` と重複するため、履歴台帳としての注記に純化する候補。

### release docs

- `docs/release/RELEASE_WBS.md` は表に集中させる候補。長い方針説明は増やさない。
- `docs/release/COMMERCIALIZATION_ROADMAP.md` は商用方針、Go / No-Go、Image Strategy、Safety Principleに集中させる候補。
- `PROJECT_CONTROL.md` にはrelease全体の要約だけを残す。

### `STATUS_DASHBOARD.html`

- 詳細な正本文言を持ちすぎない。
- WBS集計、P0カテゴリ、正本リンク、Go / No-Go抜粋に留める。
- 将来は `docs/release/RELEASE_WBS.md` から生成するか、手動snapshotとして更新日と出典を明記する。

## 4. 削ってはいけない候補

以下は Phase 3-B / 3-C / 3-D の短縮対象にしない。
prompt / generator / validator / tests が仕様前提として参照している可能性があるためである。

- `docs/CORE_CONCEPT.md`
- `docs/STATE_STRUCTURE.md`
- `docs/NEW_SESSION_INITIALIZATION.md`
- `docs/EVENT_CARD_PLAYABILITY.md`
- `docs/VOICE_CONTINUITY.md`
- `docs/GROWTH_UPDATE_LOOP.md`
- `docs/ROMANCE_INTIMACY_GROWTH.md`
- `docs/RESUME_SMOKE_TEST.md`
- `docs/STORY_RELATIONSHIP_ACCUMULATION.md`
- `docs/CRISIS_COMBAT_ABILITY_CONSTRAINT_LOOP.md`
- `docs/ENGINE_RUNNER.md`
- `docs/specs/PLAY_MODE_SPEC.md`
- `prompt/*.md`

追加で慎重に扱うファイル:

- `docs/EMOTIONAL_DESIGN_PRINCIPLES.md`: `prompt/core.md` と generator prompt から参照される。
- `docs/LILIA_PERSONA_PROFILE.md`: `prompt/newgame.md` / `prompt/save_resume.md` / `prompt/startup.md` から参照される。
- `docs/RELATIONSHIP_CHANGE_AUDIT.md`: WBS、ROADMAP、Commercializationで関係変化監査の根拠になっている。
- `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md`: tests と手動checklistから参照される。
- `tests/**/*.md`: 実行メモであり正本ではないが、手動検証手順として残す。
- `tools/**/*.py`: 今回コード変更禁止。docstringやコメント参照の整理も Phase 3-A では行わない。

確認メモ:

- `prompt/core.md`, `prompt/newgame.md`, `prompt/save_resume.md`, `prompt/startup.md`, `prompt/style_reference.md` は複数の `docs/*` 正本を直接参照している。
- `tools/session/document_validator.py` は `docs/EVENT_CARD_PLAYABILITY.md` を参照している。
- `tools/character/profile_generator.py`, `tools/session/document_generator.py`, `tools/story/spine_generator.py` は `docs/EMOTIONAL_DESIGN_PRINCIPLES.md` を参照している。
- `tests/resume_smoke/manual_checklist.md` と `tests/mvp_playtest/manual_checklist.md` は `docs/RESUME_SMOKE_TEST.md` / `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md` を参照している。

## 5. Phase 3-B 実行案: HANDOFF短縮

目的:

- `docs/HANDOFF.md` を別セッション再開用の短い引き継ぎに戻す。
- 履歴台帳や長期計画を兼ねない。

推奨構成:

1. LILIAとは
2. 現在の決定事項
3. 直近の現在地
4. 次タスク
5. 参照すべき正本リンク
6. HANDOFF更新ルール

実行順:

1. `docs/HANDOFF.md` の見出し一覧を確認する。
2. Wave 4〜11などの長い完了履歴を `docs/archive/IMPLEMENTATION_HISTORY.md` / `docs/ROADMAP.md` 参照へ置換する案を作る。
3. 現在のP0優先順を `PROJECT_CONTROL.md` と矛盾しない形で短く残す。
4. 本文削除前に、削除予定箇所が他ファイルに残っているか確認する。
5. 1回のPRではHANDOFFだけを短縮する。

残すべき内容:

- 直近で作業者が迷う注意点。
- P0の次タスク。
- どの正本を読めばよいか。
- 更新ルール。

逃がす内容:

- 古いWave詳細。
- 完了済み機能の網羅一覧。
- 長期候補。
- 商用化Go / No-Goの詳細。

## 6. Phase 3-C 実行案: ROADMAP整理

目的:

- `docs/ROADMAP.md` を長期実装順、wave履歴、MVP境界、保留判断の正本に寄せる。
- 現在地・次タスク運用は `PROJECT_CONTROL.md` / `docs/HANDOFF.md` へ寄せる。

実行順:

1. `docs/ROADMAP.md` の `Current Position`, `Next Task`, `Completed Foundation`, `Implementation Milestones` の重複を棚卸しする。
2. 完了済みWaveの詳細を、`docs/archive/IMPLEMENTATION_HISTORY.md` への参照に変えられる箇所を特定する。
3. `## 5. Next Task` の古い内容を現在のP0優先順と照合する。
4. ROADMAPには長期順序、MVP境界、保留判断を残す。
5. 1回のPRではROADMAPだけを短縮する。

残すべき内容:

- 長期waveの順序。
- 採用 / 不採用の理由。
- Pending Decisions。
- MVP境界。

逃がす内容:

- 実装済みwaveの詳細な作業ログ。
- 直近実行タスク。
- WBS status。

## 7. Phase 3-D 実行案: release docs整理

目的:

- release関連の正本を役割別に分ける。
- WBS、商用方針、司令塔、Dashboardの重複を減らす。

役割分担:

| File | 残す内容 | 逃がす内容 |
|---|---|---|
| `docs/release/RELEASE_WBS.md` | ID、Task、Status、Priority、Done Criteria、必要なら短いSchedule | 商用価値説明、Go / No-Go詳細、画像戦略の長文 |
| `docs/release/COMMERCIALIZATION_ROADMAP.md` | 商用MVP、Do Not Build、Image Strategy、Phase Plan、Go / No-Go、Safety Principle | タスクstatus、詳細な実装手順、WBS表の複製 |
| `PROJECT_CONTROL.md` | P0優先順と正本リンク | release詳細本文 |
| `STATUS_DASHBOARD.html` | WBS snapshotとP0カテゴリの人間用ビュー | 正本相当の詳細説明 |

実行順:

1. WBSのstatus棚卸しを先に行う。
2. `AI-001` / `AI-002` / `TEMPO-001` / `ARC-008` / `STORY-005` / `STORY-006` など、仕様文書に既にあるがWBSではtodoの項目を「仕様done / 実装todo / 検証todo」に分ける案を作る。
3. Commercialization RoadmapのThree Hook / Story Continuation / Safety詳細を、方針として必要な粒度に保つ。
4. Dashboardはrelease docsの要約ビューとして更新するだけにする。
5. 1回のPRではrelease docsだけを扱う。

## 8. 安全ルール

- いきなり削除しない。
- まず短縮対象を1ファイルずつ扱う。
- 短縮前に、対象本文が `PROJECT_CONTROL.md` / `docs/ROADMAP.md` / `docs/archive/IMPLEMENTATION_HISTORY.md` / release docs のどこに残るか確認する。
- 各短縮後に `rg` で参照確認する。
- `git diff --check` を必ず実行する。
- `git diff --stat` と `git status --short` を報告する。
- コード変更禁止。
- ファイル移動禁止。
- 既存ファイル削除禁止。
- `STATUS_DASHBOARD.html` を正本化しない。
- Markdown正本をHTMLへ置き換えない。
- prompt / generator / validator / tests から参照される仕様docsは短縮対象にしない。
- `docs/archive/IMPLEMENTATION_HISTORY.md` はarchiveだが、履歴台帳として消さない。

## 9. 推奨確認コマンド

```sh
rg -n "docs/HANDOFF.md|docs/ROADMAP.md|docs/release/RELEASE_WBS.md|docs/release/COMMERCIALIZATION_ROADMAP.md|docs/archive/IMPLEMENTATION_HISTORY.md|STATUS_DASHBOARD.html" .
rg -n "Three Hook|Arc Closure|Story Continuation|AI Playtest|Go / No-Go|WebUI|Security|Image" PROJECT_CONTROL.md docs/HANDOFF.md docs/ROADMAP.md docs/release docs/archive/IMPLEMENTATION_HISTORY.md STATUS_DASHBOARD.html
rg -n "docs/(CORE_CONCEPT|STATE_STRUCTURE|NEW_SESSION_INITIALIZATION|EVENT_CARD_PLAYABILITY|VOICE_CONTINUITY|GROWTH_UPDATE_LOOP|ROMANCE_INTIMACY_GROWTH|RESUME_SMOKE_TEST|STORY_RELATIONSHIP_ACCUMULATION|CRISIS_COMBAT_ABILITY_CONSTRAINT_LOOP|ENGINE_RUNNER)\\.md" prompt tools scripts tests
git diff --check
git diff --stat
git status --short
```

`docs/INTEGRITY_AUDIT_20260505.md` は過去監査の引用が多いため、通常の参照確認では必要に応じて別扱いにする。
