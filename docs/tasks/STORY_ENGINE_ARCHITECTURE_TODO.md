# LILIA Story Engine Architecture TODO

## 1. Purpose

この文書は、`docs/visual/lilia_story_engine_map.md` の図を前提に、LILIAで実現したい体験に対して現在のアーキテクチャが妥当か、どこに何を足し引きすべきかを整理するTODOである。

正式仕様ではなく、実装前の設計判断メモとして扱う。

## 2. Current Assessment

現時点の評価:

- 現在のフローは、LILIAの目的に対して大枠では妥当。
- LILIAは単発の小説生成ではなく、ユーザー入力、状態変化、関係変化、次の入口が循環するAI TRPG型体験である。
- 現在の図はその循環を表せている。
- ただし、図にある全要素を同じ重さで実装してはいけない。
- 中核要素と補助要素を分ける必要がある。

## 3. Architecture Goal

LILIAで実現したいこと:

```txt
プレイヤーが自由入力する。
ヒロインが人格・記憶・関係をもって反応する。
出来事や会話によって関係・認識・記憶が変わる。
その変化が次の場面や次の反応に効く。
長期的に「その人との物語」が育つ。
```

## 4. Core Architecture

中核として残すもの:

- Player Orientation
- Active Event Card
- Dramatic Question
- Choice Tension
- Irreversible Delta
- Next Curiosity
- Save / Resume Loop

補助要素:

- Want / Fear / Misbelief
- Dialogue Collision
- Desire / Obstacle / Cost
- Causality detail
- Story Function diagnostic tags

棚・候補:

- story_deck
- candidate hook
- background hook

保存先:

- memory
- relationship
- beliefs
- voice

## 5. Event Card Minimum Core

`current/event_card.md` に実装する場合の最小中核候補:

- Player-Facing Problem
- Dramatic Question
- Active Hook / First Concrete Action
- Choice Tension
- Relationship Stake
- Irreversible Delta
- Next Curiosity

注意:

Want / Fear / Misbelief、Dialogue Collision、Desire / Obstacle / Cost、Causality detail は重要だが、毎回すべてを同じ重さで必須欄にすると重くなる。

まずは補助情報として扱い、必要なsceneでのみ前景化する。

## 6. Additions Needed

今の図に追加・明確化すべきもの:

### Knowledge Boundary

- プレイヤーが知っていること
- 作中人物が推測していること
- GMだけが隠してよいこと
- 判断材料として隠してはいけないこと

### Save Mode Gate

Play Mode中の保存候補と、Save Mode / apply-turn による確定保存を分ける。

```txt
Play Mode Output
→ State Update Candidates
→ Save Mode / apply-turn
→ memory / relationship / beliefs / voice
```

### Priority / Arbitration

複数状態ファイルが矛盾または重複した場合の優先順位を整理する。

目安:

1. `current/scene.md`
2. `current/event_card.md`
3. `relationship / memory / beliefs / voice`
4. `hotset`
5. `story_deck`

## 7. Things To Avoid

避けること:

- 状態ファイルを増やせば良くなる、という発想
- story_deck の素材を promotion なしに本文へ出すこと
- Player Orientation を説明過多にすること
- Causality を重いプロットエンジンにすること
- 15機能を固定プロット順として扱うこと
- Want / Fear / Misbelief を毎ターン全部前景化すること
- 1ターンで複数の主題を出すこと

## 8. Open Questions

今後判断すること:

- event_card の必須項目はどこまで増やすか
- Want / Fear / Misbelief を profile / relationship_spine / event_card のどこに置くか
- Knowledge Boundary を event_card に含めるか、別ファイルにするか
- Next Curiosity と Next Hook の責務をどう分けるか
- Story Function 15 tags を図では階段から診断タグ群に変えるか
- AI Playtest Judge にどこまで評価させるか

## 9. Next Actions

実装タスク:

- [ ] Mermaid図に Save Mode Gate を追加する
- [ ] Mermaid図に Knowledge Boundary を追加する
- [ ] Mermaid図に Three Hook Spine の3軸吸着を追加する
- [ ] 15機能の図を Ladder ではなく Diagnostic Tags / Toolbox として見せる案を検討する
- [ ] event_card の最小中核7項目を確定する
- [ ] `docs/EVENT_CARD_PLAYABILITY.md` への反映案を作る
- [ ] `templates/session/current/event_card.md` への反映案を作る
- [ ] `tools/session/document_generator.py` の group_a prompt 更新案を作る
- [ ] `tools/session/document_validator.py` の軽量チェック案を作る
- [ ] AI Playtest Judge に追加する観点を整理する

## 10. Decision Log

現時点の判断:

- 現在のアーキテクチャは、LILIAの目的に対して大枠では妥当。
- ただし、図にある要素をすべて同じ重さで実装しない。
- 中核は Player Orientation / Active Event Card / Dramatic Question / Choice Tension / Irreversible Delta / Next Curiosity / Save-Resume Loop。
- 面白さ不足はアーキテクチャ全体の誤りではなく、event_card と Play Mode における「変化を生む中核項目」の不足として扱う。
- 次の一手は、図を増やすことではなく event_card の最小中核を決めること。

## Completion Conditions

- `docs/tasks/STORY_ENGINE_ARCHITECTURE_TODO.md` が作成されている。
- `docs/visual/lilia_story_engine_map.md` との関係が明記されている。
- 現在のアーキテクチャ評価が残っている。
- 中核 / 補助 / 棚 / 保存先が分けられている。
- 次にやることがチェックリスト化されている。
- 正式仕様ではなく設計TODOとして読める。
