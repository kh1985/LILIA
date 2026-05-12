# Knowledge Boundary Implementation Design

## 1. Purpose

この文書は、LILIAのPlay Mode / Save Mode / resumeをまたいで、GMが「誰が何を知っているか」を管理するための実装設計である。

発端は `session_003` の初回sceneで、ヒロイン側とGM側はUSBの不自然さを把握していたが、プレイヤーが開始時点で何を知っているかが本文に十分変換されず、プレイヤーから見ると「話が見えない」状態になったこと。

これは初回sceneだけの問題ではない。継続プレイ中も、真相、観察、推測、共有済み情報、未開示情報をGMが裁定し続ける必要がある。

## 2. Architecture Name

この層を以下の名前で扱う。

```txt
Knowledge Boundary Gate
```

役割:

- 真相は隠す。
- 判断材料は隠さない。
- ヒロインには、ヒロインが知り得ることだけを言わせる。
- プレイヤーには、今動くための足場を渡す。
- ターンで知識が変わったら Save Mode / apply-turn で更新する。

## 3. Managed Information

最低限、GMは以下を分けて把握する。

- GMしか知り得ない情報
- プレイヤーが判断のために知っているべき情報
- プレイヤーが現在知っている情報
- ヒロインが知っている情報
- ヒロインが誤解・推測している情報
- プレイヤーとヒロインが共有済みの情報
- その場で観察できる情報
- まだ誰も確定していない不明情報
- 次に明かしてよい条件
- まだ本文にも台詞にも出してはいけない情報
- このターンで新しく判明した情報
- 情報の出どころ
- 情報の確度

## 4. File Responsibilities

### `current/knowledge_state.md`

知識台帳の正本。各項目に `key / value / fictional_status / source / known_to / acquired_at / weight / notes` を持たせる。

主な分類:

- `known_to: [GM]`: GMだけが扱う情報
- `known_to: [protagonist]`: プレイヤーが現在知っている情報
- `known_to: [heroine]`: ヒロインが知っている情報
- `known_to: [heroine, protagonist]`: 共有済み情報
- `fictional_status: observable`: その場で観察可能な情報
- `fictional_status: gm_only`: 段階開示する真相
- `fictional_status: meta-system`: フィクション内に出してはいけない運用情報

### `current/scene.md`

現在地、見えているもの、直前の出来事、プレイヤーの足場を持つ。

今後追加・強化したい項目:

- 主人公がなぜここにいるか
- 主人公がこのscene開始時点で知っていること
- 本文冒頭で必ず見せる前提

### `current/event_card.md`

今この場で触れる入口と、選択が何に作用するかを持つ。

今後追加・強化したい項目:

- Player-Facing Problem
- Player Needed Orientation
- Inciting Incident
- Reveal Control
- Do Not Reveal Yet

### `story_spine.md`

GMだけが持つ真相、Reveal Ladder、長期の背景圧を持つ。Play Mode本文やヒロイン台詞へ直接漏らさない。

### `lilia/main/beliefs.md`

ヒロインの仮説、誤解、疑いを持つ。事実ではなく、ヒロイン側の受け取りとして扱う。

## 5. Runtime Loop

### Newgame / first_scene_ready

```txt
answers.md
↓
character.yaml / profile.md
↓
story_spine / relationship_spine
↓
current/scene.md / current/event_card.md / current/knowledge_state.md
↓
Knowledge Boundary Gate
↓
first_scene_ready
```

first_scene_ready前に確認すること:

- 主人公がなぜこのsceneにいるか。
- 主人公が開始時点で何を知っているか。
- ヒロインが開始時点で何を知っているか。
- GMだけが隠す真相と、プレイヤーに見せる判断材料が分かれているか。

### Play Mode前

GMは `knowledge_state.md` を読み、以下を裁定する。

- この情報は誰が知っているか。
- ヒロインの台詞に出してよいか。
- 地の文として観察可能か。
- プレイヤーが判断する足場は足りているか。
- 真相を隠したまま、何を見せれば進めるか。

Play Mode生成直前は `ReplyContextBundle` を入口にする。

- `Heroine Reply Context`: ヒロインが知覚・記憶・推測・誤解できる情報だけを本文の主材料にする。
- `Pressure Context`: GM内部圧を、観測可能な状況、沈黙、所作、台詞、返せる入口へ変換する。
- `GM Control Context`: event_card、scene function、relationship stake、hidden truth、story_spine、next hookをGM専用に分離する。

`tools/session/reply_context.py` は `tools/session/knowledge_boundary.py` を再利用し、保存更新やmigrationは行わない。

### Play Mode本文

本文は以下を守る。

- GMだけの真相を説明しない。
- ヒロインが知らない情報を台詞にしない。
- プレイヤーが知らない前提で判断を迫らない。
- 必要なら短く地の文で足場を出す。

### Save Mode / apply-turn

このターンで変化した知識を保存候補にする。

- プレイヤーが新しく知ったこと
- ヒロインが新しく知ったこと
- 共有済みに昇格したこと
- ヒロインの仮説・誤解が変わったこと
- Reveal Ladderから開示済みに変わったこと
- まだGMだけに残すこと

### Resume

resume時は、最新の `knowledge_state.md` を使って、同じ知識境界から再開する。
raw session filesを同列に読む前に `ReplyContextBundle` を読み、Heroine Reply ContextをGM Control Contextより前に置く。

## 6. Immediate Implementation

今すぐ実装する最小単位:

```txt
tools/session/knowledge_boundary.py
```

責務:

- `knowledge_state.md` のYAML blockを読む。
- 知識項目を正規化する。
- GM / protagonist / heroine / shared / observable / do-not-reveal / suspicion に分類する。
- `gm_only` や `meta-system` が漏れていないか軽量検査する。
- validatorや将来のPlay Mode prompt builderから共通利用できる形にする。

今すぐやらないこと:

- Play Mode本文生成の全面変更
- apply-turn merge logicの大改修
- 新しい大きな状態ファイルの追加
- すべてのevent_card項目の一括必須化

Template / Design 追加反映:

- `templates/session/current/scene.md` に Player Orientation を追加済み。
- `templates/session/current/event_card.md` に Player-Facing Entrance と Knowledge Boundary / Reveal Control を追加済み。
- `templates/session/knowledge_state.md` の説明を Shared Facts / Observable Now / Reveal Conditions / Do Not Reveal Yet / Newly Learned This Turn / source・evidence・certainty の読み方に拡張済み。
- 既存の `knowledge_state.md` YAML items block shape は維持する。

## 7. Proposed Python API

```python
from tools.session.knowledge_boundary import assess_knowledge_boundary

report = assess_knowledge_boundary(knowledge_state_md)

report.errors
report.warnings
report.boundary.player_known
report.boundary.heroine_known
report.boundary.shared_facts
report.boundary.gm_truth
report.boundary.do_not_reveal_yet
```

## 8. Validator Integration

`tools/session/document_validator.py` は、既存の構文検査に加えて以下を検査する。

- `gm_only` は `known_to: [GM]` だけにする。
- `meta-system` は `known_to: [GM]` だけにする。
- `shared` は原則 `protagonist` と `heroine` の両方を含む。
- 必須フィールドの欠落を検出する。

最初は漏洩リスクの高いものをerrorにし、設計密度の不足はwarningに留める。

## 9. Future Template Updates

次の実装単位で検討する。

- `apply-turn` の実merge logicで knowledge_state の昇格・追加をより明示的に扱う。最小実装済み。
- AI Playtest Judge に、プレイヤーが判断材料なしで迫られていないかを見る観点を追加する。最小実装済み。

## 10. Decision

- Knowledge Boundary Gate は初回sceneだけではなく、継続プレイ全体のGM制御レイヤーである。
- `knowledge_state.md` は既に入口として存在するため、新しい巨大なMarkdownを増やすより、まず既存ファイルを強くする。
- `tools/session/knowledge_boundary.py` は将来ではなく今作る。理由は、分類と漏洩検査は小さく実装でき、以後のgenerator / validator / Play Mode / apply-turnの共通基盤になるため。
- ただし、本文生成や保存更新の全面変更はこの設計書だけでは行わない。まず分類・検査の基盤を置く。

## 11. Next Actions

- [x] `docs/tasks/KNOWLEDGE_BOUNDARY_IMPLEMENTATION_DESIGN.md` を作成する。
- [x] `tools/session/knowledge_boundary.py` を追加する。
- [x] `tools/session/document_validator.py` から軽量検査を呼ぶ。
- [x] unit testで分類と漏洩検査を確認する。
- [x] `current/scene.md` templateに Player Orientation を追加する。
- [x] `current/event_card.md` templateに Player-Facing Entrance / Knowledge Boundary / Reveal Control を追加する。
- [x] `knowledge_state.md` template説明に Shared Facts / Observable Now / Reveal Conditions / Do Not Reveal Yet / Newly Learned This Turn を追加する。
- [x] downstream Group A promptを更新する。
- [x] first_scene_ready前validatorに Player Orientation不足チェックを追加する。
- [x] Save Mode / apply-turn promptで knowledge_state 更新候補を強化する。
- [x] apply-turn merge logicで knowledge_state 昇格・追加をより明示的に扱う。
- [x] AI Playtest Judge に Knowledge Boundary / Player Orientation 観点を追加する。
