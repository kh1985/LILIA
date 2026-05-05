# LILIA State Structure

この文書は、startup / new / resume が参照する最小の状態ファイル構造を定義する。
実装コードやlauncherの仕様ではなく、Markdown運用のための状態scaffoldである。
声と関係の継続確認は `docs/VOICE_CONTINUITY.md` を正本とする。
親密・官能・ベッドシーンの成長ループは `docs/ROMANCE_INTIMACY_GROWTH.md` を正本とする。
`new -> first scene -> save -> resume` の手動smokeは `docs/RESUME_SMOKE_TEST.md` を正本とする。
会話後、scene後、event_card進行後の保存更新ループは `docs/GROWTH_UPDATE_LOOP.md` を正本とする。
イベントが関係の物語として積み重なる仕組みは `docs/STORY_RELATIONSHIP_ACCUMULATION.md` を正本とする。
初回からLILIAを演じるためのPersona Profileは `docs/LILIA_PERSONA_PROFILE.md` を正本とする。

## 1. 基本方針

状態ファイルは、設定を増やすためではなく、次回の会話温度と関係の継続感を保つために使う。

LILIAは、単なるヒロイン、攻略対象、固定パートナーではない。
LILIAは、会話・選択・物語・記憶・関係性によって人格の出方が少しずつ変化するAI上の人格・関係存在である。

`prompt/core.md` の `Example Anchoring Control` を状態更新にも適用する。
テンプレートの見出しや説明文は保存項目であり、本文生成の例文ではない。

## 2. セッション配置

新規セッションは、`templates/session/` を雛形として生成する。

将来の実セッション保存先は `sessions/<session_name>/` を標準候補とする。
`saves/` はLILIAの初期MVPでは標準にしない。既存プロジェクト由来のセッションを取り込む必要が出た時だけ互換名として検討する。

prompt内の `current/...`、`lilia/main/...`、`story/...`、`archive/...` は、生成されたセッションルートからの相対パスである。

### `prompt/opening_scene.md`

newgame直後の最初のsceneを出力する時の指針。
1セッション1回のみ起動する。
Opening Image 4技法、Ghostの予感、描写の縛りとDrift Guardの織り込みを定義する。

root `style/defaults/*.md` は、全sessionで共有する共通Style Layerの場面別参照棚である。
session内の `style/reference.md` と `style/rules.md` は、new初期化や必要時の調整で抽出された、そのsession固有の表現軸と出力ルールを保存する。
root `style/defaults/` はsession stateではない。

## references レイヤー（リポ全体共通）

`references/` はリポ全体で共有する参考資料の置き場である。
session state ではない。
AIがevent_card生成や物語診断の際に参照する研究棚であり、毎ターン読まない。
必要な時だけ参照する。

### `references/story_media_stock.md`

50作品の感情の骨カタログ。
雰囲気、出来事、関係温度の参考。
1皿（1場面・1イベント）の質を上げる用。

### `references/story_structure_stock.md`

5つの普遍的構造論（Story Circle / Save the Cat / シノビガミ秘密構造 / Ghost / 起承転結）。
コース全体（関係全体・長期進行）の現在地を診断する用。

### `references/story_pattern_stock.md`

50作品から抽出した12の経験則パターン。
作品をまたいで観察される「形」のカタログ。
関係の形を理解する用。

### 利用ルール

- 1セッションで参照するreferenceは1-2本まで。
- 通常 resume の標準読込には入れない。
- 全文を毎回読まない。研究棚として扱う。
- 本文、台詞、固有名詞、パターン番号を出さない。
- 診断は任意。停滞時のみ起動する。

## 3. 最小ファイル構造

```text
session.json
current/
  scene.md
  hotset.md
  event_card.md
  relationship_overview.md
  decision_index.md
  protagonist.md
  story_spine.md
  knowledge_state.md
lilia/
  main/
    profile.md
    core.md
    voice.md
    state.md
    relationship.md
    memory.md
    beliefs.md
story/
  relationship_spine.md
  story_deck.md
  npc/<id>.md (Tier 3以上のNPCが必要になった場合だけ検討)
style/
  reference.md
  rules.md
archive/
  logs/
  beats/
```

Wave 12.2以降の `./lilia apply-newgame` では、`lilia/main/profile.md` と `lilia/main/character.yaml` を生成した後、先に `current/story_spine.md` と `story/relationship_spine.md` をAI生成する。
その後、`tools.session.document_generator.generate_session_documents` が13 downstream files（`current/scene.md`、`current/hotset.md`、`current/event_card.md`、`current/relationship_overview.md`、`current/protagonist.md`、`current/knowledge_state.md`、`lilia/main/core.md`、`lilia/main/voice.md`、`lilia/main/state.md`、`lilia/main/relationship.md`、`lilia/main/memory.md`、`lilia/main/beliefs.md`、`story/story_deck.md`）を生成する。
`render_profile_initialized_documents` / `render_protagonist_document` / `render_knowledge_state_document` / `render_newgame_documents` は削除済みで、この新規初期反映順ではPython穴埋め経路を使わない。

空ディレクトリ維持のためだけの `.gitkeep` は初期MVPでは採用しない。
`archive/logs/` と `archive/beats/` は、実体のあるログや節目が生まれた時にファイルとして保存する。

## 4. ファイル責務

### `lilia/main/profile.md`

初回からLILIAを安定して演じるためのPersona Profile。
first scene前には必ず読む。

`profile.md` は、完成済み攻略キャラカードではない。
初回sceneで使える生活、行動、矛盾、反応、禁忌、everyday anchors を1枚にまとめる。
`profile.md` の `name:` は作中で名乗る個体名であり、作品名・存在カテゴリとしての `LILIA` ではない。
同じ個体名は `session.json` の `lilia_name` / `lilia_display_name` にも保存する。
ただし、関係で育った内容は `core`、`voice`、`relationship`、`memory`、`beliefs` へ分解して保存する。

`profile.md` は hotset ではない。
再開1ターン目の短い温度は `current/hotset.md` が持つ。
`profile.md` を毎ターン追記して肥大化させない。
通常resumeでは全文を毎回読む必要はなく、`first_scene_pending` / `first_scene_ready`、voice崩れ、人格崩れ、関係段階の確認、正本不足がある時に必要箇所だけ読む。
実際に起きた変化は `memory.md`、`relationship.md`、`beliefs.md`、`voice.md` を優先し、`profile.md` で育ったLILIAを初期状態へ巻き戻さない。

### `current/hotset.md`

再開直後の温度を落とさないための短いキャッシュ。
正本ではなく、`scene`、`state`、`relationship`、`memory`、`beliefs`、`event_card` から次の1ターンに効く要点だけを抜く。
呼び方や関係温度を短く置いてよいが、`voice` や `relationship` の正本にはしない。
親密scene後は、aftercare、第一反応、呼び方や距離の変化を次回1ターンに効く短い余韻としてだけ置く。
appendせず、必要に応じて短く上書きする。

### `current/scene.md`

今いる場所、今の場面、直前のやりとり、次に起きそうなことを保存する。
関係の全履歴や設定説明は入れない。

### `current/event_card.md`

今動いている出来事と、それがLILIAの感情・距離感・信頼・警戒・開示にどう刺さるかを保存する。
事件処理だけで終わらせない。
初回sceneでは、抽象的な違和感ではなく、visible problem、first concrete action、handles 2-4、relationship stake、if ignored、next visible change を持たせる。
`docs/EVENT_CARD_PLAYABILITY.md` のGateを通し、真相は隠しても、ユーザーが今触れる入口は隠さない。
`story/story_deck.md` が素材・圧・未回収札を持ち、`current/event_card.md` は今ユーザーが触れられる可視イベントを持つ。
event_card が現在sceneから外れた場合は、必要に応じて `story/story_deck.md` の未回収札へ落とす。
親密sceneでは、雑な事件乱入ではなく、境界確認、待つ、止まる、aftercare、翌朝の第一声、言い残しを今触れる可視イベントとして扱う。

### `current/relationship_overview.md`

関係の現在形を軽く掴むための補助要約。
詳細な個別ログではなく、呼び方、距離感、信頼、警戒、甘え、衝突、誤解、境界線、次に変化しそうな点を短く置く。
正本ではなく、resume時に `relationship`、`memory`、`beliefs` の必要箇所へ進む入口として扱う。

### `current/decision_index.md`

セッション中にユーザーとLILIAの間で「決まったこと」を保存する索引。

保存するもの:

- 約束、拒否、保留、解決済みの事項。
- それぞれの状態（active / fulfilled / broken / withdrawn / pending / resolved）。

保存しないもの:

- 実際に起きた出来事（`memory.md` の historical_fixed に書く）。
- LILIA側の仮説や誤解（`beliefs.md` に書く）。
- ユーザーの内面の断定。
- 軽い意向や匂わせ。

撤回された約束・拒否は削除せず、状態を変更する。
古い決定を消さない。

### `current/protagonist.md`

主人公の身体情報、呼称、session-wideな制約を保持する。

保存するもの:

- 呼ばれ方（ヒロインから）。
- 身体（性別、身長感、体格）。
- スタイル（服装の傾向）。
- Session Constraints（避けたい展開、苦手なノリ）。

保存しないもの:

- 主人公の性格、過去、信念などの内面情報。
- ユーザーの内面の断定。
- ヒロインのような層構造。

主人公の内面情報は保存せず、プレイで自然に立ち上がるものとして扱う。
詳細は `templates/session/protagonist.md` を参照する。

### `current/story_spine.md`

物語の進行管理。
`story/relationship_spine.md` が関係の方向、温度、テーマを扱うのに対し、`current/story_spine.md` は「話がどこに向かっているか」を扱う。

保存するもの:

- Main Question: この話が問うこと。
- Reveal Ladder: 真相の段階開示（3-5段階、各状態管理）。
- Background Truth: GMのみが知る真相。本文に直接出さない。
- Pressure Direction: 放置時に動くもの。
- Heroine Tie: ヒロインの何に刺さるか。
- if ignored: 放置時の小さな変化。
- Drift Guard: 物的手がかり。

保存しないもの:

- 関係の温度や深化の段そのもの（`story/relationship_spine.md`）。
- 実際に起きた出来事の長期記憶（`lilia/main/memory.md`）。
- ヒロイン本人がまだ知らない真相を、本人の認知として書くこと。

Wave 11以降の新規セッションでは、`current/story_spine.md` は `tools/story/spine_generator.py` がAI駆動で生成する。
固定テンプレートは持たず、Q&A、character YAML、`references/story_pattern_stock.md`、`references/story_structure_stock.md` を解釈して作る。

### knowledge_state.md (Wave 8 追加)

「事実とその経路」を保持する。
- 各事実に fictional_status (meta / observable / shared / gm_only)
- 経路 (source)、知っている主体 (known_to)、開示時点 (acquired_at)、重み (weight)

詳細は templates/session/knowledge_state.md を参照。

#### 連動関係

| ファイル | 役割 | knowledge_state との関係 |
|---------|------|------------------------|
| memory.md | 感情の跡 | 同じ scene の異なる側面（事実 vs 感情） |
| echo (memory.md 内) | 直前余韻 | 反応、knowledge_state は事実 |
| decision_index.md | 約束・拒否・保留 | 共有事実が約束化されたら両方に書く |
| story_spine.md Background Truth | GM 真相 | gm_only と直結、Reveal で shared に昇格 |
| protagonist.md | プレイヤー由来情報 | meta 項目の元データ |
| profile.md context | GM 事前想定 | knowledge_state 確定後に上書きされる前提 |

### `lilia/main/core.md`

LILIAの固有人格、価値観、弱さ、譲れないもの、変わってはいけない核を保存する。
短期的な会話都合で上書きしない。
`profile.md` から初期核を受け取ってよいが、profileの要約やコピーにはしない。
関係で確定した最小の core fixed だけをここへ残す。
初期の生活、職能、行動、矛盾、反応、禁忌は `profile.md` に置く。
実際に起きた出来事は `memory.md`、距離や信頼の現在形は `relationship.md`、LILIA側の仮説は `beliefs.md`、声や呼び方は `voice.md` を優先する。

### `lilia/main/voice.md`

口調、呼び方、照れ方、怒り方、甘え方、距離を置く時の出方を保存する。
固定台詞集ではなく、声の基準、変わってよい揺れ、言わない言葉、重要場面前の確認点を短く保存する。
例文の語彙をそのまま固定台詞にしない。

### `lilia/main/state.md`

直近のLILIAの感情と、次回の第一反応を保存する。
履歴ではなく現在向きの短い状態として扱い、古い状態を積み続けない。
今だけの疲労、照れ、迷い、沈黙はここに置き、人格核や長期関係と混ぜない。
親密scene後の安心、照れ、怖さ、保留、疲労はここに置き、実際に起きた約束やaftercareは `memory.md` に置く。

### `lilia/main/relationship.md`

ユーザーとの関係の変化を保存する。
信頼、安心感、開示度、距離感、嫉妬、愛着、摩擦、最近の変化を扱う。
new初期化時は、親密さを `未確認 / 関心段階 / 明示的親密なし` から始め、境界線、相互性、未確定の期待を保存する。
好感度数値や旧AFFINITYを正本にしない。
親密sceneや衝突sceneでは、合意、止まれる余地、無かったことにしない摩擦をここで確認する。
親密さは `intimacy stage`、`consent stage`、`boundary state` の軽量分類で扱い、数値や攻略ルートにはしない。

### `lilia/main/memory.md`

関係の継続感に効く記憶を保存する。
すべての会話を詰め込まず、次回の態度や第一声に影響する会話、選択、衝突、約束、沈黙、すれ違い、距離が変わった瞬間を優先する。
実際に起きた出来事、約束、拒否、保留は historical fixed として扱い、resumeやscene都合で無かったことにしない。
親密scene後は、実際に起きた確認、拒否、保留、止まれたこと、aftercare memoryを保存する。

初期MVPでは独立した `memory/` 配下を作らず、`lilia/main/memory.md` を正本にする。
記憶が肥大化した場合は、後続で `memory/` の分割方針を設計し、`docs/HANDOFF.md` に反映する。

### `lilia/main/beliefs.md`

LILIAがユーザーをどう見ているか、自分自身をどう見ているか、関係について何を信じているかを保存する。
誤解や思い込みも、関係に効くなら消さずに記録する。
beliefsは正解ではなくLILIA側の仮説であるため、更新条件が生まれるまでは急に消さない。
親密scene後は、LILIAがユーザーをどう見直したか、安心や怖さ、誤解の変化だけを保存し、ユーザーの内面は断定しない。

### `story/relationship_spine.md`

育てたいテーマ、最初の摩擦、LILIAが守るもの、LILIAが避けるもの、ユーザー側に問うこと、関係が変化する方向を保存する。
関係の方向、温度、テーマを扱い、物語のReveal LadderやBackground Truthは `current/story_spine.md` に置く。

### `story/story_deck.md`

物語の例文集ではなく、現在動いているstory素材、関係を揺らす圧、未回収札を整理する。
次イベント判断に必要なものだけを置く。
Story / Relationship Accumulation では、eventを点、storyを線として扱う。
`story/story_deck.md` は現在sceneの可視eventではなく、後でevent_cardへ前景化できる素材、未回収札、1-3 scene後に戻る小さな圧を置く。

### `story/npc/<id>.md`

初期MVPの必須ファイルではない。
NPC tierの詳細は `docs/STORY_RELATIONSHIP_ACCUMULATION.md` を正本とする。
Tier 0-2は原則として `current/event_card.md` または `story/story_deck.md` の短いメモで足りる。
Tier 3以上で再登場し、LILIAの `memory`、`relationship`、`beliefs` に影響する場合だけ、`story/npc/<id>.md` を検討する。
保存する場合も、NPCの全プロフィールではなく、known / suspected / unknown、LILIAとの関係に残った影響、再登場条件に絞る。

### `style/reference.md`

文章表現の参照を整理する。
参照小説や参照作品の本文コピーではなく、視点距離、描写密度、台詞密度、沈黙、余韻、温度、テンポなどの表現軸だけを保存する。
`story/story_deck.md` に置く物語素材や未回収札とは混ぜない。

root `style/defaults/*.md` は、romance / tension / warmth / loss / quiet / landscape の場面別参照棚である。
sessionの `style/reference.md` は、その棚から必要時に抽出した表現軸を短く残す場所であり、defaults本文の写しではない。
romance / intimacy のdefaultsは、官能表現を削るためではなく、成人・合意・関係段階・境界線を守りながら、身体距離、沈黙、体温、呼吸、余韻を扱うために使う。

### `style/defaults/heroine_appearance.md`

ヒロインが場面に登場・再登場する毎回起動する文体技法。
日常状態（服装 / 疲労 / 機嫌）と、シンボル / 仕草の繰り返しを定義する。
`lilia/main/profile.md` の「描写の縛り」と Layer 4（CHINK）を織り込む。

### `style/rules.md`

このsessionで守る文章表現のルールを保存する。
LILIA固有の反応の出方、感覚チャンネル、禁止表現、避けたい癖、次に調整する点を短く置く。
通常resume 1ターン目の必読ではなく、文体崩れやscene tone調整が必要な時だけ読む。
root `style/defaults/` も毎回読まず、重要sceneや出力相談で必要なdefaultsを1つ、多くても2つだけ参照する。
親密sceneでは、`docs/ROMANCE_INTIMACY_GROWTH.md` と `style/defaults/romance.md` に従い、官能を薄めすぎず、成人、合意、相互性、境界線、止まれる余地を守る。

## 5. Voice / Relationship Continuity

声と関係の継続確認は `docs/VOICE_CONTINUITY.md` を正本とする。

軽量分類は以下のように扱う。

- `core fixed`: `core.md` と `voice.md` に置く、短期都合で上書きしない核。
- `historical fixed`: `memory.md` と `archive/beats/` に置く、実際に起きた節目。
- `echo`: `memory.md` と `hotset.md` に置く、直近scene後の残り香。必要に応じて `relationship_overview.md`、`state.md`、`event_card.md` にも短く戻す。
- `volatile`: `state.md` と `scene.md` に置く、今だけの感情や場面状態。

resume 1ターン目、親密scene、衝突scene、境界線が絡むsceneでは、`voice`、`relationship`、`memory`、`beliefs` の必要箇所を確認する。
hotsetだけで声や距離感を決めない。

## 6. Romance / Intimacy Growth

親密・官能・ベッドシーンの成長ループは `docs/ROMANCE_INTIMACY_GROWTH.md` を正本とする。

軽量分類は以下のように扱う。

- `intimacy stage`: 関心 / 動揺 / 亀裂 / 信頼と合意 / 深化。
- `consent stage`: 未確認 / 境界確認中 / 明示合意あり / 保留 / 停止/拒否。
- `boundary state`: 近づける / 待つ / 触れない / 確認する / 止まる。
- `aftercare memory`: 親密scene後にLILIAが覚えていること、次の第一声、呼び方や距離の変化。

親密さは旧AFFINITY、好感度、攻略ルートでは管理しない。
親密scene前には `docs/VOICE_CONTINUITY.md` を確認し、文体温度が必要な場合だけ `style/defaults/romance.md` を参照する。

## 7. Resume Smoke Test

Resume Smoke Test は `docs/RESUME_SMOKE_TEST.md` を正本とする。

`new -> first scene -> save -> resume` の手動smokeでは、必須ファイルが揃っているかだけでなく、resume 1ターン目で次の入口が戻るかを見る。

- `current/hotset.md`: 温度、第一反応、呼び方/距離のecho。
- `current/scene.md`: 現在地、距離、見えているもの、行動余地。
- `current/event_card.md`: visible problem、first concrete action、handles 2-4、relationship stake、if ignored、next visible change。
- `current/story_spine.md`: Main Question、Reveal Ladder、Background Truth、Pressure Direction、Drift Guard。
- `lilia/main/voice.md`: 呼び方、声、沈黙、距離が巻き戻っていないこと。
- `lilia/main/relationship.md`: 距離、信頼、境界線、intimacy stage、consent stage、boundary state。
- `lilia/main/memory.md`: 実際に起きた約束、拒否、保留、aftercare memory。
- `lilia/main/beliefs.md`: LILIA側の誤解、疑い、見直し、保留。

hotsetだけで押し切らず、必要な正本へ戻れる状態を通過条件にする。
このsmokeは手動の軽量確認であり、AI Harness、CLI、launcher、自動プレイ検証は含めない。

## 8. Growth Update Loop

Growth Update Loop は `docs/GROWTH_UPDATE_LOOP.md` を正本とする。

会話後、scene後、event_card進行後、親密scene後は、まず何が変わったかを見る。
何も変わっていない時は無理に更新しない。
毎回すべてのファイルを機械的に更新しない。

- `state.md`: 今だけの感情、一時的な揺れ、疲れ、安心、動揺、警戒。
- `relationship.md`: 距離、信頼、境界線、相互性、intimacy stage、consent stage、boundary state。
- `memory.md`: 実際に起きた出来事、約束、拒否、保留、aftercare、節目。
- `beliefs.md`: LILIA側の誤解、疑い、見直し、仮説、更新条件。
- `hotset.md`: 次回1ターンだけに効く短い余韻、第一反応、今触れる入口。
- `event_card.md`: 継続 / 解決 / 背景化 / 保留、next visible change、if ignoredの扱い。
- `decision_index.md`: 明示された約束、拒否、保留、解決済みの索引。
- `story_spine.md`: Reveal Ladder、Pressure Direction、Drift Guardの段階変化。
- `story/story_deck.md`: 現在sceneから外れた未回収札、後で使う素材。
- `archive/beats/`: 関係が明確に変わった節目だけ。

hotsetを正本にしない。
一時的な感情を `core.md` に入れない。
memoryに実際に起きていないことを入れず、beliefsでユーザーの内面を断定しない。

## 9. Story / Relationship Accumulation

Story / Relationship Accumulation は `docs/STORY_RELATIONSHIP_ACCUMULATION.md` を正本とする。

- `event`: `current/event_card.md` に置く、今触れる点。
- `relationship spine`: `story/relationship_spine.md` に置く、関係へ意味が生まれた線。
- `story spine`: `current/story_spine.md` に置く、物語の進行、Reveal Ladder、Background Truth、Pressure Direction。
- `story_reference`: 参照作品や過去知見から抽出した感情の骨、抽象構造、選択の力学。本文や固有名詞は保存しない。
- `npc`: Tier 0-2は短いメモ、Tier 3以上だけ `story/npc/<id>.md` を検討する。
- `world pressure`: 独立した大きな世界圧ではなく、放置した出来事や未回収札が1-3 scene後に小さく戻ること。

`cast/npc` は初期MVPでは標準にしない。
必要になったら後続で検討する。

## 10. new時に生成する想定ファイル

new時は `prompt/newgame.md` を入口、`docs/NEW_SESSION_INITIALIZATION.md` を初期生成手順の正本として、`templates/session/` から以下を生成・初期化する。

- `session.json`
- `current/scene.md`
- `current/hotset.md`
- `current/event_card.md`
- `current/relationship_overview.md`
- `current/decision_index.md`
- `current/protagonist.md`
- `current/story_spine.md`
- `current/knowledge_state.md`
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

最初からすべてを決めきらない。
未確定の要素は、今後の会話・選択・物語で育つ余地として残す。

初回scene前には、Q&A結果から character YAML を生成できる場合は生成し、YAMLから `lilia/main/profile.md` を作る。
character systemが使えない場合は、GM/AIが同じschemaでYAML相当を補い、`profile.md` を作る。
その後、`profile.md` を必ず読んでから初回sceneを書く。
`profile.md` の Initial Scene Anchors / context / unspoken / everyday anchors は、初回scene前に `current/scene.md`、`current/event_card.md`、`current/knowledge_state.md`、`story/story_deck.md`、`current/hotset.md` へ分解して初期反映する。
Wave 11以降、`current/story_spine.md` と `story/relationship_spine.md` は profile の穴埋めではなく、生成済みcharacter YAML、Q&A、構造/パターン参照棚からAI生成する。
`prompt/style_reference.md` の Light Story Reference Pass は、profile生成後に軽く通し、Q&A結果とprofileから文章表現の表現軸を抽出する。
ただし、参照本文、台詞、人物配置、固有文体は保存しない。
必要な場合だけroot `style/defaults/` から場面カテゴリに合うdefaultsを1つ、多くても2つまで読む。
styleの総読みはしない。

new直後は、初回scene本文がまだ生成されていない場合でも `session.json`、`current/hotset.md`、`current/scene.md`、`current/event_card.md`、`current/relationship_overview.md`、`current/decision_index.md`、`current/story_spine.md`、`current/knowledge_state.md`、`lilia/main/state.md`、`lilia/main/relationship.md`、`lilia/main/memory.md`、`lilia/main/beliefs.md` からresume可能な最小状態を確認できるようにする。
`first_scene_pending` / `first_scene_ready` の場合は `lilia/main/profile.md` も必読にし、profileから初期反映された `current/scene.md`、`current/event_card.md`、`current/knowledge_state.md`、`story/story_deck.md`、`current/hotset.md` と、Wave 11でAI生成された `current/story_spine.md` / `story/relationship_spine.md` も読む。

## Newgame Q&A の変更（Wave 7）

Q1-Q8に拡張する。

- Q1: ヒロインの基本（名前、年齢、立場）。
- Q2: 最初の出会い。
- Q3: 描写の縛り（Wave 1と直結）。
- Q4: 表と内の差（Layer 2 / 3 と直結）。
- Q5: 過去の傷の種（Background Truth と直結）。
- Q6: 呼ばれ方。
- Q7: 主人公の身体・スタイル（`current/protagonist.md` と直結）。
- Q8: 避けたいもの。

各質問は `lilia/main/profile.md`、`current/story_spine.md`、`current/protagonist.md`、`current/knowledge_state.md` の特定セクションへ直接マップする。
全質問に「おまかせ」と例を明示する。
主人公の内面情報は保存しない。

## 11. resume時の読み方

resume時は `prompt/save_resume.md` を正本とする。
起動直後に全ファイルを総読みしない。

必ず入口として確認するもの:

- `current/hotset.md`
- `current/scene.md`
- `current/event_card.md`
- `current/decision_index.md`
- `current/story_spine.md`（存在する場合のみ）
- `current/protagonist.md`（存在する場合のみ。呼称・身体距離・Session Constraints が関係する時だけ）
- `current/knowledge_state.md`（存在する場合のみ。使おうとしている情報の fictional_status / known_to が関係する時だけ）

必要箇所を確認するもの:

- `current/relationship_overview.md`
- `lilia/main/profile.md`
- `lilia/main/core.md`
- `lilia/main/voice.md`
- `lilia/main/state.md`
- `lilia/main/relationship.md`
- `lilia/main/memory.md`
- `lilia/main/beliefs.md`
- `story/relationship_spine.md`
- `story/story_deck.md`

`hotset` は正解手順書ではない。
正本側と矛盾する場合は、`state`、`relationship`、`memory`、`beliefs`、`scene`、`event_card` を確認する。
初回scene前、または声や人格の基準が足りない場合は、hotsetではなく `profile.md` の必要箇所へ戻る。

`style/reference.md` と `style/rules.md` は通常resume 1ターン目の標準読込には入れない。
root `style/defaults/*.md` も標準読込には入れない。
文体崩れ、scene tone調整、重要な恋愛/衝突場面、静かな関係変化、出力文章相談がある時だけ、`prompt/style_reference.md` を正本として必要箇所を読む。
読むdefaultsは原則1つ、多くても2つまでにする。

## 12. 採用元

- MIRA: `core / voice / state / relationship / memory / beliefs`
- inner-galge: キャラ中心 / hotset / Markdown運用 / memory model / validation / voice continuity / romance-intimacy / 更新ループ / 感情の骨の抽出手順
- LIRIA: session構造 / event_card / save/resume / archive / Visible Request Gate / Truth Hiding Boundary / Mid-Story Activation Gate / integrity check / romance / growth update / Story Reference Layer
- style reference: LIRIAの story_reference / Light Story Reference Pass / style rules / 作者別・場面別defaults と inner-galgeの抽象化手順

## 13. 採用しなかったもの

- LILIAを単なるヒロイン、攻略対象、固定パートナーとして扱う設計
- 起動時・再開時に全ファイルを総読みする重い運用
- example文を本文生成へ流用する運用
- 参照小説本文や固有文体を保存・流用する運用
- 参照作品の固有名詞、台詞、キャラ、展開順の模倣
- `story/story_deck.md` に文体参照まで詰め込む運用
- `story/story_deck.md` と `current/event_card.md` を同じ内容にする運用
- NPC全員を最初からヒロイン級に作り込む運用
- full plotを事前生成する運用
- 固定台詞集でLILIAの声を管理する運用
- hotsetを正本として扱う運用
- 毎ターン全ファイル更新
- 巨大ログ保存
- 旧AFFINITY数値、好感度、攻略ルートで親密さを管理する運用
- 空ディレクトリ維持だけの `.gitkeep` 運用
- 初回から大規模なlauncher / CLIを書くこと
- 中身の薄い巨大テンプレートを大量に増やすこと
