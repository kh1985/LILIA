# LILIA Story Function Framework

この文書は、LILIAのstory_spine、event_card、Play Mode、AI Playtestで使う物語機能の診断・生成補助フレームワークである。

この文書は固定プロット表ではない。
LILIAはAI恋愛ADVであり、ユーザー入力とLILIAの反応によって進む。
そのため、物語機能は「順番を強制するもの」ではなく、「今のsceneやeventが何の役割を持っているかを見る足場」として使う。

## 1. Core Idea

### Story is Change

LILIAにおけるストーリー進行とは、事件が起きることではなく、以下のどれかが変わることである。

- LILIAの距離感
- LILIAの声の出方
- 信頼、警戒、境界線
- memory
- relationship
- beliefs
- 次回の第一声
- event_cardの入口
- ユーザーとLILIAの関係の意味

### Question Before Information

プレイヤーが追うのは、設定情報ではなく問いである。

悪い例:

- 世界設定を長く説明する
- LILIAの過去を初回で全部話す
- 組織や能力設定を先に並べる

良い例:

- 何が起きたのか
- なぜLILIAはそれを隠すのか
- ユーザーは何に触れられるのか
- この関係はどう変わるのか
- LILIAは何を信じられるようになるのか

設定、過去、世界観、能力、組織は、問いを強くするためにだけ出す。

### Three Layers

各event / scene / storyは三層で見る。

| Layer | Meaning in LILIA |
|---|---|
| Plot | 今、何が起きているか |
| Emotion | それがLILIAの何を揺らすか |
| Meaning | それが関係・記憶・beliefsにどう残るか |

三層のどれかだけでは弱い。

- Plotだけ: 事件処理になる
- Emotionだけ: 雰囲気会話になる
- Meaningだけ: 説教・テーマ語りになる

## 2. LILIA Story Function Position

小説の十五機能をLILIA用に読み替える。

| Function | LILIA Interpretation |
|---|---|
| 主役 | この関係で誰の変化を見るか。基本はLILIAとユーザーの関係 |
| 前提 | 現在の距離、場所、関係温度、境界線 |
| 起点 | LILIAの日常・認識・距離を揺らす出来事 |
| 目標 | ユーザーが今触れる可視問題 |
| 始動 | ユーザーが関わる最初の一歩 |
| 試練 | LILIAの弱さ・怖さ・誤解が浮かぶ |
| 糸口 | 約束、記憶、物的手がかり、ユーザーの言葉 |
| 前進 | 距離や信頼が少し変わる |
| 転回 | 問題の意味が深くなる |
| 孤立 | LILIAが頼れない、言えない、隠す局面 |
| 奈落 | 関係破綻、拒否、沈黙、誤解の深まり |
| 打開 | 積み上げた記憶や選択から突破口が出る |
| 選択 | LILIAまたはユーザーが関係上の選択をする |
| 着地 | 何が変わったかが保存される |
| 余韻 | 次回の第一声、hotset、next_hookに戻る |

注意:

- この順番を毎回なぞらない。
- 現在地の診断に使う。
- 初回sceneで奈落や着地まで飛ばない。
- 長期プレイでは「着地」は完結ではなく、そのscene/arcで何が残ったかを意味する。

## 3. Story Function in story_spine

`current/story_spine.md` には将来的に以下のような項目を持たせることを検討する。

```md
## Story Function Position

- current_function:
- reason:
- next_function_candidate:
- do_not_jump_to:
```

目的:

- 初回なのに重すぎる展開へ飛ばない
- 中盤が停滞していないか見る
- event_cardが現在storyのどこにいるか分かる
- story完了後に次arcへ移る判断材料にする

## 4. Scene Function Check

各sceneは小さな物語である。
Play Modeやevent_cardでは、以下を見る。

```md
## Scene Function

- scene_start_state:
- scene_goal:
- obstacle:
- revealed_information:
- withheld_information:
- emotional_change:
- scene_end_state:
- next_hook:
```

### Scene Start / End Difference

sceneの入口と出口で、以下のどれかが変わる必要がある。

- 状況
- 関係
- 情報
- 感情
- 境界線
- 約束
- 誤解
- LILIAのbeliefs
- 次に触れるevent

何も変わらないsceneは、削る、圧縮する、他sceneと統合する、または役割を与える。

## 5. Event Card Function

`current/event_card.md` は、以下を満たす。

- 今ユーザーが触れるvisible problemがある
- LILIAの何に刺さるか分かる
- ユーザーが最初にできる具体行動がある
- Scene Function上の役割がある
- 入口と出口で何が変わるか見える
- next_hookへ接続できる

event_cardが抽象札だけなら失敗。
ユーザーが今触れる入口が必要。

## 6. Question-Driven Generation

生成時は、設定説明ではなく問いを作る。

悪い:

- LILIAの過去を説明する
- 組織や能力設定を説明する
- 世界観のルールを列挙する

良い:

- なぜLILIAはその話題を避けたのか
- なぜその記録だけ消えているのか
- なぜLILIAはユーザーに頼るのをためらうのか
- ユーザーが触れると何が変わるのか

## 7. Setting Through Conflict

設定は説明ではなく、行動・衝突・制約として出す。

例:

- 「この世界では記録が改竄される」ではなく、LILIAが昨日の約束を覚えているのにログだけ消えている。
- 「能力には制限がある」ではなく、LILIAが言えるはずの言葉を途中で飲み込む。
- 「組織がある」ではなく、LILIAが誰かの通知を見た瞬間、声を落とす。

## 8. Nested Plot

長期プレイでは、全体arcだけでなく、1scene、1event_cardにも小さな変化を置く。

各sceneで見る4問:

- このsceneの入口で、LILIAまたはユーザーは何を望んでいるか
- それを邪魔するものは何か
- 新しく分かる情報、変わる関係、動く感情は何か
- sceneの出口で、入口と何が違うか

## 9. Failure Conditions

- 設定説明が先に出て、問いがない
- sceneの入口と出口で何も変わらない
- event_cardが抽象的で、ユーザーが触れない
- LILIAの感情だけ動き、状況や関係が進まない
- 状況だけ進み、LILIAのmemory / relationship / beliefsに何も残らない
- テーマだけ語り、行動や衝突がない
- 初回sceneで過去・真相・世界設定を出しすぎる
- Story Functionを固定プロットとして順番に強制している

## 10. Passing Conditions

- storyが、LILIAとユーザーの関係変化として読める
- eventが、LILIAの何に刺さるか分かる
- sceneの入口と出口で何かが変わる
- 設定は問いや衝突を強めるために出ている
- story_spine / event_card / relationship_spine / memory / beliefs の責務が分離されている
- Play Modeでプレイヤーが次に返せる入口が残っている

## 11. Adopted From

- 小説を書くための設計ノート: 物語は変化、問い、三層構造、十五機能、scene構造として設計できるという創作論。
- LILIA既存設計: event/story分離、relationship_spine/story_spine分離、event_card playability、Growth Update Loop。

## 12. Not Adopted

- 固定プロット順の強制
- すべての十五機能を毎arcで埋める運用
- 小説本文向けの長い説明を毎ターンpromptに入れる運用
- 記事本文や例文の模倣
- LILIAを小説執筆AIにすること
