# LILIA Story Function Framework

この文書は、LILIAのhook、scene、event_card、apply-turn、AI Playtestで使う物語機能の診断フレームである。
この文書は仕様説明であり、code、template、WBS status、実装順の変更を含まない。

Story Functionは固定プロット順ではない。
「今このhook / scene / event_cardが、物語上どんな役割をしているか」を見るための内部タグである。
Play Mode本文に「今は試練です」「このsceneの機能は糸口です」のような管理語を出さない。
Three Hook Spineも選択肢UIではない。
Main / Relationship / Life-Exploration hookは、脱線後にplayを戻すための内部return pathであり、Play Modeでは1本のplayable entranceだけを前景化する。

## 1. Core Idea

物語は事件の羅列ではなく、変化を読ませるものとして扱う。
プレイヤーが追うのは情報ではなく問いである。

LILIAでsceneが進んだと言えるのは、入口と出口で以下のどれかが変わった時である。

- 状況
- 関係
- 情報
- 感情
- 役割
- 目的
- 場所の意味
- 約束、拒否、保留、境界線
- LILIAのmemory / relationship / beliefs
- 次に触れるActive Hook

単に場所だけが変わっても、緊張の種類が同じなら進行不足である。
路地、コンビニ、コインランドリー、公園、バス停へ移動しても、同じ足音、同じ通知、同じ気配だけで引っ張るならclosure不足として扱う。

## 2. Adopted / Not Adopted

採用するもの:

- MIRA: `core / voice / state / relationship / memory / beliefs` の人格構造。
- inner-galge: キャラ中心の会話体験、hotsetによる再開時の温度維持、Markdown運用。
- LIRIA: session構造、event_card、保存再開、archive、next_hook promotionの考え方。

採用しないもの:

- 固定プロット順として十五機能をなぞる運用。
- 毎ターン3つの選択肢を出すUI。
- Relationshipを好感度、攻略ルート、bondとして扱う運用。
- heavy case engine / villain engine / organization engine。
- Play Mode本文に内部タグ、Judge語、保存判断を出す運用。

## 3. Fifteen Story Functions

十五機能は、現在地を診断するためのタグである。
順番を強制せず、必要な時に現在のhook / scene / event_cardへ1つまたは少数だけ付ける。
event_card / Three Hook / AI Judge / apply-turn の内部判断に使い、Play Mode本文には機能名を出さない。
sceneの出口で何も変わっていなければ、そのsceneは弱い。
特に前進、転回、着地、余韻はArc Closureと強く接続する。

各Functionは以下の形式で読む。
これは固定プロット順ではなく、scene / hook / event_cardの役割を誤解しないための辞書である。

### 主役

- 原文の問い: 読者は誰を追えばよいのか。
- LILIAでの意味: 今このsceneで誰の変化を追うのか。主人公か、LILIAか、NPCか、関係そのものかを見る。
- event_card / hookでの使い方: Active HookのRelationship StakeやScene Functionで、誰の変化を前景化するかを決める。毎回プレイヤーだけを主役にしない。
- exit condition の例: LILIAの境界線が言葉になった。NPCが一歩だけ動けた。主人公とLILIAの距離の意味が変わった。
- 失敗パターン: 誰の変化を見るsceneか不明なまま、事件や情報だけが進む。LILIAを事件処理の駒にする。

補足:
LILIAでは、LILIAの境界線、NPCの恐怖、関係の変化そのものがscene上の主役になることもある。

### 前提

- 原文の問い: どんな暮らしやルールの上に物語があるのか。
- LILIAでの意味: このsceneを理解するための生活、場所、関係、ルールは何か。
- event_card / hookでの使い方: `entry_state`、`current/scene.md`、Active HookのVisible Problemに、場所、時間、関係、仕事、生活圏、使える/使えない手段を短く置く。
- exit condition の例: プレイヤーが今どこにいて、誰とどんな距離で、何が使えないかを理解できる。
- 失敗パターン: 長い設定説明になる。場所や関係が曖昧で、何に触れればよいか分からない。

補足:
前提は長い設定説明ではない。
sceneを読むための足場である。

### 起点

- 原文の問い: 何が起きて、いつもの流れが崩れるのか。
- LILIAでの意味: 日常、会話、仕事、移動、関係の流れを崩した出来事は何か。
- event_card / hookでの使い方: Active HookのVisible ProblemやFirst Concrete Actionに、最初に触れる乱れを置く。
- exit condition の例: 何が普段と違うのかが見え、主人公またはLILIAが反応できる。
- 失敗パターン: 起点が抽象的な違和感だけで、誰が何に困っているか分からない。

補足:
大事件でなくてよい。
落とし物、連絡不通、見知らぬ人物、沈黙、断られた提案、予定変更でもよい。

### 目標

- 原文の問い: 主人公は何を求めて進むのか。
- LILIAでの意味: 主人公またはLILIAは、今何を求めて動けるのか。
- event_card / hookでの使い方: `current_question`とFirst Concrete Actionで、外側の目標と内側の願いを分ける。
- exit condition の例: 外側の目標に一歩近づく、または内側の願いが言葉や行動として少し満たされる。
- 失敗パターン: 何を求めて動くsceneか分からず、雰囲気だけが続く。外側の達成だけで関係に何も残らない。

補足:
外側の目標と内側の願いを分ける。

- 外側: 駅まで行く / 写真を確認する / 誰かを安全な場所へ移す。
- 内側: 急かさずに同じ場にいる / 怖さを言葉にする / 境界線を守る。

### 始動

- 原文の問い: 主人公はどんな理由で動き始めるのか。
- LILIAでの意味: 誰が、なぜ一歩動くのか。
- event_card / hookでの使い方: Handles 2-4やFirst Concrete Actionに、最初の小さな能動性を置く。巻き込まれ型でも「自分はこうする」が必要。
- exit condition の例: 主人公、LILIA、NPCの誰かが、逃げる、待つ、見る、残る、帰る、電話する、黙って横に立つなどの一歩を取る。
- 失敗パターン: 外圧だけが動き、誰も選ばず、プレイヤーの返せる入口がない。

補足:
逃げる、待つ、見る、残る、帰る、電話する、黙って横に立つ、なども始動になる。

### 試練

- 原文の問い: 最初にぶつかる大きな困難は何か。
- LILIAでの意味: 何が難しいのか。時間、距離、恐怖、境界線、誤解、仕事、危険、生活事情、LILIAの拒否や保留などを見る。
- event_card / hookでの使い方: Relationship StakeやIf Ignoredに、sceneを難しくしている圧を1つ置く。
- exit condition の例: 困難が一度正面から扱われる。怖さを言う、待つ、触れない、帰る、保留を尊重するなどができる。
- 失敗パターン: 戦闘や大事件だけを試練と誤解する。同じ試練を足し続けてclosureを遅らせる。

補足:
LILIAの境界線を越えずに支える、怖いと言う、待つ、触れない、帰る判断をする、なども試練になる。

### 糸口

- 原文の問い: 何を得て、誰や何に支えられるのか。
- LILIAでの意味: 次へ進むために何を得るのか。情報、物、約束、同行、場所、許可、役目、言葉、観察結果など。
- event_card / hookでの使い方: Next Visible Changeやnext_hook_candidateに、次の行動を可能にする小さな足場を置く。
- exit condition の例: 問題は解決していないが、次にできる行動が1つ増える。
- 失敗パターン: 糸口が万能解決になる。逆に糸口が曖昧で、次に何ができるか分からない。

補足:
糸口は問題を全部解決するものではない。
次の行動を可能にする小さな足場である。

### 前進

- 原文の問い: 何に成功し、どんな変化が見えるのか。
- LILIAでの意味: 何に成功し、何が少し変わったのか。
- event_card / hookでの使い方: `change_delta`、Next Visible Change、hook stateの`advanced`候補として扱う。
- exit condition の例: 安全な場所に着いた。スマホを取り返した。LILIAが主人公へ小さな役目を渡した。主人公が怖いと言えた。NPCが一歩だけ動けた。
- 失敗パターン: 前進後も同じ試練、足音、通知、気配を足し続ける。成果があったのにArc Closure候補として見ない。

補足:
小さな成果でよい。
前進したら、同じ試練を追加し続けず、Arc Closure候補として見る。

### 転回

- 原文の問い: 何がわかり、問題の意味がどう変わるのか。
- LILIAでの意味: 問題の意味がどう変わったのか。
- event_card / hookでの使い方: Active Hookのcurrent_questionやRelationship Stakeを更新する。Main Hookだと思っていたものがRelationship Hookへ寄ることもある。
- exit condition の例: 助ける話が、本人の選択を待つ話へ変わる。事件が、関係の境界線の話へ変わる。
- 失敗パターン: 真相説明だけで終わり、sceneの問いや関係の意味が変わらない。

補足:
敵だと思った相手が単純な敵ではなかった。
助ける話だと思ったら、本人の選択を待つ話だった。
事件だと思ったら、関係の境界線の話だった。
恋愛だと思ったら、仕事や生活の線引きの話だった。

### 孤立

- 原文の問い: 何を失い、自分で選ばざるをえなくなるのか。
- LILIAでの意味: 何が使えなくなり、誰が自分で選ばざるをえなくなるのか。
- event_card / hookでの使い方: blocked / pending / solo Life Hookとして、頼れない手段や同行しない理由を明確にする。
- exit condition の例: LILIAが同行しない条件が分かる。主人公だけが行く理由が明確になる。NPC本人が選ぶしかない状態になる。
- 失敗パターン: 孤立を物理的な一人だけに限定する。非同行を人格や生活の表現ではなく拒絶だけとして扱う。

補足:
頼れた手段が使えない。
LILIAが同行しない。
主人公だけが行く。
NPC本人が選ばなければならない。
言い訳が使えなくなる。
こうした状態も孤立である。

### 奈落

- 原文の問い: 主人公の心が最も追い込まれる状況は何か。
- LILIAでの意味: 誰の心や関係が一番沈むのか。
- event_card / hookでの使い方: Relationship Hookのworsened候補、境界線違反、信頼喪失、帰れなさ、選択ミスとして扱う。
- exit condition の例: 関係が切れそうになる。信頼が失われる。境界線を越えたことが明確になる。帰れない/戻れない状態が出る。
- 失敗パターン: 毎回重い絶望にする。恋愛や生活sceneで必要以上に事件化する。

補足:
LILIAでは、毎回重い絶望にしない。
恋愛や生活sceneでは小さな奈落でよい。

### 打開

- 原文の問い: 突破口になるものは何か。
- LILIAでの意味: これまで積んだ何が突破口になるのか。
- event_card / hookでの使い方: memory、relationship、beliefs、decision_index、過去の約束や観察を使って、無理のない突破口を作る。
- exit condition の例: 前に置いた約束、道具、関係、言葉、観察、待った時間、断った経験が、次の行動を可能にする。
- 失敗パターン: 突然の新設定や未保存の小道具で救う。active stateにない手がかりをresume 1ターン目で生やす。

補足:
突然の新設定で救わない。
前に置いた約束、道具、関係、言葉、観察、待った時間、断った経験から突破口を出す。

### 選択

- 原文の問い: 中心問題に対して、主人公は何を選ぶのか。
- LILIAでの意味: 中心問題に対して、誰が何を選ぶのか。
- event_card / hookでの使い方: Handles 2-4、decision_index、exit_conditionで、主人公、LILIA、NPCの選択を扱う。
- exit condition の例: 帰る/残る、同行する/しない、見る/見ない、話す/保留する、受け取る/返す、近づく/距離を戻す、のどれかが明確になる。
- 失敗パターン: 選択をプレイヤーだけの番号選択肢にする。LILIAやNPCのagencyを消す。

補足:
主人公だけでなく、LILIAやNPCが選ぶこともある。

### 着地

- 原文の問い: 何が決まり、何が変わったとわかるのか。
- LILIAでの意味: 何が決まり、何が変わったと分かるのか。
- event_card / hookでの使い方: hook stateのresolved / pending / background / archived、memory / relationship / beliefs / decision_index保存候補として扱う。
- exit condition の例: 今夜はここで止める。明日また来る。LILIAが主人公を少し違う役割で見る。NPCが一歩動ける。関係の保留状態が明確になる。
- 失敗パターン: 完全解決しないと着地ではないと誤解する。着地後も同じsceneを続ける。

補足:
事件の完全解決でなくてよい。
小さな決着も着地である。

### 余韻

- 原文の問い: 読み終えたあとに、どんな感情を残すのか。
- LILIAでの意味: 変化後に、どんな感情や関係の温度を残すのか。
- event_card / hookでの使い方: hotset、Next Hook、next_hook_candidate、LILIAの第一声、沈黙、距離へ短く落とす。
- exit condition の例: 変化後の温度が1つ残り、次のActive Hookへ接続できる。余韻が保存候補やnext_hookへ渡る。
- 失敗パターン: 余韻を長くしすぎる。scene closure後に新しい足音、通知、敵、謎を足してsceneを延命する。

補足:
余韻は長くしすぎない。
scene closure後、1-2ターン以内に短く残す。
次のActive Hookへ接続する。

## 4. Example: 葵の逃避/護送scene

この例はStory Functionの使い方を説明するための例である。
人物名、場面、持ち物、台詞、モチーフを今後のセッション本文、新規キャラクター、event_card生成へ流用してはいけない。

- 主役: 葵と主人公の距離、またはフードの人が動けるか。
- 起点: 路地で葵と遭遇し、奥から足音が近づく。
- 目標: フードの人を人の声がある場所へ移す。
- 試練: 追跡者、恐怖、名前をつけないで見ること。
- 糸口: 主人公が数える、後ろを見る、普通の会話をする役を担える。
- 前進: スマホを取り返す、人の声がある場所へ近づく。
- 転回: フードの人が単なる被害者ではなく、自分の行き先を選ぶ問題になる。
- 着地: バス停や人の声がある場所で一度息を整え、次の行き先を選ぶ状態になる。
- 余韻: 葵が主人公に「怖いですか」と確認し、関係の温度を残す。

この例でのArc Closure:

- 前進まで来たのに、足音、通知、気配を足し続けるとclosure不足になる。
- バス停到達やスマホ回収は、Arc Closure候補として扱う。
- その後は、余韻、状況整理、次の問い、Active Hook切替へ進む。

Example Anchoring Control:

この文書内の「葵の逃避/護送scene」例は、Story Functionの使い方を説明するための例であり、今後のセッション本文・新規キャラクター・event_card生成へ、人物名、場面、持ち物、台詞、モチーフを流用してはいけない。

抽出してよいのは、以下の構造だけである。

- sceneの主役を誰に置くか。
- 起点、目標、試練、糸口、前進、転回、着地、余韻の見方。
- 前進後に同じ緊張を足し続けるとclosure不足になるという判断。
- scene function / exit condition / change_delta の使い方。

注意:

- 十五機能を全sceneに全部埋めない。
- 初期sceneで奈落や着地へ飛ばない。
- 長期プレイでは、着地は完結ではなく、そのsceneで残った変化を意味する。
- 機能名は内部診断タグであり、作中本文には出さない。
- Play Mode本文に「今は前進です」などと出さない。
- event_card / Three Hook / AI Judge / apply-turnの判断に使う。

## 5. Scene Function

Scene Functionは、将来 `current/event_card.md` に追加できる軽量概念である。
これは「このsceneが何を達成するためのsceneか」を示す。

候補項目:

```md
## Scene Function

- function:
- current_question:
- entry_state:
- exit_condition:
- change_delta:
- next_hook_candidate:
```

各項目の意味:

- `function`: 試練、糸口、前進、転回、余韻など。Story Functionから選ぶが、固定順にはしない。
- `current_question`: このsceneでプレイヤーが追う問い。
- `entry_state`: scene開始時の状況、関係、感情、情報、役割。
- `exit_condition`: 何が起きたらこのsceneは閉じてよいか。
- `change_delta`: 入口と出口で何が変わるか。
- `next_hook_candidate`: 閉じた後に接続する候補hook。

Scene Functionはevent_cardの補助であり、story_deckではない。
event_cardは今触れるActive Hookの可視イベントを持つ。
story_deckは素材棚、未回収札、Candidate Hook、Background Hookを保持する。

## 6. Scene Progression

Scene Progressionは、sceneの入口と出口で何が変わったかを見る。

変化候補:

- 状況が変わった。
- 関係が変わった。
- 情報が変わった。
- 感情が変わった。
- 役割が変わった。
- 目的が変わった。
- 場所が変わっただけでなく、その場所の意味が変わった。

移動だけでは不十分である。
同じ緊張を別の場所へ持ち運ぶだけなら、sceneは進んでいない。

## 7. Arc Closure

Arc Closureは、sceneの機能が達成されたら、同じ緊張や同じモチーフを足して延命せず、1-2ターン以内に閉じるルールである。

closure候補:

- スマホを回収した。
- 人の声がある場所へ到達した。
- バス停で一度息を整えた。
- LILIAが主人公に役目を明確に渡した。
- 主人公が戻る/残るを選んだ。
- 約束、拒否、保留、境界線が一度言葉になった。
- sceneの問いに一度答えが出た。

sceneの核が成立したら、以下へ進む。

- 余韻
- 状況整理
- 次の問い
- Active Hook切替
- memory / relationship / beliefs / decision_index の保存候補
- Candidate Hook生成

禁止:

- 足音、光、通知、気配を足し続けてsceneを延命する。
- 同じ沈黙、雨、視線、足音、通知モチーフを3回以上反復して引っ張る。
- closure後に美文だけで数ターン続け、次に触れる入口を消す。

## 8. Hook Relationship

Story FunctionはHookを進めるための内部タグである。
Hookそのものは `docs/specs/THREE_HOOK_SPINE.md` を正本とする。

関係:

- Hook: Main / Relationship / Life の進行軸。
- Active Hook: 今このsceneで触れる可視イベント。
- Scene Function: Active Hook上のsceneが何を達成するか。
- Scene Progression: scene入口と出口で何が変わったか。
- Arc Closure: Scene Functionが達成された後、延命せず閉じるルール。
- Candidate Hook: closure後に次へ接続できる候補。

Play Modeでは原則Active Hookを1本だけ前景化する。
Story FunctionやScene Functionを本文に出さず、LILIAの声、状況、問い、具体行動へ変換する。
3本hookを本文末に並べず、1つのscene pressure、会話、物、沈黙、誘いへ変換する。

## 9. apply-turn / AI Playtest

Save Mode / apply-turnでは、以下を内部的に扱える。

- Scene Functionが達成されたか。
- Exit Conditionを満たしたか。
- change_deltaがあったか。
- Active Hookを継続、背景化、resolved化、worsened化するか。
- Candidate Hookを生成するか。
- Candidate Hookをactive stateへpromotionするか。

AI Playtest Judgeは将来、以下を見られるようにする。

- Scene Functionが達成されたか。
- Exit Conditionを満たした後に1-2ターンで閉じたか。
- 同じ緊張を足してsceneを延命していないか。
- scene入口と出口で何が変わったか。
- 次のActive Hookへ切り替わったか。
- 3本hookを毎ターン全部出していないか。
- Life Hookが脱線を自然に吸着できたか。

この判定語はJudge / report / Save Mode用であり、Play Mode本文には出さない。

## 10. Failure Patterns

- Story Functionを固定プロット順として強制する。
- Play Mode本文に「試練」「糸口」「Scene Function」などの管理語を出す。
- sceneの入口と出口で何も変わらない。
- 情報説明だけで問いがない。
- event_cardとstory_deckが同じ内容になる。
- scene closure後に足音、通知、気配を足して延命する。
- 同じ沈黙、雨、視線、足音、通知モチーフを3回以上反復する。
- next_hookをstory_deckに置いただけでactive化したつもりになる。
- 3本hookを毎ターン3択UIとして出す。
- story_deck / hotsetを、promotionなしにactive event sourceとして扱う。

## 11. Passing Conditions

- Story Functionは診断タグとして使われ、固定順ではない。
- Play Modeでは管理語が出ず、問いと具体行動に変換されている。
- sceneの入口と出口で何かが変わっている。
- event_cardは今触れるActive Hookだけを持っている。
- story_deckは素材棚、Candidate Hook、Background Hookを保持している。
- closure後は余韻、状況整理、次の問い、Active Hook切替へ進める。
- apply-turn / Judgeが将来参照できる粒度でScene FunctionとExit Conditionが定義されている。
