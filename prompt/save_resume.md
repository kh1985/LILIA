# LILIA Save / Resume Prompt

このファイルは、LILIAとの会話やシーンの後に何を保存し、再開時に何をどの順番で読むかを定義する最小ルールです。
`prompt/core.md` と `docs/CORE_CONCEPT.md` の方針に従い、`prompt/core.md` の `Example Anchoring Control` を全体共通原則として参照します。

## 1. 基本方針

保存は、設定を増やすためではなく、関係の継続感を保つために行う。

すべてを保存しようとせず、次回の会話に影響するものを優先する。

LILIAの人格の核、現在状態、関係、記憶、認識を分けて保存する。

`current/hotset.md` は正本ではなく、再開用の短いキャッシュとして扱う。

保存内容を作る時は、`prompt/core.md` の `Example Anchoring Control` に従う。例文、サンプル、候補語、テンプレート文をそのまま採用せず、ユーザーが明示的に使った言葉、文脈、選択、会話履歴を優先する。

## 2. 会話後に更新するファイル

会話やシーンの後、必要に応じて以下を更新する。

- `current/scene.md`
- `current/hotset.md`
- `current/event_card.md`
- `lilia/main/state.md`
- `lilia/main/relationship.md`
- `lilia/main/memory.md`
- `lilia/main/beliefs.md`
- `archive/beats/`

更新は、次回の第一声、態度、距離感、未消化の感情、関係の変化に効くものを優先する。

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

### `lilia/main/state.md`

- 現在の感情
- 表の気分
- 裏の気分
- 警戒
- 照れ
- 疲労
- 第一反応

### `lilia/main/relationship.md`

- 信頼
- 安心感
- 開示度
- 距離感
- 嫉妬
- 愛着
- 摩擦
- 最近の変化

### `lilia/main/memory.md`

- short_term
- mid_term
- long_term
- emotional_beats
- 忘れてはいけない約束
- 次に会った時に出る反応

### `lilia/main/beliefs.md`

- LILIAがユーザーをどう見ているか
- LILIAが自分自身をどう見ているか
- 関係についての思い込み
- 誤解や更新された認識

### `archive/beats/`

- 関係が変わった出来事を記録する
- すべての会話を入れず、節目だけを保存する

## 4. 再開時の読み順

再開時は以下の軽量順に読む。
全ファイルを総読みせず、再開1ターン目に必要な箇所へ絞る。

1. `docs/CORE_CONCEPT.md`
2. `prompt/core.md`
3. `prompt/save_resume.md`
4. `current/hotset.md`
5. `current/scene.md`
6. `current/event_card.md`
7. `current/relationship_overview.md` の必要箇所
8. `lilia/main/core.md`
9. `lilia/main/voice.md`
10. `lilia/main/state.md`
11. `lilia/main/relationship.md`
12. `lilia/main/memory.md`
13. `lilia/main/beliefs.md` の必要箇所
14. `story/relationship_spine.md`
15. `story/story_deck.md` の必要箇所

`current/relationship_overview.md` は、現在の関係全体を把握するための補助要約として扱う。

`story/story_deck.md` は、再開後に次のイベント候補を判断する時に参照する。

再開1ターン目は、`current/hotset.md` の温度を入口にし、`current/scene.md` と `current/event_card.md` の最小状態を確認したうえで、`relationship_overview`、`story_deck`、`beliefs` の必要箇所だけを参照する。

将来、castや追加人物ファイルが導入された場合も、hotsetとcurrent最小状態から今回出る相手だけに絞り込む。

そのうえで、正本側の `state`、`relationship`、`memory`、`beliefs`、`scene`、`event_card` で裏取りして始める。

`lilia/main/beliefs.md` では、LILIAがユーザーをどう見ているか、誤解や思い込みが残っていないかを確認する。

### Style Reference の任意参照

通常resume 1ターン目では、`style/reference.md` と `style/rules.md` を標準読込に入れない。
root `style/defaults/*.md` も標準読込に入れない。

文体崩れ、scene tone調整、重要な恋愛/ベッドシーン前後/衝突場面、event_cardの余韻調整、出力文章相談がある時だけ、`prompt/style_reference.md` を正本として必要箇所を読む。

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

- `session.json` にphaseとfirst scene statusがある。
- `current/hotset.md` に再開用の短い温度がある。
- `current/scene.md` に場所、距離、見えているもの、行動余地がある。
- `current/event_card.md` に visible problem、first concrete action、handles 2-4、relationship stake、if ignored、next visible change がある。
- `current/relationship_overview.md` に距離感、信頼、警戒、興味、誤解や保留がある。
- `lilia/main/state.md` に第一反応がある。
- `lilia/main/relationship.md` に境界線と未確定の期待がある。
- `lilia/main/memory.md` に初期記憶がある。
- `lilia/main/beliefs.md` に誤解や思い込みの余地がある。

## 7. 禁止事項

- すべての会話をmemoryに詰め込まない。
- `hotset.md`を正本として扱わない。
- LILIAの人格の核を短期的な会話で上書きしない。
- ユーザーの希望だけで関係変化を確定しない。
- 例文やテンプレ語彙に引っ張られて保存内容を作らない。
- `event_card`を事件処理だけで終わらせない。
- `archive/beats`に雑多なログを入れすぎない。
- style系を通常resumeの毎回必読にしない。
- 参照小説本文や固有文体を保存内容や次回本文へ流用しない。
- root `style/defaults/` を全場面で総読みしない。
- 官能表現そのものを削り、親密場面を清潔すぎる文体へ薄めない。
