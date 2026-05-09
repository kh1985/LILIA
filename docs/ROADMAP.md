# LILIA Roadmap

この文書は、LILIA開発の長期実装順、MVP境界、wave履歴を管理する正本である。
現在地、直近タスク、βタスク表、商用方針をここへ重複させすぎない。

- 現在地と優先順位: `PROJECT_CONTROL.md`
- 直近引き継ぎ: `docs/HANDOFF.md`
- βまでのタスク状態: `docs/release/RELEASE_WBS.md`
- 商用MVP境界、Go / No-Go、画像・安全方針: `docs/release/COMMERCIALIZATION_ROADMAP.md`
- 完了済み実装履歴の台帳: `docs/archive/IMPLEMENTATION_HISTORY.md`
- 人間用ビュー: `STATUS_DASHBOARD.html`。正本ではない。

## 1. Goal

LILIAを、`new` / `resume` で実際に遊べて、記憶・関係・人格の変化が保存される最小プレイ可能版にする。

LILIAは単なるヒロイン、キャラ、攻略対象、固定パートナーではなく、会話・選択・物語・記憶・関係性によって人格の出方が少しずつ変化するAI上の人格・記憶・関係存在として扱う。

官能・親密表現は削除対象ではない。
成人・合意・相互性・境界線を必須条件にしつつ、身体距離、触れる/触れない境界、沈黙、呼吸、体温、余韻、aftercareをLILIAの主要体験価値として扱う。

## 2. Source of Truth Map

| 領域 | 正本 |
|---|---|
| 中核思想 | `docs/CORE_CONCEPT.md` |
| 現在地、優先順位、正本一覧 | `PROJECT_CONTROL.md` |
| 直近作業、次タスク、引き継ぎ | `docs/HANDOFF.md` |
| 長期実装順、MVP境界、wave履歴 | `docs/ROADMAP.md` |
| 完了済み実装履歴の台帳 | `docs/archive/IMPLEMENTATION_HISTORY.md` |
| session / state構造 | `docs/STATE_STRUCTURE.md` |
| new / Q&A / 初期生成 | `docs/NEW_SESSION_INITIALIZATION.md`, `prompt/newgame.md` |
| startup / resume / save | `prompt/startup.md`, `prompt/save_resume.md`, `docs/RESUME_SMOKE_TEST.md` |
| Play Mode本文品質 | `prompt/core.md`, `docs/specs/PLAY_MODE_SPEC.md` |
| LILIA profile | `docs/LILIA_PERSONA_PROFILE.md` |
| player input境界 | `docs/PLAYER_INPUT.md` |
| event_card可プレイ性 | `docs/EVENT_CARD_PLAYABILITY.md` |
| voice continuity | `docs/VOICE_CONTINUITY.md` |
| romance / intimacy | `docs/ROMANCE_INTIMACY_GROWTH.md` |
| relationship change audit | `docs/RELATIONSHIP_CHANGE_AUDIT.md` |
| growth update | `docs/GROWTH_UPDATE_LOOP.md` |
| story / relationship accumulation | `docs/STORY_RELATIONSHIP_ACCUMULATION.md` |
| story / scene機能診断 | `docs/STORY_FUNCTION_FRAMEWORK.md` |
| opening scene | `docs/OPENING_SCENE_GENERATION.md` |
| emotional design | `docs/EMOTIONAL_DESIGN_PRINCIPLES.md` |
| crisis / combat / ability | `docs/CRISIS_COMBAT_ABILITY_CONSTRAINT_LOOP.md` |
| technical / gameplay integrity | `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md` |
| engine runner | `docs/ENGINE_RUNNER.md` |
| Codex rollout logs | `docs/CODEX_ROLLOUT_LOGS.md` |
| βタスク表 | `docs/release/RELEASE_WBS.md` |
| 商用化方針、Go / No-Go、安全、画像 | `docs/release/COMMERCIALIZATION_ROADMAP.md` |
| AI Playtest | `docs/testing/AI_PLAYTEST_PLAN.md` |
| 人間用Dashboard | `STATUS_DASHBOARD.html`。Markdown正本ではない |

## 3. Current Position

ここでは長期履歴のための短い現在地だけを置く。
詳細な現在地と優先順位は `PROJECT_CONTROL.md`、人間用の見取り図は `STATUS_DASHBOARD.html` を見る。

- CLI MVP / `new` / Q1-Q9 / `apply-newgame` / AI profile / story spine / downstream docs / `scene-tick` / `apply-turn` / resume系validator / growth smoke は実装済み。
- WebUI、画像PoC、Security、課金、利用規約、外部β確認は未完了。
- β前P0のstatusとDone Criteriaは `docs/release/RELEASE_WBS.md` を正本にする。
- 商用βのMust Have、Go / No-Go、画像戦略、安全原則は `docs/release/COMMERCIALIZATION_ROADMAP.md` を正本にする。
- 「実装済み」「仕様済み」「β完了」は同じ意味ではない。β完了扱いはWBSのDone Criteriaで判断する。

## 4. Long-Term Implementation Order

この表は長期順序の見取り図である。
現在の次タスクは `PROJECT_CONTROL.md` / `docs/HANDOFF.md`、タスクstatusは `docs/release/RELEASE_WBS.md` を見る。

| Order | Area | Purpose | Status source |
|---|---|---|---|
| 1 | Foundation | LILIAの中核思想、session構造、prompt境界、style参照、保存再開の足場を作る。 | Wave History / `docs/archive/IMPLEMENTATION_HISTORY.md` |
| 2 | AI-driven session generation | Q1-Q9、character YAML、AI profile、spines、13 downstream docsを生成する。 | Wave 11〜12.2 |
| 3 | Continuity / Playability gates | voice continuity、event_card playable、opening clarity、Example Anchoringを検査・抑制する。 | Wave 13〜16 / X / Y |
| 4 | Play / Save / Resume verification | `save` / `apply-turn` / `resume` / `event_card` の実プレイ確認を行う。 | `docs/release/RELEASE_WBS.md` の `P-002〜P-004` |
| 5 | Three Hook / Tempo | 脱線してもMain / Relationship / Life-Explorationへ戻れる進行骨格を作る。 | WBS `HOOK-*`, `TEMPO-*` |
| 6 | Story Continuation / Travel | 初期story後の次arc、大移動branch、LILIA同行可否、open arc上限を扱う。 | WBS `ARC-*` |
| 7 | AI Playtest Smoke | normal / passive / boundary / attacker / wanderer / travelerで破綻を検出する。 | `docs/testing/AI_PLAYTEST_PLAN.md`, WBS `AI-*` |
| 8 | WebUI / Security / Image | 商用β前にブラウザ体験、runtime分離、画像PoCを用意する。 | WBS `WEB-*`, `SEC-*`, `IMG-*` |
| 9 | Paid beta support | 規約、決済、募集、外部テスト、Go / No-Goを用意する。 | WBS `PAY-*`, `MKT-*`, `REL-*`; `docs/release/COMMERCIALIZATION_ROADMAP.md` |
| 10 | Post-beta expansion | 複数ヒロイン、異界 / 能力、漫画化、共同体、長期記憶拡張を検討する。 | `Pending / Future Work` |

## 5. Wave History

詳細な完了済み一覧は `docs/archive/IMPLEMENTATION_HISTORY.md` も参照する。
この表は「どのwaveで何をしたか」の読み取り用であり、βタスクstatusではない。

| Wave | Status | Summary |
|---|---|---|
| Wave 1 | done | 散文層・キャラ会議変換。LILIAの人格と会話の基礎を整えた。 |
| Wave 2 | done | echo拡張・`decision_index`。過去の反応や決定が次回の温度に残る足場を追加した。 |
| Wave 3 | done | 50作品参考カタログ。参照作品を本文模倣ではなく感情の骨として使う棚を作った。 |
| Wave 4 | done | Structure / Pattern Reference Libraries。`references/story_structure_stock.md` と `references/story_pattern_stock.md` を追加し、Story Diagnosisを接続した。 |
| Wave 5 | done | Story Spine導入。旧テンプレートから始まり、後続WaveでAI駆動の `current/story_spine.md` / `story/relationship_spine.md` へ移行した。 |
| Wave 6 | done | Opening Scene & Heroine Appearance。初回登場用promptと再登場時の表現参照を追加した。 |
| Wave 7 | done | Newgame Q&A Refinement & Protagonist Profile。Q&Aと主人公profileの保存先を整理した。 |
| Wave 8 | done | Knowledge Boundary Management。`current/knowledge_state.md` と meta / observable / shared / gm_only の境界を導入した。 |
| Wave 9 | done | Root Cure。例文固定、fallback literal、keyword固定、validator、loggingの問題を修正した。 |
| Wave 10 | done | Q&A Redesign。性格、見た目、出会い、主人公情報、呼称を聞くinteractive flowを整理した。 |
| Wave 10.1 | done | Q3-Q5 Independence Restoration。描写の縛り、表と内の差、内面に持っているものを再分離した。 |
| Wave 10.2 | done | Main Question Template Flexibility。傷だけでなく、選択、発見、変化、葛藤の問いを扱えるようにした。 |
| Wave 10.3 | done | Fallback Field Quality + Knowledge Boundary Meta HIDDEN。身体特徴混入やmeta推測を抑えた。 |
| Wave 10.4 | done | Protagonist Inner Monologue Boundary。行頭括弧を主人公の内心としてGM only扱いにした。 |
| Wave 11 | done | AI-driven Story / Relationship Spine Generation。spine生成をAI駆動へ移し、validatorと再生成を追加した。 |
| Wave 12.1 | done | AI-driven LILIA Persona Profile Generation。character YAMLから `lilia/main/profile.md` をAI生成する経路を追加した。 |
| Wave 12.2 | done | AI-driven Downstream Session Documents。profile / character YAML / spines / Q&A から13 downstream filesをAI生成する経路を追加した。 |
| Wave 13 | done | Voice Continuity Gate Validator。resume入口とapply-turn後のsoft fail validatorを追加した。 |
| Wave 14 | done | Event Card Playability Gate Validator。`current/event_card.md` が今触れる可視イベントかを検査するcheckerを追加した。 |
| Wave 15 | done | Engine Runner Refactor。LLM CLI runner境界を `docs/ENGINE_RUNNER.md` と共通runnerへ寄せた。 |
| Wave 16 | done | Opening Pattern Stock Integration。opening pattern stockを初回scene生成へ接続し、Opening Planを正本化した。 |
| Wave X-4 | done | Opening Plan / clarity_anchors Hard Requirement。主人公の職業・目的・場所・関係性が冒頭本文から読めるようにした。 |
| Wave Y-B1 | done | ヒロイン第一反応情報の抽象レベル分離。voice / state / event_card / hotset / sceneの似た反応情報を読み分けるルールを追加した。 |
| Wave Y-C | done | Heroine Entrance Density Profile / Opening Requirements。初登場の見た目、所作、職能、生活痕、矛盾、境界を多軸化した。 |
| Wave Y-D | done | Example Anchoring Control Generator Reference。`prompt/core.md` の共通原則をprofile generatorへ届かせる仕組みを追加した。 |
| Wave Y-F | done | Auto-save Chain Closure。`scene-tick` と `apply-turn` のSave Mode連鎖をprompt運用として閉じた。 |
| Wave Y-G | dropped | Terminal Recording via `script`。ANSIエスケープが多く実用にならず廃止した。 |
| Wave Y-H | done | Codex Rollout Logs Archive。`./lilia archive-codex-logs` と `docs/CODEX_ROLLOUT_LOGS.md` を追加した。 |
| Growth Smoke / Long Growth MVP | done | `growth-smoke` / `long-growth` / `dev-growth` とdev menu項目を追加し、複数segmentのtranscript / judge / summaryを保存する軽量成長観察を作った。 |
| Arc Closure Guard | spec done | `docs/specs/PLAY_MODE_SPEC.md` にsceneの核成立後、余韻を1〜2ターンで閉じる仕様を追加した。Judge実装やWBS完了扱いは別管理。 |
| Literary scene situations | done | `style/defaults/scene_situations.md` を追加し、文豪系9シチュエーションを `prompt/core.md` から参照する形で接続した。 |
| Emotional Design Principles | done | `docs/EMOTIONAL_DESIGN_PRINCIPLES.md` を正本化し、prompt / generator群から参照した。 |
| Hidden深化ベクトル軸名修正 | done | `relationship.md` の6軸を安心 / 欲情 / 共犯 / 生活 / 受容 / 摩耗に戻し、初期βでは通常進行メーターにしない方針を記録した。 |
| LILIA Individual Name | done | `session.json` に `lilia_name` / `lilia_display_name` を持たせ、作中名と作品名を分けた。 |

## 6. Implementation Notes by Area

### 6.1 Session / Generation

- `./lilia apply-newgame` は character YAML -> AI profile -> AI spines -> 13 downstream docs の順で初期反映する。
- `profile.md` は first scene前に読む人格正本であり、関係で育った内容は `core / voice / relationship / memory / beliefs` へ分解して保存する。
- `saves/` はgit管理外。実session本文、個人ログ、`/tmp` の実体はrepoに入れない。

### 6.2 Play / Save / Resume

- Play Modeでは通常応答を優先し、ファイル編集、diff、保存更新ログを割り込ませない。
- Save Modeでは `turn_update.md` を作り、`./lilia apply-turn <session> <turn_update.md>` で必要なstateだけ更新する。
- `scene-tick` はautosave counterを進める。10ターン到達時の保存連鎖はWave Y-Fでprompt運用として閉じたが、β完了はWBSの実機確認で判断する。

### 6.3 Quality Gates

- Voice Continuity Gate ValidatorはWave 13でsoft failとして導入した。hard fail化、呼び方厳密比較、relationship語彙リスト正本化は将来判断。
- Event Card Playability Gate ValidatorはWave 14で導入した。Crisis / Ability、Intimacy / Boundary、Truth Hidingの細部検査は別Wave候補。
- Opening Plan、clarity anchors、Example Anchoring Controlは、例文固定や初回sceneの情報不足を防ぐために維持する。

### 6.4 Long-term Boundary

- 初期MVPでは1人のLILIAとの関係が面白いことを優先する。
- AFFINITY / bond / 好感度 / 攻略ルートを正本にしない。
- heavy case engine、villain engine、combat engine、漫画化、複数ヒロイン、AI Harness本格運用は初期MVPに入れない。
- 参照作品や作者の直接模倣、固有名詞、台詞、展開順の流用をしない。

## 7. Pending / Future Work

このセクションは長期候補の索引であり、タスク表ではない。
P0 / P1 / status / Done Criteria は `docs/release/RELEASE_WBS.md` を正本にする。

### 7.1 β前P0として別管理するもの

- Play / Save / Resume確認: `P-002` / `P-003` / `P-004`
- Three Hook Spine MVP: `HOOK-001〜HOOK-007`
- Story Continuation / Travel Branch MVP: `ARC-001〜ARC-007`
- Arc Closure / Tempo Guard: `TEMPO-*`, `ARC-008〜ARC-011`
- AI Playtest Smoke: `AI-001〜AI-008`
- WebUI / Security / Image / Release: `WEB-*`, `SEC-*`, `IMG-*`, `REL-*`

詳細は `docs/release/RELEASE_WBS.md` を見る。
商用上の理由、Go / No-Go、安全原則、画像方針は `docs/release/COMMERCIALIZATION_ROADMAP.md` を見る。

### 7.2 中期候補

- Romance / Intimacy Growth Loop の実生成コード接続。
- Crisis / Combat / Ability Constraint Loop の実生成コード接続。
- Resume Smoke Test の自動化。
- Story / Relationship Accumulation Loop の動的生成。
- Hidden深化ベクトル運用ロジックの再検討。初期βでは通常進行メーターにしない。
- Deepening Tags機械チェック。inner-galge由来の14タグとヒロイン追加機構は未実装。
- Intimacy Stage / Consent Stage / Boundary State の機械チェック。
- 軽量 Integrity Audit Tool。
- Player Action Prompt改修。ユーザーが次に返せる入口を示すが、番号メニュー化は慎重に扱う。
- Wave Y-E: `document_generator` / `spine_generator` への Example Anchoring Control 導入。
- Wave Y-A: inner-galge runtime由来のテンポ管理ルールのうち、β後に残す重い調整。
- JSONL -> Markdown 変換。Codex rollout JSONLの可読化は必要時に検討する。
- ダイス機構。対象は世界事象のみで、LILIAの好意や内面は判定対象にしない。
- GraphRAG再検討。複数ヒロイン後、または長期セッションが十分伸びた後に再検討する。

### 7.3 Legacy Pending Items P-A through P-G

2026-05-07整理時の保留ラベルは、履歴と判断経緯として残す。
詳細タスクやstatusは `docs/release/RELEASE_WBS.md` を優先する。

| Label | Topic | Current treatment |
|---|---|---|
| P-A | テンポ管理 | β前は Lightweight Tempo Guard / Arc Closure Guard としてP0品質条件へ寄せる。重い文量スコア化は中期以降。 |
| P-B | Hidden深化ベクトル運用 | 初期βでは通常進行メーターにしない。深い関係到達後の質的管理候補として保持する。 |
| P-C | 深化タグ機械チェック | inner-galge由来の14タグとヒロイン追加機構は未実装。中期候補。 |
| P-D | 3本フック運用（戦闘なし版） | 2026-05-07にβ前P0へ格上げ。WBSの `HOOK-001〜HOOK-007` で管理する。 |
| P-D2 | Story Continuation / Travel Branch MVP | 2026-05-07にβ前P0として追加。WBSの `ARC-001〜ARC-007` で管理する。 |
| P-E | 世界移動・物語射程の境界 | 自然範囲、関係段階判定、射程外、世界観違反の4段階を仮案として保持する。 |
| P-F | NPC昇格 | 初期βではNPCをヒロインに昇格しない。複数ヒロインWaveで再判断する。 |
| P-G | 軽量Integrity Audit Tool | `docs/INTEGRITY_AUDIT_20260505.md` の手順を将来コマンド化する候補。 |

### 7.4 長期候補

- 複数ヒロイン管理。
- NPC TieringとNPC昇格。ただし初期βではNPCをヒロインに昇格しない。
- 共同体 / 生活 / ビジネス。
- 経営・お金回り。
- 世界・異界設定。
- 敵・組織・勢力クロック。
- 戦闘・能力系。
- 画像、漫画、export pipeline。
- 品質自動検証、AI Harness、本格自動プレイ。

## 8. Design Holds

実装前に判断が必要な議題:

- Hidden深化ベクトル: 0-5数値運用、自然言語運用、ハイブリッドのどれにするか。初期βでは本格運用しない。
- プレイヤー宣言応答ルール: 主人公の所持品 / 能力 / 行動はどこまで世界事実として扱うか。LILIAの内面や好意は対象外にする。
- ダイス機構: 何面ダイス、確率、適用シーン、物語反映の基準。
- GraphRAG: 導入タイミングと代替としての軽量Integrity Audit。
- 行動選択肢3つ提示: 返しやすさと番号メニュー禁止の緊張をどう扱うか。
- 世界移動・物語射程: 同じ街、別都市、物語射程外、世界観違反の境界。
- NPC昇格: 初期βではヒロイン非昇格。複数ヒロインWaveで再判断する。

## 9. Adoption Boundaries

採用するもの:

- MIRA: `voice / state / relationship / memory / beliefs`
- inner-galge: style defaults、romance/intimacy運用、memory model、validation、voice continuity、command導線、プレイヤーが触れる足場、更新ループ、参考作品から感情の骨を抽出して現在キャラへ変換する手順
- LIRIA: session構造、event_card、save/resume、archive、story_reference / Light Story Reference Pass、Story Reference Layer、selection signals、candidate shortlist、Reference Engine、style defaults、romance、case/runtimeの運用知見、Visible Request Gate、Truth Hiding Boundary、Mid-Story Activation Gate、integrity check、growth update

採用しないもの:

- LILIAを単なるヒロイン、攻略対象、固定パートナーとして扱う設計。
- 旧ハーレム攻略前提、旧AFFINITY数値、bond、好感度、攻略ルート。
- 固定台詞集、hotset正本化、毎ターン全ファイル更新、巨大ログ保存。
- 参照作者や作品の直接模倣、参照小説本文の保存・流用、固有名詞や展開順の模倣。
- 抽象的な違和感だけでevent_cardを進める運用。
- 親密sceneを雑な事件乱入で壊す運用。
- 最初からheavy case engine / villain / combat / manga pipelineをMVP必須にすること。

## 10. Update Rules

- マイルストーン、wave、MVP境界、設計保留の扱いが変わったら `docs/ROADMAP.md` を更新する。
- 現在地、優先順位、正本一覧は `PROJECT_CONTROL.md` を更新する。
- 直近作業、次タスク、再開時の注意は `docs/HANDOFF.md` を更新する。
- βタスクのstatus、priority、Done Criteriaは `docs/release/RELEASE_WBS.md` を更新する。
- 商用MVP境界、Go / No-Go、画像・安全方針は `docs/release/COMMERCIALIZATION_ROADMAP.md` を更新する。
- Dashboardは人間用ビューであり、正本更新の代替にしない。
- `prompt/core.md` の `Example Anchoring Control` を維持し、例文を本文生成へ流用しない。

## 11. Why This Order

LILIAはAI上の人格・記憶・関係存在であり、new/resumeだけでなく、関係・声・官能・事件・世界圧・検証が段階的に接続される必要がある。

旧LIRIA / inner-galgeには実装済みまたは検証済みの運用知見がある。
ただしLILIAは新規プロジェクトなので、旧固有設定ではなく、手順・責務・表現技法だけを移植する。

官能・親密表現はユーザー体験上の重要な魅力であり、削除ではなく安全条件つきで活かす。

実装順が共有されていないと、CodexがCLI、重い事件エンジン、画像・漫画化へ早く進みすぎるリスクがある。
まずは1人のLILIAとの関係が面白く、保存・再開で温度が落ちないことを優先する。

Story / Relationship Accumulation Loop を World Autonomy / Pressure Loop より先に置く理由は、外圧を先に大きくすると、LILIAとの関係ではなく世界設定が主役になりやすいためである。
先に、eventがmemory / relationship / beliefs / voiceへ残る線として積み重なる仕組みとNPC tierを固定し、その中で小さな外圧を扱う。
