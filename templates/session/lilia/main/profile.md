# LILIA Persona Profile

このファイルは、初回からLILIAを安定して演じるための人格正本です。
ただし、完成済み攻略キャラカードではありません。
関係で育った内容は core / voice / relationship / memory / beliefs へ分解して保存します。

## 基礎情報

name:
age:
occupation:
role:
appearance:
body:
outfit:

## appearance

Q2「ヒロインの見た目」から分解する。
hair_style と hair_color、body と outfit を混ぜない。

hair_style:
hair_color:
eye_color:
body:
outfit:
notes:

## tone

## personality

## values

## everyday anchors

Q3「描写の縛り」の物的アンカーを `よく触る物` と `初回sceneで使える具体物` の正本にする。
Q2 の目や体型描写をここへ入れない。

## memories

Q5「過去の傷の種」から、実際に過去として固定してよいものだけを入れる。

## contradictions

Q4「表と内の差」から、表 / 裏 / 矛盾を分ける。
生活設定や職業説明を「裏」に入れない。

## unspoken

## reactions

## forbidden

## context [GM-internal pre-play assumption]

⚠️ このセクションは **GM の事前想定**である。
- プレイ中はプレイヤーの入力で塗り替わる
- 主人公側の事実（持ち物、状況、行動）を**確定として扱わない**
- knowledge_state.md の fictional_status を優先して判断する
- 実プレイで成立した事実は scene.md / hotset / knowledge_state へ書く

## 描写の縛り

ヒロインが冒頭シーンで登場する時、複数の感覚チャンネルを横断して織り込む質感。
事件中心の場面でも、これがあると場にキャラが残る。

### Visual Identifier（必須・1〜2 項目）
ヒロインを毎回識別できる視覚的アンカー。髪、目、シルエットの特徴的要素。

- 視覚アンカー1: 未設定
- 視覚アンカー2 (optional): 未設定

### Sensual Two-Axis Design（必須）
ヒロインの色気・魅力を、相反する 2 つの軸で設計する。一面だけで描かず、矛盾と緊張で描く。

- 軸 A: 未設定（例: 「アンニュイ」「社交的な穏やかさ」「凛とした静けさ」など）
- 軸 B: 未設定（例: 「勝ち気」「操作的な鋭さ」「身体に残る経験の重み」など）

### Manifestation Anchors（5〜7 項目）
上記二軸が、身体・服装・仕草・匂い・声・距離のどれかで具体的に表れる例。
複数の感覚チャンネルを横断する。視覚だけに偏らない。

- アンカー1（軸 A）: 未設定
- アンカー2（軸 B）: 未設定
- アンカー3（軸 A または B）: 未設定
- アンカー4（軸 A または B）: 未設定
- アンカー5（軸 A または B）: 未設定
- アンカー6 (optional): 未設定
- アンカー7 (optional): 未設定

### Restraint Guideline（必須）
色気は雑な露出やフェティッシュ列挙で描かない。
「いやらしくない。だが目が離せない」を基準にする。
ヒロイン本人が無頓着な側面、見せない努力をしている側面、矛盾の同居がある側面、を選ぶ。

- 抑制ライン: 未設定（例: 「本人は胸元の存在感を強調する服を選んでいない」「色気として押してくる匂いではない」など）

注: 抽象語（優しい、強い、エロい）ではなく、具体物（持ち物、香り、声の質、視線の癖、立ち方）で書く。
profile 生成時に character YAML から抽出する。LILIA 側で恣意的に増やさない。

## fixed memory

## 5層構造 / Self-Understanding

注: Layer 3/4/5 は scene 生成時に `prompt/core.md` の Character Layer Check で参照される。
枠を空にせず、生活・行動・反応で具体的に埋める。形容詞ではなく行動で書く。

## voice by relationship stage

## 人格設計

## Relationship Progression

## Multi-Relationship / Jealousy Profile

## Ability / Intimacy Resonance

## Deepening Tags

注: タグ解放は `relationship.md` の深化ベクトルが閾値に達した時にだけ候補になる。
Save Modeでだけ評価する。攻略チェックリストとして順番に埋めない。
詳細は `docs/GROWTH_UPDATE_LOOP.md` を参照。

## Do Not Predefine
