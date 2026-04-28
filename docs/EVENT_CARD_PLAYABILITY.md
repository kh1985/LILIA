# LILIA Event Card Playability Gate

この文書は、`current/event_card.md` を、抽象的な違和感メモではなく、ユーザーが今すぐ触れる可視イベントにするための設計正本です。
実装コードやlauncher仕様ではなく、new / resume / 通常sceneで event_card を作る時の軽量Gateを定義します。

## 1. Purpose

Event Card Playability Gate は、今のsceneでユーザーが何に触れればLILIAとの関係が動くのかを明確にする。

LILIAでは、ストーリーは主役ではない。
event_card は事件処理ではなく、LILIAの人格、記憶、信頼、警戒、沈黙、境界線、親密さの出方を少し動かすための入口である。

## 2. Source Of Truth

- event_card設計正本: `docs/EVENT_CARD_PLAYABILITY.md`
- state構造: `docs/STATE_STRUCTURE.md`
- new初期化: `docs/NEW_SESSION_INITIALIZATION.md`
- new開始prompt: `prompt/newgame.md`
- save/resume: `prompt/save_resume.md`
- style参照: `prompt/style_reference.md`
- voice continuity: `docs/VOICE_CONTINUITY.md`

prompt側には実行時の短い確認だけを置く。
Gateの詳細、失敗条件、採用元、不採用方針はこの文書を正本にする。

## 3. Core Distinction

- `story/story_deck.md`: 物語素材、圧、未回収札、後で使える札を持つ。
- `current/event_card.md`: 今のsceneでユーザーが触れられる可視イベントを1つ持つ。

`story_deck` は素材棚であり、今すぐ触る場面そのものではない。
`event_card` は現在の入口であり、裏設定、真相、長いプロット、文体参照を抱え込まない。
`story_deck` の「初回sceneで使う小さな出来事」は素材名や未回収札として短く置き、現在sceneで触る内容は `event_card` に参照/変換して置く。

## 4. Required Fields

`current/event_card.md` は最低限、以下を持つ。

- `Visible Problem`
- `First Concrete Action`
- `Handles 2-4`
- `Relationship Stake`
- `If Ignored`
- `Next Visible Change`

これらが空なら、初回sceneやresume 1ターン目を始める前に補う。

## 5. Gate Conditions

### Visible Problem

ユーザーに見えている問題があること。
抽象的な違和感だけで終わらせない。

- 誰が困っているか。
- 何が止まりそうか。
- 何に触れれば入口になるか。

真相は隠してよい。
ただし、触れる入口まで隠してはいけない。

### First Concrete Action

ユーザーが最初にできる具体行動があること。
`調べる`、`話す` だけで終わらせず、何を、誰に、どう触るかが分かる粒度にする。

初回sceneでは重すぎない一手にする。

### Handles 2-4

ユーザーが触れる取っ掛かりを2-4個だけ置く。
handles は正解選択肢ではない。
それぞれ、関係の温度が少し違う入口にする。

handle種別の例:

- `ask`
- `wait`
- `comfort`
- `challenge`
- `avoid`
- `promise`
- `touch boundary`
- `memory`
- `style/tone`

この一覧は候補語であり、固定選択肢ではない。
ユーザーの文脈、現在scene、LILIAの状態に合わせて自然な入口へ変換する。

### Relationship Stake

そのeventが、LILIAとの関係に何を残すかを明確にする。

事件解決ではなく、以下のどれかに刺さること。

- 信頼
- 警戒
- 誤解
- 距離
- 親密さ
- 沈黙
- 境界線
- 記憶
- beliefs

### If Ignored

ユーザーが触れなかった場合、世界や関係が少しだけ動く。
放置即失敗にはしない。
ただし完全停止もしない。

1-3 scene以内に見える変化として返す。
eventが現在sceneから下がる場合は、必要に応じて `story/story_deck.md` の未回収札へ落とす。

### Next Visible Change

次にユーザーが見て分かる変化を1つ置く。
内部状態だけで終わらせない。

変化は、LILIAの第一反応、呼び方、返信速度、沈黙、距離、話題の避け方、保存されなかった言葉などに出す。
呼び方や声の変化を置く場合は、`docs/VOICE_CONTINUITY.md` に従い、前回までの `voice`、`relationship`、`memory`、`beliefs` と矛盾させない。

## 6. Truth Hiding Boundary

真相、裏事情、LILIAの本音のすべてをevent_cardで明かさない。

隠してよいもの:

- 本当の原因
- LILIAがまだ言えない本音
- 誤解の正解
- 後で効く未回収札
- まだLILIA自身にも分かっていない気持ち

隠してはいけないもの:

- ユーザーが今触れる入口
- 誰が困っているか、または何が止まりそうか
- 最初にできる行動
- 関係に残る賭け
- 放置時の小さな変化

目標は、「何が起きているかは全部分からないが、何に触ればよいかは分かる」状態である。

## 7. Mid-Story Activation Gate

途中で新しいevent_cardを出す時は、現在の `scene`、`relationship`、`memory`、`beliefs`、`relationship_spine`、`story_deck` に接続しているか確認する。
親密scene、衝突scene、境界線sceneでは、`voice` と呼び方も確認する。

新しいevent_cardを作ってよい場面:

- 背景の未回収札が前景化した。
- ユーザーが別の圧、場所、人物、約束、境界線へ能動的に触れた。
- 既存eventの `if ignored` が見える変化として返ってきた。
- LILIAの記憶、誤解、保留、境界線が現在sceneで揺れた。

避けること:

- 唐突な事件や乱入で親密sceneを壊す。
- 抽象設定や組織だけを増やす。
- 既存の `handles`、`if ignored`、`next visible change` に接続できない謎を足す。

親密場面では、event_card は雑な妨害ではなく、境界線、aftercare、翌朝の第一声、言い残し、止まれる余地として機能させる。

## 8. Style / Intimacy Connection

event_card は文体参照そのものではない。
文体軸は `style/reference.md` と `style/rules.md` に置く。

ただし、ロマンス、衝突、静かな変化、危機などの場面では、必要時だけ `style/defaults/` から1つ、多くても2つまで参照してよい。

官能・親密表現は削除しない。
ただしevent_cardで初回からベッドシーンや恋愛成立を確定しない。

親密eventでは、成人、合意、相互性、境界線、止まれる余地を必ず守る。

## 9. Gate Failure Conditions

以下のどれかに当てはまる場合、event_cardはGate未通過である。

- visible problem が抽象的すぎる。
- first concrete action がない。
- handles が0個、1個、または5個以上ある。
- relationship stake が事件処理だけで、LILIAとの関係に刺さらない。
- if ignored がない。
- next visible change がない。
- 真相を隠しすぎて、ユーザーが何をすればよいか分からない。
- story_deck と event_card が同じ内容になっている。
- LILIAの内面を全部説明しすぎている。
- ユーザーの内面を断定している。
- 初回から重いcase_engine / villain / combatへ広げている。
- 親密sceneを雑な事件乱入で壊している。
- 官能・親密を安全の名目で全部薄めている。

## 10. Gate Pass Conditions

以下を満たす場合、event_cardはGate通過である。

- ユーザーが今すぐ触れる入口がある。
- LILIAの人格、記憶、関係、beliefsに刺さる。
- 放置時にも小さな変化がある。
- 次に見える変化がある。
- story_deckとは責務分離されている。
- 通常sceneでは `hotset` / `scene` / `event_card` だけで、最初の1ターンの入口が戻る。
- 親密scene、衝突scene、境界線が関わるsceneでは、必要箇所だけ `relationship`、`beliefs`、`style/rules` も確認できる。
- 声、呼び方、距離感に変化を残す場合は、`docs/VOICE_CONTINUITY.md` のGateに接続できる。
- 初回sceneでも重すぎない。
- 親密・官能の余地を消さず、成人、合意、相互性、境界線を守る。

## 11. Save / Resume Handling

保存時は、event_cardを長いログにしない。
現在sceneで触れる入口、放置時の変化、関係に残るものだけを残す。

resume時は、`current/hotset.md`、`current/scene.md`、`current/event_card.md` を入口にする。
event_cardがGate未通過なら、本文を始める前に最小補正する。
hotsetには、event_cardの現在温度と次の入口を短く抜く。
ただし、hotsetを正解ルート表、todo、複数アンカーの一覧にしない。

event_cardが現在sceneから外れた場合は、`story/story_deck.md` の未回収札へ落とすか、閉じた関係変化として `archive/beats/` に送る。

## 12. 採用元

- MIRA: `state / relationship / memory / beliefs`
- inner-galge: hotset、Markdown運用、validation、プレイヤーが触れる行動余地の足場、voice continuity
- LIRIA: event_card、case_engineの可視入口、Visible Request Gate、Truth Hiding Boundary、Mid-Story Activation Gate、save/resume方針

## 13. 採用しなかったもの

- 重いcase_engine
- villain_engine / organization
- combat処理
- 複数ヒロイン事件構造
- 真相の全開示
- 抽象的な違和感だけで進める運用
- 親密sceneを雑な事件乱入で壊す運用
- 官能表現そのものの削除
- 初回から大規模な分岐管理やCLI実装

## 14. Reason

New Session Initialization でevent_cardの枠はできたが、可プレイ性がなければ初回sceneでユーザーが何をすればよいか分からなくなる。

LILIAではストーリーは主役ではなく、関係と人格の出方を変化させる装置である。

event_card は、事件メモではなく、LILIAの反応、記憶、信頼、境界線に刺さる小さな出来事として扱う必要がある。

真相を隠しても、ユーザーが触れる入口は隠してはいけない。

resume時にevent_cardが弱いと、再開1ターン目の温度と行動余地が落ちる。
