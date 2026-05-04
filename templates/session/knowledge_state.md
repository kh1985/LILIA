# Knowledge State

このファイルは「事実とその経路」を保持する。
「感情の跡」は memory.md、「真相」は story_spine.md の Background Truth、
「約束・拒否・保留」は decision_index.md にある。役割を混ぜない。

## このファイルの目的

各知識項目について、以下を管理する:
- 事実そのもの（value）
- 知識主体（誰が知っているか）
- 経路（どう知ったか）
- 状態（fictional_status）
- 重み（記憶としての重さ）

これを GM が参照することで、scene 生成時に「この情報を使っていいか」を判断できる。

## ステータス（fictional_status）の4種類

各項目はこの4つのどれかを持つ。

### meta
プレイヤー由来のメタ情報。フィクション内ではまだ開示されていない。
scene 内で開示装置（自己紹介、伝票、名札、観察など）を経由するまで、
ヒロイン・NPC は知らない扱いとする。

例: protagonist.md の呼ばれ方（Q6 で答えた呼称）

### observable
視覚的・物理的に観察可能。ヒロインがその場で見れば自然に認識できる。
初対面でも使ってよい。

例: 主人公の身長、服装、性別、現在の表情

### shared
scene の中で開示された情報。双方知っている共有事実。

例: scene 1 で主人公が「便利屋です」と言った後の職業情報

### gm_only
GM だけが知っている真相。ヒロイン本人も知らない可能性がある。
story_spine.md の Background Truth と紐づく。

例: ヒロインの過去の傷の真相、ヒロインも言語化していない自己の核

## 各項目の構造

各知識項目は以下のフィールドを持つ:

```yaml
- key: <一意な識別子>
  value: <事実そのもの>
  fictional_status: meta | observable | shared | gm_only
  source: <情報源>
    - protagonist  # Q&A 由来
    - heroine_self_disclosure  # ヒロインが自己開示
    - protagonist_self_disclosure  # 主人公が自己開示
    - observation  # 観察により獲得
    - inferred  # 推論で獲得（弱い）
    - story_spine  # GM 真相由来
  known_to: [<知っている主体のリスト>]
    - 主体名: protagonist, heroine, GM, NPC_<名前>
  acquired_at: <scene 番号 or "pre_play">
  weight: low | medium | high
  notes: <自由記述、開示条件や注意点>
```

## 初期化（newgame 時）

newgame で以下を生成する。詳細は prompt/newgame.md を参照。

### protagonist 由来項目（Q6/Q7 から）

- 主人公の呼ばれ方 → meta、source: protagonist、known_to: [protagonist]
- 主人公の性別 → observable、source: protagonist、known_to: [protagonist, heroine（初対面で観察）]
- 主人公の身長感 → observable、同上
- 主人公の体格 → observable、同上
- 主人公の服装傾向 → observable、同上

### profile 由来項目（Q1/Q3/Q4 から）

- ヒロインの名前 → shared（自己紹介で開示される前提）、source: heroine_self_disclosure、known_to: [heroine]、acquired_at: pre_play
  - 注: 初対面で開示されると `acquired_at: scene_1` になる
- ヒロインの職業・立場 → 同上
- ヒロインの描写の縛り（物的アンカー） → observable、known_to: [heroine, protagonist]、acquired_at: scene_1

### story_spine 由来項目（Q5 から）

- Background Truth の各要素 → gm_only、source: story_spine、known_to: [GM]
- Reveal Ladder の各段階 → gm_only 初期、開示時に shared へ昇格

### Session 制約（Q8 から）

- Session Constraints → meta-system、known_to: [GM]、フィクション内に出さない

## 知識項目テンプレート

```yaml
items:
  # ===== protagonist 由来 =====
  - key: protagonist_call_name
    value: (newgame で Q6 から)
    fictional_status: meta
    source: protagonist
    known_to: [protagonist]
    acquired_at: pre_play
    weight: medium
    notes: "ヒロインが知る経路がない時点では使わない。自己紹介、伝票、名札、紹介などの装置を経由する"

  - key: protagonist_gender
    value: (newgame で Q7 から)
    fictional_status: observable
    source: protagonist
    known_to: [protagonist]  # ヒロインは観察で初対面から認識
    acquired_at: pre_play
    weight: low
    notes: "視覚的に観察可能"

  - key: protagonist_height
    value: (newgame で Q7 から)
    fictional_status: observable
    source: protagonist
    known_to: [protagonist]
    acquired_at: pre_play
    weight: low

  - key: protagonist_build
    value: (newgame で Q7 から)
    fictional_status: observable
    source: protagonist
    known_to: [protagonist]
    acquired_at: pre_play
    weight: low

  - key: protagonist_style
    value: (newgame で Q7 から)
    fictional_status: observable
    source: protagonist
    known_to: [protagonist]
    acquired_at: pre_play
    weight: low

  # ===== heroine 自己情報 =====
  - key: heroine_name
    value: (newgame で Q1 から)
    fictional_status: meta  # 自己紹介前は meta
    source: heroine_self_disclosure
    known_to: [heroine]
    acquired_at: pre_play
    weight: high
    notes: "初対面で自己紹介すると shared に昇格"

  - key: heroine_occupation
    value: (newgame で Q1 から)
    fictional_status: meta
    source: heroine_self_disclosure
    known_to: [heroine]
    acquired_at: pre_play
    weight: medium

  - key: heroine_visual_anchor
    value: (newgame で Q3 から、または profile から抽出)
    fictional_status: observable
    source: observation
    known_to: [heroine, protagonist]  # 視覚観察可能
    acquired_at: scene_1
    weight: medium
    notes: "Wave 1 の描写の縛り、Wave 6 で毎回繰り返される"

  # ===== gm 真相 =====
  - key: heroine_background_truth
    value: (newgame で Q5 から、story_spine.md と同期)
    fictional_status: gm_only
    source: story_spine
    known_to: [GM]
    acquired_at: pre_play
    weight: high
    notes: "Reveal Ladder で段階的に開示される"

  # ===== セッション制約 =====
  - key: session_constraints
    value: (newgame で Q8 から)
    fictional_status: meta-system
    source: protagonist
    known_to: [GM]
    acquired_at: pre_play
    weight: low
    notes: "GM 内部参照のみ。フィクション内に出さない"
```

## 更新タイミング

Save Mode で以下のいずれかが起きた時、turn_update.md に書く。

### fictional_status の昇格

- `meta` → `shared`: ヒロインまたは主人公が scene 内で開示した
- `meta` → `observable`: 装置（伝票、名札など）経由で観察可能になった
- `gm_only` → `shared`: Reveal Ladder の段階が revealed になった

### 新規項目の追加

- scene 内で新しい事実が開示された
- 観察により新しい情報が獲得された

### known_to の追加

- 新しい主体（NPC など）が情報を知った

### 重みの変化

- 同じ情報が繰り返し言及されて重みが上がる
- 時間経過で薄れたいときは重みを下げる（任意）

### turn_update.md の書き方

```markdown
## knowledge_state

### 昇格
- protagonist_call_name: meta → shared
  - 開示経路: 主人公が「かねこです」と自己紹介した
  - acquired_at: scene_1
  - 知った主体: heroine

### 新規
- protagonist_occupation
  - value: 便利屋
  - fictional_status: shared
  - source: protagonist_self_disclosure
  - known_to: [protagonist, heroine]
  - acquired_at: scene_1
  - weight: medium
```

### apply-turn でのマージ

apply-turn は turn_update.md の `## knowledge_state` セクションを読み、
current/knowledge_state.md の対応する項目を更新する。

ロジック:
- 既存項目の状態変化 → ステータス更新
- 新規項目 → items に追加
- known_to の追加 → リストに append（重複排除）

## 連動仕様

knowledge_state.md は他のファイルと**役割を分担しつつ連動**する。
役割が重複しないように設計されている。

### memory.md との関係

| ファイル | 持つ情報 |
|---------|---------|
| knowledge_state.md | 事実、経路、誰が知ってるか、状態 |
| memory.md | 感情の跡、印象、心情 |

例（構造説明のみ。literal として真似しないこと）:
- knowledge_state: `主人公が便利屋 (shared, scene_1, weight: medium)`
- memory.md: `主人公が「[職業/役割]です」と言った時、[ヒロインA]はその話題に少し慎重になった（emotional_beat）`

両者は**同じ scene の異なる側面**を保持する。連動は AI がプロンプト時に両方読むことで成立する。

### echo との関係

| ファイル | 持つ情報 |
|---------|---------|
| knowledge_state.md | 事実の状態（shared か否かなど） |
| echo (memory.md 内) | 直前 scene の余韻、第一反応 |

例（構造説明のみ。literal として真似しないこと）:
- knowledge_state: `主人公が便利屋 (shared)`
- echo: `[共有された事実]に、[ヒロインA]が小さく反応した。距離が少し変わった`

knowledge_state は事実、echo は反応。連動は AI 判断。

### decision_index.md との関係

| ファイル | 持つ情報 |
|---------|---------|
| knowledge_state.md | 「事実」が共有されているか |
| decision_index.md | 「約束・拒否・保留」 |

例（構造説明のみ。literal として真似しないこと）:
- knowledge_state: `カフェで会う約束 (shared, scene_2, weight: high)`
- decision_index: `約束: 明日カフェで会う / state: active / 期限: 明日`

knowledge_state は「双方が知っている事実」、decision_index は「未来への拘束力」。
両方持つ場合あり（重複ではなく相補）。

### story_spine.md との関係

| ファイル | 持つ情報 |
|---------|---------|
| knowledge_state.md | 各段階の現在の fictional_status |
| story_spine.md Reveal Ladder | 段階定義そのもの |
| story_spine.md Background Truth | gm_only の真相 |

連動:
- Reveal Ladder の段階が `revealed` に進んだら、knowledge_state の対応項目も `gm_only` → `shared` になる
- Save Mode で両方を同時更新する（重複入力を許容）

### protagonist.md との関係

| ファイル | 持つ情報 |
|---------|---------|
| knowledge_state.md | protagonist 由来項目の fictional_status |
| protagonist.md | プレイヤー由来の身体情報・呼称・制約（不変の元データ） |

protagonist.md は newgame で生成された後、原則変わらない（kk が手動編集する場合を除く）。
fictional_status の変化は knowledge_state.md でのみ追跡する。

### profile.md との関係

profile.md の `context` セクション（current_situation 等）は GM 内部の事前想定。
Wave 8 で **GM-internal pre-play assumption** として扱う（後述の実装3）。
knowledge_state.md には含めない（profile に残す）。
