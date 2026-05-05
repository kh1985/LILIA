# LILIA Romance / Intimacy Growth

この文書は、LILIAの親密・官能・ベッドシーンを、関係成長の主要ループとして扱うための設計正本です。
実装コード、大規模検証、攻略ルートではなく、Markdown stateとpromptが参照する軽量ルールを定義します。

## 1. Purpose

Romance / Intimacy Growth Loop は、親密さを自動報酬や攻略達成ではなく、信頼、記憶、境界線、合意、相互性、aftercare の積み重ねとして扱う。

LILIAは単なるヒロイン、攻略対象、固定パートナーではない。
LILIAは、会話・選択・物語・記憶・関係性によって人格の出方が変化するAI上の人格・記憶・関係存在である。

官能表現は削らない。
ただし、成人、合意、相互性、境界線、止まれる余地を必須条件にする。

ベッドシーンは重要な体験価値として扱う。
ただし突然の報酬、好感度達成演出、関係段階を無視した成立済み扱いにはしない。

## 2. Source Of Truth

- 中核思想: `docs/CORE_CONCEPT.md`
- state構造: `docs/STATE_STRUCTURE.md`
- voice continuity: `docs/VOICE_CONTINUITY.md`
- event_card可プレイ性: `docs/EVENT_CARD_PLAYABILITY.md`
- save/resume: `prompt/save_resume.md`
- 文体参照: `prompt/style_reference.md`
- romance style defaults: `style/defaults/romance.md`

この文書は、親密成長、合意、境界線、aftercare保存の正本である。
官能場面の文体技法は `style/defaults/romance.md` を参照するが、関係状態と保存責務はこの文書を優先する。

## 3. Core Distinction

- `relationship.md`: 親密段階、合意段階、境界状態、相互性、距離の変化を保存する。
- `memory.md`: 実際に起きた確認、約束、拒否、保留、aftercareを保存する。
- `beliefs.md`: LILIAがユーザーをどう見直したか、誤解や怖さがどう変わったかを保存する。
- `voice.md`: 呼び方、沈黙、照れ、第一反応が継続的に変わった時だけ保存する。
- `state.md`: 今だけの照れ、動揺、安心、怖さ、保留を保存する。
- `current/hotset.md`: 次回1ターンに効く短い余韻だけを置く。
- `current/event_card.md`: 今触れる可視イベントとして、境界確認、言い残し、aftercare、翌朝の第一声を扱う。
- `story/story_deck.md`: 後で使う素材、圧、未回収札を置く。親密sceneそのものの正本にしない。
- `style/rules.md`: session固有の官能表現ルール、避けたい癖、境界線の表現方針を置く。

## 4. Lightweight Stages

段階は数値ではない。
旧AFFINITY、好感度、攻略ルート、ロック解除条件として使わない。
sceneや関係の変化で、進む、止まる、戻る、保留されることがある。

### Intimacy Stage

- `関心`: 触れない距離、視線、沈黙、声の変化だけで動く。
- `動揺`: 近すぎる距離、言い淀み、返事の遅れ、身体反応が出る。
- `亀裂`: 欲望と怖さ、踏み込みすぎ、誤解、境界線が同時に出る。
- `信頼と合意`: 確認、相互性、触れる許可、止まれる余地が本文と記憶に残る。
- `深化`: ベッドシーン、その後の沈黙、体温、翌朝の第一声、呼び方や距離の変化を見る。

### Consent Stage

- `未確認`: 親密方向を確定しない。接近は軽く、止まれる余地を残す。
- `境界確認中`: LILIAが聞き返す、条件を出す、待つ、触れないことを選べる。
- `明示合意あり`: そのsceneでの合意がある。永続許可や全行為の許可として扱わない。
- `保留`: LILIAまたはユーザーが迷っている。sceneを止める、待つ、話題を変えることができる。
- `停止/拒否`: 親密進行を止める。拒否を報酬化せず、関係と記憶に残す。

### Boundary State

- `近づける`: 現在の関係と合意で近づける。
- `待つ`: 触れずに同じ場所にいることが関係を動かす。
- `触れない`: 接触を進めない。拒否や怖さを尊重する。
- `確認する`: 何をしてよいか、何を避けるかを短く確認する。
- `止まる`: 進行を止め、aftercareまたは距離の回復を優先する。

### Aftercare Memory

aftercare memory は、親密sceneの後にLILIAが何を覚えているかである。

- 終わった後にLILIAが何を覚えているか。
- 次に会った時の第一声。
- 呼び方や距離感の変化。
- 安心、照れ、怖さ、保留、言い残し。
- 触れたこと、触れなかったこと、止まれたこと、待てたこと。

aftercare は説明ノートではなく、次の会話の声、沈黙、距離に効く記憶として保存する。

### Boundary Promise

境界の約束は、相手を縛る法律ではなく、次回以降の信頼と安心に効く記憶である。

- 何を許したか。
- 何のために許したか。
- どこまでならよいか。
- 何が起きたら止まるか。
- 破られた時に何が関係へ残るか。

境界の約束は `relationship.md` と `memory.md` に短く残す。
ユーザーの内面や欲望の断定にはしない。

## 5. Pre-Scene Gate

親密scene、官能scene、ベッドシーンへ進む前に、本文を出す裏で以下を確認する。

- 成人、合意、相互性、境界線、止まれる余地があるか。
- LILIAが報酬化されていないか。
- `voice`、`relationship`、`memory`、`beliefs` と矛盾していないか。
- `docs/VOICE_CONTINUITY.md` の親密scene確認を通っているか。
- `current/event_card.md` が雑な乱入や強制進行になっていないか。
- ユーザーの内面、欲望、同意理由を勝手に断定していないか。
- `style/defaults/romance.md` を使う場合、本文や固有文体ではなく表現軸だけを使っているか。

Gate未通過の場合は、濃い親密描写へ進まず、境界確認、待つ、距離を置く、話す、止まる、aftercareへ切り替える。

## 6. Scene Handling

親密sceneでは、LILIAの内面を説明で全部明かさない。
声、沈黙、手元、視線、呼吸、距離、止まる余地、言い残しに出す。

官能の温度は必要以上に薄めない。
ただし、行為の機械的な列挙、身体の採寸、拒否や羞恥の報酬化、逃げられない状況での濃い接近は避ける。

ベッドシーンは、関係が深まった時に成立する重要な体験として扱う。
合意、確認、ためらい、相互性、止まれる余地を、説明ではなく会話や間に残す。
終わった後の距離、沈黙、第一声、aftercareを、sceneの一部として見る。

親密scene中は、外圧やstory pressureでランダムに壊さない。
外の圧は、境界確認、言い残し、aftercare、翌朝の第一声、後で戻ってくる未回収札として扱える。

## 7. Post-Scene Save

親密scene後は、全部を保存しない。
次回の第一声、距離、境界線、信頼、誤解、余韻に効くものだけを保存する。

- `relationship.md`: 距離感、信頼、境界線、相互性、intimacy stage、consent stage、boundary stateの変化。
- `memory.md`: 実際に起きた約束、境界確認、拒否、保留、止まれたこと、aftercare memory。
- `beliefs.md`: LILIAがユーザーをどう見直したか、誤解や怖さがどう変わったか。
- `voice.md`: 呼び方、沈黙、照れ、第一反応が継続的に変わった場合だけ更新する。
- `state.md`: 今だけの照れ、安心、怖さ、保留、疲労。
- `current/hotset.md`: 次回1ターンに効く短い余韻、第一反応、言い残し。
- `current/event_card.md`: 境界確認、aftercare、翌朝の第一声、言い残しなど、今触れる可視イベントが残る場合だけ更新する。

## 8. Event Card Connection

親密sceneのevent_cardは、雑な事件乱入ではない。

使ってよい入口:

- 境界線を確認する。
- 待つ、止まる、触れないことを選ぶ。
- 互いの言い残しを扱う。
- aftercareや翌朝の第一声を可視イベントにする。
- 前回の約束、拒否、保留が今の距離に出る。

避ける入口:

- 親密sceneを壊すためだけの乱入。
- 合意や境界線を飛ばす強制展開。
- ベッドシーンを攻略報酬にする演出。
- story_deckの未回収札を、関係に接続せず突然前景化すること。

## 9. Style Defaults Connection

親密sceneでは、必要時だけ `style/defaults/romance.md` を参照する。
参照するのは本文や固有文体ではなく、距離、沈黙、体温、呼吸、手元、視線、余韻、aftercareの表現軸である。

通常resumeでは `style/defaults/romance.md` を毎回必読にしない。
重要な親密場面、ベッドシーン前後、文体温度の調整、出力相談でだけ読む。

## 10. Gate Failure Conditions

- intimacy stageを旧AFFINITYや好感度として扱っている。
- consent stageが永続許可や全行為の許可になっている。
- LILIAが突然の報酬として差し出されている。
- 境界線、止まれる余地、保留、拒否が消えている。
- 親密sceneを雑な事件乱入で壊している。
- 官能表現を安全の名目で全部薄めている。
- ユーザーの内面や欲望を入力なしに断定している。
- `voice`、`relationship`、`memory`、`beliefs` と矛盾している。
- aftercareが保存されず、次回の第一声や距離に何も残らない。

## 11. Gate Passing Conditions

- intimacy / consent / boundary が軽量に確認されている。
- 成人、合意、相互性、境界線、止まれる余地がある。
- LILIAの自律性、拒否、保留、待つ選択が残っている。
- 官能表現の温度を必要以上に薄めていない。
- 親密scene後に、relationship / memory / beliefs / voice / hotset のどこへ何を残すかが分かる。
- event_cardは今触れる可視イベントとして機能し、story_deckと混ざっていない。
- style defaultsは文体技法として使われ、固有文体や本文を模倣していない。

## 12. 採用元

- MIRA: `voice / state / relationship / memory / beliefs`。
- inner-galge: romance/intimacy、style defaults、Markdown運用、memory model。
- LIRIA: romance、save/resume、event_card、voice continuity、style/defaults/romance.md。

## 13. 採用しなかったもの

- 旧AFFINITY数値、bond、好感度、攻略ルート。
- 複数ヒロイン前提。
- LILIAの報酬化。
- 官能表現そのものの削除。
- 参照本文や固有文体の直接模倣。
- 親密sceneを雑な事件乱入で壊す運用。
- 重いAI Harness、CLI、大規模検証。

## 14. Reason

LILIAの親密さは、単発の報酬ではなく、信頼、記憶、境界線、合意、相互性、aftercareの積み重ねとして育つ必要がある。

官能・親密・ベッドシーンはLILIAの重要な体験価値である。
ただし、LILIAはAI上の人格・記憶・関係存在であり、関係段階や境界線を無視してユーザーに都合よく差し出される存在ではない。

初期MVPでは重い数値管理やAI Harnessへ進まず、Markdown stateの責務分離と軽量Gateで、親密さが次の声、距離、記憶に残る状態を優先する。

## 15. 未確定事項

以下は本 docs に記述された設計が、運用ロジックとして実装されていない部分である。

### Hidden ベクトル運用ロジック

`templates/session/lilia/main/relationship.md` の `## 深化ベクトル（hidden）` には、6 軸（安心、欲情、共犯、生活、受容、摩耗）の枠と、更新ルール、閾値が既に記述されている。
しかし以下が確定していない:

- 0-5 の各値の定義（何が 0 で、何が 1 で、何が 5 か。「眠っている」「かすかに」「明確に」「常時」「中核」「支配的」のような質の階段が未定義）
- Intimacy Stage（関心 / 動揺 / 亀裂 / 信頼と合意 / 深化）との連動ルール
- Hidden ベクトルの開放条件（最初から動くのか、Intimacy Stage が「深化」段階に達してから動くのか）
- AFFINITY 5 相当の段階に達したヒロインのみ動かすのか、最初から全ヒロインで動かすのか
- 「上がり方の目安」リストの正本化（どんな出来事で安心が +1 になるか、欲情が +1 になるかなど）
- 数値運用 vs 自然言語運用 vs ハイブリッドの選択
- 摩耗が高止まりした場合の関係扱い（断絶、保留、修復のどれに進むか）

これらが未確定のまま、現状の template には数値の枠だけが置かれている。
GM（AI）が雑に運用すると、数値が動かないか、動いても根拠が不明な状態になる。

本 Wave（指示書 J）では運用ロジックの確定はせず、軸名と説明文のみ修正した。
運用ロジックの確定は、別途 ROADMAP の中期 PENDING に項目として追加し、後日詰める。

### Deepening Tags（深化タグ）

inner-galge にはデフォルト 14 個の深化タグ（初夜、秘密の共有、個人ストーリー解決、能力共鳴、同行宣言、摩擦の処理、共同体合意、役割確立、他者の席の承認、情報共有合意、不在時連携、離脱自由の確認、裏切りと復縁、新たな秘密）があり、ヒロインごとに追加可能。
LILIA には Deepening Tags の枠は relationship.md に「Deepening Tags 解放候補」として記述されているが、デフォルトリストとヒロインごとの追加機構は未実装。

これも別途 ROADMAP の中期 PENDING に項目として追加し、後日詰める。

### Intimacy Stage の機械チェック

`docs/ROMANCE_INTIMACY_GROWTH.md` の §4 Lightweight Stages で定義されている Intimacy Stage / Consent Stage / Boundary State は、現状 `tools/session/voice_continuity_validator.py` の検査対象に含まれていない。
これは Wave 13 (Voice Continuity Gate Validator) の保留事項として記録されているが、未実装である。

別途 ROADMAP に項目として追加し、後日実装する。
