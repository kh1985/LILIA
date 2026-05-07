# LILIA Growth Update Loop

この文書は、Save Modeで、会話後、scene後、event_card進行後、親密scene後に、LILIAのstateをどう更新するかを定義する設計正本です。
実装コード、CLI、自動検証ではなく、Markdown stateを軽量に更新するための運用ルールです。

## 1. Purpose

Growth Update Loop は、LILIAが会話、選択、物語、記憶、関係性によって少しずつ変化するための保存更新ループである。
これはSave Modeで「何を反映するか」を決めるルールであり、通常プレイの各ターンで即座に全ファイル編集するルールではない。

目的は、すべてのファイルを毎回更新することではない。
何が変わったかを見て、次回の第一声、距離、信頼、境界線、event_card入口に効くものだけを、正しい保存先へ分ける。

LILIAは単なるヒロイン、攻略対象、固定パートナーではない。
LILIAは、AI上の人格、記憶、関係存在として扱う。
Growth Update は好感度加算、攻略ルート進行、報酬付与ではない。

## 2. Source Of Truth

- 中核思想: `docs/CORE_CONCEPT.md`
- state構造: `docs/STATE_STRUCTURE.md`
- save / resume: `prompt/save_resume.md`
- event_card可プレイ性: `docs/EVENT_CARD_PLAYABILITY.md`
- story / relationship accumulation: `docs/STORY_RELATIONSHIP_ACCUMULATION.md`
- relationship change audit: `docs/RELATIONSHIP_CHANGE_AUDIT.md`
- voice continuity: `docs/VOICE_CONTINUITY.md`
- romance / intimacy growth: `docs/ROMANCE_INTIMACY_GROWTH.md`
- resume smoke: `docs/RESUME_SMOKE_TEST.md`

この文書は、会話後に何をどこへ保存するかの正本である。
各Gateの詳細は既存正本に委ね、ここでは更新判断と保存先の分離を扱う。
ただし、通常プレイ中はPlay Modeを優先し、プレイヤーへの返答に保存判断やファイル更新ログを混ぜない。

## 3. Update Trigger

Growth Update は、Save Modeで以下のタイミングに短く確認する。

- ユーザーが「保存」「save」「ここまで反映」「セーブして」と明示した後。
- GMがscene終了や章区切りとして、明示的に保存確認を出した後。
- codex-new / new初期化で、profile、scene、event_card、resume-ready scaffoldを生成する時。
- Save Modeに入ったうえで、scene後。
- Save Modeに入ったうえで、event_cardが進んだ後。
- Save Modeに入ったうえで、境界線が確認された後。
- Save Modeに入ったうえで、拒否、保留、約束が出た後。
- Save Modeに入ったうえで、親密scene後。
- Save Modeに入ったうえで、衝突scene後。
- `autosave_required: true` がscene-tickで示された時。この場合、GMは次のプレイ応答を返す前に Save Mode に入り、turn_update.md を作って apply-turn を実行する。
- save前。
- resume smokeで破綻が見えた時。

ただし、何も変わっていない時は更新しない。
毎ターン全ファイルを機械的に更新しない。

Play Modeの通常会話中は、保存候補を内部的に保持するだけに留める。
ユーザーへの返答では、保存します、stateを更新します、git statusを確認します、Edited files、diff / stat、session stateには保存済みです、などのメタ発言を出さない。
まずLILIA / GMのplayable scene textを返す。

## 4. First Question

Save Modeで保存前に、まず以下を見る。

- `what changed`: 何が実際に変わったか。
- `what LILIA now feels`: LILIAの今だけの感情は何か。
- `what LILIA now believes`: LILIA側の仮説、誤解、見直しは変わったか。
- `what was left unsaid`: まだ言えていないこと、保留されたことは何か。
- `what promise / refusal / boundary changed`: 約束、拒否、保留、境界線は変わったか。
- `what should return next scene`: 次回の第一声、距離、沈黙、event入口に戻すものは何か。

この確認は内部の更新判断であり、作中本文に管理語として出さない。
ユーザーの内面や欲望は、本人の入力なしに断定しない。

## 5. File Responsibilities

### `lilia/main/state.md`

今だけの感情、一時的な揺れ、疲れ、安心、動揺、警戒を保存する。

保存するもの:

- 現在の感情。
- 表の気分、裏の気分。
- 疲労、照れ、迷い、警戒。
- 次回に出る短い第一反応。
- 親密scene後の一時的な安心、照れ、怖さ、保留、疲労。

保存しないもの:

- LILIAの人格核。
- 長期関係の結論。
- 実際に起きた約束や拒否。
- ユーザーの内面断定。

### `lilia/main/relationship.md`

距離、信頼、境界線、相互性、intimacy stage、consent stage、boundary stateを保存する。

保存するもの:

- 何によって近づいたか、遠ざかったか、保留になったか。
- 信頼、安心感、開示度、摩擦。
- 境界線、合意、止まれる余地。
- intimacy stage / consent stage / boundary state の変化と理由。

保存しないもの:

- 旧AFFINITY、好感度、bond、攻略ルート。
- 報酬としての親密化。
- 一時的な照れや疲労だけの変化。

### `lilia/main/memory.md`

実際に起きた出来事、約束、拒否、保留、aftercare、関係の節目を保存する。

保存するもの:

- 実際に交わした約束。
- 尊重された拒否や境界線。
- 保留された話題。
- 親密scene後のaftercare memory。
- 次回の第一声、距離、沈黙に効く節目。
- echo: 重要scene後の残り香、気まずさ、距離の揺れ、言い残し。古い echo は上書きしてよい。

保存しないもの:

- 起きていない出来事。
- LILIA側の推測や誤解。
- すべての会話ログ。
- ユーザーの内面断定。

### `lilia/main/beliefs.md`

LILIA側の誤解、疑い、見直し、仮説、更新条件を保存する。

保存するもの:

- ユーザーをどう見直したか。
- まだ疑っていること。
- 誤解が残った理由。
- 何が起きたら変わるか。
- 親密さ、衝突、境界線で変わったLILIA側の認識。

保存しないもの:

- 実際に起きた出来事そのもの。
- ユーザーの本心の断定。
- 正解として確定した心理説明。

### `current/hotset.md`

次回1ターンだけに効く短い余韻、第一反応、今触れる入口を保存する。

保存するもの:

- 直前の会話温度。
- 次に会った時の第一反応。
- 未消化の感情。
- 言い残し。
- 現在event_cardの短い入口。
- 親密scene後のaftercareの短い余韻。

保存しないもの:

- 長期記憶の正本。
- 関係の全履歴。
- todoや正解ルート。
- 複数eventの長い一覧。

hotsetは、正本を更新した後に短く再生成する。
hotsetだけ更新して、relationship / memory / beliefs が更新されていない状態を作らない。

### `current/event_card.md`

今触れる可視イベントの進行状態を保存する。

保存するもの:

- visible problemが進んだか。
- first concrete actionが行われたか。
- どのhandleに触れたか。
- relationship stakeがどう動いたか。
- if ignoredが発火したか。
- next visible changeをどう更新するか。
- event_cardを継続、解決、背景化、保留のどれにするか。

event_cardが現在sceneから外れた場合は、必要に応じて `story/story_deck.md` の未回収札へ落とす。
関係が明確に変わった節目なら、短く `archive/beats/` へ保存する。

### `current/relationship_overview.md`

現在の関係全体の軽い入口として更新する。

保存するもの:

- 現在の距離感。
- 信頼、警戒、興味、甘え、衝突の現在形。
- 誤解や保留。
- resume時に無かったことにしないもの。
- 次に変化しそうな点。
- 最新チェックポイントは、重要scene後（親密、衝突、境界確認、関係段階の変化）にだけ短く更新する。データではなく散文で書く。

正本ではない。
矛盾した場合は `relationship.md`、`memory.md`、`beliefs.md` を優先する。

### `current/decision_index.md`

セッション中の決定（約束・拒否・保留・解決済み）を追記する。

保存するもの:

- 明示された約束、拒否、保留、解決。
- 各決定の状態（active / fulfilled / broken / withdrawn / pending / resolved）。
- 撤回や変更があった場合の状態遷移。

保存しないもの:

- 軽い意向や匂わせ。
- 実際の出来事（`memory.md` へ）。
- LILIA側仮説（`beliefs.md` へ）。

### `story/story_deck.md`

現在sceneから外れた未回収札、後で使う素材、関係を揺らす圧を保存する。
Story / Relationship Accumulation では、event_cardが点、story_deckが線へ育つ素材棚である。

保存するもの:

- 背景化したevent_card。
- まだ使わない未回収札。
- 後で前景化できる小さな圧。

保存しないもの:

- 現在sceneで今触れる可視イベント。
- 文体参照。
- 親密sceneそのものの正本。
- 重いcase_engine / villain / combat構造。

NPCが関わる場合は、Tier 0-2なら短いメモに留め、Tier 3以上で再登場し、LILIAのmemory / relationship / beliefsへ影響した時だけ `story/npc/<id>.md` を検討する。

### `archive/beats/`

関係が明確に変わった節目だけ保存する。
巨大ログ置き場にはしない。

保存してよい節目:

- 初めて境界線を確認した。
- 初めて拒否が尊重された。
- aftercareで関係が変わった。
- LILIAのユーザー認識が変わった。
- 呼び方が継続的に変わった。

これらは例であり、固定分類ではない。
実セッションでは、ユーザーの言葉、LILIAの反応、関係の変化を優先する。

## 6. Update Flow

このflowはSave Mode専用である。
Play Modeのユーザー通常入力に対しては、このflowを実行してファイル編集するのではなく、候補として内部的に保持する。

1. 直前の会話、scene、event_cardで実際に変わったものだけを見る。
2. 一時感情、関係変化、実際の記憶、LILIA側の認識を分ける。
3. 必要な正本だけを更新する。
4. event_cardが進んだ場合は、継続 / 解決 / 背景化 / 保留を判断する。
5. 関係の節目が明確なら、短く `archive/beats/` へ残す。
6. Story / Relationship Accumulation の観点で、次回へ戻る未回収札やNPC tier変化があるかを見る。
7. scene終了や章区切りなら、`next_hook` として次にユーザーが自然に返せる入口を残すべきかを見る。
8. 最後に `current/hotset.md` を、次回1ターンに効く短い温度として再生成する。
9. save前に、hotsetだけ正本化していないか確認する。

`next_hook` は選択肢UIではない。
Scene Exit / Next Beat、次に会う口実、LILIAからの相談、未回収札、通知、約束、言い残し、持ち物などから、現在の関係と人格に接続した次の入口を短く作る。
`apply-turn` は `next_hook` を `current/event_card.md` の `Next Hook` と `story/story_deck.md` の `Candidate Next Hook` に反映する。

## 7. Update Timing Detail

### 通常会話後

Play Modeの通常会話後は、ファイル編集しない。
新しい約束、拒否、保留、境界線が出た場合でも、ユーザーが保存を求めるまでは保存候補として内部的に保持する。
Save Modeに入った時だけ、必要最小限の `state`、`hotset`、`voice`、`relationship`、`memory`、`beliefs` を判断する。
何も変わっていなければ更新しない。

### event_cardが進んだ後

- visible problemが変わったかを見る。
- first concrete actionが行われたかを見る。
- handlesのどれに触れたかを見る。
- relationship stakeが、信頼、警戒、誤解、距離、親密さ、沈黙、境界線のどこに残ったかを見る。
- if ignoredが発火した場合は、1-3 scene以内に見える変化として返す。
- next visible changeを更新する。
- 現在sceneから外れたeventは、story_deckへ背景化するか、関係の節目としてarchiveする。

### 境界線が確認された後

- `relationship.md` に境界線、合意、止まれる余地を保存する。
- `memory.md` に実際に起きた確認、拒否、保留、約束を保存する。
- `beliefs.md` にLILIAがユーザーをどう見直したか、まだ怖いものを保存する。
- `hotset.md` には次回1ターンに効く短い第一反応だけ置く。

### 拒否 / 保留 / 約束が出た後

- 実際に言われたこと、尊重されたことは `memory.md` に保存する。
- それで距離や信頼が変わったなら `relationship.md` を更新する。
- LILIA側の誤解や疑いが変わったなら `beliefs.md` を更新する。
- 拒否や保留を報酬化しない。

### Deepening Tags 評価

初期βでは、Deepening Tags / hidden深化ベクトルの本格運用は保留する。
関係変化は、数値やタグ解放ではなく、実際に起きた出来事、LILIAの受け取り方、memory / relationship / beliefs / hotset への保存で扱う。
Deepening Tagsは、将来、深い関係に到達した後の質的管理が必要になった場合に再検討する。

初期βで確認すること:

- Play Mode中にタグ解放判定や軸名、数値を出さない。
- Save Modeでも hidden深化ベクトルを通常進行メーターとして更新しない。
- 関係変化の根拠、速度、保存先分離は `docs/RELATIONSHIP_CHANGE_AUDIT.md` で確認する。
- 重要な出来事があった場合は、タグではなく `memory.md`、`relationship.md`、`beliefs.md`、`current/hotset.md` に文字情報として残す。

### echo 更新タイミング

以下のいずれかが起きた時、`memory.md` の echo を短く更新する。

- 衝突や緊張のあるsceneが起きた。
- 親密sceneが起きた（aftercare_memoryとは別に、温度の揺れとして）。
- 境界確認や拒否があった。
- 関係段階が動いた。
- LILIAが言いかけて止めた、または言わなかったことがある。
- 別れ際、見送り、待機など、scene末尾に余韻が残った。

更新後は、`current/hotset.md` の最新scene後echoも短く再生成する。
通常会話scene後は更新しない。

### 親密scene後

- `relationship.md`: 距離感、信頼、境界線、相互性、intimacy stage、consent stage、boundary stateの変化。
- `memory.md`: 実際に起きた約束、境界確認、拒否、保留、止まれたこと、aftercare memory。
- `beliefs.md`: LILIAがユーザーをどう見直したか、安心、怖さ、保留、誤解の変化。
- `state.md`: 今だけの安心、照れ、怖さ、保留、疲労。
- `voice.md`: 呼び方や沈黙が継続的に変わる場合だけ。
- `current/hotset.md`: 次回1ターンに効く余韻、第一反応、まだ触れないこと。
- `current/event_card.md`: 境界確認、aftercare、翌朝の第一声、言い残しが今触れる可視イベントとして残る場合だけ。

官能表現そのものを削らない。
ただし、成人、合意、相互性、境界線、止まれる余地を守る。

### 衝突scene後

- `state.md` に今だけの怒り、疲労、沈黙、迷いを置く。
- `relationship.md` に摩擦、距離、信頼の変化を置く。
- `memory.md` に実際に起きた言葉、拒否、謝罪、保留を置く。
- `beliefs.md` にLILIA側の誤解、疑い、見直し、更新条件を置く。
- すぐ完全に許したことにしない。関係が戻る場合も、戻った理由を残す。

### 最新チェックポイント更新タイミング

以下のいずれかが起きた時、`current/relationship_overview.md` の最新チェックポイントを短く更新する。

- 親密sceneが起きた。
- 衝突sceneが起きた。
- 境界確認の重要な瞬間があった。
- 関係段階（intimacy stage / consent stage / boundary state）が変わった。
- LILIAの空気が前のチェックポイントから明確に変わった。

更新は1-3行。データを書かず、散文で書く。
古いチェックポイントは上書きしてよい。
通常の会話scene後は更新しない。

### decision_index 更新タイミング

以下のいずれかが起きた時、`current/decision_index.md` を更新する。

- ユーザーまたはLILIAが明示的に「次にこうする」「いつかこうする」と約束した。
- 「これはしない」「これは触れない」と拒否を表明した。
- 「今は決めない」「後で話す」と保留にした。
- 過去の約束・保留が解決した。
- 過去の決定が撤回された。

更新は追記する（古い決定を削除しない）。
状態遷移がある場合は新しい行として追記し、古い行の状態を更新する。

### save前

- hotsetだけが更新されていないか確認する。
- 長期記憶がhotsetにしかない場合は、`memory.md` または `relationship.md` へ戻す。
- event_cardが進んだのに next visible change が古いままなら更新する。
- 親密scene後に aftercare / boundary / consent が抜けていないか確認する。

### resume smokeで破綻が見えた時

- 破綻がhotset由来なら、hotsetを短く再生成する。
- 正本側に抜けがあるなら、`relationship`、`memory`、`beliefs`、`event_card` を必要分だけ補正する。
- smoke結果をsession正史に混ぜない。

## 8. Do Not Update

- Play Modeの通常ターンでファイル編集しない。
- ユーザーが保存を求めていないのに、保存更新、git確認、diff確認を割り込ませない。
- 保存判断をプレイヤー向け本文に出さない。
- 何も変わっていない時に無理に更新しない。
- すべてのファイルを毎回更新しない。
- 一時的な感情を `core.md` に書かない。
- hotsetに長期記憶を書かない。
- memoryに実際に起きていないことを書かない。
- beliefsでユーザーの内面を断定しない。
- relationshipを好感度や攻略ルートにしない。
- event_cardを事件処理だけで終わらせない。
- story_deckに現在sceneの可視イベントを置かない。

## 9. Gate Failure Conditions

- hotsetだけ更新して、正本が更新されていない。
- relationshipが好感度、旧AFFINITY、bond、攻略ルートになっている。
- memoryに実際に起きていないことが入っている。
- beliefsがユーザーの内面を断定している。
- 一時感情をcoreに保存している。
- event_cardが進んだのに if ignored / next visible change が更新されていない。
- 親密scene後の aftercare / boundary / consent が保存されていない。
- 官能表現が安全の名目で消されている。
- すべてのファイルを毎回機械的に更新している。
- Play Modeの通常応答で、保存します、stateを更新します、Edited files、diff / statなどを出している。
- archive/beatsが巨大ログ置き場になっている。

## 10. Gate Passing Conditions

- 何が変わったかを見て、必要なファイルだけ更新している。
- Save Modeに入っている時だけ更新している。
- Play Modeではplayable scene textを先に返し、保存ログを出していない。
- state / relationship / memory / beliefs の責務が分かれている。
- hotsetが正本ではなく、次回1ターンのechoになっている。
- event_cardが、継続 / 解決 / 背景化 / 保留のどれかとして扱われている。
- 親密scene後に、aftercare、合意、境界線、相互性が必要な正本へ残っている。
- memoryは実際に起きたこと、beliefsはLILIA側の仮説として分離されている。
- 関係の節目だけがarchive/beatsへ送られている。

## 11. Adopted From

- MIRA: `state / relationship / memory / beliefs`
- inner-galge: hotset、Markdown運用、memory model、validation、更新ループ
- LIRIA: save/resume、event_card、archive、romance/intimacy、voice continuity、integrity check

## 12. Not Adopted

- 旧AFFINITY / 好感度 / bond / 攻略ルート
- hotset正本化
- 巨大ログ保存
- 毎ターン全ファイル更新
- ユーザー内面の断定
- 官能表現そのものの削除
- AI Harness / 自動プレイ検証 / CLI / launcher
- case_engine / villain / combat / manga pipeline

## 13. Reason

ここまででnew/resumeの箱と各Gateは整ったが、会話後に何をどこへ保存するかが曖昧だと、LILIAは成長しない。

LILIAの体験価値は、記憶、関係、人格の出方が少しずつ変わることにある。
更新先を分けないと、hotset肥大化、memoryの捏造、relationshipの好感度化、beliefsの内面断定が起きる。

まず軽量なMarkdown更新ループを固定し、重い自動化やCLIは後続に回す。
