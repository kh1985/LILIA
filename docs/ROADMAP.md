# LILIA Roadmap

この文書は、LILIA開発の長期実装順とMVP境界を管理する正本である。
思想・中核概念は `docs/CORE_CONCEPT.md`、直近の引き継ぎは `docs/HANDOFF.md`、state構造は `docs/STATE_STRUCTURE.md`、event_card可プレイ性は `docs/EVENT_CARD_PLAYABILITY.md`、voice continuityは `docs/VOICE_CONTINUITY.md`、romance/intimacy growthは `docs/ROMANCE_INTIMACY_GROWTH.md`、resume smokeは `docs/RESUME_SMOKE_TEST.md`、growth updateは `docs/GROWTH_UPDATE_LOOP.md`、story / relationship accumulationは `docs/STORY_RELATIONSHIP_ACCUMULATION.md`、crisis / combat / ability constraintは `docs/CRISIS_COMBAT_ABILITY_CONSTRAINT_LOOP.md`、technical / gameplay integrity checksは `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md` を正本にする。

## 1. Goal

LILIAを、`new` / `resume` で実際に遊べて、記憶・関係・人格の変化が保存される最小プレイ可能版にする。

LILIAは単なるヒロイン、キャラ、攻略対象、固定パートナーではなく、会話・選択・物語・記憶・関係性によって人格の出方が少しずつ変化するAI上の人格・記憶・関係存在として扱う。

官能・親密表現は削除対象ではない。
成人・合意・相互性・境界線を必須条件にしつつ、身体距離、触れる/触れない境界、沈黙、呼吸、体温、余韻、aftercareをLILIAの主要体験価値として扱う。

## 2. Current Position

- concept / growth basis: 完了
- save/resume 軽量読み順: 完了
- startup分岐: 完了
- state scaffold: 完了
- style reference scaffold: 完了
- Style Defaults / Intimacy Defaults Completion: 完了
- New Session Initialization: 設計仕様完了 / 実生成コード未実装
- Case / Event Card Playability Gate: 設計仕様完了 / 実生成コード未実装
- Relationship / Character Voice Continuity Gate: 設計仕様完了 / 実生成コード未実装
- Romance / Intimacy Growth Loop: 設計仕様完了 / 実生成コード未実装
- Resume Smoke Test: 手動smoke仕様完了 / 実生成コード未実装
- Growth Update Loop: 設計仕様完了 / 実生成コード未実装
- Story / Relationship Accumulation Loop: docs正本化完了 / テンプレート最小接続完了 / 実生成コード未実装
- Crisis / Combat / Ability Constraint Loop: docs正本化完了 / テンプレート最小接続完了 / 実生成コード未実装
- Technical + Gameplay Integrity Checks: docs正本化完了 / manual checklist最小接続完了 / 最小スクリプト未実装
- 旧LIRIA / inner-galge調査に基づく長期実装順の反映: 完了
- 次は Technical + Gameplay Integrity Checks の最小スクリプト要否確認、またはMVP Playtest準備

## 3. Completed Foundation

1. Concept / Growth Basis
   - `docs/CORE_CONCEPT.md` を正本として、LILIAの中核、価値提供、記憶、人格、設計原則を固定した。
   - Status: 完了

2. Save / Resume Reading Order
   - `prompt/save_resume.md` を正本として、保存対象と再開時の軽量読み順を固定した。
   - Status: 完了

3. Startup Flow
   - `prompt/startup.md` を正本として、起動直後の `new` / `resume` / `consult` / `unknown` 分岐を固定した。
   - Status: 設計仕様完了 / 実生成コード未実装

4. State Scaffold
   - `docs/STATE_STRUCTURE.md` と `templates/session/` で、最小state / memory / relationship / story / style構造を固定した。
   - Status: 完了

## 4. Implementation Milestones

1. Style Defaults / Intimacy Defaults Completion
   - `style/defaults/romance.md`、`tension.md`、`warmth.md`、`loss.md`、`quiet.md`、`landscape.md` をroot `style/defaults/` に追加する。
   - 旧LIRIA / inner-galge の作者別・場面別メソッドを、本文コピーや固有文体模倣ではなく、表現技法・温度・視点距離・余白の参照棚としてLILIA向けに移植する。
   - 官能・親密表現は削除しない。ベッドシーン、身体距離、触れる/触れない境界、沈黙、呼吸、体温、余韻、aftercareはLILIAの主要体験価値として残す。
   - 成人・合意・相互性・境界線を必須条件にする。
   - 旧ハーレム攻略、旧AFFINITY依存、kaneco固有、旧セッション固有設定は採用しない。
   - Status: 完了

2. New Session Initialization
   - `prompt/newgame.md` のQ&A結果から `session.json`、`current/*`、`lilia/main/*`、`story/*`、`style/*` を初期生成する。
   - 旧LIRIAの `create_session`、Initial Story Assembly、`extract_newgame_state_candidates` の思想を、LILIAの1人運用とMarkdown scaffoldへ軽量化して採用する。
   - 初回scene前に、関係温度、生活の足場、LILIAが守っているもの、避けているもの、小さな出来事、style参照を短く接続する。
   - `docs/NEW_SESSION_INITIALIZATION.md` を正本として、Q&Aから各ファイルへの写像、Light Story Reference Passの出力先、new直後resume可能な最小状態を固定した。
   - `templates/session/` は `session.json`、`current/event_card.md`、`current/hotset.md`、`style/rules.md` などを初期化ルールに合わせて補強済み。
   - Status: 完了

3. Case / Event Card Playability Gate
   - 旧LIRIAの Visible Request Gate、Truth Hiding Boundary、Mid-Story Activation Gate を、LILIAの `current/event_card.md` 向けに再設計する。
   - `event_card` は抽象的な違和感だけでなく、誰が、何で困り、何に触れるかを持つ。
   - 最低限、visible problem、first concrete action、handles 2-4個、if ignored、next visible change、relationship stakeを持たせる。
   - 真相は隠してよいが、依頼や場面の可プレイ性は隠さない。
   - `story/story_deck.md` は素材・圧・未回収札、`current/event_card.md` は今触れる可視イベントとして責務分離する。
   - `docs/EVENT_CARD_PLAYABILITY.md` を正本として、Gate通過条件、Gate失敗条件、Truth Hiding Boundary、Mid-Story Activation Gate、親密sceneとの接続を固定した。
   - `templates/session/current/event_card.md` は handles 2-4、Truth Hiding Boundary、ユーザーへの行動余地を保存できる形へ補強済み。
   - Status: 完了

4. Relationship / Character Voice Continuity Gate
   - LILIAの声、呼び方、関係認識、誤解、信頼、摩擦がresumeで巻き戻らないようにする。
   - inner-galge / LIRIA の memory model、validation、integrity check をLILIA向けに採用する。
   - `core fixed`、`historical fixed`、`echo`、`volatile` の分類を、`lilia/main/*`、`current/*`、`archive/*`、`hotset` に対応づける。
   - 重要場面前、親密場面前、衝突場面前には voice check を行い、`voice`、`relationship`、`beliefs`、直近memory、境界線を確認する。
   - `docs/VOICE_CONTINUITY.md` を正本として、Gate通過条件、Gate失敗条件、resume時の扱い、親密scene/衝突scene/境界線sceneの確認を固定した。
   - `templates/session/lilia/main/voice.md`、`relationship.md`、`memory.md`、`beliefs.md`、`current/relationship_overview.md`、`current/hotset.md` を、声と関係の継続確認に必要な最小欄へ補強済み。
   - Status: 完了

5. Romance / Intimacy Growth Loop
   - 親密・官能・ベッドシーンを、関係成長の主要ループとして扱う。
   - 自動報酬ではなく、関係段階、合意、相互性、境界線、aftercareを前提にする。
   - 官能を清潔化しすぎない。濃度は露骨な語彙ではなく、距離、沈黙、体温、呼吸、躊躇、視線、手元、余韻で上げる。
   - 旧LIRIA `prompt/romance.md` と `style/defaults/romance.md` の思想を参考にするが、旧AFFINITY数値や複数ヒロイン前提は採用しない。
   - `docs/ROMANCE_INTIMACY_GROWTH.md` を正本として、intimacy stage、consent stage、boundary state、aftercare memory、親密scene前Gate、親密scene後の保存先を固定した。
   - `templates/session/lilia/main/relationship.md`、`memory.md`、`beliefs.md`、`state.md`、`voice.md`、`current/relationship_overview.md`、`current/event_card.md`、`current/hotset.md`、`style/rules.md` を、親密成長とaftercare保存に必要な最小欄へ補強済み。
   - Status: 完了

6. Resume Smoke Test
   - 生成済みsessionを `resume` で軽量に読み、1ターン目の温度が落ちないか確認する。
   - 口調が巻き戻らないか、hotsetが正解ルートやtodoになっていないか、関係温度とevent_cardの入口が戻るかを見る。
   - `new -> first scene -> save -> resume` を最初の手動smokeとして固定する。
   - `docs/RESUME_SMOKE_TEST.md` を正本として、手動smokeの観点、resume 1ターン目の通過条件、failure examples、採用しない重い検証を固定した。
   - `tests/resume_smoke/manual_checklist.md` と `tests/resume_smoke/sample_session.md` を追加し、手動検証の足場を置いた。
   - Status: 完了

7. Growth Update Loop
   - 会話後に `state`、`relationship`、`memory`、`beliefs`、`hotset`、`event_card` をどう更新するかを実運用できる形にする。
   - 重要場面後は、what changed、what LILIA now believes、what was left unsaid、next pressure or promise を残す。
   - 関係が変わった出来事は `archive/beats/` に節目として保存する。
   - `docs/GROWTH_UPDATE_LOOP.md` を正本として、更新タイミング、各ファイルの保存責務、親密scene後/event_card後/archive/beatsの扱い、failure条件を固定した。
   - `templates/session/current/event_card.md` と `templates/session/story/story_deck.md` を、event_cardの進行状態と背景化した未回収札を扱える最小形へ補強した。
   - Status: 完了

8. Story / Relationship Accumulation Loop
   - イベントを点、ストーリーを線として扱い、出来事がLILIAの記憶、関係、beliefs、voiceへ残ることで物語が進む形にする。
   - 旧LIRIAの Story Reference Layer、selection signals、candidate shortlist、Reference Engine を、参照作品の模倣ではなく感情の骨の抽出として採用する。
   - inner-galge の `エピソードタイプ -> 参考作品 -> 感情の骨 -> 現在キャラへ変換 -> 分岐点 -> 書く` をLILIA向けに軽量化する。
   - NPCは Tier 0-5 で分類し、LILIAの記憶、関係、beliefsに影響した時だけ段階的に昇格させる。
   - World Autonomy / Pressure Loop は独立した大きな世界圧ではなく、このLoopの下位要素として扱う。
   - 下位要素としての World Autonomy / Pressure は、放置した出来事、未回収札、言い残し、境界線、約束、記録のズレが1-3 scene後に小さく戻ることとして扱う。
   - 親密sceneを雑な乱入で壊さず、life pressure、social pressure、relationship pressure、secret exposure pressureを生活、信用、沈黙、約束の小さな変化として扱う。
   - `docs/STORY_RELATIONSHIP_ACCUMULATION.md` を正本として、Event / Story、Story Reference Engine、Selection Signals、Reference Engine、NPC tier、NPC昇格条件、生成粒度、World Autonomy / Pressureの扱いを固定した。
   - `templates/session/current/event_card.md`、`story/story_deck.md`、`story/relationship_spine.md` と `prompt/newgame.md`、`prompt/save_resume.md` へテンプレート最小接続を反映した。
   - Status: docs正本化完了 / テンプレート最小接続完了 / 実生成コード未実装

9. Crisis / Combat / Ability Constraint Loop
   - `docs/CRISIS_COMBAT_ABILITY_CONSTRAINT_LOOP.md` を正本として追加済み。
   - 危機・戦闘・能力は、単なるバトルではなく、関係と自己理解を揺らすために使う。
   - ability cost、trace、relationship risk、condition、direct pressureを扱う。
   - 逃げる、守る、交渉する、隠す、耐える、助けを呼ぶ、能力を使う、代償を払う、を同じ重さで扱う。
   - 旧LIRIA / inner-galge の `combat.md` を参考にするが、LILIAではHP、部位管理、重い数値戦闘を初期MVP必須にしない。
   - `templates/session/current/event_card.md` の `Crisis / Ability Check`、`templates/session/story/story_deck.md` の `Crisis / Ability Echo`、`templates/session/lilia/main/state.md` の `Crisis / Ability Condition`、`templates/session/story/relationship_spine.md` の危機後の頼り方 / 頼られ方、能力使用後の信頼 / 警戒、`prompt/newgame.md` / `prompt/save_resume.md` の正本参照へテンプレート最小接続を反映済み。
   - Status: docs正本化完了 / テンプレート最小接続完了 / 実生成コード未実装

10. Technical + Gameplay Integrity Checks
   - MVP前後に、`new -> first scene -> save -> resume` の破綻を検出するチェックを追加する。
   - repo integrity、session integrity、prompt auditor、romance/intimacy boundary regression、voice continuity、event_card playabilityを対象にする。
   - 旧LIRIAの `check_repo_integrity`、`check_session_integrity`、`liria_prompt_auditor`、PI Player、AI Persona Playtest、AI Player Harness を参考にする。
   - 初期は軽い手動/スクリプトsmokeを優先し、AI Harness本実行や大量ログ分析は通常チェックに入れない。
   - `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md` を正本として追加済み。
   - `docs/RESUME_SMOKE_TEST.md` に横断integrity正本への参照を追加し、`tests/resume_smoke/manual_checklist.md` に Integrity Cross-Check を最小接続済み。
   - scriptsを作るかどうかは次タスクで確認する。初期MVPではAI Harness、大量ログ解析、launcher / CLI、production CIはまだ入れない。
   - Status: docs正本化完了 / manual checklist最小接続完了 / 最小スクリプト未実装

11. Launcher / CLI
   - state初期化とsmoke testが固まった後に実装する。
   - `new` / `resume` / `consult` / session list / prompt-only / engine fallback を扱う。
   - 旧LIRIA `play.sh`、`liria`、`scenarios/liria/config.sh` と inner-galge command系を参考にする。
   - 起動時に全prompt・全stateを総読みしない。
   - Status: 未着手

12. Visual Character Sheet / Manga Export Pipeline
   - MVP後の拡張として残す。
   - 旧LIRIA `prompt/visual_character_sheet.md`、`prompt/manga_export.md`、`create_manga_export.sh` を参考にする。
   - 自然文で漫画化、PV、三面図、立ち絵依頼を受ける導線を残す。
   - 最初からMVP必須にはしない。
   - 生成物、長いprompt、画像タスクはsession正史に混ぜず、将来のexport packageへ分離する。
   - Status: 後続

13. MVP Playtest
   - 1人のLILIAで、開始、再開、関係変化、保存更新が一連の体験として成立するか検証する。
   - 恋愛、日常、衝突、親密、event_card、save/resumeの少なくとも1往復を手動で通す。
   - Status: 未着手

14. Extensions
   - export、セッション一覧、複数LILIA、UI、外部連携などをMVP後に検討する。
   - Status: 後続

## 5. Next Task

次の実作業は Technical + Gameplay Integrity Checks の最小スクリプト要否確認、またはMVP Playtest準備。

Technical + Gameplay Integrity Checks はdocs正本化とmanual checklist最小接続が完了済みであり、最小スクリプトは未実装である。
次は、ファイル存在確認、見出し確認、ROADMAP / HANDOFF のNext Task簡易確認程度の最小スクリプトが必要かを確認する。
不要なら、MVP Playtest準備へ進む。
初期MVPではAI Harness本実行、大量ログ分析、launcher / CLI、production CIはまだ入れない。

## 6. Update Rules

- マイルストーンが進んだら `docs/ROADMAP.md` を更新する。
- `docs/HANDOFF.md` は直近作業・次タスク・引き継ぎに限定する。
- 小さな文言修正だけなら `docs/ROADMAP.md` は更新しなくてよい。
- 実装順を変えた場合は理由を短く残す。
- `prompt/core.md` の `Example Anchoring Control` を維持し、例文を本文生成へ流用しない。
- 官能・親密表現を削除する方向へ変更する場合は、成人・合意・相互性・境界線を守ったうえで体験価値を保てるかを必ず確認する。

## 7. 採用元

- MIRA: `voice / state / relationship / memory / beliefs`
- inner-galge: style defaults、romance/intimacy運用、memory model、validation、voice continuity、command導線、プレイヤーが触れる選択肢の足場、更新ループ、参考作品から感情の骨を抽出して現在キャラへ変換する手順
- LIRIA: session構造、event_card、save/resume、archive、story_reference / Light Story Reference Pass、Story Reference Layer、selection signals、candidate shortlist、Reference Engine、style defaults、romance、case/runtimeの運用知見、Visible Request Gate、Truth Hiding Boundary、Mid-Story Activation Gate、integrity check、growth update

combat / villain_engine / visual / manga pipeline / AI Harness は、長期ROADMAP上の後続参照候補であり、初期MVP、New Session Initialization、Event Card Playability Gateには採用しない。

## 8. 採用しなかったもの

- LILIAを単なるヒロイン、攻略対象、固定パートナーとして扱う設計
- 旧ハーレム攻略前提
- kaneco固有設定
- 旧セッション固有人物
- 旧AFFINITY数値、bond、好感度、攻略ルートを正本にする運用
- 親密さを自動報酬や攻略達成として扱う運用
- 固定台詞集でLILIAの声を管理する運用
- hotsetを正本として扱う運用
- 毎ターン全ファイルを更新する運用
- 巨大ログ保存をGrowth Updateの必須にする運用
- 参照作者や作品の直接模倣
- 参照小説本文の保存・流用
- 参照作品の固有名詞、台詞、キャラ、展開順の模倣
- NPC全員をヒロイン級に作り込む運用
- full plotを事前生成する運用
- style系を通常resumeの毎回必読にする重い運用
- 安全の名目で官能表現そのものを削り、親密場面を薄める運用
- 抽象的な違和感だけでevent_cardを進める運用
- 親密sceneを雑な事件乱入で壊す運用
- 最初から重いcase_engine / villain / combat / manga pipelineを全部MVP必須にすること
- AI Harness本実行や大量ログ分析を通常チェックへ入れること

## 9. 理由

LILIAはAI上の人格・記憶・関係存在であり、new/resumeだけでなく、関係・声・官能・事件・世界圧・検証が段階的に接続される必要があるため。

旧LIRIA / inner-galgeには、すでに実装済みまたは検証済みの運用知見がある。
ただし、LILIAは新規プロジェクトなので、旧固有設定ではなく、手順・責務・表現技法だけを移植する。

官能・親密表現はユーザー体験上の重要な魅力であり、削除ではなく安全条件つきで活かす必要がある。

実装順が共有されていないと、CodexがCLI、重い事件エンジン、画像・漫画化へ早く進みすぎるリスクがある。
まずは1人のLILIAとの関係が面白く、保存・再開で温度が落ちないことを優先する。

Story / Relationship Accumulation Loop を World Autonomy / Pressure Loop より先に置く理由は、外圧を先に大きくすると、LILIAとの関係ではなく世界設定が主役になりやすいためである。
先に、eventがmemory / relationship / beliefs / voiceへ残る線として積み重なる仕組みとNPC tierを固定し、その中で小さな外圧を扱う。
