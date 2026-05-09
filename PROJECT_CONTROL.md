# LILIA Project Control

このファイルは、人間とCodexが最初に読む1枚の司令塔である。
詳細仕様をここへ統合しない。どのMarkdownを正本として読むか、何を補助資料として扱うか、何を将来archiveへ逃がせるかだけを決める。

## 現在地

LILIAは、会話・選択・物語を記憶し、関係性と人格の出方が少しずつ変化していくAI恋愛シミュレーションである。
LILIAを所有物、攻略対象、ユーザーに都合よく最適化される存在として扱わない。

2026-05時点の現在地:

- CLI中心のMVP基盤は進んでいる。`new` / Q1-Q9 / AI profile / story spine / downstream docs / `scene-tick` / `apply-turn` / resume系validatorは到達済み。
- 商用βとしては未到達。WebUI、画像PoC、課金、利用規約、β募集導線、ユーザー向けLLM runtime分離、安全対策、外部テストが残っている。
- β前P0は、実プレイの保存再開、Three Hook Spine、Story Continuation / Travel Branch、AI Playtest Smoke、WebUI、安全分離、画像PoCに集中する。
- `STATUS_DASHBOARD.html` は人間用ビューであり、正本ではない。Markdown正本をHTMLに置き換えない。

## βまでの優先順位

β前は `docs/release/RELEASE_WBS.md` のP0をタスク正本にする。
ただし、設計思想や仕様判断は該当docsを優先する。

1. `P-002` / `P-003` / `P-004`: save / apply-turn、resume 1ターン目、event_card playableの実機確認。
2. `HOOK-001` から `HOOK-007`: Three Hook Spine MVP。脱線しても Main Hook / Relationship Hook / Life-Exploration Hook のどれかへ戻れること。
3. `ARC-001` から `ARC-007`: Story Continuation / Travel Branch MVP。初期story完了後の次arc、大移動branch、LILIA同行可否、未解決arc上限。
4. `AI-001` 以降: AI Playtest Smoke。normal / passive / boundary / attacker / wanderer / travelerを使い、巻き戻り、停滞、漏洩、脱線耐性を見る。
5. `WEB-*` / `SEC-*`: WebUIと安全分離。商用βでは、ユーザー向けLLMがshell、filesystem、repo root、secret、他ユーザーsessionへ到達しないこと。
6. `IMG-*`: 節目画像PoC。同一人物性、可愛さ、商用サンプルとしての安定性を確認する。
7. `PAY-*` / `MKT-*` / `REL-*`: 利用規約、決済、β募集、身内テスト、外部テスト、Go / No-Go。

注意:

- `docs/release/COMMERCIALIZATION_ROADMAP.md` には商用βスコープがかなり書かれているが、`docs/release/RELEASE_WBS.md` の一部タスクはまだtodoである。次回以降、仕様記述済みと実装済みを分けて棚卸しする。
- `docs/testing/AI_PLAYTEST_PLAN.md` は大量ベンチを非目標にしている。一方、WBSには100ターン級smokeがある。これは常時大量ベンチではなく、β前の軽量release smokeとして扱う。

## 正本ファイル一覧

### 入口 / 司令塔

- `AGENTS.md`: Codexが最初に読む入口。短い作業ルールだけを置く。
- `PROJECT_CONTROL.md`: 人間とCodexの司令塔。現在地、正本一覧、優先順位、archive候補を置く。
- `docs/CORE_CONCEPT.md`: LILIAの最上位思想。
- `docs/ROADMAP.md`: 長期実装順、MVP境界、保留判断の正本。
- `docs/HANDOFF.md`: 直近作業、次タスク、引き継ぎの正本。長期実装順は `docs/ROADMAP.md` を優先する。

### 商用β / リリース管理

- `docs/release/RELEASE_WBS.md`: βまでのタスク、優先度、状態、完了条件の正本。
- `docs/release/COMMERCIALIZATION_ROADMAP.md`: 商用MVP境界、Go / No-Go、画像戦略、安全原則、段階計画の正本。
- `docs/specs/PLAY_MODE_SPEC.md`: Play Mode本文品質、Lightweight Tempo Guard、Arc Closure Guardの正本。
- `docs/testing/AI_PLAYTEST_PLAN.md`: AI Playtestのpersona、loop、judge、report形式の正本。
- `docs/archive/IMPLEMENTATION_HISTORY.md`: 完了済みWaveと実装履歴の台帳。現在ステータスや次タスクの正本にはしない。

### session / prompt / state

- `docs/STATE_STRUCTURE.md`: session/state構造と各ファイル責務の正本。
- `docs/NEW_SESSION_INITIALIZATION.md`: Q&Aから実sessionへ初期生成する順序と保存粒度の正本。
- `docs/LILIA_PERSONA_PROFILE.md`: `lilia/main/profile.md` の目的、責務、初回scene前の使い方の正本。
- `docs/PLAYER_INPUT.md`: 行動・発言と内心を分けるプレイヤー入力ルールの正本。
- `prompt/core.md`: 会話生成、Play Mode / Save Mode境界、Example Anchoring Controlの正本。
- `prompt/startup.md`: `new` / `resume` / `consult` / `unknown` の起動分岐正本。
- `prompt/newgame.md`: 新規開始Q&Aと初期化時の実行prompt正本。
- `prompt/save_resume.md`: Save Mode / Resume Modeの実行prompt正本。

### 体験品質 / 関係成長

- `docs/EVENT_CARD_PLAYABILITY.md`: `current/event_card.md` を今触れる可視イベントにする正本。
- `docs/VOICE_CONTINUITY.md`: 声、呼び方、距離感、記憶、境界線を巻き戻さない正本。
- `docs/ROMANCE_INTIMACY_GROWTH.md`: 親密、官能、合意、境界線、aftercareの正本。
- `docs/RELATIONSHIP_CHANGE_AUDIT.md`: AFFINITY / bond非採用と文字ベース関係変化監査の正本。
- `docs/GROWTH_UPDATE_LOOP.md`: Save Modeで何をどこへ保存更新するかの正本。
- `docs/STORY_RELATIONSHIP_ACCUMULATION.md`: Eventを関係のStoryとして積み上げる正本。
- `docs/STORY_FUNCTION_FRAMEWORK.md`: story / scene / event_cardの機能診断フレーム。固定プロット表ではない。
- `docs/EMOTIONAL_DESIGN_PRINCIPLES.md`: story / scene / event_card / dialogueの感情設計正本。

### 条件付き仕様 / 技術仕様 / 検証

- `docs/OPENING_SCENE_GENERATION.md`: 初回scene冒頭生成とOpening Planの正本。
- `docs/CRISIS_COMBAT_ABILITY_CONSTRAINT_LOOP.md`: 危機、戦闘、能力を関係変化へ接続する条件付き正本。
- `docs/RESUME_SMOKE_TEST.md`: `new -> first scene -> save -> resume` の手動smoke正本。
- `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md`: repo / docs / prompt / template / gameplayの横断整合チェック正本。
- `docs/ENGINE_RUNNER.md`: LLM CLI runner境界の正本。

## 補助資料 / ビュー

以下は正本ではない。必要時だけ参照する。

- `STATUS_DASHBOARD.html`: 人間用ビュー。Markdown正本の代替ではない。
- `docs/DOCUMENT_REORGANIZATION_PLAN.md`: Phase 2-Aの整理計画。将来の移動案と参照修正候補。
- `docs/DOCUMENT_DEDUPLICATION_PLAN.md`: Phase 3-Aの重複整理計画。HANDOFF / ROADMAP / release docs の短縮候補。
- `docs/CODEX_ROLLOUT_LOGS.md`: Codexログ取り込み運用メモ。
- `docs/INTEGRITY_AUDIT_20260505.md`: 2026-05-05時点の大型監査レポート。判断の証跡であり、現在仕様の正本ではない。
- `docs/CLAUDE.md` / `prompt/CLAUDE.md` / `references/CLAUDE.md`: 自動生成memory系の未追跡メモ。設計正本ではない。

## 作業別の読み方

毎回すべてを読まない。
まず `PROJECT_CONTROL.md` で正本を確認し、作業に必要なものだけ読む。

- 開発再開 / 引き継ぎ: `docs/HANDOFF.md`, `docs/ROADMAP.md`, `docs/release/RELEASE_WBS.md`
- 商用β判断: `docs/release/COMMERCIALIZATION_ROADMAP.md`, `docs/release/RELEASE_WBS.md`, `docs/testing/AI_PLAYTEST_PLAN.md`
- Play Mode品質: `docs/specs/PLAY_MODE_SPEC.md`, `prompt/core.md`, `docs/EVENT_CARD_PLAYABILITY.md`, `docs/VOICE_CONTINUITY.md`
- new / session生成: `prompt/newgame.md`, `docs/NEW_SESSION_INITIALIZATION.md`, `docs/STATE_STRUCTURE.md`, `docs/LILIA_PERSONA_PROFILE.md`
- save / resume / state更新: `prompt/save_resume.md`, `docs/GROWTH_UPDATE_LOOP.md`, `docs/RESUME_SMOKE_TEST.md`
- story / event設計: `docs/STORY_RELATIONSHIP_ACCUMULATION.md`, `docs/STORY_FUNCTION_FRAMEWORK.md`, `docs/EMOTIONAL_DESIGN_PRINCIPLES.md`
- 親密 / 境界線: `docs/ROMANCE_INTIMACY_GROWTH.md`, `docs/RELATIONSHIP_CHANGE_AUDIT.md`, `docs/VOICE_CONTINUITY.md`
- 危機 / 能力: `docs/CRISIS_COMBAT_ABILITY_CONSTRAINT_LOOP.md`
- 技術生成 / CLI runner: `docs/ENGINE_RUNNER.md`
- 横断監査: `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md`, `docs/INTEGRITY_AUDIT_20260505.md`

## WBS / ROADMAP / HANDOFF / Dashboard の役割分担

- `docs/release/RELEASE_WBS.md`: βまでのタスク正本。ID、優先度、状態、完了条件はここを更新する。
- `docs/ROADMAP.md`: 長期順序とMVP境界の正本。実装順やMVP境界を変えたらここへ理由を短く残す。
- `docs/HANDOFF.md`: 直近の現在地、次タスク、引き継ぎだけを書く。Wave履歴や長期計画を増やしすぎない。
- `STATUS_DASHBOARD.html`: 人間用ビュー。古くなる可能性があるため、正本として扱わない。Markdown正本をHTMLへ置き換えない。

更新判断:

- タスク状態が変わったら `docs/release/RELEASE_WBS.md`。
- 実装順、MVP境界、保留判断が変わったら `docs/ROADMAP.md`。
- 次にCodexへ渡す作業、直近の注意、引き継ぎが変わったら `docs/HANDOFF.md`。
- 見た目で共有したい時だけ `STATUS_DASHBOARD.html` を更新する。ただしDashboardだけ更新して正本を変えた扱いにしない。

## 次にCodexへ投げるタスク

優先順:

1. `docs/release/RELEASE_WBS.md` のstatus棚卸し。既に仕様が書かれている `AI-001` / `AI-002` / `TEMPO-001` / `ARC-008` / `STORY-005` / `STORY-006` などを、仕様done・実装todoに分けて整理する。
2. `docs/HANDOFF.md` の圧縮。直近作業、次タスク、注意点に絞り、古いWave履歴は `docs/archive/IMPLEMENTATION_HISTORY.md` へ寄せる方針を作る。
3. `docs/ROADMAP.md` の完了Wave詳細を履歴側へ寄せる候補整理。ROADMAPは現在地、次順、保留判断に寄せる。
4. `P-002` / `P-003` / `P-004` の実機確認計画を1枚化する。`save -> apply-turn -> resume 1ターン目 -> event_card playable` を最短で見る。
5. Three Hook Spine MVPの最小実装範囲を確定する。`HOOK-001` から始め、既存 `docs/specs/PLAY_MODE_SPEC.md` と `docs/STORY_RELATIONSHIP_ACCUMULATION.md` を正本として使う。
6. `STATUS_DASHBOARD.html` を「snapshot / human view」と明記するか、WBSから生成する運用に寄せる。

## archive候補

以下は将来の統合・追加整理候補である。移動済みのファイルは現在のパスを正とする。

- `docs/INTEGRITY_AUDIT_20260505.md`: 一回性の大型監査レポート。`docs/archive/audits/` 相当へ移す候補。正本ではなく証跡。
- `docs/CLAUDE.md`: 自動生成memory系。未追跡ファイルであり、設計正本にしない。
- `prompt/CLAUDE.md`: 自動生成memory系。未追跡ファイルであり、prompt正本にしない。
- `references/CLAUDE.md`: 自動生成memory系。未追跡ファイルであり、reference正本にしない。
- `STATUS_DASHBOARD.html`: 正本ではなくスナップショットビュー。トップ維持。古い表示とWBSの集計ズレが出るため、将来は生成ビュー化候補。
- `docs/HANDOFF.md` の古いWave履歴: `docs/archive/IMPLEMENTATION_HISTORY.md` へ統合候補。
- `docs/ROADMAP.md` の完了Wave詳細: `docs/archive/IMPLEMENTATION_HISTORY.md` へ統合候補。ただしROADMAP本体は正本として残す。
- `docs/archive/IMPLEMENTATION_HISTORY.md` のPending / Commercialization Gap: `docs/ROADMAP.md` / `docs/release/RELEASE_WBS.md` と重複するため、履歴台帳に純化する候補。

## 既知の重複・ズレ

- `STATUS_DASHBOARD.html` の集計は `docs/release/RELEASE_WBS.md` とズレる可能性がある。Dashboardを正本にしない。
- `docs/release/RELEASE_WBS.md` の一部todoは、仕様文書上は既に定義済みのものを含む。次回棚卸しで、仕様doneと実装doneを分ける。
- `prompt/core.md` と `prompt/save_resume.md` でautosave表現に差がある。現行運用では、`prompt/save_resume.md` の毎ターン `scene-tick` と `autosave_required: true` 時のSave Mode遷移を優先して確認する。
- `docs/HANDOFF.md` と `docs/ROADMAP.md` は履歴が重複している。HANDOFFは直近、ROADMAPは長期、IMPLEMENTATION_HISTORYは履歴に分離していく。
