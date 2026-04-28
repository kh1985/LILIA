# LILIA Style Reference Layer

このファイルは、LILIA全体で共有するStyle Layerの入口です。
参照小説や参照作品の本文を保存する場所ではなく、場面ごとの表現技法を選ぶための参照棚です。

セッションごとの抽出結果は、生成されたsessionルート内の `style/reference.md` と `style/rules.md` に保存します。
共通の場面別defaultsは、このroot `style/defaults/` 配下に置きます。

## 基本方針

- 作家名や作品名は、文体命令ではなく内部用の技法棚として扱う。
- 「〇〇風に書く」ではなく、視点距離、描写密度、沈黙、余韻、温度、テンポへ分解する。
- 参照本文、台詞、人物配置、展開順、固有文体は保存しない。
- `prompt/core.md` の `Example Anchoring Control` を必ず守る。
- `story/story_deck.md` には文体参照を混ぜない。

## 読み込み方針

通常resume 1ターン目では、root `style/defaults/` もsession `style/` も標準読込に入れない。

Style Layerを読むのは、以下の場合だけにする。

- 文体が崩れている
- 初回scene前のLight Story Reference Passを行う
- 重要なロマンス、衝突、危機、喪失、静かな関係変化を扱う
- scene toneや視点距離を調整したい
- ユーザーが文章表現や参照作品について相談している

読むdefaultsは原則1つ、多くても2つまでにする。
全defaultsの総読みはしない。

## Defaults Catalog

- `style/defaults/romance.md`: 親密さ、距離、合意、境界線、照れ、触れない時間。
- `style/defaults/tension.md`: 危機、衝突、圧、能力違和感、情報の段階開示。
- `style/defaults/warmth.md`: 日常、食事、短い会話、不器用な気遣い、安心の回復。
- `style/defaults/loss.md`: 喪失、不在、返事のなさ、残された物、続く日常。
- `style/defaults/quiet.md`: 沈黙、内省、歩く速度、手元の物、光と時間。
- `style/defaults/landscape.md`: 場所、天候、音の不在、色、影、生活の足場。

## 変換手順

1. 今の場面で動かしたい関係温度を一行で言う。
2. 必要なdefaultsを1つ選ぶ。迷う場合は読まない。
3. defaultsから本文ではなく、技法名と調整軸だけを取る。
4. `lilia/main/core.md`、`voice.md`、`state.md`、`relationship.md`、`memory.md`、`beliefs.md` に照らす。
5. 現在の場所、距離、沈黙、第一反応、言い残しへ変換する。
6. 出力前に、参照元の台詞、場面運び、人物配置、固有文体が混ざっていないか確認する。

## 禁止事項

- 参照小説本文の長い引用を保存しない。
- 作家や作品の固有文体を直接模倣しない。
- 例文を本文生成へ流用しない。
- LILIAを攻略対象、報酬、所有物として扱う表現にしない。
- ユーザーの内面や欲望を断定しない。
- style情報を `story/story_deck.md` に詰め込まない。
- resume時にstyle系を毎回必読にしない。
