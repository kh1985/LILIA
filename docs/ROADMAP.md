# LILIA Roadmap

この文書は、LILIA開発の長期実装順とMVP境界を管理する正本である。
思想・中核概念は `docs/CORE_CONCEPT.md`、直近の引き継ぎは `docs/HANDOFF.md`、state構造は `docs/STATE_STRUCTURE.md`、プレイヤー入力規則は `docs/PLAYER_INPUT.md`、persona profileは `docs/LILIA_PERSONA_PROFILE.md`、event_card可プレイ性は `docs/EVENT_CARD_PLAYABILITY.md`、voice continuityは `docs/VOICE_CONTINUITY.md`、romance/intimacy growthは `docs/ROMANCE_INTIMACY_GROWTH.md`、resume smokeは `docs/RESUME_SMOKE_TEST.md`、growth updateは `docs/GROWTH_UPDATE_LOOP.md`、story / relationship accumulationは `docs/STORY_RELATIONSHIP_ACCUMULATION.md`、crisis / combat / ability constraintは `docs/CRISIS_COMBAT_ABILITY_CONSTRAINT_LOOP.md`、technical / gameplay integrity checksは `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md` を正本にする。

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
- Growth Update Loop: 設計仕様完了 / apply-turn MVP実装済み / next_hook導線追加済み / autosave counter導入済み / scene-tick MVP実装済み
- Story / Relationship Accumulation Loop: docs正本化完了 / event/story_deck/profile初期生成コード接続済み / story_spine・relationship_spine は Wave 11 でAI駆動化済み / ましろ・つむぎ・全Qおまかせ smoke 通過
- Story Reference Engine 強制導線: prompt 接続済み
- 5層 self-understanding 参照導線: prompt 接続済み
- Deepening Tags 評価基準: GROWTH_UPDATE_LOOP + relationship template 接続済み
- Crisis / Combat / Ability Constraint Loop: docs正本化完了 / テンプレート最小接続完了 / 実生成コード未実装
- Technical + Gameplay Integrity Checks: docs正本化完了 / manual checklist最小接続完了 / 最小スクリプト不要判断済み
- MVP Playtest: PASS with minor follow-up candidates / minor follow-up反映済み
- Full Loop Manual Smoke: checklist追加済み
- Launcher / CLI: 最小launcher実装済み / prompt-only smoke完了 / UX小修正済み / AI engine接続済み
- Newgame Q&A Q1-Q9: ヒロイン基本（性格含む）/ 見た目 / 描写の縛り / 表と内の差 / 内面に持っているもの / 出会い + 関係起点 / 呼ばれ方 / 主人公の身体・格好・仕事 / 避けたい展開へ更新済み。interactive 1問ずつ表示と補足質問 flow は維持。
- LILIA Persona Profile: character YAML 素材生成と AI-driven profile.md 生成導線を追加済み。Wave 12.2 で apply-newgame は character YAML 生成後に `generate_profile_document` を呼び、`current/story_spine.md` / `story/relationship_spine.md` をAI生成してから、`tools.session.document_generator.generate_session_documents` で13 downstream filesを生成する流れへ接続した。profile validation失敗は `ProfileGenerationError` で hard-fail。Q&A は Q1-Q9。First Scene Quality Gate に2項目追加済み。
- Wave 1（散文層・キャラ会議変換）: 実装済み
- Wave 2（echo拡張・decision_index）: 実装済み
- Wave 3（50作品参考カタログ）: 実装済み
- Wave 4（Structure / Pattern Reference Libraries）: 実装済み
- Wave 5（story_spine導入）: 実装済み
- Wave 6（Opening Scene & Heroine Appearance）: 実装済み
- Wave 7（Newgame Q&A Refinement & Protagonist Profile）: 実装済み
- Wave 8（Knowledge Boundary Management）: 実装済み
- Wave 9（Root Cure: Examples / Fallback / Keyword / References / Validator / Logging）: 実装済み
- Wave 10（Q&A Redesign with GM Supplementary Question Flow）: 実装済み
- Wave 10.1（Q3-Q5 Independence Restoration）: 実装済み
- Wave 10.2（Main Question Template Flexibility）: 実装済み
- Wave 10.3（Fallback Field Quality + Knowledge Boundary Meta HIDDEN）: 実装済み
- Wave 10.4（Protagonist Inner Monologue Boundary）: 実装済み
- Wave 11（AI-driven Story / Relationship Spine Generation）: 実装済み
- Wave 12.2（AI-driven Downstream Session Documents）: 実装済み。apply-newgame は spines 生成後に `tools/session/document_generator.py` を呼び、13 downstream files をAI生成する。`tools/session/document_validator.py` がテンプレ見出し、文崩壊、テンプレ表現、重複、Q丸写し、GM only漏洩、knowledge_state YAMLを検証する。
- LILIA Individual Name: `session.json` の `lilia_name` / `lilia_display_name` に作中名を保持
- 旧LIRIA / inner-galge調査に基づく長期実装順の反映: 完了
- 次は実プレイで10ターン到達時の保存提案UXを確認すること、または `apply-turn` の実プレイ検証

### Wave 4: Reference Libraries [完了]

- `references/story_structure_stock.md` と `references/story_pattern_stock.md` を追加。
- Event Creation Procedure §4 を3 reference対応に拡張。
- Story Diagnosis セクション追加。

### Wave 5: Story Spine [完了]

- `templates/session/story/story_spine.md` を追加した（Wave 11で削除済み）。
- newgameで `current/story_spine.md` を初期生成した（Wave 11以降はAI駆動）。
- Story Spine Awareness（prompt/core.md）を追加。
- Event Creation Procedureと連携。
- save / apply-turn連携。
- responsibility separation: relationship_spine vs story_spine。

### Wave 6: Opening Scene & Heroine Appearance [完了]

- `prompt/opening_scene.md`（初回登場、最大気合い）。
- `style/defaults/heroine_appearance.md`（毎回登場、状態 + シンボル繰り返し）。
- `prompt/core.md` に Scene Entry Check。
- `prompt/newgame.md` に opening_scene参照。

### Wave 7: Newgame Q&A Refinement & Protagonist Profile [完了]

- Q1-Q8 に再設計（LILIA構造への直接マップ）。
- `templates/session/protagonist.md` を追加。
- 主人公の身体情報のみ保存（内面はプレイで立ち上がる）。
- `prompt/opening_scene.md`、`style/defaults/heroine_appearance.md`、`prompt/core.md` に protagonist 連携。

## Wave 8: Knowledge Boundary Management [完了]
- templates/session/knowledge_state.md
- fictional_status 4種類 (meta / observable / shared / gm_only)
- newgame で初期化、Save Mode で更新
- prompt/core.md に Knowledge Boundary Awareness と Authorship Boundary
- 既存ファイル（memory, echo, decision_index, story_spine, protagonist, profile）と連動

## Wave 9: Root Cure — Examples / Fallback / Keyword / References / Validator / Logging [完了]
- prompt/templates の具体例を構造プレースホルダへ寄せ、literal copy禁止の見出しを追加。
- opening_scene の良い例を具体sceneから Part 1-3 の構造説明へ置換。
- style defaults は雨 / 夕暮れ / 路地に偏らない複数軸例へ分散。
- story_pattern_stock / story_structure_stock は旧セッション固有名・固有傷・固有sceneを外し、主要箇所に `[ヒロインA]` 形式のplaceholder例を3つ以上追加。
- `FALLBACK_LILIA_NAMES` と keyword → literal fallback を廃止し、profile / answers 抽出と placeholder fallback に寄せた。
- apply-newgame 最終段に omakase / hardcoded literal validator を追加した。検知時は再推論を試し、失敗時は placeholder 化してログへ警告する。
- `logs/apply_newgame_*.log` / `logs/apply_turn_*.log` を追加した。プレイ本文とAI出力本文は保存しない。
- autosave report: `scene-tick` は `session.json` の autosave counter を進めるだけで、自動保存や `apply-turn` 実行はしない。`apply-turn` 後に counter をリセットする。Wave 9 では報告のみで未修正。

## Wave 10: Q&A Redesign with GM Supplementary Question Flow [完了]
- Newgame Q&A を8問から6問へ再設計。
- Q1 に性格を追加し、Q2 に見た目（髪型・髪色・目・体型・服装）を追加。
- Q3 は描写の縛り / 表と内の差 / 過去の傷 / 避けたい展開を受ける自由欄へ統合。
- Q4 は最初の出会い + 関係性の起点、Q5 は主人公の身体・格好・仕事、Q6 は呼ばれ方。
- `./lilia new` のデフォルトを interactive flow にし、`--prompt-only` batch mode は維持。
- GM 補足質問は必須欠落または抽象表現のみの場合に各 Q 最大1回だけ行う。「おまかせ」「特になし」は尊重する。
- profile template と生成 profile に appearance / body / outfit の受け皿を追加。

## Wave 10.1: Q3-Q5 Independence Restoration [完了]
- Wave 10 の自由欄統合だけを巻き戻し、Newgame Q&A を9問へ更新。
- Q1 性格、Q2 見た目、Q8 主人公仕事、interactive flow、GM補足質問は維持。
- Q3 描写の縛り、Q4 表と内の差、Q5 過去の傷を独立させ、それぞれ profile / story_spine の特定フィールドへ直接写像する。
- Q2 appearance parsing を補強し、hair_style / hair_color、body / outfit の混同を避ける。
- 旧8問 answers.md と Wave10の6問 answers.md は互換形式として引き続き受ける。
- Q5 の主人公仕事を protagonist.md / knowledge_state.md へ接続。

## Wave 10.2: Main Question Template Flexibility [完了]
- Q5 を「内面に持っているもの」へ改名し、傷・癖・特徴・職業的なもの・葛藤を受けられるようにした。
- story_spine の Main Question を5パターン（傷の治癒 / 選択 / 発見 / 変化 / 葛藤）へ拡張した。
- Reveal Ladder / Background Truth / Pressure Direction も選択パターンに合わせて生成する。
- 殺し屋・組織人・特殊職などを、必ず「傷を抱えて扱い直す」構文へ押し込まない。

## Wave 10.3: Fallback Field Quality + Knowledge Boundary Meta HIDDEN [完了]
- Q3 omakase fallback で `everyday anchors.よく触る物` に身体特徴や服装が入らないよう、持ち物・アクセサリー・小物だけを抽出対象にした。
- Q4 omakase fallback で `contradictions.裏` に生活設定や持ち物リストが入らないよう、内面的な状態・感情・反応パターンだけを抽出対象にした。
- resume / apply-turn 用 context では、ヒロインが知らない `knowledge_state.md` の meta 値を `[HIDDEN until shared in scene]` に置換し、服装や姿勢から推測して言い当てる経路を塞いだ。
- 既存セッションのファイル自体は retrofit しないが、次回 context 構築時から meta HIDDEN が効く。

## Wave 10.4: Protagonist Inner Monologue Boundary [完了]
- 行頭または半角空白/タブ直後の `（...）` / `(...)` を主人公の内心として扱い、語の直後の括弧は補足として行動側に残す。
- `prompt/core.md` に `[PLAYER_INNER_MONOLOGUE - GM_ONLY]` と `[PLAYER_ACTION]` の境界を追加し、ヒロインが内心の語彙や内容を台詞・反応に使わないようにした。
- `./lilia format-input` でプレイヤー入力を同じ境界形式へ整形できるようにした。
- `docs/PLAYER_INPUT.md` を追加し、行動、内心、補足括弧の書き分けをユーザー向けに説明した。

## Wave 11: AI-driven Story / Relationship Spine Generation [完了]
- `tools/story/spine_generator.py` と `tools/story/spine_validator.py` を追加し、`./lilia apply-newgame` の `current/story_spine.md` / `story/relationship_spine.md` 生成をAI駆動へ移行した。
- generator は Q1-Q9 と生成済み character YAML を読み、`references/story_pattern_stock.md` から1-2パターン、`references/story_structure_stock.md` から1構造を選んで両spineを書く。
- prompt投入前に参照棚から観察作品行や具体例を取り除き、validatorで作品名literal混入、必須セクション欠落、空欄回避、文崩壊、同一フレーズ反復、Q1丸写しを検査する。
- invalid時は最大2回再生成し、3回失敗したら `apply-newgame` を失敗させる。壊れたspineは保存しない。
- `templates/session/story/story_spine.md` と `templates/session/story/relationship_spine.md` は削除した。既存セッションへのretrofitはしない。
- `current/knowledge_state.md` の story_spine 由来項目は、最終AI生成された story_spine から同期する。
- ましろ、つむぎ、全Qおまかせの新規smokeで生成と validator pass を確認した。

## 候補（優先度順、未確定）

- Wave 12: 能力（内面の発露）。
- Wave 13: 異界。
- Wave 14: 組織。
- Wave 15: 複数ヒロイン。
- Wave 16: 共同体・生活・ビジネス。
- Wave 17: NPC 知識管理（knowledge_state 拡張）。

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

2.5 LILIA Persona Profile Generation
   - inner-galge / character の「自然言語指示 -> character YAML -> 登場前キャラmd」の流れを、LILIA向けに「character YAML -> `lilia/main/profile.md`」へ変換して採用する。
- `profile.md` は、first scene前に読む人格正本であり、完成済み攻略キャラカードではない。
- 関係で育った内容は `core / voice / relationship / memory / beliefs` へ分解して保存する。
- profileの Initial Scene Anchors / context / unspoken / everyday anchors は、初回scene前に `current/scene.md`、`current/event_card.md`、`story/story_deck.md`、`story/relationship_spine.md`、`current/hotset.md`、`lilia/main/*` へ分解して初期反映する。
- Multi-Relationship / Jealousy Profile は latent、Ability / Intimacy Resonance は dormant として持つ。
   - AFFINITY、bond、好感度、攻略ルート、ハーレム前提は採用しない。
   - 2026-05-02: `./lilia apply-newgame` を改造し、LLM CLI(codex / claude)経由の character YAML 生成を default 経路にした。
   - `--engine codex|claude|auto` フラグで engine を選択可能(default auto)。`tools/character/core/master.py` の `generate_characters` も engine 引数対応。
   - `scripts/lilia_generate_character_yaml.py` も `--engine` 対応。
   - 2026-05-05 Wave 12.1: `./lilia apply-newgame` は character YAML 生成後に `tools.character.profile_generator.generate_profile_document(answers=..., character_yaml=..., engine=...)` を呼び、AI-driven `profile.md` を生成する。
   - 2026-05-05 Wave 12.2: `apply-newgame` は profile validation後に `tools/story/spine_generator.py` で `current/story_spine.md` / `story/relationship_spine.md` を生成し、その後 `tools.session.document_generator.generate_session_documents` へ profile / character YAML / 両spine / Q&A を渡して13 downstream filesを生成する。
   - `tools/session/document_generator.py` と `tools/session/document_validator.py` を追加した。downstream docsは3グループでAI生成し、validator失敗時は各グループ最大2回再試行する。
   - `render_profile_initialized_documents` / `render_protagonist_document` / `render_knowledge_state_document` / `render_newgame_documents` は削除済み。新規初期反映のPython穴埋め経路は廃止した。
   - profile generator の検証失敗は `ProfileGenerationError` で hard-fail し、logに `[profile] generated via`、validation pass/retry_count、sections_countを残す。
   - Q&A は Q1-Q9。
   - First Scene Quality Gate に「LILIA側からの重い開示禁止」「ユーザー側の存在理由」を追加。
   - Status: 実装済み / AI-driven profile生成導線追加済み / spine-before-docs順序へ変更 / downstream docs generator実装済み / session_010・session_011・全Qおまかせ apply-newgame smokeはWave 12.1時点の結果

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
   - `./lilia apply-turn <session> <turn_update.md>` をSave Mode用MVPとして追加済み。`scene` / `relationship_overview` / `next_hook` もturn_update経由で反映できる。
   - 通常プレイ中は自動保存せず、ユーザーの明示saveやscene区切りでSave Modeに入った時だけ使う。
   - autosave counterは `session.json` に持ち、`./lilia scene-tick <session>` で通常プレイ1ターンごとに進める。
   - `scene-tick` は10ターン到達時に `autosave_required: true` にするが、自動保存や `apply-turn` 実行はしない。
   - 次タスクは、実プレイで10ターン到達時の保存提案UXを確認すること、または `apply-turn` の実プレイ検証。
   - Status: apply-turn MVP実装済み / next_hook導線追加済み / scene-tick MVP実装済み / 自動保存は未実装

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
   - `templates/session/current/event_card.md` の `Crisis / Ability Check`、`templates/session/story/story_deck.md` の `Crisis / Ability Echo`、`templates/session/lilia/main/state.md` の `Crisis / Ability Condition`、`prompt/newgame.md` / `prompt/save_resume.md` の正本参照へテンプレート最小接続を反映済み。危機後の頼り方 / 頼られ方、能力使用後の信頼 / 警戒は Wave 11以降の関係spine AI生成・更新で扱う。
   - Status: docs正本化完了 / テンプレート最小接続完了 / 実生成コード未実装

10. Technical + Gameplay Integrity Checks
   - MVP前後に、`new -> first scene -> save -> resume` の破綻を検出するチェックを追加する。
   - repo integrity、session integrity、prompt auditor、romance/intimacy boundary regression、voice continuity、event_card playabilityを対象にする。
   - 旧LIRIAの `check_repo_integrity`、`check_session_integrity`、`liria_prompt_auditor`、PI Player、AI Persona Playtest、AI Player Harness を参考にする。
   - 初期は軽い手動/スクリプトsmokeを優先し、AI Harness本実行や大量ログ分析は通常チェックに入れない。
   - `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md` を正本として追加済み。
   - `docs/RESUME_SMOKE_TEST.md` に横断integrity正本への参照を追加し、`tests/resume_smoke/manual_checklist.md` に Integrity Cross-Check を最小接続済み。
   - 最小スクリプトは現時点では不要と判断済み。初期MVPでは手動チェックでMVP Playtestへ進む。
   - 初期MVPではAI Harness、大量ログ解析、launcher / CLI、production CIはまだ入れない。
   - Status: docs正本化完了 / manual checklist最小接続完了 / 最小スクリプト不要判断済み

11. Launcher / CLI
   - state初期化とsmoke testが固まった後に実装する。
   - `new` / `resume` / `consult` / session list / prompt-only / engine fallback を扱う。
   - 旧LIRIA `play.sh`、`liria`、`scenarios/liria/config.sh` と inner-galge command系を参考にする。
   - 起動時に全prompt・全stateを総読みしない。
   - `./lilia` を追加済み。
   - `new`、`resume`、`list-sessions`、`prompt-only` の最小コマンドを実装済み。
   - `templates/session/` から `saves/<session_name>/` へsession scaffoldを作成できる。
   - session名未指定時は `session_001` 形式で未使用名を採番し、resume時は最新sessionを検出する。
   - `saves/` はgit管理外にし、実sessionや個人ログをrepoへ入れない。
   - 最小運用確認で、`list-sessions` はresume対象の最新sessionを先頭に出し、`*` で示す形へ調整済み。
   - prompt-onlyはAIを実行しないmanual prompt bundleであり、必要ならリダイレクトして使う案内を追加済み。
   - `--run` と `--engine codex|claude|auto` を追加済み。`auto` は codex を優先し、なければ claude を使う。
   - AI CLIへ渡すprompt bundleは一時ファイル経由で渡し、実session本文や個人ログはrepoに入れない。
   - AI Harness、自動プレイ生成、大量ログ解析、画像/漫画export、production CIは入れていない。
   - Status: 最小launcher実装済み / prompt-only smoke完了 / UX小修正済み / AI engine接続済み

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
   - `tests/mvp_playtest/manual_checklist.md` を追加済み。これは新しい設計正本ではなく、`new -> first scene -> save -> resume` を1周通すための手動playtest実行メモである。
   - `/tmp/lilia_mvp_playtest_manual_001` で手動実行し、`new -> first scene -> save -> resume` を1周通過済み。
   - `tests/mvp_playtest/results/2026-04-29_manual_001.md` に PASS with minor follow-up candidates として結果サマリを記録済み。
   - minor follow-upとして、`templates/session/session.json` の `source_prompt_versions` に Story / Relationship Accumulation と Crisis / Combat / Ability Constraint の正本参照を追加済み。
   - 実セッション本文、実Q&A、実会話本文、個人プレイログ、`/tmp` のsession実体はrepoに入れない。
   - Status: PASS with minor follow-up candidates / minor follow-up反映済み

14. Extensions
   - export、セッション一覧、複数LILIA、UI、外部連携などをMVP後に検討する。
   - Status: 後続

## 5. Next Task

次の実作業は、実プレイで10ターン到達時の保存提案UXを確認すること、`apply-turn` の実プレイ検証、または改造した `./lilia apply-newgame` で新しいセッションを作って実プレイ検証すること。

MVP Playtest は `/tmp/lilia_mvp_playtest_manual_001` で `new -> first scene -> save -> resume` を1周通過済みで、結果は `tests/mvp_playtest/results/2026-04-29_manual_001.md` に記録済みである。
minor follow-upとして `templates/session/session.json` の `source_prompt_versions` 補正も完了している。

`./lilia` で `new` / `resume` / `list-sessions` / `prompt-only` の最小導線を実装済みである。
最小運用確認では、最新session表示とprompt-only案内を小修正済みである。
`--run` と `--engine codex|claude|auto` によりAI CLI接続も追加済みである。
Newgame Q&A は Q1-Q9 で、ヒロインの基本、見た目、描写の縛り、表と内の差、内面に持っているもの、最初の出会い、呼ばれ方、主人公の身体・格好・仕事、避けたい展開を聞く。Q3/Q4/Q5はそれぞれ profile / story_spine の特定フィールドへ直接写像する。
Persona Profile導線では、first scene前に `lilia/main/profile.md` を作り、profileの具体物、職能、生活、反応、矛盾、禁忌を使って初回sceneを書く。
次は、scene中のテンポを壊さずに `scene-tick` が10ターン到達を知らせられるか、改造した `./lilia apply-newgame` で profile.md が LLM CLI 経由で具体化されているか、first scene の蓋然性が play_003 より上がっているかを実プレイで確認する。
engine ごとの生成品質の差(codex vs claude)も確認する。
AI Harness本実行、大量ログ分析、自動プレイ生成、production CIはまだ入れない。

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
