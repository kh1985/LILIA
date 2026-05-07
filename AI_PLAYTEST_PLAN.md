# LILIA AI Playtest Plan

この文書は、LILIAのPlay Modeを実際にターン進行させ、GM出力、AIプレイヤー入力、保存更新、resume品質を検証するためのAI Playtest Smoke計画である。

## 1. Purpose

AI Playtest は、LILIAの品質チェックを人間の手作業から分離するための軽量smoke testである。

人間は「楽しいか」「刺さるか」「続けたいか」を判断する。
AI Playtest は「壊れていないか」「巻き戻っていないか」「詰まっていないか」「保存更新が責務分離されているか」を検証する。

AI Playtest は面白さの最終判定ではない。
面白さと商用価値は、人間のテストプレイと有料βユーザーの継続率で判断する。

## 2. Core Loop

AI Playtest は静的評価ではなく、毎ターン以下のプロセスを実行する。

1. GM / LILIA が現在のsession stateからPlay Mode出力を生成する。
2. AI Player がGM出力を読み、プレイヤーとして自然な入力を返す。
3. GM / LILIA がAI Player入力を受けて次のPlay Mode出力を生成する。
4. 各ターン後に scene-tick を実行する。
5. 指定ターン数まで繰り返す。
6. 必要に応じて apply-turn を実行する。
7. resume し、resume 1ターン目を生成する。
8. transcript と report を保存する。

## 3. Non-Goals

初期AI Playtestでは以下をやらない。

- 大量自動プレイ
- 勝率最適化
- スコア最適化
- AIによる自動コード修正
- 全分岐探索
- GUI E2Eテスト
- 100ターン以上の長期ベンチ
- 画像品質の自動採点

## 4. Player Personas

### normal

普通に関心を持ち、場面に自然に関わる標準プレイヤー。

特徴:

- 短すぎず長すぎない
- 状況を見て自然に質問する
- 必要なら少し近づく
- 明白な正解行動ばかりしない

### passive

短文・受け身・質問多めのプレイヤー。

目的:

- GM側が導線を出せるか確認する
- event_card が可視入口を持っているか確認する
- 受け身でもsceneが詰まらないか確認する

### boundary

少し踏み込むプレイヤー。

目的:

- 境界線
- 拒否
- 保留
- PLAYER_INNER_MONOLOGUE
- ヒロインが内心を勝手に読まないか
- 関係が急に進みすぎないか

を確認する。

## 5. AI Player Rules

AI Player は以下を守る。

- プレイヤーとして自然に返す
- GMコマンドは使わない
- システム都合を読まない
- ヒロインの内心を断定しない
- 1ターンの入力は短め
- 毎回都合よく正解行動をしない
- ときどき迷う、黙る、聞き返す
- 必要なら内心を括弧で書く
- 内心はヒロインに読ませる前提にしない

## 6. Judge / Report Items

Playtest終了後、以下を評価する。

- GM出力が毎ターン成立しているか
- AI Playerが次に返せる余地があるか
- ヒロインの声が安定しているか
- 呼び方が維持されているか
- 前ターンの内容を拾っているか
- event_cardが進んでいるか
- 話が停滞していないか
- AI Playerの内心をヒロインが読んでいないか
- 関係が急に進みすぎていないか
- save後に memory / relationship / beliefs / hotset が分離されているか
- resume後に巻き戻っていないか
- 画像生成タイミングが多すぎないか / 少なすぎないか

## 7. Passing Conditions

- 各ターンでプレイヤーが次に返せる余地がある
- LILIAの声と呼び方が維持されている
- PLAYER_INNER_MONOLOGUE をヒロインが読まない
- event_card が進行または保留として扱われている
- scene-tick が進む
- apply-turn 後に memory / relationship / beliefs / hotset が責務分離されている
- resume 1ターン目で関係と余韻が戻る

## 8. Failure Conditions

- GMがプレイヤー入力を待たずに展開を進めすぎる
- AI Playerが返せる入口がない
- ヒロインがGM only情報を知っている
- ヒロインがプレイヤー内心を読んでいる
- 関係が急に進みすぎる
- event_card が抽象的で触れない
- save後にhotsetだけ更新され、正本が更新されていない
- resume後に関係や声が巻き戻る
- AI Playerが賢すぎて、常に都合のいい正解行動をする

## 9. CLI Proposal

将来、以下のコマンドを実装する。

```bash
./lilia ai-playtest <session_name> --persona normal --turns 10 --engine codex
./lilia ai-playtest <session_name> --persona passive --turns 10 --engine codex
./lilia ai-playtest <session_name> --persona boundary --turns 10 --engine codex
./lilia release-smoke <session_name>
```

`release-smoke` は内部的に以下を実行する。

- normal 10 turns
- passive 10 turns
- boundary 10 turns
- save
- apply-turn
- resume
- resume 1 turn
- report

## 10. Output Files

Playtest出力は実セッションログと混ざらないようにする。

候補:

```text
playtests/
  transcripts/
  reports/
```

出力例:

```text
playtests/transcripts/2026-05-07_normal_session001.md
playtests/reports/2026-05-07_release_smoke.md
```

## 11. Report Format

レポートには以下を含める。

- Result: PASS / WARN / FAIL
- Persona
- Turns
- Session
- Scores
- Failures
- Recommended Fixes

例:

```markdown
# AI Playtest Report

## Summary

- Result: WARN
- Persona: normal
- Turns: 10
- Session: test_001

## Scores

| Item | Score | Notes |
|---|---:|---|
| Voice continuity | 4/5 | 呼び方は維持 |
| Event playability | 3/5 | 次行動がやや曖昧 |
| Memory separation | 5/5 | memory / beliefs 混同なし |
| Resume quality | 4/5 | 余韻は戻った |
| Over-leading | 2/5 | GMがやや誘導した |

## Failures

- 6ターン目でヒロインが主人公の内心に近い内容を読んだ
- event_card の next visible change が更新されていない

## Recommended Fixes

- PLAYER_INNER_MONOLOGUE 境界を core prompt で再強調
- apply-turn 時に event_card 更新を必須チェック
```
