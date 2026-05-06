# Opening Scene Generation

この文書は、`references/opening_pattern_stock.md` を初回scene生成へ接続する運用フローの正本である。
冒頭本文そのものではなく、Q&A素材から `current/scene.md` の `Opening Plan` を作り、`prompt/opening_scene.md` がそれを読んで8〜15文の冒頭へ変換するまでを扱う。

## Purpose

Opening Pattern Stock は、冒頭で「何から見せるか」「プレイヤーをどこへ立たせるか」を決めるための構造棚である。

目的は、作品名やパターン名を本文へ出すことではない。
Q&A、profile、story_spine、relationship_spine から、初回sceneの入口だけを短く設計し、プレイヤーが訳の分からないまま濃い描写へ放り込まれる事故を避ける。

## Flow

```text
Q&A Q1-Q9
  |
  v
character YAML / profile.md
  |
  v
story_spine.md / relationship_spine.md
  |
  v
tools.session.document_generator group_a
  |
  +-- reads references/opening_pattern_stock.md (sanitized)
  |
  v
current/scene.md
  |
  +-- ## Opening Plan
      selected_patterns
      selection_reason
      must_include
      4_jobs
      clarity_anchors
      opening_caveats
  |
  v
prompt/opening_scene.md
  |
  v
first scene text (8-15 sentences)
```

## Opening Plan Selection

`Opening Plan` は AI が Q&A と生成済み state を解釈して選ぶ。
コードでパターンを決め打ちしない。

必須ルール:

- A群（O1-O4）から1つ。
- D群（O13-O15）から1つ。
- B群（O5-O8）またはC群（O9-O12）から最大1つ。
- 同じ群から2つ選ばない。
- 3つ以上の混在を避ける。

Q9 に「停滞を避けたい」がある場合、O9 / O10 / O14 は優先候補になる。
Q5 に過去の傷や秘密が強い場合、O5 / O11 は候補になる。
Q6 が偶然の出会いや発見を含む場合、O13 / O14 は候補になる。

## Four Jobs

冒頭は以下の4つの仕事のうち最低2つを果たす。
ただし Orientation は必須である。

- Hook: 次の文を読みたくなる引っかかり。
- Orientation: 主人公がどこにいて、何者かの手がかり。
- Agency Placement: プレイヤーが観察者 / 介入者 / 当事者のどれかを取れる状態。
- Unresolved Hook: 次のターンへ持ち越す問い。

これらは説明しない。
本文の場所、物、音、行動、沈黙として配置する。

## Clarity Anchors

`clarity_anchors` は、分かりやすさを説明調にせず担保するための足場である。

- `protagonist_role`: 主人公の職業・立場が分かる描写。
- `protagonist_purpose`: なぜ今その場にいるかが分かる描写。
- `location_function`: 固有名詞だけでなく、何の場所かが分かる描写。
- `heroine_relation`: 主人公とLILIAの関係性が分かる手がかり。

悪い例:

```text
鴉ノ宿のガラス戸を細く叩いていた。
```

良い例:

```text
オカルトショップ『鴉ノ宿』のガラス戸を、雨が細く叩いていた。
```

## O14 Safety Rule

O14（救助・発見）を選んだ場合、冒頭は必ず発見の瞬間から始める。
助けた後、介抱済み、毛布を掛けた後から始めない。

主人公の職業、なぜそこにいるか、初対面かどうかを3〜5文以内に読める形で置く。
濃いヒロイン描写より先に、血、靴、音、落ちた小物などの物的手がかりを置く。

## Validation

`tools/session/document_validator.py` は `Opening Plan` を soft warning として検査する。
第一版では hard fail にしない。
既存セッションに `## Opening Plan` が無くても resume を壊さないためである。

検査するもの:

- `selected_patterns` が O1〜O15 の範囲内。
- A群1つ + D群1つを満たす。
- B/C群は最大1つ。
- `4_jobs` の4項目が埋まっている。
- `must_include` が1件以上ある。
- `clarity_anchors` の4項目が埋まっている。

## 採用元

- inner-galge: reference棚を内部ノートとして読み、本文へ作品名やパターン名を出さない運用。
- LIRIA: session stateに現在の入口をMarkdownで保存し、resume時の温度と行動余地を維持する運用。
- LILIA既存方針: Example Anchoring Control、Event Card Playability、Voice Continuity。

## 採用しないもの

- パターン選択をPythonコードで決め打ちすること。
- 冒頭本文に O1〜O15 の名前を出すこと。
- 既存セッションに `Opening Plan` を必須化して resume を壊すこと。
- 冒頭で世界設定を長く説明すること。
