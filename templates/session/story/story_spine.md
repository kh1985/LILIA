# Story Spine

物語の固めの背骨。relationship_spine.md（関係の方向・温度）とは別に、
「この話が何の話で、どう進むか」を保持する GM 内部資料。

固定プロットではなく、AI が次の入口を判断する材料。
本文・台詞・ヒロインの認知に直接出さない。

## Main Question

この話が問うこと（1行）。

newgame の Q&A から AI が生成する。プレイ進行で書き換え可能。

形式の例:
- 「Xという生き方をしてきた者が、Yと出会えるか」
- 「Aは自分のBに気づけるか」
- 「2人の関係はCを越えられるか」

(未設定)

## Reveal Ladder

謎・関係・真相の段階開示。3〜5段階。
各段階は「進んだら何が見える/分かるか」と現在の状態を持つ。

状態:
- pending: まだ見えていない
- in_progress: 部分的に開示中（1〜2 scene かけて見え始めている）
- revealed: 開示済み
- closed: 開示後、関係の中で消化された要素

newgame で初期3段階を仕込む。残りは進行に応じて Save Mode で追加。
段階を一気に2つ進めない。1段ごとに2-3 scene かけて咀嚼する。

1. [pending] (未設定)
2. [pending] (未設定)
3. [pending] (未設定)

## Background Truth (GM only)

この話の真相。本文には出さない。
Reveal Ladder の各段階で、この真相の一部が表に出るように撒く。
references/story_pattern_stock.md の P3（Ghost）と直結。

newgame で最低限の骨だけ生成。詳細は進行に応じて足す。
kk が Save Mode で直接書き加えてもよい。

(未設定)

## Pressure Direction

ユーザーが放置・脱線・無視した時、世界側で動くこと。3項目程度。

状態:
- standing: 未発火、待機中
- fired: 発火済み、効果が現れた
- recurring: 繰り返し効くタイプ

全部同時に動かさない。1-3 scene 後に小さく1つ返す。

1. [standing] (未設定)
2. [standing] (未設定)
3. [standing] (未設定)

## Prize（任意）

関係者全員が欲する1つのもの。物・人・概念どれでもよい。
references/story_structure_stock.md のシノビガミ秘密構造から。

これが関係の核になる場合のみ設定する。空欄でも可。

(未設定)

## Heroine Tie

この話がヒロインの何に刺さるか。
profile.md / relationship_spine.md から抽出して具体化する。

- 生活: (未設定)
- 秘密: (未設定)
- 境界: (未設定)
- 感情: (未設定)

## if ignored

放置時、1-3 scene 以内に小さく返ること。Pressure Direction の小型版。

newgame で 1〜3 項目を仕込む。

1. (未設定)
2. (未設定)
3. (未設定)

## Drift Guard

物語が霧にならないための具体物。
Background Truth と紐づく物的手がかり（references/story_pattern_stock.md P3 の観察可能な形）。

形式: `物名 — Background Truth の何に紐づくか`

newgame で初期の手がかりを撒く。進行で追加。

(未設定)
