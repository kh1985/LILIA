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
- `docs/STORY_RELATIONSHIP_ACCUMULATION.md` を作成済み。イベントがLILIAとの関係の物語として積み重なる仕組み、Story Reference Engine、NPC tier、World Autonomy / Pressureの位置づけを定義する正本。
- `tests/resume_smoke/manual_checklist.md` と `tests/resume_smoke/sample_session.md` を追加済み。手動smokeの確認項目と、非正史サンプルを置く。
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
- 初回sceneテストで、Event Cardは機能したが、LILIAが無難で優しいヒロインに寄りやすい問題を確認済み。`prompt/newgame.md` のQ&Aを v1.1 として、LILIAそのものを決めさせる質問から、初回sceneで表へ出る側面、関係位置、生活の足場、今日の保留、許されている距離、関係が動く小さな出来事、避けたいことを聞く構造へ調整済み。
- `prompt/newgame.md` のQ&A v1.1は、各Qに「この質問で決めること」「選択肢風の例」「答え方例」を追加し、プレイヤーが短く答えやすい具体文へ調整済み。例は固定選択肢ではなく、生成時は抽象軸として扱う。
- inner-galge / character の「自然言語指示 -> character YAML -> 登場前キャラmd」の流れを、LILIA向けに「character YAML -> `lilia/main/profile.md`」へ変換する Persona Profile 方針を追加済み。
- `docs/LILIA_PERSONA_PROFILE.md` を作成済み。`profile.md` は first scene前に読む人格正本であり、完成済み攻略キャラカードではない。関係で育った内容は `core / voice / relationship / memory / beliefs` へ分解して保存する。
- `tools/character/` に character YAML生成の最小schema / Claude CLI bridgeを追加済み。`scripts/lilia_generate_character_yaml.py` はQ&Aや自然言語指示からcharacter YAMLを生成するstandalone wrapperで、内部でClaude CLIを実際に呼ぶ。Claude CLIがない場合は失敗してよい。
- `./lilia` launcherは外部character YAML生成を自動実行しない。`new` / `apply-newgame` はQ&A fallbackで `profile.md` を作り、必要な時だけ人間または後続自動化が `scripts/lilia_generate_character_yaml.py` を明示実行する。
- `scripts/lilia_character_to_profile.py` を追加済み。character YAMLから `lilia/main/profile.md` を生成し、必要ならsource/debug用に `lilia/main/profile.yaml` も保存できる。
- `templates/session/lilia/main/profile.md` を追加済み。`./lilia apply-newgame` は外部character systemを強制せず、Q&A fallbackとして `profile.md` も生成する。
- Persona Profile導線の最小確認として、既存character YAMLから `/tmp/lilia_profile_session/lilia/main/profile.md` を生成し、`./lilia prompt-only new test_persona_profile` のprompt bundleに Persona Profile Generation Pass と first scene前 profile必読指示が入ることを確認済み。
- `prompt/newgame.md` に `First Scene Quality Gate` を追加済み。初回sceneが助け待ち一本道、明白な正解行動、信頼上昇だけの処理、欠けた台詞や壊れた引用符を含む出力にならないよう軽く確認する。
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
- Story / Relationship Accumulation Loop のテンプレート最小接続が完了済み。`current/event_card.md` に Story Residue、`story/story_deck.md` に World Pressure / 1-3 Scene Return と NPC / Contact Notes、`story/relationship_spine.md` に 固定しないこと と 次に変わりうる点を追加し、`prompt/newgame.md` / `prompt/save_resume.md` に正本参照を追加済み。
- `docs/CRISIS_COMBAT_ABILITY_CONSTRAINT_LOOP.md` を作成済み。危機・戦闘・能力を勝敗処理ではなく、関係、記憶、beliefs、voice、自己理解に残る揺れとして扱う正本。
- Crisis / Combat / Ability Constraint Loop では、初期MVPに HP管理、ダメージ計算、部位管理、行動順、combat engine、villain_engine、case_engine、巨大組織戦、親密sceneへの雑な乱入を採用しない。
- Crisis / Combat / Ability Constraint Loop のテンプレート最小接続が完了済み。`current/event_card.md` に `Crisis / Ability Check`、`story/story_deck.md` に `Crisis / Ability Echo`、`lilia/main/state.md` に `Crisis / Ability Condition`、`story/relationship_spine.md` に危機後の頼り方 / 頼られ方、能力使用後の信頼 / 警戒を追加し、`prompt/newgame.md` / `prompt/save_resume.md` に `docs/CRISIS_COMBAT_ABILITY_CONSTRAINT_LOOP.md` 参照を追加済み。
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

## 4. 採用元

- MIRA: 人格構造 `core / voice / state / relationship / memory / beliefs`、特に voice / memory / beliefs
- inner-galge: キャラ中心、hotset、Markdown運用、character YAMLから登場前mdを作る流れ、style defaults、romance/intimacy運用、memory model、validation、voice continuity、command導線、更新ループ、感情の骨を抽出して現在キャラへ変換する手順
- LIRIA: session構造、event_card、save/resume、archive、story_reference / Light Story Reference Pass、Story Reference Layer、selection signals、candidate shortlist、Reference Engine、style defaults、romance、case/runtimeの運用知見、Visible Request Gate、Truth Hiding Boundary、Mid-Story Activation Gate、integrity check、manual smoke、growth update

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
- 次の実作業は、新Q&A v1.1 + Persona Profile導線で `./lilia codex-new <session>` を再テストすること。
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
