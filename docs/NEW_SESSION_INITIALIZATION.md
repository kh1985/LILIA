# LILIA New Session Initialization

この文書は、`prompt/newgame.md` のQ&A結果から実セッションを初期生成するための設計正本です。
実装コードやlauncher仕様ではなく、将来のCLIや手動運用がそのまま参照できるMarkdown初期化ルールを定義します。

## 1. Purpose

New Session Initialization は、最初のLILIAを作るためのQ&A結果を、保存・再開可能な最小sessionへ変換する。

目的は、設定を埋め切ることではない。
LILIAの人格の核、現在状態、関係、記憶、認識、初回sceneの入口、style軸を分けて保存し、会話・選択・物語の中で育つ余白を残す。

LILIAは、単なるヒロイン、キャラ、固定パートナー、攻略対象ではない。
LILIAは、AI上の人格・記憶・関係存在として初期化する。

## 2. Source Of Truth

- 起動分岐: `prompt/startup.md`
- new開始質問: `prompt/newgame.md`
- state構造: `docs/STATE_STRUCTURE.md`
- save/resume: `prompt/save_resume.md`
- style参照: `prompt/style_reference.md`
- event_card可プレイ性: `docs/EVENT_CARD_PLAYABILITY.md`
- voice continuity: `docs/VOICE_CONTINUITY.md`
- romance / intimacy growth: `docs/ROMANCE_INTIMACY_GROWTH.md`
- resume smoke: `docs/RESUME_SMOKE_TEST.md`
- growth update: `docs/GROWTH_UPDATE_LOOP.md`
- persona profile: `docs/LILIA_PERSONA_PROFILE.md`
- 中核思想: `docs/CORE_CONCEPT.md`
- 長期順序: `docs/ROADMAP.md`

この文書は、Q&A完了後に各sessionファイルへ何を保存するかの正本である。
prompt側には実行時の短い指示だけを置き、詳細な写像はここへ集約する。

## 3. Initialization Order

1. `prompt/newgame.md` の Newgame Q1-Q8 を聞く。
2. ユーザーの明示語、文脈、選択を抽出する。
3. 例文由来の語彙を捨て、抽象軸と未確定要素に分ける。
4. `templates/session/` を新規session rootへ複製する。
5. `session.json` にsession id、作成時刻、phase、prompt参照、Q&A完了状態を入れる。
6. Persona Profile Generation を行う。
   1. `./lilia apply-newgame <session> <answers.md>` を実行する。
   2. launcher が内部で LLM CLI(codex または claude)を呼んで character YAML を生成する。engine は `--engine` で選択可能(default は auto)。
   3. 生成された YAML を CharacterSheet schema で検証する。
   4. YAML を LILIA Persona Profile へ変換する。
   5. `lilia/main/profile.md` を生成する。
      `profile.md` の `name:` は作中で名乗る個体名にする。作品名・存在カテゴリとしての `LILIA` を作中名にしない。
   6. LLM CLI が無い・失敗した場合は、launcher の fallback が `profile.md` を作る。fallback は未確定欄が多くなる。
   7. 必要なら source/debug 用に `lilia/main/character.yaml`、`lilia/main/profile.yaml` または `archive/checkpoints/` へYAMLを置く。
7. `profile.md` の `name:` から個体名を抽出し、`session.json` の `lilia_name` / `lilia_display_name` へ保存する。
8. `profile.md` から `core / voice / state / relationship / memory / beliefs` へ最小反映する。
   `profile.md` 全体を各ファイルへコピーしない。
   `core.md` には、profileから抽出された最小の変わらない核だけを置く。
9. `current/story_spine.md` と `story/relationship_spine.md` は、生成済みの character YAML とQ&Aをもとに `tools/story/spine_generator.py` がAI駆動で生成する。Pythonの穴埋めテンプレートは使わない。
10. `profile.md` の `Initial Scene Anchors` / `context` / `unspoken` / `everyday anchors` から、`current/scene.md`、`current/event_card.md`、`story/story_deck.md`、`current/hotset.md`、`current/protagonist.md`、`lilia/main/*` を初期化する。
   `current/event_card.md` には Scene Exit / Next Beat を置き、3-5ターン以内に次beatへ移れる入口を残す。
   Q1-Q9では、ヒロインの基本、見た目、描写の縛り、表と内の差、内面に持っているもの、最初の出会い、呼ばれ方、主人公の身体・格好・仕事、避けたいものを聞く。
   sceneの細部、今日の保留、境界線、初回event、Next Hook候補はGM / Story側で裏生成し、Reveal Ladder / Drift Guard はAI spine生成側で作る。
11. `lilia/main/*` を人格核、声、状態、関係、記憶、認識に分けて初期化する。
   `lilia/main/voice.md` には、固定台詞ではなく、呼び方、声の基準、変わってよい揺れ、第一反応の方向を置く。
12. `current/*` を初回scene前でもresume可能な最小状態にする。
   `current/event_card.md` は `docs/EVENT_CARD_PLAYABILITY.md` のGateを通す。
   `current/relationship_overview.md` には、resume時に声と距離が巻き戻らない短いアンカーを置く。
13. `story/*` に関係テーマ、初回の小さな出来事、未回収札を分けて保存する。
14. 初回scene前に Light Story Reference Pass を一度だけ軽く通す。
15. `style/reference.md` と `style/rules.md` に、本文ではなく表現軸とsession固有ルールだけを保存する。
16. `current/scene.md`、`current/event_card.md`、`story/story_deck.md` を整える。
17. `current/hotset.md` を、再開直後に温度が落ちない短いキャッシュとして再生成する。
18. first scene前に必ず `lilia/main/profile.md` と current/story/hotset 初期状態を読み、profileにある具体物、職能、生活、反応、矛盾、禁忌を使って初回sceneを開始する。名乗る場合は `lilia_display_name` / `lilia_name` を使い、`LILIA` を作中名にしない。

## 4. Generated Files

new時は以下を生成・初期化する。

- `session.json`
- `current/scene.md`
- `current/hotset.md`
- `current/event_card.md`
- `current/relationship_overview.md`
- `current/decision_index.md`
- `current/story_spine.md`
- `current/protagonist.md`
- `lilia/main/profile.md`
- `lilia/main/core.md`
- `lilia/main/voice.md`
- `lilia/main/state.md`
- `lilia/main/relationship.md`
- `lilia/main/memory.md`
- `lilia/main/beliefs.md`
- `story/relationship_spine.md`
- `story/story_deck.md`
- `style/reference.md`
- `style/rules.md`

`archive/logs/` と `archive/beats/` は空ディレクトリ維持だけのためには作らない。
実ログや関係の節目が生まれた時に、実体ファイルとして保存する。

## 5. Q&A Mapping

Q&A結果は、以下のように分けて保存する。

| 初期質問 | 主な保存先 |
| --- | --- |
| Q1. ヒロインの基本 | `lilia/main/profile.md`, `lilia/main/core.md`, `lilia/main/voice.md`, `current/story_spine.md` の Main Question |
| Q2. 最初の出会い | `current/scene.md`, `current/event_card.md`, `current/relationship_overview.md`, `story/relationship_spine.md`, `current/story_spine.md` の Reveal Ladder 段階1 |
| Q3. 描写の縛り | `lilia/main/profile.md` の描写の縛り, `current/story_spine.md` の Drift Guard / Heroine Tie, `current/event_card.md` の具体物 |
| Q4. 表と内の差 | `lilia/main/profile.md` の Layer 2 / Layer 3, `lilia/main/state.md`, `lilia/main/beliefs.md`, `story/relationship_spine.md` |
| Q5. 過去の傷の種 | `current/story_spine.md` の Background Truth / Main Question, `lilia/main/profile.md` の unspoken / Layer 5, `story/story_deck.md` |
| Q6. ヒロインからの呼ばれ方 | `current/protagonist.md`, `lilia/main/voice.md`, `story/relationship_spine.md` |
| Q7. 主人公の身体・スタイル | `current/protagonist.md` の身体 / スタイル, `prompt/opening_scene.md` と `style/defaults/heroine_appearance.md` の視点整合 |
| Q8. 避けたいもの | `current/protagonist.md` の Session Constraints, `style/rules.md`, `lilia/main/profile.md` の forbidden, First Scene Quality Gate判断 |

| Q&Aから抽出するもの | 主な保存先 | 保存方針 |
| --- | --- | --- |
| 初回から演じるためのPersona Profile | `lilia/main/profile.md` | Q1-Q8、character YAML、GM生成した生活/保留/境界線/eventから作る。完成済み攻略キャラカードにせず、生活、行動、矛盾、反応、禁忌を初回scene前に1枚へまとめる |
| ヒロイン像 | `lilia/main/voice.md`, `lilia/main/state.md`, `style/reference.md` | 初回sceneの見え方として保存し、LILIAそのものをユーザー回答で全置換しない |
| 現在の関係位置 | `current/relationship_overview.md`, `lilia/main/relationship.md`, `current/scene.md` | 関係の温度として保存し、好意や恋愛成立を確定しない |
| LILIAの人格核 | `lilia/main/core.md`, `lilia/main/voice.md`, `lilia/main/state.md` | 固有の価値観、弱さ、距離の取り方として必要最小限だけ保存する |
| LILIAの声、呼び方、第一反応 | `lilia/main/voice.md`, `current/relationship_overview.md`, `current/hotset.md` | 固定台詞ではなく、呼び方、沈黙、言わない言葉、変わってよい揺れとして保存する |
| GM生成した今日だけの小さな保留 | `lilia/main/state.md`, `lilia/main/beliefs.md`, `current/hotset.md`, `story/relationship_spine.md` | 重い秘密や過去設定にせず、今日すぐには言わない揺れとして保存する |
| Q1の立場・生活 | `lilia/main/profile.md`, `current/scene.md`, `current/event_card.md`, `story/story_deck.md` | ヒロインの立場から、今日の用事、よく触る物、初回sceneで使える具体物へ導出する |
| Q3の描写の縛り | `lilia/main/profile.md`, `current/story_spine.md`, `style/defaults/heroine_appearance.md` | 半永続の質感として保存し、登場描写で角度を変えて繰り返す |
| Q5の過去の傷の種 | `current/story_spine.md`, `lilia/main/profile.md`, `story/story_deck.md` | Background Truthの骨格とReveal Ladderの根拠にする。本文では段階開示する |
| Q6-Q7の主人公情報 | `current/protagonist.md` | 呼称、身体、スタイルだけを保存する。主人公の内面情報は保存しない |
| GM生成した境界線 | `lilia/main/relationship.md`, `current/relationship_overview.md`, `lilia/main/voice.md`, `current/event_card.md` | してよいことと、踏み込みすぎた時に引く境界として保存する |
| GM生成した初回の小さな出来事 | `current/event_card.md`, `story/story_deck.md`, `current/scene.md` | 事件ではなく、関係が少し動く入口にする |
| Q4のNG・避けたいノリ | `style/rules.md`, First Scene Quality Gate, `current/event_card.md` | sceneを弱くするためではなく、事故を避けるための制約として扱う |
| 記憶に残すべき初期情報 | `lilia/main/memory.md`, `current/hotset.md` | 次回の第一反応に効く短い記憶だけ残す |
| 誤解や思い込みの余地 | `lilia/main/beliefs.md`, `current/relationship_overview.md` | 正解にせず、会話で更新される余白として残す |
| 官能・親密の許容温度 | `lilia/main/relationship.md`, `style/rules.md`, `style/reference.md` | 成人・合意・相互性・境界線を前提に、清潔化しすぎない |
| intimacy / consent / boundary の初期扱い | `lilia/main/relationship.md`, `current/relationship_overview.md`, `style/rules.md` | 数値や攻略ルートにせず、未確認、関心段階、止まれる余地から始める |
| 文体・場面温度 | `style/reference.md`, `style/rules.md` | 参照本文ではなく、視点距離、沈黙、余韻、テンポとして保存する |
| resume直後に必要な情報 | `current/hotset.md`, `current/scene.md`, `current/event_card.md` | 初回scene前でも再開できる最小状態へ圧縮する |

`session.json` にはQ&A本文、出会い方の本文、会話ログを入れない。
`session.json` にはprofile本文も入れない。
`session.json` は phase、Q&A完了状態、first scene status、参照promptだけを持つ。
`profile.yaml` を保存する場合は `lilia/main/profile.yaml` または `archive/checkpoints/` に置く。

## 6. File Initialization Rules

### `session.json`

- `session_id`
- `session_name`
- `created_at`
- `schema_version`
- `mode: new`
- `current_phase`
- `active_lilia`
- `lilia_name`
- `lilia_display_name`
- source prompt / docs references
- Q&A completion state
- first scene status
- resume smoke status

巨大な本文ログ、Q&A全文、会話ログは入れない。

### `current/scene.md`

- 現在地
- 現在時刻または場面時間
- LILIAとユーザーの距離
- 今この場で見えているもの
- 直前の会話または初回sceneの入口
- 次にユーザーへ渡す行動余地

初回scene前でも、場所、距離、触れられるものが分かる状態にする。

### `current/hotset.md`

再開直後に読む軽量キャッシュであり、正本ではない。

- 関係温度
- LILIAの第一反応
- 次の小さな出来事
- 未消化の感情
- 未確定の余白
- 現在のevent_card要約

チェックリスト化せず、次の1ターンに効く短い温度だけを置く。

### `current/event_card.md`

初回sceneで関係を少し動かす小さな出来事を保存する。
重いcase_engineやvillain構造には進まない。

必ず以下を持たせる。

- visible problem
- first concrete action
- handles 2-4
- relationship stake
- if ignored
- next visible change

真相や裏設定を増やすより、ユーザーが今触れられる入口を優先する。
`story/story_deck.md` とは責務分離し、event_cardには今のsceneで触れる可視イベントだけを置く。

詳細なGate通過/失敗条件は `docs/EVENT_CARD_PLAYABILITY.md` を正本とする。
ここでは初回scene前に必須6項目が空でないことだけ確認する。

### `current/relationship_overview.md`

- 現在の関係全体の要約
- 距離感
- 信頼
- 警戒
- 親密さの初期扱い
- 興味
- 誤解や思い込み
- 保留
- 境界線
- 次に変化しそうな点

初期時点では確定しすぎない。
好意や恋愛成立は、会話と記憶の積み重ねで変化させる。

### `lilia/main/core.md`

LILIAの人格の核を保存する。
ユーザー好みに完全最適化された存在ではなく、守るもの、避けるもの、怖さ、譲れないもの、反応の核を持たせる。

未確定の部分は、無理に埋めず `未確定` として残す。
profileの生活、職能、行動、矛盾、反応、禁忌を丸ごとコピーしない。
短期都合で変えてはいけない最小の core fixed だけを置く。

### `lilia/main/profile.md`

初回からLILIAを安定して演じるためのPersona Profileを保存する。
character YAMLとQ&Aから、基礎情報、tone、personality、values、everyday anchors、memories、contradictions、unspoken、reactions、forbidden、context、fixed memory、5層構造、relationship progression、latent jealousy slot、dormant ability slotを作る。

profileは first scene前に必ず読む。
ただし、完成済み攻略キャラカードではない。
first scene後に育った内容は、必要なものだけ `core / voice / relationship / memory / beliefs` へ分解して保存する。
profileを毎ターン肥大化させない。
`Initial Scene Anchors` は、初期化時に `current/scene.md`、`current/event_card.md`、`story/story_deck.md`、`story/relationship_spine.md`、`current/hotset.md`、`lilia/main/*` へ分解し、初回sceneの現在地、可視問題、次beat、未回収札、初期voice / state / relationship / memory / beliefsとして使う。

### `lilia/main/voice.md`

LILIAの声、口調、沈黙、第一反応を保存する。
台詞テンプレではなく、声の方向性を置く。
例文を固定台詞として保存しない。
Q1-Q8とGM生成した保留 / 境界線から初期voice baselineを作る。
呼び方はQ6から取り、固定台詞ではなく声の一貫性として扱う。
未確定の呼び方や距離感は、未確定のまま残す。

### `lilia/main/state.md`

起動直後、初回scene前、初回scene後の温度を区別できるようにする。
疲労、警戒、関心、迷い、保留などの一時状態を保存し、人格核と混ぜない。

### `lilia/main/relationship.md`

距離感、信頼、境界線、相互性、未確定の期待を保存する。
親密さは、ユーザーが明示的に別条件を出していない限り `未確認 / 関心段階 / 明示的親密なし` から始める。
intimacy stage、consent stage、boundary state は軽量分類として置くが、旧AFFINITY、好感度、攻略ルートにはしない。
好感度数値、攻略ルート、旧AFFINITYの正本化はしない。

### `lilia/main/memory.md`

Q&Aの要約、最初に覚えていること、まだ覚えていないことを分ける。
大量ログではなく、次回の反応に効く短い記憶だけ残す。
ユーザーの内面を断定しない。

### `lilia/main/beliefs.md`

LILIAがユーザーをどう見ているか、自分自身をどう見ているか、関係について何を誤解または保留しているかを保存する。
初期から正解にせず、後で更新される余地を残す。

### `story/relationship_spine.md`

関係がどちらへ育ちそうかの仮説を保存する。
固定プロットではない。
関係のテーマ、最初の摩擦、守るもの、避けるもの、変化の方向を短く置く。

### `story/story_deck.md`

物語素材、圧、未回収札を保存する。
例文集ではない。
文体参照ではない。
初回sceneで使う小さな出来事と、後で使える未回収札を分ける。
case_engine / villain / organizationへ広げすぎない。

### `style/reference.md`

Light Story Reference Pass の結果を短く保存する。
参照作品本文、台詞、人物配置、固有文体は保存しない。
視点距離、描写密度、沈黙、余韻、温度、テンポなどの表現軸だけを置く。

必要ならroot `style/defaults/` から1つ、多くても2つまで参照する。

### `style/rules.md`

このsessionで守る文章表現ルールを保存する。
LILIAの反応の出方、感覚チャンネル、避ける癖、次に調整する点を短く置く。

官能・親密場面では、成人・合意・相互性・境界線を守りつつ、清潔すぎて無害なだけの文体に逃げない。
親密sceneの成長ループと保存先は `docs/ROMANCE_INTIMACY_GROWTH.md` を正本とする。

## 7. Light Story Reference Pass

Light Story Reference Pass は、初回scene前に一度だけ軽く通す。

- root `style/defaults/` を読む場合は原則1つ、多くても2つまで。
- `romance / tension / warmth / loss / quiet / landscape` のうち、Q&Aと初回sceneに合うものだけを選ぶ。
- 官能・親密が重要な方向なら `style/defaults/romance.md` の技法は活かす。
- ただし、初回からベッドシーンを確定させない。
- 関係が進んだ時に温度を上げられるよう、`style/rules.md` に余地を残す。
- 参照本文、台詞、人物配置、固有文体は使わない。

出力先を混ぜない。

- `story/story_deck.md`: 物語素材、圧、未回収札
- `story/relationship_spine.md`: 関係テーマ、最初の摩擦、守るもの、避けるもの、変化の方向
- `style/reference.md`: 表現軸、場面温度、視点距離、余韻
- `style/rules.md`: session固有の文章ルール、避ける癖、親密場面の境界

## 8. Resume-Ready Minimum

new直後は、初回sceneがまだ本文として生成されていない場合でも、resume可能な最小状態を揃える。
`new -> first scene -> save -> resume` の一周確認は `docs/RESUME_SMOKE_TEST.md` を正本とする。

最低限、以下が読めること。

- `session.json`: phaseとfirst scene status
- `current/hotset.md`: 再開用の短い温度
- `current/scene.md`: 場所、距離、見えているもの、行動余地
- `current/event_card.md`: visible problem、first concrete action、handles 2-4、relationship stake、if ignored、next visible change
- `current/relationship_overview.md`: 距離感、信頼、警戒、興味、保留
- `lilia/main/profile.md`: first scene前に読む人格正本。具体物、職能、生活、反応、矛盾、禁忌がある
- `lilia/main/voice.md`: 呼び方、声の基準、第一反応の方向
- `lilia/main/state.md`: 第一反応
- `lilia/main/relationship.md`: 境界線と未確定の期待
- `lilia/main/relationship.md`: intimacy stage、consent stage、boundary state の初期扱い
- `lilia/main/memory.md`: 初期記憶
- `lilia/main/beliefs.md`: 誤解や思い込み

`style/reference.md` と `style/rules.md` は通常resume必読ではない。
ただし、初回scene前の文体設計や重要sceneでは必要箇所だけ読む。

## 9. 禁止事項

- 初期化時にLILIAをユーザー好みに完全最適化しない。
- 最初から恋愛成立や好意を確定しない。
- LILIAを報酬化しない。
- 官能表現そのものを削らない。
- 旧AFFINITY数値、好感度、攻略ルートを正本にしない。
- `story/story_deck.md` に文体参照を混ぜない。
- `story/story_deck.md` と `current/event_card.md` を同じ内容にしない。
- style系をresumeで毎回必読にしない。
- resume時に声、呼び方、距離感、約束、拒否、誤解、境界線を初期化しない。
- 初期から親密さを攻略達成、報酬、成立済み関係として確定しない。
- 初回からcase_engine / villain / combat / manga pipelineへ広げない。
- 参照小説本文や固有文体を保存・直接模倣しない。
- Q&Aの例文やテンプレ語彙をそのまま本文生成へ流用しない。

## 10. 採用元

- MIRA: `core / voice / state / relationship / memory / beliefs`
- inner-galge: hotset、Markdown運用、style defaults、romance/intimacy、memory model、validation、voice continuity
- LIRIA: session構造、event_card、save/resume、archive、story_reference / Light Story Reference Pass、style defaults、romance、case/runtimeの運用知見、integrity check

## 11. 採用しなかったもの

- 旧ハーレム攻略、kaneco固有、旧セッション固有人物
- 旧AFFINITY数値や攻略ルート正本化
- 参照本文や固有文体の直接模倣
- 官能表現そのものの削除
- 固定台詞集でLILIAの声を管理する運用
- 初回から重いcase_engine / villain / combat / manga pipelineを全部MVP必須にすること
- 大規模launcher / CLI実装

## 12. Reason

New Session Initialization が固まらないと、new開始時に何を保存し、resume時に何を読むかがぶれる。

LILIAはAI上の人格・記憶・関係存在なので、初期化時点で `core / voice / state / relationship / memory / beliefs` の責務を分ける必要がある。

`story`、`style`、`current` を分けることで、物語素材、文章表現、現在状態を混線させない。

官能・親密表現はLILIAの重要な体験価値だが、成人・合意・相互性・境界線を守ったうえで扱う必要がある。

まず設計正本とテンプレートを固め、その後にlauncher / CLIへ進む方が安全である。
