# LILIA State Structure

この文書は、startup / new / resume が参照する最小の状態ファイル構造を定義する。
実装コードやlauncherの仕様ではなく、Markdown運用のための状態scaffoldである。

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

## 3. 最小ファイル構造

```text
session.json
current/
  scene.md
  hotset.md
  event_card.md
  relationship_overview.md
lilia/
  main/
    core.md
    voice.md
    state.md
    relationship.md
    memory.md
    beliefs.md
story/
  relationship_spine.md
  story_deck.md
style/
  reference.md
  rules.md
archive/
  logs/
  beats/
```

空ディレクトリ維持のためだけの `.gitkeep` は初期MVPでは採用しない。
`archive/logs/` と `archive/beats/` は、実体のあるログや節目が生まれた時にファイルとして保存する。

## 4. ファイル責務

### `current/hotset.md`

再開直後の温度を落とさないための短いキャッシュ。
正本ではなく、`scene`、`state`、`relationship`、`memory`、`beliefs`、`event_card` から次の1ターンに効く要点だけを抜く。
appendせず、必要に応じて短く上書きする。

### `current/scene.md`

今いる場所、今の場面、直前のやりとり、次に起きそうなことを保存する。
関係の全履歴や設定説明は入れない。

### `current/event_card.md`

今動いている出来事と、それがLILIAの感情・距離感・信頼・警戒・開示にどう刺さるかを保存する。
事件処理だけで終わらせない。

### `current/relationship_overview.md`

関係の現在形を軽く掴むための補助要約。
詳細な個別ログではなく、距離感、信頼、警戒、甘え、衝突、次に変化しそうな点を短く置く。

### `lilia/main/core.md`

LILIAの固有人格、価値観、弱さ、譲れないもの、変わってはいけない核を保存する。
短期的な会話都合で上書きしない。

### `lilia/main/voice.md`

口調、呼び方、照れ方、怒り方、甘え方、距離を置く時の出方を保存する。
例文の語彙をそのまま固定台詞にしない。

### `lilia/main/state.md`

直近のLILIAの感情と、次回の第一反応を保存する。
履歴ではなく現在向きの短い状態として扱い、古い状態を積み続けない。

### `lilia/main/relationship.md`

ユーザーとの関係の変化を保存する。
信頼、安心感、開示度、距離感、嫉妬、愛着、摩擦、最近の変化を扱う。

### `lilia/main/memory.md`

関係の継続感に効く記憶を保存する。
すべての会話を詰め込まず、次回の態度や第一声に影響する会話、選択、衝突、約束、沈黙、すれ違い、距離が変わった瞬間を優先する。

初期MVPでは独立した `memory/` 配下を作らず、`lilia/main/memory.md` を正本にする。
記憶が肥大化した場合は、後続で `memory/` の分割方針を設計し、`docs/HANDOFF.md` に反映する。

### `lilia/main/beliefs.md`

LILIAがユーザーをどう見ているか、自分自身をどう見ているか、関係について何を信じているかを保存する。
誤解や思い込みも、関係に効くなら消さずに記録する。

### `story/relationship_spine.md`

この関係で育ちそうなテーマ、LILIA側の課題、ユーザーに問うこと、関係が変化する方向を保存する。

### `story/story_deck.md`

物語の例文集ではなく、現在動いているstory素材、関係を揺らす圧、未回収札を整理する。
次イベント判断に必要なものだけを置く。

### `style/reference.md`

文章表現の参照を整理する。
参照小説や参照作品の本文コピーではなく、視点距離、描写密度、台詞密度、沈黙、余韻、温度、テンポなどの表現軸だけを保存する。
`story/story_deck.md` に置く物語素材や未回収札とは混ぜない。

### `style/rules.md`

このsessionで守る文章表現のルールを保存する。
LILIA固有の反応の出方、感覚チャンネル、禁止表現、避けたい癖、次に調整する点を短く置く。
通常resume 1ターン目の必読ではなく、文体崩れやscene tone調整が必要な時だけ読む。

## 5. new時に生成する想定ファイル

new時は `prompt/newgame.md` を正本として、`templates/session/` から以下を生成・初期化する。

- `session.json`
- `current/scene.md`
- `current/hotset.md`
- `current/event_card.md`
- `current/relationship_overview.md`
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

初回scene前には、`prompt/style_reference.md` の Light Story Reference Pass を軽く通し、Q&A結果から文章表現の表現軸を抽出する。
ただし、参照本文、台詞、人物配置、固有文体は保存しない。

## 6. resume時の読み方

resume時は `prompt/save_resume.md` を正本とする。
起動直後に全ファイルを総読みしない。

必ず入口として確認するもの:

- `current/hotset.md`
- `current/scene.md`
- `current/event_card.md`

必要箇所を確認するもの:

- `current/relationship_overview.md`
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

`style/reference.md` と `style/rules.md` は通常resume 1ターン目の標準読込には入れない。
文体崩れ、scene tone調整、重要な恋愛/衝突場面、出力文章相談がある時だけ、`prompt/style_reference.md` を正本として必要箇所を読む。

## 7. 採用元

- MIRA: `core / voice / state / relationship / memory / beliefs`
- inner-galge: キャラ中心 / hotset / Markdown運用
- LIRIA: session構造 / event_card / save/resume / archive
- style reference: LIRIAの story_reference / Light Story Reference Pass / style rules と inner-galgeの抽象化手順

## 8. 採用しなかったもの

- LILIAを単なるヒロイン、攻略対象、固定パートナーとして扱う設計
- 起動時・再開時に全ファイルを総読みする重い運用
- example文を本文生成へ流用する運用
- 参照小説本文や固有文体を保存・流用する運用
- `story/story_deck.md` に文体参照まで詰め込む運用
- 空ディレクトリ維持だけの `.gitkeep` 運用
- 初回から大規模なlauncher / CLIを書くこと
- 中身の薄い巨大テンプレートを大量に増やすこと
