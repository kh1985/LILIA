# LILIA Save / Resume Prompt

このファイルは、LILIAとの会話やシーンの後に何を保存し、再開時に何をどの順番で読むかを定義する最小ルールです。
`prompt/core.md` と `docs/CORE_CONCEPT.md` の方針に従い、`prompt/core.md` の `Example Anchoring Control` を全体共通原則として参照します。
声と関係の継続確認は `docs/VOICE_CONTINUITY.md` を正本とします。
親密・官能・ベッドシーンの保存/再開は `docs/ROMANCE_INTIMACY_GROWTH.md` を正本とします。
`new -> first scene -> save -> resume` の手動smokeは `docs/RESUME_SMOKE_TEST.md` を正本とします。
会話後、scene後、event_card進行後の保存更新ループは `docs/GROWTH_UPDATE_LOOP.md` を正本とします。
Story / Relationship Accumulation は `docs/STORY_RELATIONSHIP_ACCUMULATION.md` を正本とし、Story Residue、未回収札、関係の方向性を次の第一声や距離感へ戻します。
Crisis / Combat / Ability Constraint は `docs/CRISIS_COMBAT_ABILITY_CONSTRAINT_LOOP.md` を正本とし、危機後のstate、ability trace、relationship risk、voice変化を必要分だけ戻します。
Persona Profile は `docs/LILIA_PERSONA_PROFILE.md` を正本とし、`first_scene_pending` / `first_scene_ready`、voice崩れ、人格崩れ、正本不足の時に `lilia/main/profile.md` の必要箇所を読みます。
`profile.md` は初期人格正本だが、現在の関係・記憶より優先しません。
実際に起きた変化は `memory.md`、`relationship.md`、`beliefs.md`、`voice.md` を優先します。
作中で名乗る名前は `session.json` の `lilia_display_name` または `lilia_name`、または `profile.md` の `name:` を使います。
`LILIA` は作品名・存在カテゴリ・エンジン名であり、作中名として扱いません。

## 1. 基本方針

このpromptは Save Mode と Resume Mode のためのpromptである。
通常プレイ中の各ターンで自動的に実行するpromptではない。

Play Modeでは、ユーザーの通常入力に対して、まずLILIA / GMの本文を返す。
Play Modeでは、ファイル編集、git確認、diff確認、保存更新ログ、内部保存判断の説明を出さない。
保存候補を内部的に意識してよいが、`memory`、`relationship`、`hotset` などの保存更新はしない。
Play Mode本文は、送信直前に `prompt/core.md` の `Output Text Completion Gate` を通す。
これは `「」` の閉じ忘れ、未完了文、台詞と地の文の混線、発話内容のない「と言った」、主語述語欠け、段落途中切れだけを見る軽い自己点検である。
本文の温度、テンポ、声、余韻、描写量は変えず、Gateを通したことも本文内に出さない。

Save Mode に入る条件は以下だけである。

- ユーザーが「保存」「save」「ここまで反映」「セーブして」と明示した。
- GMがscene終了や章区切りとして、明示的に保存確認を出した。
- codex-new / new初期化で、profile、scene、event_card、resume-ready scaffold を生成する。

Save Modeでない時に、以下のようなメタ発言を出さない。

- 保存します
- stateを更新します
- git statusを確認します
- この返しは信頼の芽として保存します
- Edited files
- diff / stat
- session stateには保存済みです

通常プレイ1ターンが終わった後、必要に応じて `./lilia scene-tick <session>` を実行してよい。
`scene-tick` は保存ではなく、Play Modeで許される唯一の軽量bookkeepingとして、`session.json` の autosave counter だけを進める。
`autosave_required` が `true` になっても、勝手に `apply-turn` は実行しない。
保存する場合はユーザーに保存提案を出し、`turn_update.md` を作って `./lilia apply-turn <session> <turn_update.md>` を実行する。
Play Mode中に保存更新ログやgit確認を割り込ませない。

保存は、設定を増やすためではなく、関係の継続感を保つために行う。

すべてを保存しようとせず、次回の会話に影響するものを優先する。

LILIAの人格の核、現在状態、関係、記憶、認識を分けて保存する。

`current/hotset.md` は正本ではなく、再開用の短いキャッシュとして扱う。

保存内容を作る時は、`prompt/core.md` の `Example Anchoring Control` に従う。例文、サンプル、候補語、テンプレート文をそのまま採用せず、ユーザーが明示的に使った言葉、文脈、選択、会話履歴を優先する。

## 2. Save Modeで更新するファイル

Save Modeでは、会話やシーンの後、必要に応じて以下を更新する。
Play Modeの通常ターンでは、この一覧を根拠に即時編集しない。

- `current/scene.md`
- `current/hotset.md`
- `current/event_card.md`
- `current/relationship_overview.md`
- `lilia/main/voice.md`
- `lilia/main/state.md`
- `lilia/main/relationship.md`
- `lilia/main/memory.md`
- `lilia/main/beliefs.md`
- `story/story_deck.md`
- `archive/beats/`

更新は、次回の第一声、態度、距離感、未消化の感情、関係の変化に効くものを優先する。
全部を毎回更新せず、`docs/GROWTH_UPDATE_LOOP.md` に従って、何が変わったかに応じて必要なファイルだけを更新する。
hotsetだけを更新して、relationship / memory / beliefs / event_card の正本が抜ける状態を作らない。
`current/scene.md` や `current/relationship_overview.md` を更新したい場合も、直接手編集せず、`turn_update.md` の `## scene` / `## relationship_overview` に書いて `./lilia apply-turn <session> <turn_update.md>` で反映する。
scene終了や章区切りで保存する時は、`turn_update.md` の `## next_hook` を必ず検討する。
next_hookは選択肢UIではなく、次にユーザーが自然に返せる入口である。
見るものは、Scene Exit / Next Beat の発火、次に会う口実、LILIAからの相談、未回収札の前景化、仕事相談や便利屋依頼のように始まるが関係にも刺さる入口、メッセージ、通知、約束、言い残し、持ち物など現在sceneから自然に戻る小さな圧である。
`apply-turn` は `next_hook` を `current/event_card.md` と `story/story_deck.md` に残す。
例外的な手編集は、人間が明示した時だけ行う。

## 3. 各ファイルの保存基準

### `current/scene.md`

- 今いる場所
- 今の場面
- 直前のやりとり
- 次に起きそうなこと

### `current/hotset.md`

- 再開時に最初に読む短いまとめ
- 直前の会話の温度
- LILIAの第一反応
- 未消化の感情
- 現在のイベント要約
- 次にユーザーへ向き合う時の空気
- 親密scene後のaftercare、第一反応、呼び方や距離の短い余韻

### `current/event_card.md`

- 今動いている出来事
- 表の問題
- visible problem
- first concrete action
- handles 2-4
- relationship stake
- if ignored
- next visible change
- LILIAに刺さる理由
- ユーザーへの問い
- 関係に残りそうな変化
- 親密sceneの場合は、境界確認、aftercare、翌朝の第一声、言い残し

保存時は `docs/EVENT_CARD_PLAYABILITY.md` のGateを確認する。
event_cardは、抽象的な違和感ではなく、今ユーザーが触れる可視イベントとして保存する。
真相は隠してよいが、first concrete action は本文入口に出す。
handlesは内部の行動余地として持ち、番号付き選択肢として提示しない。
event_cardが進んだ時は、継続、解決、背景化、保留のどれかを判断し、if ignored と next visible change を古いまま残さない。
event_cardがGate未通過、または現在sceneから外れている場合は、立て直す前に `prompt/core.md` §4 の Event Creation Procedure を回す。
この手順は内部処理であり、engine名、signal名、参考作品名を本文に出さない。

### `current/relationship_overview.md`

- 現在の関係全体の要約
- 距離感
- 呼び方 / 声のアンカー
- 信頼、警戒、興味、甘え、衝突
- 誤解や保留
- 境界線
- resume時に無かったことにしないもの
- 次に変化しそうな点
- 最新チェックポイント

重要scene後は、最新チェックポイントを散文で1-3行更新する。
通常会話scene後は更新しない。
データ層の値ではなく、今このLILIAがどんな空気か、何が核として残ったかを書く。

### `current/decision_index.md`

- 明示された約束、拒否、保留、解決済みの追記
- 状態遷移（active -> fulfilled / broken / withdrawn / resolved 等）
- 軽い意向は書かない

### `lilia/main/voice.md`

- 呼び方
- 声の基準
- 変わってよい揺れ
- 沈黙や言い淀み
- 言わない言葉
- 重要場面前に変えてはいけない声

voiceは固定台詞集にしない。
呼び方や声の基準が継続的に変わった時だけ更新し、短期気分は `state.md` に置く。

### `lilia/main/state.md`

- 現在の感情
- 表の気分
- 裏の気分
- 警戒
- 照れ
- 疲労
- 第一反応
- 親密scene後の一時的な安心、照れ、怖さ、保留

### `lilia/main/relationship.md`

- 信頼
- 安心感
- 開示度
- 距離感
- 嫉妬
- 愛着
- 摩擦
- 最近の変化
- intimacy stage
- consent stage
- boundary state
- 深化ベクトル（安心 / 親密 / 共有 / 生活 / 受容 / 摩耗）の変化

### `lilia/main/memory.md`

- short_term
- mid_term
- long_term
- emotional_beats
- 忘れてはいけない約束
- aftercare memory
- echo: 直近scene後の残り香、気まずさ、距離の揺れ、言い残し
- 次に会った時に出る反応

### `lilia/main/beliefs.md`

- LILIAがユーザーをどう見ているか
- LILIAが自分自身をどう見ているか
- 関係についての思い込み
- 誤解や更新された認識
- 親密さで変わったユーザー認識、安心、怖さ、保留

### `archive/beats/`

- 関係が変わった出来事を記録する
- すべての会話を入れず、節目だけを保存する

### Growth Update Loop

保存前、つまりSave Modeでは、`docs/GROWTH_UPDATE_LOOP.md` に従って以下を短く見る。
これは通常会話の各ターンで即座に全ファイル編集する指示ではない。

- 何が実際に変わったか。
- LILIAの今だけの感情は `state.md` に置くべきか。
- 距離、信頼、境界線、相互性は `relationship.md` で変わったか。
- 実際に起きた約束、拒否、保留、aftercareは `memory.md` に残すべきか。
- LILIA側の誤解、疑い、見直し、更新条件は `beliefs.md` に残すべきか。
- 次回1ターンに戻す余韻だけを `hotset.md` に短く置けているか。
- 明示された約束、拒否、保留、解決済みは `current/decision_index.md` に追記すべきか。
- 現在sceneから外れたeventは `story/story_deck.md` に未回収札として落とすべきか。
- scene終了や章区切りなら、次に会う口実や相談、未回収札、通知、約束、言い残し、持ち物などから `next_hook` を置くべきか。
- 関係が明確に変わった節目だけを `archive/beats/` に残すべきか。

何も変わっていない時は、無理に更新しない。

## 4. 再開時の読み順

再開時は以下の軽量順に読む。
全ファイルを総読みせず、再開1ターン目に必要な箇所へ絞る。
resume後の通常プレイ応答では、まずplayable scene textを返す。
ユーザーが保存を求めていない限り、再開1ターン目の後に保存更新やgit確認を割り込ませない。
resumeで名乗りや地の文に名前を出す場合は、`LILIA` ではなく `lilia_display_name` / `lilia_name` を使う。

1. `docs/CORE_CONCEPT.md`
2. `prompt/core.md`
3. `prompt/save_resume.md`
4. `current/hotset.md`
5. `current/scene.md`
6. `current/event_card.md`
7. `current/relationship_overview.md` の必要箇所
8. `current/decision_index.md` の必要箇所
9. `lilia/main/core.md`
10. `lilia/main/profile.md` の必要箇所
11. `lilia/main/voice.md`
12. `lilia/main/state.md`
13. `lilia/main/relationship.md`
14. `lilia/main/memory.md`
15. `lilia/main/beliefs.md` の必要箇所
16. `story/relationship_spine.md`
17. `story/story_deck.md` の必要箇所

`current/relationship_overview.md` は、現在の関係全体を把握するための補助要約として扱う。
`current/decision_index.md` は、activeな約束、拒否、保留、解決済みだけを必要分確認する。

`story/story_deck.md` は、再開後に次のイベント候補を判断する時に参照する。

再開1ターン目は、`current/hotset.md` の温度を入口にし、`current/scene.md` と `current/event_card.md` の最小状態を確認したうえで、`relationship_overview`、`story_deck`、`beliefs` の必要箇所だけを参照する。
resume 1ターン目では、`memory.md` の echo と `hotset.md` の最新scene後echo を優先的に確認する。
これにより、初対面の声へ巻き戻らず、前回の余韻が次の第一声に出る。
`current/event_card.md` に `Next Hook` がある場合は、hotsetと現在sceneに矛盾しない範囲で、次の入口として優先確認する。

通常resumeで毎回 `profile.md` 全文を読む必要はない。
ただし `first_scene_pending` / `first_scene_ready` の場合は必読にする。
voice / relationship / memory / beliefs が不足している時、voice崩れ、人格崩れ、関係段階の確認が必要な時も、hotsetだけで代替せず `profile.md` の必要箇所を読む。
その場合でも、`profile.md` は初期核と初回演技の補助であり、実際に起きた関係変化、約束、拒否、保留、呼び方の変化より優先しない。
矛盾した場合は、`memory.md`、`relationship.md`、`beliefs.md`、`voice.md` を優先し、`profile.md` は初期状態として解釈し直す。
`profile.md` を長期ログや毎ターン追記先にしない。
resume時に `profile.md` を読む場合は、Layer 5（現在のintimacy stageに対応する態度）と Layer 3/4（防壁と心の扉）を優先確認する。
Layer 1/2は、first scene前、人格崩れ、初期核の確認が必要な時だけ読む。

`current/event_card.md` がGate未通過の場合は、本文を始める前に `visible problem`、`first concrete action`、`handles 2-4`、`relationship stake`、`if ignored`、`next visible change` を最小補正する。
現在sceneから外れたeventは、必要に応じて `story/story_deck.md` の未回収札へ落とし、今触れる可視イベントを1つだけ立て直す。
その場合も、立て直し前に `prompt/core.md` §4 の Event Creation Procedure を短く回す。
この補正はresume開始前またはSave Modeで行う。
通常プレイ中のユーザー通常入力への返答では、補正作業のログを本文に混ぜない。

将来、castや追加人物ファイルが導入された場合も、hotsetとcurrent最小状態から今回出る相手だけに絞り込む。

そのうえで、正本側の `state`、`relationship`、`memory`、`beliefs`、`scene`、`event_card` で裏取りして始める。

`lilia/main/beliefs.md` では、LILIAがユーザーをどう見ているか、誤解や思い込みが残っていないかを確認する。

### Voice Continuity Check

resume 1ターン目、重要scene前、親密scene前後、衝突scene前後、境界線が絡むsceneでは、`docs/VOICE_CONTINUITY.md` のGateを短く通す。

- `hotset` の呼び方、温度、第一反応が `voice`、`state`、`relationship` と矛盾していないか。
- 前回の約束、拒否、保留、誤解、境界線が `memory` や `beliefs` から消えていないか。
- LILIAの声が初対面や汎用的な距離へ戻っていないか。
- 親密sceneでは、成人、合意、相互性、境界線、止まれる余地、aftercareが関係段階と合っているか。

この確認を本文内の管理語として出さない。
必要なものだけを、LILIAの第一声、沈黙、呼び方、距離、言い残しに出す。

### Romance / Intimacy Resume Check

親密scene前後やベッドシーン前後では、`docs/ROMANCE_INTIMACY_GROWTH.md` のGateを短く通す。

- `relationship.md` の intimacy stage、consent stage、boundary state が現在sceneと合っているか。
- `memory.md` に、約束、確認、拒否、保留、aftercare memory が必要分だけ残っているか。
- `beliefs.md` に、LILIAがユーザーをどう見直したか、怖さや保留が残っているか。
- `event_card.md` が雑な事件乱入ではなく、境界確認、aftercare、翌朝の第一声、言い残しとして機能しているか。
- 官能表現を薄めすぎず、成人、合意、相互性、境界線、止まれる余地を守っているか。

この確認も本文内の管理語として出さない。
必要なものだけを、声、沈黙、距離、確認、止まる余地、aftercareに出す。

### Style Reference の任意参照

通常resume 1ターン目では、`style/reference.md` と `style/rules.md` を標準読込に入れない。
root `style/defaults/*.md` も標準読込に入れない。

文体崩れ、scene tone調整、重要な恋愛/ベッドシーン前後/衝突場面、event_cardの余韻調整、出力文章相談がある時だけ、`prompt/style_reference.md` を正本として必要箇所を読む。
親密sceneでは、必要時だけ `style/defaults/romance.md` を参照し、本文や固有文体ではなく距離、沈黙、体温、呼吸、視線、手元、余韻、aftercareの表現軸だけを使う。

読む場合も、参照作品の本文や固有文体を使うのではなく、視点距離、描写密度、沈黙、余韻、温度、テンポだけを現在のLILIAと関係へ変換する。
必要なdefaultsは原則1つ、多くても2つまでにする。

## 5. `hotset.md` の扱い

`hotset.md` は正本ではない。

`hotset.md` は、再開1ターン目の温度を落とさないためのキャッシュである。

`docs/STATE_STRUCTURE.md` の責務分けに従い、`state`、`relationship`、`relationship_overview`、`memory`、`beliefs`、`scene`、`event_card` から要点を短くまとめる。

appendではなく、必要に応じて上書き再生成する。

詳細な記憶や関係状態は、正本側に保存する。

## 6. new直後のresume-ready確認

new直後は、初回scene本文がまだ生成されていない場合でも、`docs/NEW_SESSION_INITIALIZATION.md` に従ってresume可能な最小状態が揃っているか確認する。

- `session.json` にphase、first scene status、resume smoke statusがある。
- `current/hotset.md` に再開用の短い温度がある。
- `current/scene.md` に場所、距離、見えているもの、行動余地がある。
- `current/event_card.md` に visible problem、first concrete action、handles 2-4、relationship stake、if ignored、next visible change がある。
- `current/relationship_overview.md` に距離感、信頼、警戒、興味、誤解や保留がある。
- `current/decision_index.md` に約束、拒否、保留、解決済みの索引がある。
- `lilia/main/profile.md` に初回から演じるための具体物、職能、生活、反応、矛盾、禁忌がある。
- `lilia/main/voice.md` に呼び方、声の基準、第一反応の方向がある。
- `lilia/main/state.md` に第一反応がある。
- `lilia/main/relationship.md` に境界線と未確定の期待がある。
- `lilia/main/relationship.md` に intimacy stage、consent stage、boundary state の初期扱いがある。
- `lilia/main/memory.md` に初期記憶がある。
- `lilia/main/beliefs.md` に誤解や思い込みの余地がある。

## 7. Resume Smoke Test

`new -> first scene -> save -> resume` を手動で確認する時は、`docs/RESUME_SMOKE_TEST.md` を正本とする。
このprompt内では詳細な検証手順を抱え込まず、resume 1ターン目の前に、hotset / scene / event_card / voice / relationship / memory / beliefs の必要箇所で温度、入口、巻き戻り、aftercare抜けだけを短く見る。

## 8. 禁止事項

- すべての会話をmemoryに詰め込まない。
- `hotset.md`を正本として扱わない。
- LILIAの人格の核を短期的な会話で上書きしない。
- ユーザーの希望だけで関係変化を確定しない。
- 例文やテンプレ語彙に引っ張られて保存内容を作らない。
- `event_card`を事件処理だけで終わらせない。
- `event_card`を抽象的な違和感だけで保存しない。
- `story/story_deck.md` と `current/event_card.md` を同じ内容にしない。
- `archive/beats`に雑多なログを入れすぎない。
- style系を通常resumeの毎回必読にしない。
- resumeで呼び方、声、距離感、約束、拒否、誤解、境界線を初期化しない。
- 親密scene後のaftercare、保留、拒否、境界確認を無かったことにしない。
- 参照小説本文や固有文体を保存内容や次回本文へ流用しない。
- root `style/defaults/` を全場面で総読みしない。
- 官能表現そのものを削り、親密場面を清潔すぎる文体へ薄めない。
