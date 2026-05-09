# LILIA Story Function Framework

この文書は、LILIAのhook、scene、event_card、apply-turn、AI Playtestで使う物語機能の診断フレームである。

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

| Function | LILIA用の意味 |
|---|---|
| 主役 | この変化を誰の関係として読むか。基本は主人公とLILIAの関係。 |
| 前提 | 現在の距離、場所、生活、仕事、境界線、未解決の圧。 |
| 起点 | 日常や関係の温度を揺らす出来事、違和感、依頼、言い残し。 |
| 目標 | プレイヤーが今触れる可視問題、問い、具体的な入口。 |
| 始動 | 主人公が関わる最初の一歩。話す、待つ、触れない、同行を頼むなど。 |
| 試練 | LILIAの怖さ、弱さ、誤解、境界線、生活事情が表に出る。 |
| 糸口 | 約束、記憶、物的手がかり、LILIAの言い淀み、主人公の選択。 |
| 前進 | 関係、情報、状況、役割のどれかが少し進む。 |
| 転回 | 問題の意味が変わる。事件ではなく関係の意味が深くなることも含む。 |
| 孤立 | LILIAが頼れない、言えない、主人公が単独で動く、または関係が離れる。 |
| 奈落 | 拒否、沈黙、誤解、危機、生活の破綻、関係の痛みが底に触れる。 |
| 打開 | 積み上げた記憶、尊重、観察、選択から突破口が出る。 |
| 選択 | 主人公またはLILIAが、戻る/残る、言う/黙る、同行/非同行などを選ぶ。 |
| 着地 | そのscene / hookで何が変わったかを保存候補へ落とす。 |
| 余韻 | 次回の第一声、hotset、next hook、Active Hook切替へ接続する。 |

注意:

- 十五機能を全sceneに全部埋めない。
- 初期sceneで奈落や着地へ飛ばない。
- 長期プレイでは、着地は完結ではなく、そのsceneで残った変化を意味する。
- 機能名は内部診断タグであり、作中本文には出さない。

## 4. Scene Function

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

## 5. Scene Progression

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

## 6. Arc Closure

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

## 7. Hook Relationship

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

## 8. apply-turn / AI Playtest

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

## 9. Failure Patterns

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

## 10. Passing Conditions

- Story Functionは診断タグとして使われ、固定順ではない。
- Play Modeでは管理語が出ず、問いと具体行動に変換されている。
- sceneの入口と出口で何かが変わっている。
- event_cardは今触れるActive Hookだけを持っている。
- story_deckは素材棚、Candidate Hook、Background Hookを保持している。
- closure後は余韻、状況整理、次の問い、Active Hook切替へ進める。
- apply-turn / Judgeが将来参照できる粒度でScene FunctionとExit Conditionが定義されている。
