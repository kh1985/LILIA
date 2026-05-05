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
- 官能寄りの表現技法は削除しない。成人・合意・相互性・関係段階・境界線を守ったうえで、LILIAの重要な魅力として活かす。

## 3. 現在の実装状況

- `docs/CORE_CONCEPT.md` を作成済み。
- `templates/session/` を作成済み。
- `docs/STATE_STRUCTURE.md` を作成済み。startup / new / resume が参照する最小state scaffold、session配置、new時生成ファイル、resume時読込方針を定義済み。
- `docs/NEW_SESSION_INITIALIZATION.md` を作成済み。`prompt/newgame.md` のQ&A結果から `session.json`、`current/*`、`lilia/main/*`、`story/*`、`style/*` を初期生成する写像と順序を定義する正本。
- `docs/EVENT_CARD_PLAYABILITY.md` を作成済み。`current/event_card.md` を抽象的な違和感ではなく、今触れる可視イベントにするGateの正本。
- `docs/VOICE_CONTINUITY.md` を作成済み。LILIAの声、呼び方、距離感、信頼、誤解、記憶、境界線がnew/resume/重要sceneで巻き戻らないようにするGateの正本。
- `docs/ROMANCE_INTIMACY_GROWTH.md` を作成済み。親密・官能・ベッドシーンを、信頼、記憶、境界線、合意、相互性、aftercareの積み重ねとして扱う正本。
- `docs/RESUME_SMOKE_TEST.md` を作成済み。`new -> first scene -> save -> resume` の手動smoke、resume 1ターン目の通過条件、failure examples、採用しない重い検証を定義する正本。
- `docs/GROWTH_UPDATE_LOOP.md` を作成済み。会話後、scene後、event_card進行後、親密scene後に、何をどこへ保存更新するかを定義する正本。
- `prompt/core.md` に Event Creation Procedure と Character Layer Check を追加済み。
- `docs/GROWTH_UPDATE_LOOP.md` に Deepening Tags 評価を追加済み。
- `templates/session/lilia/main/relationship.md` に深化ベクトル欄を追加済み。
- `templates/session/lilia/main/profile.md` に描写の縛りセクションを追加済み。
- `templates/session/current/relationship_overview.md` に最新チェックポイントセクションを追加済み。
- `prompt/core.md` に Incident to Character Voice Conversion を追加済み。
- `templates/session/lilia/main/memory.md` の echo セクションを拡張済み。
- `templates/session/current/decision_index.md` を新規追加済み。
- `prompt/core.md` に Echo Awareness と Decision Awareness を追加済み。
- `docs/STORY_RELATIONSHIP_ACCUMULATION.md` を作成済み。イベントがLILIAとの関係の物語として積み重なる仕組み、Story Reference Engine、NPC tier、World Autonomy / Pressureの位置づけを定義する正本。
- `references/story_media_stock.md` を新規追加（LIRIAから移植）。Event Creation Procedure から参照される50作品の研究棚。
- `tests/resume_smoke/manual_checklist.md` と `tests/resume_smoke/sample_session.md` を追加済み。手動smokeの確認項目と、非正史サンプルを置く。
- `tests/full_loop/manual_checklist.md` を追加済み。new / profile / first scene / Play Mode / scene-tick / apply-turn / resume を1本で確認する手動smoke手順である。
- `docs/ROADMAP.md` を作成済み。長期実装順とMVP境界の正本として、マイルストーン、現在地、次タスクを管理する。
- 旧LIRIA / inner-galge zip調査に基づき、`docs/ROADMAP.md` に Style Defaults / Intimacy Defaults Completion、New Session Initialization、Event Card Playability Gate、Voice Continuity Gate、Romance / Intimacy Growth Loop、World Autonomy / Pressure Loop、Crisis / Combat / Ability Constraint Loop、Integrity Checks、Launcher / CLI、Visual / Manga Pipeline の順番を反映済み。
- `prompt/style_reference.md` と `templates/session/style/` を作成済み。参照小説・参照作品から本文ではなく表現軸を抽出し、Light Story Reference Pass としてnew初回scene前や必要時だけ使う方針を定義済み。
- root `style/defaults/` を作成済み。romance / tension / warmth / loss / quiet / landscape の場面別Style Defaultsを、作者別メソッドの直接模倣ではなく表現技法・温度・視点距離・余白の参照棚として移植済み。
- `style/defaults/romance.md` は、官能そのものを削らず、ベッドシーン、身体距離、触れる/触れない境界、体温、呼吸、沈黙、余韻を、成人・合意・関係段階・境界線のもとで扱う方針へ補強済み。
- `prompt/core.md` を作成済み。
- `prompt/core.md` に `Example Anchoring Control` を追加済み。
- `prompt/core.md` の読み順は、`current/relationship_overview.md` と `beliefs` を含め、保存・再開の詳細は `prompt/save_resume.md` を正本にする形へ調整済み。
- `prompt/startup.md` を作成済み。起動直後の `new` / `resume` / `consult` / `unknown` 分岐を定義し、詳細は `prompt/newgame.md` と `prompt/save_resume.md` に委ねる。
- `prompt/newgame.md` を作成または更新済み。
- `prompt/newgame.md` は `docs/NEW_SESSION_INITIALIZATION.md` を参照し、Q&A結果から各ファイルへ反映する写像、Light Story Reference Pass、new直後resume可能な最小状態を明記済み。
- `prompt/newgame.md` のQ&Aは Wave 10.3 時点で Q1-Q9。Wave 10 の性格/見た目/主人公仕事/interactive補足質問、Wave 10.1 の描写の縛り/表と内の差/内面に持っているものの独立質問、Wave 10.2 の Main Question 5パターンを維持する。
- `templates/session/protagonist.md` を追加済み。新規セッションでは `current/protagonist.md` に主人公の呼称、身体、スタイル、Session Constraints だけを保存する。主人公の内面情報は保存しない。
- Q3は `profile.md` の描写の縛りと everyday anchors、Q4は `profile.contradictions`、Q5は「内面に持っているもの」として `profile.memories` / `unspoken` と AI生成される `current/story_spine.md` の Background Truth / Reveal Ladder に解釈反映する。Q7-Q8は `current/protagonist.md` へ直結する。
- Wave 10.3 で fallback 品質を補強済み。Q3 omakase時の `よく触る物` は持ち物・アクセサリー・小物のみ、Q4 omakase時の `裏` は内面的な状態のみを採用する。
- Wave 10.3 で Knowledge Boundary を強化済み。resume / apply-turn の context では、ヒロインが知らない meta 値を `[HIDDEN until shared in scene]` に置換する。
- Wave 10.4 でプレイヤー入力境界を追加済み。行頭または半角空白/タブ直後の `（...）` / `(...)` は主人公の内心として扱い、ヒロインの認識には入れない。ユーザー向け説明は `docs/PLAYER_INPUT.md`。
- Wave 11 で `current/story_spine.md` / `story/relationship_spine.md` の穴埋め生成を廃止し、`tools/story/spine_generator.py` が Q1-Q9、生成済みcharacter YAML、`references/story_pattern_stock.md`、`references/story_structure_stock.md` からAI生成する経路に移行済み。`tools/story/spine_validator.py` が作品名literal混入、必須セクション、空欄回避、文崩壊、同一フレーズ反復、Q1丸写しを検査する。
- inner-galge / character の「自然言語指示 -> character YAML -> 登場前キャラmd」の流れを、LILIA向けに「character YAML -> `lilia/main/profile.md`」へ変換する Persona Profile 方針を追加済み。
- `docs/LILIA_PERSONA_PROFILE.md` を作成済み。`profile.md` は first scene前に読む人格正本であり、完成済み攻略キャラカードではない。関係で育った内容は `core / voice / relationship / memory / beliefs` へ分解して保存する。
- `tools/character/` に character YAML生成の最小schema / LLM CLI(codex / claude) bridgeを追加済み。
- `./lilia apply-newgame` を改造し、LLM CLI(codex / claude)経由の character YAML 生成を default 経路にした。`--engine codex|claude|auto` フラグで engine を選択可能。default は auto(codex 優先、claude fallback)。内部で `tools/character/core/master.py` の `generate_characters(instruction, engine)` を呼ぶ。character YAML が生成できない場合、Wave 11 の spine生成もできないため `apply-newgame` は失敗する。
- `tools/character/core/master.py` の `generate_characters` を engine 引数対応にした(default `claude` で後方互換)。
- `scripts/lilia_generate_character_yaml.py` も `--engine codex|claude|auto` フラグに対応した standalone wrapper として残す。
- Wave 12.1 で `./lilia apply-newgame` の profile生成を `tools.character.profile_generator.generate_profile_document(answers=..., character_yaml=..., engine=...)` へ切り替えた。流れは character YAML生成 -> AI-driven `profile.md` 生成 -> `render_profile_initialized_documents` による current/story/lilia 初期反映。
- profile generator が `ProfileGenerationError` を投げた場合、`apply-newgame` は hard-fail する。ログには `[profile] generated via`、`[profile] validation`、`retry_count`、`sections_count` を残す。
- `./lilia` は `scripts/lilia_character_to_profile.py` を import しない。pydantic 不在fallbackは `tools/character/core/simple_schema.py` に移し、旧 `scripts/lilia_character_to_profile.py` は削除済み。
- Wave 12.1 smoke は `wave12_sakura`(session_010)、`wave12_akari`(session_011)、`wave12_omakase`(全Qおまかせ)で実施済み。いずれも profile validator pass、24セクション生成、旧 `profile/answers から再推論` 残骸なし。
- `templates/session/lilia/main/profile.md` を追加済み。`profile.md` はAI-driven生成を正本にし、launcher内の旧Python変換fallbackを正本にしない。
- `session.json` に `lilia_name` / `lilia_display_name` を追加済み。LILIAは作品名・存在カテゴリであり、作中の名乗りはPersona Profile / character YAML由来の個体名を使う。
- `apply-newgame` は、生成した `profile.md` の Initial Scene Anchors / context / unspoken / everyday anchors を `current/scene.md`、`current/event_card.md`、`story/story_deck.md`、`current/hotset.md`、`lilia/main/*` へ初期反映する。`current/story_spine.md` と `story/relationship_spine.md` は Wave 11 のAI spine生成結果を使う。
- 初回 `current/event_card.md` には Scene Exit / Next Beat を置き、雨宿りや立ち話だけで停滞せず、3-5ターン以内に次beatへ進める入口を持たせる。
- Persona Profile導線の最小確認として、既存character YAMLから `/tmp/lilia_profile_session/lilia/main/profile.md` を生成し、`./lilia prompt-only new test_persona_profile` のprompt bundleに Persona Profile Generation Pass と first scene前 profile必読指示が入ることを確認済み。
- `prompt/newgame.md` に `First Scene Quality Gate` を追加済み。初回sceneが助け待ち一本道、明白な正解行動、信頼上昇だけの処理、LILIA側からの重い開示、ユーザー側の存在理由欠落、欠けた台詞や壊れた引用符を含む出力にならないよう軽く確認する。
- `prompt/core.md` に `Output Text Completion Gate` を追加済み。First Scene / resume 1ターン目 / Play Mode応答の送信直前に、`「」` の閉じ忘れ、未完了文、台詞と地の文の混線、発話内容のない「と言った」、主語述語欠け、段落途中切れだけを最小修正する。温度やテンポは変えない。
- `prompt/save_resume.md` は作成済みで、保存・再開promptとしてレビュー済み。
- `prompt/save_resume.md` は、再開読み順に `current/relationship_overview.md`、`story/story_deck.md`、`lilia/main/beliefs.md` の必要箇所確認を含める軽量順へ調整済み。
- `prompt/save_resume.md` は、new直後のresume-ready確認として `session.json`、`hotset`、`scene`、`event_card`、`relationship_overview`、`state`、`relationship`、`memory`、`beliefs` の最小状態を確認する方針を追加済み。
- `prompt/core.md`、`prompt/newgame.md`、`prompt/save_resume.md` に Event Card Playability の短い実行ルールを反映済み。詳細は `docs/EVENT_CARD_PLAYABILITY.md` を正本にする。
- `prompt/core.md`、`prompt/newgame.md`、`prompt/save_resume.md`、`prompt/style_reference.md` に Voice Continuity の短い実行ルールを反映済み。詳細は `docs/VOICE_CONTINUITY.md` を正本にする。
- `prompt/core.md`、`prompt/newgame.md`、`prompt/save_resume.md`、`prompt/style_reference.md` に Romance / Intimacy Growth の短い実行ルールを反映済み。詳細は `docs/ROMANCE_INTIMACY_GROWTH.md` を正本にする。
- `templates/session/` は New Session Initialization に合わせて補強済み。`session.json` にphaseとprompt参照、`current/event_card.md` に visible problem / first concrete action / handles 2-4 / relationship stake / if ignored / next visible change、session style rulesに intimacy / boundary の欄を追加済み。
- Case / Event Card Playability Gate は設計仕様とテンプレート補強が完了済み。`current/event_card.md` は、今のsceneでユーザーが触れる入口、放置時の小さな変化、次に見える変化、LILIAとの関係に残るものを持つ。
- Relationship / Character Voice Continuity Gate は設計仕様とテンプレート補強が完了済み。`core fixed`、`historical fixed`、`echo`、`volatile` をLILIA向けに軽量採用し、`voice`、`relationship`、`memory`、`beliefs` の責務分離と重要scene前の確認を固定済み。
- Romance / Intimacy Growth Loop は設計仕様とテンプレート補強が完了済み。`intimacy stage`、`consent stage`、`boundary state`、`aftercare memory` を軽量採用し、親密scene前後に何を確認し、どのstateへ保存するかを固定済み。
- Resume Smoke Test は手動smoke仕様が完了済み。`new -> first scene -> save -> resume` で、必須ファイル、resume 1ターン目の入口、voice continuity、relationship / memory / beliefs、romance / intimacy の戻りを確認する。
- Growth Update Loop は設計仕様とテンプレート最小補強が完了済み。何が変わったかに応じて `state`、`relationship`、`memory`、`beliefs`、`hotset`、`event_card`、`story_deck`、`archive/beats` を必要分だけ更新する。
- Story / Relationship Accumulation Loop はdocs正本化が完了済み。`event` は今触れる点、`story` は関係に意味が生まれた線として扱い、NPCはtierに応じて段階的に作る。
- Story / Relationship Accumulation Loop のテンプレート最小接続が完了済み。`current/event_card.md` に Story Residue、`story/story_deck.md` に World Pressure / 1-3 Scene Return と NPC / Contact Notes を追加し、`prompt/newgame.md` / `prompt/save_resume.md` に正本参照を追加済み。`story/relationship_spine.md` は Wave 11 以降AI生成で初期化する。
- `docs/CRISIS_COMBAT_ABILITY_CONSTRAINT_LOOP.md` を作成済み。危機・戦闘・能力を勝敗処理ではなく、関係、記憶、beliefs、voice、自己理解に残る揺れとして扱う正本。
- Crisis / Combat / Ability Constraint Loop では、初期MVPに HP管理、ダメージ計算、部位管理、行動順、combat engine、villain_engine、case_engine、巨大組織戦、親密sceneへの雑な乱入を採用しない。
- Crisis / Combat / Ability Constraint Loop のテンプレート最小接続が完了済み。`current/event_card.md` に `Crisis / Ability Check`、`story/story_deck.md` に `Crisis / Ability Echo`、`lilia/main/state.md` に `Crisis / Ability Condition` を追加し、危機後の頼り方 / 頼られ方、能力使用後の信頼 / 警戒は関係spineのAI生成・更新で扱う。`prompt/newgame.md` / `prompt/save_resume.md` に `docs/CRISIS_COMBAT_ABILITY_CONSTRAINT_LOOP.md` 参照を追加済み。
- `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md` を作成済み。repo / session / prompt / gameplay の横断整合チェックを、重いAI Harnessや大量ログ解析ではなく軽い手動確認と将来の最小スクリプト余地として扱う正本。
- Technical + Gameplay Integrity Checks は manual checklist最小接続が完了済み。`docs/RESUME_SMOKE_TEST.md` に横断integrity正本への参照を追加し、`tests/resume_smoke/manual_checklist.md` に Integrity Cross-Check を追加済み。
- Technical + Gameplay Integrity Checks の最小スクリプトは現時点では不要と判断済み。初期MVPでは手動チェックで進め、AI Harness、大量ログ解析、自動プレイ生成、launcher / CLI、production CI はまだ入れない。
- `tests/mvp_playtest/manual_checklist.md` を追加済み。MVP Playtestで `new -> first scene -> save -> resume` を1周通し、event_card、voice、relationship / memory / beliefs、romance / intimacy、story accumulation、crisis / ability、growth update、resume 1ターン目を確認するための実行用メモであり、新しい設計正本ではない。
- MVP Playtest は `/tmp/lilia_mvp_playtest_manual_001` で手動実行済み。結果は PASS with minor follow-up candidates で、`tests/mvp_playtest/results/2026-04-29_manual_001.md` にサマリを記録済み。
- MVP Playtestのminor follow-upとして、`templates/session/session.json` の `source_prompt_versions` に Story / Relationship Accumulation と Crisis / Combat / Ability Constraint の正本参照を追加済み。
- `/tmp` の実session本文、実Q&A、実会話本文、個人プレイログはrepoに入れていない。
- `./lilia` を追加済み。`new`、`resume`、`list-sessions`、`prompt-only` の最小Launcher / CLIとして、`templates/session/` から `saves/<session_name>/` へsession scaffoldを作成し、prompt確認できる。
- `./lilia` は session名未指定時に `session_001` 形式で未使用名を採番し、resume時は最新sessionを検出する。
- 最小運用確認で、`list-sessions` はresume対象の最新sessionを先頭に出し、`*` で示す形へ調整済み。prompt-onlyにはAIを実行しないmanual prompt bundleであることと、必要ならリダイレクトできる案内を追加済み。
- `./lilia` に `--run` と `--engine codex|claude|auto` を追加済み。`auto` は codex を優先し、なければ claude を使う。AI CLIへ渡すprompt bundleは一時ファイル経由で渡す。
- `saves/` は `.gitignore` でgit管理外にしている。AI Harness、自動プレイ生成、大量ログ解析、画像/漫画export、production CI はまだ入れていない。

prompt内の `current/...`、`lilia/main/...`、`story/...`、`archive/...` は、生成されたセッションルートからの相対パスとして扱う。テンプレート上では `templates/session/` 配下に対応する。

## Wave 4 完了 — Structure / Pattern Reference Libraries

### 追加

- `references/story_structure_stock.md` — 5つの普遍的構造論。
- `references/story_pattern_stock.md` — 50作品から抽出した12パターン。

### 修正

- `prompt/core.md` Event Creation Procedure §4 を3 reference対応に拡張。
- `prompt/core.md` に Story Diagnosis セクション追加（任意、停滞時のみ起動）。
- `docs/STATE_STRUCTURE.md` referencesセクションを3ファイル対応に拡張。

### 状態

- AI動的状態管理は変更なし（newgame / save / apply-turn は触っていない）。
- 既存セッションにも後付けで効果が出る。
- ロールバック容易（references削除 + prompt revert）。

### 次の Wave

- Wave 5: story_spine の導入（Main Question / Reveal Ladder / Background Truth / Pressure Direction）。

## Wave 5 完了 — Story Spine

### 追加

- `templates/session/story/story_spine.md` — 当時のテンプレ。Wave 11 で削除済み。
- newgameで `current/story_spine.md` が生成される（Wave 11以降はAI駆動、既存セッションには影響しない）。

### 修正

- `prompt/newgame.md` — story_spine初期化手順追加。
- `prompt/core.md` — Story Spine Awarenessセクション + Event Creation Procedure連携。
- `prompt/save_resume.md` — story_spine更新基準追加。
- `./lilia` — TURN_UPDATE_TARGETSに `story_spine` 追加。
- `docs/STATE_STRUCTURE.md` — currentにstory_spine追記。
- `docs/STORY_RELATIONSHIP_ACCUMULATION.md` — 責務分離追加。

### 状態

- 新規セッションはnewgameでstory_spine生成。Wave 11以降はQ&Aとcharacter YAMLからAI生成する。
- 既存セッションはstory_spine無しで継続可能。
- kkが既存セッションに手書きでstory_spineを作る選択肢あり。

### 次の Wave 候補

- 既存セッションへのretrofitツール。
- 複数LILIA運用への拡張。
- referenceに多様なヒロイン例追加。

## Wave 6 完了 — Opening Scene & Heroine Appearance

### 追加

- `prompt/opening_scene.md` — newgame直後の最初のscene用指針（1セッション1回）。
- `style/defaults/heroine_appearance.md` — ヒロイン登場時に毎回起動する文体技法。

### 修正

- `prompt/core.md` — Scene Entry Checkセクション追加。
- `prompt/newgame.md` — 最初のscene出力時に `opening_scene.md` 参照を明示。
- `docs/STATE_STRUCTURE.md` — 新規2ファイルの役割を追記。

### 状態

- 動的状態管理は変更なし（newgame / save / apply-turn は触っていない）。
- 既存セッションへの影響なし。既存セッションでもheroine_appearanceは再登場時に参照可能だが、状態ファイルを増やさない。
- ロールバック容易。

### 次の Wave 候補

- Wave 12: 能力（内面の発露）。
- Wave 13: 異界（条件付き空間）。
- Wave 14: 組織（圧の発生装置）。
- Wave 15: 複数ヒロイン。
- Wave 16: 共同体・生活・ビジネス。

## Wave 7 完了 — Newgame Q&A Refinement & Protagonist Profile

### 追加

- `templates/session/protagonist.md` — 主人公プロフのテンプレ。
- 新規セッションで `current/protagonist.md` が生成される。

### 修正

- `prompt/newgame.md` — Q&A を Q1-Q8 に再設計し、各 Q → current/ マッピングを追加。
- `prompt/opening_scene.md` — protagonist.md 参照を追加。
- `style/defaults/heroine_appearance.md` — 主人公の距離感への参照を追加。
- `prompt/core.md` — Protagonist Awareness セクション追加。
- `prompt/save_resume.md` — resume読み順に `current/protagonist.md` を必要箇所参照として追加。
- `docs/STATE_STRUCTURE.md` / `docs/NEW_SESSION_INITIALIZATION.md` — protagonist.md と Q&A 変更を反映。

### 状態

- 新規セッションは Q1-Q8 で開始し、`current/protagonist.md` が生成される。
- 既存セッションは `protagonist.md` 無しで継続可能。
- 既存セッションへのretrofitは行わない。

### 次の Wave 候補

- Wave 12: 能力（内面の発露）。
- Wave 13: 異界。
- Wave 14: 組織。
- Wave 15: 複数ヒロイン。
- Wave 16: 共同体・生活・ビジネス。

## Wave 8 完了 — Knowledge Boundary Management

### 追加
- `templates/session/knowledge_state.md` — 知識管理テンプレ
- 新規セッションで `current/knowledge_state.md` が生成される
- fictional_status (meta / observable / shared / gm_only) で各事実をラベル管理

### 修正
- `prompt/newgame.md` — knowledge_state.md 初期化手順追加
- `prompt/core.md` — Knowledge Boundary Awareness、Authorship Boundary セクション追加
- `prompt/save_resume.md` — knowledge_state 更新基準追加
- `prompt/opening_scene.md` — knowledge_state 参照追加
- `style/defaults/heroine_appearance.md` — knowledge_state 参照追加
- `templates/session/lilia/main/profile.md` — context セクションに GM-internal pre-play assumption マーク
- `scripts/lilia_character_to_profile.py` — 生成 profile の context に同マークを付与
- `./lilia` — TURN_UPDATE_TARGETS に "knowledge_state" 追加
- `docs/STATE_STRUCTURE.md` — knowledge_state.md と連動関係を追記

### 状態
- 新規セッションは knowledge_state.md が生成される
- 既存セッション（旧手動セッション、session_003 など）は knowledge_state.md 無しで継続可能
- 既存セッションへの retrofit は行わない

### 解決される問題
- 初対面で meta 情報（呼称等）を勝手に使う
- GM が主人公側の事実を勝手に作る authorship 越境
- 情報経路の追跡不能

### 次の Wave 候補
- Wave 12: 能力（内面の発露）
- Wave 13: 異界
- Wave 14: 組織
- Wave 15: 複数ヒロイン
- Wave 16: 共同体・生活・ビジネス
- Wave 16: NPC 知識管理（knowledge_state 拡張、必要があれば）

## Wave 9 完了 — Root Cure: Examples / Fallback / Keyword / References / Validator / Logging

### 修正
- `prompt/` と `templates/session/` の具体名例を `[ヒロインA]` などの構造プレースホルダへ置換し、主要な例ヘッダに「構造説明のみ。literal として真似しないこと」を明記した。
- `prompt/opening_scene.md` の良い例は、雨 / 店 / ピアス / カップ等の具体sceneではなく、Part 1-3 の構造プレースホルダに置換した。
- `style/defaults/romance.md`、`landscape.md`、`heroine_appearance.md` は、雨 / 夕暮れ / 路地の一択にならないよう、時間帯・場所・感覚・生活密度の複数軸例へ分散した。
- `references/story_pattern_stock.md` と `references/story_structure_stock.md` は、旧セッション固有名・固有傷・固有sceneを外し、触った主要パターン/構造に `[ヒロインA]` 形式のplaceholder例を3つ以上置いた。
- `./lilia` の `FALLBACK_LILIA_NAMES` と keyword → literal fallback を廃止し、名前・場所・素材は profile / answers からの抽出、再推論不可時の placeholder へ寄せた。
- `scripts/lilia_character_to_profile.py` の everyday anchors は、keyword から固定具体物を足す方式をやめ、profile に存在する appearance / context / role の語彙から抽出する。
- apply-newgame 最終段に validator を追加し、omakase literal と旧 hardcoded literal を検知した場合は再推論、失敗時は placeholder へ置換してログ警告を残す。
- `logs/apply_newgame_*.log` / `logs/apply_turn_*.log` を追加し、開始/終了、Q&A、fallback、validator、参照/更新ファイルを記録する。プレイ本文とAI出力本文は保存しない。

### 状態
- prompt/reference/code fallback/validator/logging は完了。`references/story_media_stock.md` は触っていない。
- 旧 literal は validator 検知リストとして `HARDCODED_LITERALS` にのみ残る。生成値として使う fallback からは外した。
- autosave report: `./lilia scene-tick <session>` は `session.json` の `autosave.turns_since_save` を進め、interval到達時に `autosave_required: true` を立てるだけで、自動保存や `apply-turn` は実行しない。`apply-turn` 実行後は counter を `0 / false` に戻す。Wave 9 では修正しない。

## Wave 10 完了 — Q&A Redesign with GM Supplementary Question Flow（履歴）

### 修正
- Wave 10 時点では `prompt/newgame.md` を Q1-Q6 構成へ再設計した。Q1 は性格を含む基本、Q2 は見た目、Q3 は自由欄、Q4 は出会い + 関係起点、Q5 は主人公の身体・格好・仕事、Q6 は呼ばれ方。
- `./lilia new` はデフォルトで interactive flow を開始する。TTY では Q1 から順番に質問し、非TTYでは Q1 を表示して batch mode への導線を出す。
- Wave 10 時点の `./lilia new --prompt-only` は batch mode として残し、Q1-Q6 を一括表示する。
- GM 補足質問は必須欠落または抽象形容詞のみの時だけ、各 Q 最大1回まで行う。「おまかせ」「特になし」は追加質問しない。
- `templates/session/lilia/main/profile.md` と生成 profile に `appearance` / `body` / `outfit` の受け皿を追加した。
- `scripts/lilia_character_to_profile.py` は Q2 の見た目を profile appearance へ反映し、Q4 を context / 初回距離として扱う。
- `current/protagonist.md` 生成は Q5 から仕事を抽出し、`current/knowledge_state.md` に `protagonist_occupation` を追加する。

### 状態
- Wave 9 の profile 中心軸、validator、logging、literal fallback 禁止は維持。
- 旧8問 answers.md は legacy として apply-newgame で受けられるが、Wave 10 時点の新規 prompt は Q1-Q6 が正本だった。
- 既存セッションへの retrofit はしない。apply-turn は旧 profile でも継続可能。

## Wave 10.1 完了 — Q3-Q5 Independence Restoration

### 修正
- Wave 10 で統合した Q3 自由欄を巻き戻し、Newgame Q&A を Q1-Q9 構成へ更新した。
- Q1 の性格、Q2 の見た目、Q8 の主人公仕事、interactive flow、GM補足質問は Wave 10 から維持した。
- Q3（描写の縛り）→ profile.描写の縛り / everyday anchors、Q4（表と内の差）→ profile.contradictions、Q5（過去の傷）→ profile.memories / unspoken と story_spine.Background Truth の材料へ渡す。Wave 11以降、story_spine側はAIが解釈して再構成する。
- `./lilia` と `scripts/lilia_character_to_profile.py` は Wave 10.1 の9問を正本として読み、旧Wave7の8問とWave10の6問 answers.md は互換形式として受ける。
- Q2 appearance parsing を補強し、hair_style / hair_color、body / outfit を混ぜないようにした。

### 状態
- session_008 で見えた「Q3自由欄がstory_spine各欄へ丸コピーされる」問題を、新規セッションでは避ける。
- 既存セッション（session_003〜008）への retrofit はしない。
- Wave 9 の validator / logging / profile-centric fallback は維持。

## Wave 10.2 完了 — Main Question Template Flexibility

### 修正
- Q5 の表示名を「過去の傷の種」から「内面に持っているもの」へ変更し、傷・癖・特徴・職業的な残り香・葛藤をすべて入力可能にした。
- `templates/session/story/story_spine.md` に Main Question の5パターン（傷の治癒 / 選択 / 発見 / 変化 / 葛藤）と、Reveal Ladder / Background Truth / Pressure Direction の対応を追記した。Wave 11でこのテンプレートは削除され、AI spine生成へ置き換わった。
- `./lilia` の旧 story_spine fallback 生成は、Q1/Q5 から5パターンを判定していた。Wave 11以降、`current/story_spine.md` / `story/relationship_spine.md` は `tools/story/spine_generator.py` で生成する。
- 殺し屋や組織人などの特殊職では、Q5 を即「傷」と断定せず、選択または発見の問いとして扱えるようにした。

### 状態
- Wave 10.1 の Q1-Q9 構成、Q3/Q4/Q5 の直接写像、Q2 appearance parsing は維持。
- 既存セッション（session_003〜008）への retrofit はしない。
- Wave 9 の validator / logging / profile-centric fallback は維持。

## Wave 10.3 完了 — Fallback Field Quality + Knowledge Boundary Meta HIDDEN

### 修正
- `scripts/lilia_character_to_profile.py` と `./lilia` の fallback で、`everyday anchors.よく触る物` に目の色、体型、服装などが入らないようにした。Q3が未指定の場合は、持ち物・アクセサリー・小物を拾い、拾えなければ `[未確定]` placeholder にする。
- `contradictions.裏` の fallback で、夜間清掃、通勤、持ち物リストなどの生活設定を内面として扱わないようにした。Q4が未指定の場合は、感情、思考、隠した反応だけを拾い、拾えなければ `[未確定]` placeholder にする。
- `current/knowledge_state.md` を context に入れる時、ヒロインが `known_to` に含まれない `meta` 項目の `value` を `[HIDDEN until shared in scene]` に置換する。ファイル本体は変更しない。
- `prompt/core.md` と `prompt/opening_scene.md` に、HIDDEN 値を服装・姿勢・雰囲気から推測して復元しない注意を追加した。

### 状態
- 既存セッション（session_003〜009）への retrofit はしない。ただし次回 resume / apply-turn context 構築時から meta HIDDEN が効く。
- Wave 10.1 の Q1-Q9 構成と Wave 10.2 の Main Question 5パターンは維持。
- Wave 9 の validator / logging / profile-centric fallback は維持。

## Wave 10.4 完了 — Protagonist Inner Monologue Boundary

### 修正
- `./lilia` に `split_action_and_monologue()` / `format_player_input_boundary()` を追加した。
- 行頭または半角空白/タブ直後の `（...）` / `(...)` を主人公の内心として抽出し、語の直後の括弧は補足として行動側に残す。
- `./lilia format-input <player_input>` で、入力を `[PLAYER_INNER_MONOLOGUE - GM_ONLY]` と `[PLAYER_ACTION]` に整形できるようにした。
- `prompt/core.md` に Player Input Boundary を追加し、内心の内容や語彙をヒロインの台詞・反応・描写に反映しないことを明記した。
- Codex interactive new/resume の起動指示にも、各プレイヤー入力で Player Input Boundary を適用する注意を追加した。
- `docs/PLAYER_INPUT.md` を追加し、行動・発言、内心、補足括弧の書き分けをユーザー向けに記載した。

### 状態
- 既存セッション（session_003〜009）への retrofit はしない。
- Wave 10.3 の meta HIDDEN と補完関係にあり、静的meta境界と動的内心境界の両方を扱う。
- `apply-turn` は引き続き `turn_update.md` のマージのみで、生のプレイヤー入力は受け取らない。

## Wave 11 完了 — AI-driven Story / Relationship Spine Generation

### 追加
- `tools/story/spine_generator.py` — Q1-Q9、生成済みcharacter YAML、サニタイズ済み `references/story_pattern_stock.md` / `references/story_structure_stock.md` から `current/story_spine.md` と `story/relationship_spine.md` を生成する。
- `tools/story/spine_validator.py` — 作品名literal混入、必須セクション、空欄回避、文崩壊、同一フレーズ反復、Q1丸写しを検査する。

### 修正
- `./lilia apply-newgame` は character YAML 生成完了後に spine generator を呼び、validator失敗時は最大2回再生成する。3回失敗またはengine不可の場合は失敗終了し、壊れたspineを保存しない。
- `templates/session/story/story_spine.md` と `templates/session/story/relationship_spine.md` は削除済み。Wave 11以降の新規セッションのみAI生成で、既存セッションへのretrofitはしない。
- `current/knowledge_state.md` の story_spine 由来項目は、最終AI生成された story_spine から同期する。

### 状態
- `references/story_media_stock.md` は apply-newgame のprompt材料には入れず、validatorのliteral混入チェックと play中の event_card 参照棚として維持する。
- ましろ、つむぎ、全Qおまかせの新規smokeで生成と validator pass を確認済み。
- `prompt/core.md` の Event Creation Procedure は event_card 側の参照導線なので、relationship_spine参照欄の名称だけ Wave 11 に合わせた。

## 4. 採用元

- MIRA: 人格構造 `core / voice / state / relationship / memory / beliefs`、特に voice / memory / beliefs
- inner-galge: キャラ中心、hotset、Markdown運用、character YAMLから登場前mdを作る流れ、style defaults、romance/intimacy運用、memory model、validation、voice continuity、command導線、更新ループ、感情の骨を抽出して現在キャラへ変換する手順
- LIRIA: session構造、event_card、save/resume、archive、story_reference / Light Story Reference Pass、Story Reference Layer、selection signals、candidate shortlist、Reference Engine、story_media_stock、style defaults、romance、case/runtimeの運用知見、Visible Request Gate、Truth Hiding Boundary、Mid-Story Activation Gate、integrity check、manual smoke、growth update

重いcombat engine / 数値戦闘 / villain_engine / visual / manga / AI Harness は、長期ROADMAP上の参照候補であり、初期MVP、New Session Initialization、Event Card Playability Gate、Story / Relationship Accumulation Loop、Crisis / Combat / Ability Constraint Loopには採用しない。

## 5. 採用しないもの

- proxy / web research / bench
- harem名称
- 複数キャラ前提
- `cast/heroine` の復活
- case_engine / villain_engine / 重いorganization運用
- 漫画化 / AI Harness
- 自動プレイ検証や大量ログ解析をResume Smoke Testの必須条件にする運用
- 毎ターン全ファイル更新
- 巨大ログ保存をGrowth Updateの必須にする運用
- 巨大prompt分割
- 参照小説本文や固有文体の保存・直接模倣
- 参照作品の固有名詞、台詞、キャラ、展開順の模倣
- NPC全員をヒロイン級に作り込む運用
- full plotを事前生成する運用
- style系を通常resumeの毎回必読にする重い運用
- 安全の名目で官能表現そのものを削り、親密場面を薄める運用
- 旧AFFINITY数値、bond、好感度、攻略ルートを正本にする運用
- character YAMLをLILIA最終正本として扱う運用
- 親密さを自動報酬や攻略達成として扱う運用
- 固定台詞集でLILIAの声を管理する運用
- hotsetを正本として扱う運用
- 抽象的な違和感だけでevent_cardを進める運用
- 親密sceneを雑な事件乱入で壊す運用
- 最初から重いcase_engine / villain / combat / manga pipelineを全部MVP必須にすること

## 6. 次にやること

- ROADMAP上の直前項目は Launcher / CLI。最小launcher、prompt-only smoke、UX小修正、AI engine接続が完了済み。
- 次の実作業は、10ターン到達時の保存提案UXまたは `apply-turn` の実プレイ検証。
- Launcher / CLI は最小実装、AI engine接続、Codex対話導線まで完了済み。
- `./lilia new --run --engine auto` / `./lilia resume --run --engine auto` を実プレイ導線として使うため、ローカルの codex / claude 認証や権限を確認する。
- AI Harness、大量ログ解析、自動プレイ生成、production CI はまだ後続にする。
- World Autonomy / Pressure Loop は独立した大きな世界圧ではなく、Story / Relationship Accumulation Loop の下位要素として扱う。
- event_card は「抽象的な違和感」ではなく「今触れる可視イベント」として扱う。真相は隠してよいが、visible problem、first concrete action、handles 2-4、relationship stake、if ignored、next visible change は隠さない。
- story accumulation は、eventを点、storyを線として扱い、LILIAの記憶、関係、beliefs、voiceに残った変化だけを積み重ねる。
- voice continuity は「固定台詞」ではなく、呼び方、声、距離、信頼、誤解、記憶、境界線が前回からつながっているかとして扱う。
- romance / intimacy は「報酬」ではなく、intimacy stage、consent stage、boundary state、aftercare memory が関係と記憶に残る成長ループとして扱う。
- resume smoke は hotsetだけで押し切らず、scene、event_card、relationship_overview、voice、relationship、memory、beliefs の必要箇所で1ターン目の温度と入口を確認する。
- growth update は好感度加算ではなく、what changedを見て、必要な正本だけを短く更新する運用として扱う。
- persona profile は first scene前の人格正本として読み、通常resumeでは必要箇所だけ参照する。profileをhotsetや毎ターン追記ログの代替にしない。
- Newgame Q&A はQ1-Q9に更新済み。ヒロイン基本、見た目、描写の縛り、表と内の差、内面に持っているもの、出会い、呼称、主人公の身体・格好・仕事、避けたい展開を取り、`apply-newgame` は新Q1-Q9を正本として読む。旧Q1-Q8 / Wave10 Q1-Q6 answers.md は互換形式として受けられる。
- Play Mode / Save Mode を分離する。通常プレイではLILIA / GMの本文を先に返し、ファイル編集、git確認、diff確認、保存更新ログを割り込ませない。保存更新はユーザーの明示save、scene終了/章区切りの保存確認、またはnew初期化時だけ行う。
- Save Mode用に `./lilia apply-turn <session> <turn_update.md>` を実装済み。turn_updateの各セクションを対応するMarkdownへ追記し、`scene` と `relationship_overview` も `current/scene.md` / `current/relationship_overview.md` へ反映できる。`next_hook` は `current/event_card.md` と `story/story_deck.md` に残し、scene終了後の次入口候補にする。`hotset.md` だけは肥大化防止のため最新要約へ上書きする。`profile.md` は更新対象にしない。
- 通常プレイでは自動保存せず、ユーザーの明示save、scene終了/章区切りの保存確認、またはnew初期化時だけ保存更新する。保存時に `apply-turn` を使う。
- `./lilia scene-tick <session>` を追加済み。通常プレイ1ターン後に autosave counter を1つ進め、10ターン到達で `autosave_required: true` にする。
- `scene-tick` は自動保存ではなく保存提案まで。`autosave_required` が true になっても勝手に `apply-turn` は実行しない。
- `apply-turn` 実行後は autosave counter を `turns_since_save: 0` / `autosave_required: false` へリセットする。
- 長期実装順は `docs/ROADMAP.md` を正本とし、このファイルには直近の現在地と引き継ぎだけを残す。

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
- マイルストーンが進んだ場合は、長期実装順の正本である `docs/ROADMAP.md` も更新する。
- 別GPTセッションで再開する時は、まずこのファイルを読ませる。
