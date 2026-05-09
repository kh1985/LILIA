# LILIA Document Reorganization Plan

この文書は、Phase 2-A のドキュメント整理計画である。
今回はファイル移動、削除、コード変更、既存参照パス修正はしない。

目的は、トップレベル Markdown と `docs/` 配下を将来整理する前に、どのファイルをどこへ移せるか、どの参照を直す必要があるか、何を動かすと危険かを明確にすることである。

## 0. 採用 / 不採用

採用するもの:

- `PROJECT_CONTROL.md` の役割分担を採用する。`PROJECT_CONTROL.md` は司令塔、`AGENTS.md` は入口、Markdown 正本は維持する。
- `docs/ROADMAP.md` は長期順序、`docs/HANDOFF.md` は直近引き継ぎ、`RELEASE_WBS.md` はβまでのタスク正本として分離する。
- `STATUS_DASHBOARD.html` は人間用ビューとして扱い、Markdown 正本の代替にしない。
- 将来移動する場合は、移動と参照パス修正を同じ作業単位で行う。

採用しないもの:

- 今回の Phase 2-A では、既存ファイルの移動、削除、参照修正、コード変更をしない。
- prompt から直接参照される `docs/*` 正本を、整理目的だけで archive 候補にしない。
- `STATUS_DASHBOARD.html` を正本化しない。Markdown 正本を HTML に置き換えない。

## A. 現在のトップレベルファイルの役割

| File | Current role | Notes |
|---|---|---|
| `AGENTS.md` | Codex / Claude が最初に読む入口。作業開始時の読み順、LILIAの中核、作業原則、更新ルールを短く置く。 | トップ維持。詳細な正本一覧は `PROJECT_CONTROL.md` に委譲済み。 |
| `PROJECT_CONTROL.md` | 人間と Codex の司令塔。現在地、優先順位、正本一覧、補助資料、作業別の読み方、archive候補、既知の重複を管理する。 | トップ維持。ここへ詳細仕様を統合しすぎない。 |
| `RELEASE_WBS.md` | 商用βまでのタスク、状態、優先度、完了条件を管理するWBS正本。 | 将来 `docs/release/` 移動候補。ただしβタスク正本なので参照修正は必須。 |
| `PLAY_MODE_SPEC.md` | Play Mode本文品質、Lightweight Tempo Guard、Arc Closure Guardの仕様。 | 将来 `docs/specs/` 移動候補。prompt から直接参照あり。 |
| `IMPLEMENTATION_HISTORY.md` | 完了済みWaveと主要実装履歴の台帳。現在ステータスや次タスクの正本にはしない。 | 将来 `docs/archive/history/` または `docs/history/` 移動候補。 |
| `COMMERCIALIZATION_ROADMAP.md` | 商用MVP境界、Go / No-Go、画像戦略、安全原則、段階計画の正本。 | 将来 `docs/release/` 移動候補。 |
| `AI_PLAYTEST_PLAN.md` | AI Playtest Smoke の persona、loop、judge、report形式の正本。 | 将来 `docs/testing/` 移動候補。 |
| `STATUS_DASHBOARD.html` | 人間用HTMLビュー。WBSやRoadmap等の状況を見やすくするスナップショット。 | 正本ではない。トップ維持または将来 `docs/views/` / `docs/release/status/` 候補。 |

## B. 将来の配置案

| Current path | Future path candidate | Priority | Rationale |
|---|---|---|---|
| `AGENTS.md` | Keep at top level | Must keep | Codex / Claude の入口。移動すると作業開始手順が壊れる。 |
| `PROJECT_CONTROL.md` | Keep at top level | Must keep | 人間と Codex の司令塔。正本一覧と読み方の中心。 |
| `PLAY_MODE_SPEC.md` | `docs/specs/PLAY_MODE_SPEC.md` | Candidate | Play Mode品質仕様であり、`docs/specs/` に寄せると仕様群として自然。 |
| `AI_PLAYTEST_PLAN.md` | `docs/testing/AI_PLAYTEST_PLAN.md` | Candidate | AI Playtest Smoke の計画であり、testing配下が自然。 |
| `IMPLEMENTATION_HISTORY.md` | `docs/archive/history/IMPLEMENTATION_HISTORY.md` | Candidate | 完了済みWaveの履歴台帳。現在地や次タスクから分離する。履歴として頻繁に参照するなら `docs/history/IMPLEMENTATION_HISTORY.md` も候補。 |
| `COMMERCIALIZATION_ROADMAP.md` | `docs/release/COMMERCIALIZATION_ROADMAP.md` | Candidate | 商用β判断、Go / No-Go、段階計画は release 配下が自然。 |
| `RELEASE_WBS.md` | `docs/release/RELEASE_WBS.md` or keep at top level | Caution | βタスク正本で参照が多い。短期はトップ維持、Phase 2-Bでまとめて移動が安全。 |
| `STATUS_DASHBOARD.html` | Keep at top level, or `docs/views/STATUS_DASHBOARD.html` | Caution | 人間用ビュー。正本ではない。移動より先に snapshot / generated view の扱いを明記する。 |

将来ディレクトリ案:

- `docs/specs/`: Play Mode、体験品質、session / prompt仕様などの仕様文書。ただし既存 `docs/*` 正本の一括移動はしない。
- `docs/testing/`: 初回は `AI_PLAYTEST_PLAN.md` 向けの移動先候補。既存の `docs/RESUME_SMOKE_TEST.md` や `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md` をまとめて動かす意味ではない。
- `docs/release/`: 商用β、WBS、Go / No-Go、利用規約準備、リリース判断。
- `docs/archive/history/`: 完了済みWave、古い実装履歴、handoff / roadmapから退避した履歴。
- `docs/archive/audits/`: 一回性の大型監査レポート。
- `docs/views/`: HTMLや生成ビュー。Markdown正本とは別扱い。

## C. 移動してはいけない、または慎重に扱うファイル

### トップ維持が安全なファイル

| File | Treatment | Reason |
|---|---|---|
| `AGENTS.md` | Move禁止 | Codex / Claude の入口。ここが変わると作業開始手順が壊れる。 |
| `PROJECT_CONTROL.md` | Move禁止 | 司令塔。詳細正本の所在を示す中心なのでトップ維持。 |
| `docs/CORE_CONCEPT.md` | Move禁止に近い | AGENTS / prompt / PROJECT_CONTROL から中核思想として参照される。 |
| `docs/ROADMAP.md` | 慎重 | 長期順序とMVP境界の正本。AGENTS / PROJECT_CONTROL / 他docsから参照される。 |
| `docs/HANDOFF.md` | 慎重 | 直近引き継ぎの正本。AGENTS / prompt/startup から参照される。 |

### prompt から直接参照される docs 正本

以下は prompt から直接参照されるため、整理だけを理由に移動しない。
移動する場合は prompt 側の参照修正と、起動 / new / save / resume の読み順確認を同じ作業で行う。

- `docs/CORE_CONCEPT.md`
- `docs/VOICE_CONTINUITY.md`
- `docs/ROMANCE_INTIMACY_GROWTH.md`
- `docs/RESUME_SMOKE_TEST.md`
- `docs/GROWTH_UPDATE_LOOP.md`
- `docs/EVENT_CARD_PLAYABILITY.md`
- `docs/STORY_RELATIONSHIP_ACCUMULATION.md`
- `docs/EMOTIONAL_DESIGN_PRINCIPLES.md`
- `docs/NEW_SESSION_INITIALIZATION.md`
- `docs/STATE_STRUCTURE.md`
- `docs/LILIA_PERSONA_PROFILE.md`
- `docs/CRISIS_COMBAT_ABILITY_CONSTRAINT_LOOP.md`
- `docs/HANDOFF.md`

### validator / generator / tests から直接参照される docs

以下は説明文、生成prompt、validatorコメント、手動チェックリストに出てくる。
コード上の import ではないが、移動時には参照修正が必要になる。

| Referenced doc | Reference sources |
|---|---|
| `docs/EMOTIONAL_DESIGN_PRINCIPLES.md` | `tools/character/profile_generator.py`, `tools/session/document_generator.py`, `tools/story/spine_generator.py`, `prompt/core.md`, `docs/ROADMAP.md` |
| `docs/EVENT_CARD_PLAYABILITY.md` | `tools/session/document_validator.py`, `prompt/core.md`, `prompt/newgame.md`, `prompt/save_resume.md`, `prompt/style_reference.md` |
| `docs/RESUME_SMOKE_TEST.md` | `tests/resume_smoke/manual_checklist.md`, `tests/mvp_playtest/manual_checklist.md`, `prompt/core.md`, `prompt/newgame.md`, `prompt/save_resume.md`, `prompt/startup.md` |
| `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md` | `tests/mvp_playtest/manual_checklist.md`, `tests/resume_smoke/manual_checklist.md`, `docs/ROADMAP.md` |
| `docs/VOICE_CONTINUITY.md` | prompt群、`docs/ROADMAP.md` |
| `docs/ROMANCE_INTIMACY_GROWTH.md` | prompt群、`docs/ROADMAP.md` |
| `docs/GROWTH_UPDATE_LOOP.md` | prompt群、`docs/ROADMAP.md` |
| `docs/NEW_SESSION_INITIALIZATION.md` | `prompt/newgame.md`, `prompt/save_resume.md`, `prompt/style_reference.md`, `docs/ROADMAP.md` |
| `docs/STATE_STRUCTURE.md` | `prompt/newgame.md`, `prompt/save_resume.md`, `prompt/startup.md`, `docs/ROADMAP.md` |
| `docs/LILIA_PERSONA_PROFILE.md` | `prompt/newgame.md`, `prompt/save_resume.md`, `prompt/startup.md`, `docs/ROADMAP.md` |

### 正本として明記されている docs

`PROJECT_CONTROL.md` と `docs/ROADMAP.md` で正本として列挙されている `docs/*` は、Phase 2-B での移動対象から原則外す。
移動する場合は「仕様体系の再設計」として扱い、単なる整理作業とは分ける。

## D. 参照パス修正が必要な箇所

調査コマンド:

```sh
rg --line-number --fixed-strings \
  -e 'PLAY_MODE_SPEC.md' \
  -e 'AI_PLAYTEST_PLAN.md' \
  -e 'IMPLEMENTATION_HISTORY.md' \
  -e 'COMMERCIALIZATION_ROADMAP.md' \
  -e 'RELEASE_WBS.md' \
  -e 'STATUS_DASHBOARD.html' \
  -e 'docs/ROADMAP.md' \
  -e 'docs/HANDOFF.md' \
  --glob '!docs/INTEGRITY_AUDIT_20260505.md' \
  --glob '!logs/**' \
  --glob '!saves/**' \
  --glob '!playtests/**' .
```

`docs/INTEGRITY_AUDIT_20260505.md` には大量の過去監査引用があるため、通常の参照修正対象とは分ける。
将来この監査レポートを archive へ動かす場合は、歴史的引用として旧パスを残すか、監査レポート内だけ別途整理する。
この計画書自体にも棚卸し用の旧パス参照が多数あるため、Phase 2-B の旧パス残存確認では `docs/DOCUMENT_REORGANIZATION_PLAN.md` を除外するか、歴史的参照として扱う。

| Current reference | Source files / lines | Future path if moved | Fix proposal |
|---|---|---|---|
| `PLAY_MODE_SPEC.md` | `PROJECT_CONTROL.md:50`, `PROJECT_CONTROL.md:100`, `PROJECT_CONTROL.md:131`, `RELEASE_WBS.md:38`, `RELEASE_WBS.md:39`, `RELEASE_WBS.md:51`, `COMMERCIALIZATION_ROADMAP.md:206`, `prompt/core.md:240`, `docs/HANDOFF.md:46`, `docs/HANDOFF.md:121`, `IMPLEMENTATION_HISTORY.md:88` | `docs/specs/PLAY_MODE_SPEC.md` | Phase 2-Bで移動する場合、全参照を新パスへ更新。特に `prompt/core.md` は実行promptなので必ず同時修正する。 |
| `AI_PLAYTEST_PLAN.md` | `PROJECT_CONTROL.md:34`, `PROJECT_CONTROL.md:51`, `PROJECT_CONTROL.md:99`, `RELEASE_WBS.md:40`, `RELEASE_WBS.md:66`, `docs/HANDOFF.md:51`, `STATUS_DASHBOARD.html:454`, `STATUS_DASHBOARD.html:825`, `docs/ROADMAP.md:6` | `docs/testing/AI_PLAYTEST_PLAN.md` | WBS、Roadmap、Dashboardの参照を新パスへ更新。Dashboardはビューなので、移動前に生成元か手動HTMLかを確認する。 |
| `IMPLEMENTATION_HISTORY.md` | `PROJECT_CONTROL.md:52`, `PROJECT_CONTROL.md:128`, `PROJECT_CONTROL.md:144`, `PROJECT_CONTROL.md:145`, `PROJECT_CONTROL.md:146`, `docs/HANDOFF.md:51`, `STATUS_DASHBOARD.html:825`, `docs/ROADMAP.md:6` | `docs/archive/history/IMPLEMENTATION_HISTORY.md` or `docs/history/IMPLEMENTATION_HISTORY.md` | 履歴台帳として継続参照するなら `docs/history/` が読みやすい。archiveにするなら PROJECT_CONTROL の「履歴へ寄せる」記述も合わせて直す。 |
| `COMMERCIALIZATION_ROADMAP.md` | `PROJECT_CONTROL.md:33`, `PROJECT_CONTROL.md:49`, `PROJECT_CONTROL.md:99`, `RELEASE_WBS.md:25`, `docs/HANDOFF.md:51`, `STATUS_DASHBOARD.html:825`, `docs/ROADMAP.md:5`, `docs/ROADMAP.md:6` | `docs/release/COMMERCIALIZATION_ROADMAP.md` | release配下へ移す場合、WBSの完了条件とROADMAP冒頭を同時更新する。 |
| `RELEASE_WBS.md` | `AGENTS.md:56`, `PROJECT_CONTROL.md:20`, `PROJECT_CONTROL.md:33`, `PROJECT_CONTROL.md:48`, `PROJECT_CONTROL.md:98`, `PROJECT_CONTROL.md:99`, `PROJECT_CONTROL.md:111`, `PROJECT_CONTROL.md:118`, `PROJECT_CONTROL.md:127`, `PROJECT_CONTROL.md:146`, `PROJECT_CONTROL.md:151`, `COMMERCIALIZATION_ROADMAP.md:209`, `IMPLEMENTATION_HISTORY.md:91`, `IMPLEMENTATION_HISTORY.md:92`, `docs/ROADMAP.md:6`, `docs/ROADMAP.md:33`, `docs/ROADMAP.md:34`, `docs/ROADMAP.md:409`, `STATUS_DASHBOARD.html:519`, `STATUS_DASHBOARD.html:825` | `docs/release/RELEASE_WBS.md` or top維持 | 参照が多く、AGENTSからも更新ルールとして参照される。短期はトップ維持が最安全。移動する場合はAGENTSも含めて一括修正する。 |
| `STATUS_DASHBOARD.html` | `AGENTS.md:62`, `PROJECT_CONTROL.md:16`, `PROJECT_CONTROL.md:88`, `PROJECT_CONTROL.md:114`, `PROJECT_CONTROL.md:121`, `PROJECT_CONTROL.md:132`, `PROJECT_CONTROL.md:143`, `PROJECT_CONTROL.md:150`, `docs/HANDOFF.md:51` | top維持 or `docs/views/STATUS_DASHBOARD.html` | 正本ではないという記述を維持する。移動より前に snapshot / generated view の方針を確定する。 |
| `docs/ROADMAP.md` | `AGENTS.md:59`, `AGENTS.md:60`, `AGENTS.md:61`, `PROJECT_CONTROL.md:43`, `PROJECT_CONTROL.md:98`, `PROJECT_CONTROL.md:112`, `PROJECT_CONTROL.md:119`, `PROJECT_CONTROL.md:129`, `PROJECT_CONTROL.md:145`, `PROJECT_CONTROL.md:153`, `COMMERCIALIZATION_ROADMAP.md:204`, `IMPLEMENTATION_HISTORY.md:86`, `docs/HANDOFF.md:50`, `docs/HANDOFF.md:52`, `docs/HANDOFF.md:431`, `docs/HANDOFF.md:446`, `docs/NEW_SESSION_INITIALIZATION.md:30`, `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md:73`, `STATUS_DASHBOARD.html:825` | top-level docs維持 | 移動非推奨。長期順序正本として `docs/ROADMAP.md` の安定パスを維持する。 |
| `docs/HANDOFF.md` | `AGENTS.md:57`, `AGENTS.md:58`, `AGENTS.md:59`, `AGENTS.md:61`, `PROJECT_CONTROL.md:44`, `PROJECT_CONTROL.md:98`, `PROJECT_CONTROL.md:113`, `PROJECT_CONTROL.md:120`, `PROJECT_CONTROL.md:128`, `PROJECT_CONTROL.md:144`, `PROJECT_CONTROL.md:153`, `prompt/startup.md:57`, `prompt/startup.md:94`, `docs/ROADMAP.md:4`, `docs/ROADMAP.md:251`, `docs/ROADMAP.md:260`, `docs/ROADMAP.md:269`, `docs/ROADMAP.md:288`, `docs/ROADMAP.md:717`, `docs/STATE_STRUCTURE.md:283`, `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md:73`, `STATUS_DASHBOARD.html:825` | top-level docs維持 | 移動非推奨。古いWave履歴の圧縮は行うが、直近引き継ぎ正本としてパスは維持する。 |

scripts / tools 内の今回移動候補トップレベル文書への直接参照:

- `scripts/` と `tools/` に `PLAY_MODE_SPEC.md`, `AI_PLAYTEST_PLAN.md`, `IMPLEMENTATION_HISTORY.md`, `COMMERCIALIZATION_ROADMAP.md`, `RELEASE_WBS.md`, `STATUS_DASHBOARD.html`, `docs/ROADMAP.md`, `docs/HANDOFF.md` の直接参照は見つからなかった。
- ただし `tools/*` には `docs/EMOTIONAL_DESIGN_PRINCIPLES.md` と `docs/EVENT_CARD_PLAYABILITY.md` への説明上の参照がある。これらの docs は移動慎重扱い。

## E. 統合候補

### `IMPLEMENTATION_HISTORY.md` と `docs/ROADMAP.md`

現状:

- `IMPLEMENTATION_HISTORY.md` は完了済みWaveと実装履歴の台帳。
- `docs/ROADMAP.md` にも完了Wave詳細が長く残っている。

整理方針:

- 完了Waveの細かい履歴は `IMPLEMENTATION_HISTORY.md` へ寄せる。
- `docs/ROADMAP.md` は現在地、次の順序、MVP境界、保留判断に絞る。
- `docs/ROADMAP.md` 自体は正本なので archive 候補にしない。

### `RELEASE_WBS.md` と `COMMERCIALIZATION_ROADMAP.md`

現状:

- `RELEASE_WBS.md` はID、status、priority、done criteria のタスク管理。
- `COMMERCIALIZATION_ROADMAP.md` は商用MVP境界、Go / No-Go、画像戦略、安全原則、段階計画。
- 一部タスクは仕様文書上では定義済みだが、WBS上は todo のままになっている。

整理方針:

- 統合しない。
- WBSはタスク状態、Commercializationは商用判断に分ける。
- Phase 2-B以降で、WBSの todo を「仕様done / 実装todo / 検証todo」に棚卸しする。

### `docs/HANDOFF.md` と `PROJECT_CONTROL.md`

現状:

- `PROJECT_CONTROL.md` は読む地図、正本一覧、優先順位、archive候補。
- `docs/HANDOFF.md` は直近作業、次タスク、引き継ぎの正本だが、古いWave履歴が多い。

整理方針:

- 統合しない。
- `PROJECT_CONTROL.md` は司令塔として短く保つ。
- `docs/HANDOFF.md` は直近作業と次タスクへ圧縮し、古いWave履歴は `IMPLEMENTATION_HISTORY.md` へ寄せる。

### `STATUS_DASHBOARD.html` と `PROJECT_CONTROL.md`

現状:

- `STATUS_DASHBOARD.html` は人間用ビュー。
- `PROJECT_CONTROL.md` は司令塔であり、Markdown正本の所在を示す。

整理方針:

- `STATUS_DASHBOARD.html` を正本にしない。
- Dashboard更新だけでタスク状態や現在地を更新した扱いにしない。
- 将来は `RELEASE_WBS.md` から生成する運用、または `snapshot / human view` として明記する運用に寄せる。

## F. Phase 2-B の安全な実行順

1. `docs/specs/`, `docs/testing/`, `docs/release/`, `docs/archive/history/`, `docs/archive/audits/`, `docs/views/` のうち、実際に使うディレクトリだけを作成する。
2. 低リスクファイルから移動する。候補は `docs/INTEGRITY_AUDIT_20260505.md` のような一回性監査レポート。ただし今回の Phase 2-A では移動しない。
3. `IMPLEMENTATION_HISTORY.md` を履歴台帳に純化する。`docs/ROADMAP.md` / `docs/HANDOFF.md` から古いWave履歴を寄せる場合は、移動前に内容整理を済ませる。
4. `PLAY_MODE_SPEC.md` と `AI_PLAYTEST_PLAN.md` を移動する場合は、`prompt/core.md`, `RELEASE_WBS.md`, `COMMERCIALIZATION_ROADMAP.md`, `docs/HANDOFF.md`, `docs/ROADMAP.md`, `STATUS_DASHBOARD.html` の参照を同時に直す。
5. `COMMERCIALIZATION_ROADMAP.md` と `RELEASE_WBS.md` を `docs/release/` へ移す場合は、`AGENTS.md` と `PROJECT_CONTROL.md` の更新ルールも同時に直す。`RELEASE_WBS.md` は参照が多いため、短期トップ維持も許容する。
6. `STATUS_DASHBOARD.html` は最後に扱う。移動するなら、その前に「正本ではない」「snapshot / human view」であることをファイル内にも明記する。
7. 参照パスを一括修正する。`rg` で旧パスの残存を確認する。
8. `git diff --check` を実行する。
9. `git diff --stat` と `git status --short` を確認する。
10. 必要なら、小さな単位で commit / PR 化する。

## 今回の Phase 2-A で変更しないもの

- 既存ファイルの移動はしない。
- 既存ファイルの削除はしない。
- コードファイルは変更しない。
- 既存参照パスは修正しない。
- `STATUS_DASHBOARD.html` を正本扱いしない。
- `docs/` 配下の仕様正本を archive 候補にしない。
