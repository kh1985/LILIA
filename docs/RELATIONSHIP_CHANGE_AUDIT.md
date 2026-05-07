# LILIA Relationship Change Audit

この文書は、LILIAの関係変化が、数値パラメータではなく、実際に起きた出来事、LILIAの受け取り方、memory / relationship / beliefs / voice / hotset への保存によって自然に積み上がっているかを確認するための設計正本である。

## 1. Purpose

LILIAは、inner-galgeのAFFINITY / bondを初期βでは採用しない。

理由:

- LILIAは攻略対象との好感度進行ではなく、一人の人格を持つ女性との関係を描く。
- 関係の価値は、数値上昇ではなく、過程、思い出、保留、拒否、約束、境界線、生活、言い残しにある。
- プレイヤーには「あと何点で進む」ではなく、「あの出来事が関係に残った」と感じさせたい。
- LILIAの関係変化は、AIが人格フレームワーク、memory、relationship、beliefsを読んで自然に解釈することを優先する。

この文書は、関係を数値化するためのものではない。
関係変化に根拠があるか、早すぎないか、遅すぎないか、保存先が混ざっていないかを確認するための監査ルールである。

## 2. Core Policy

LILIAの関係変化は、以下の順で扱う。

1. 実際に何が起きたかを見る。
2. LILIAがそれをどう受け取ったかを見る。
3. その変化をどの保存先へ残すか決める。
4. 次回の第一声、距離、沈黙、呼び方、event_cardにどう戻るかを見る。
5. 変化が早すぎないか、遅すぎないかを確認する。

## 3. No AFFINITY / bond in Initial Beta

初期βでは以下を採用しない。

- AFFINITY
- bond
- 好感度
- 攻略ルート進行
- 数値による恋愛ロック解除
- 「一定値に達したので恋愛成立」という処理

ただし、inner-galge由来の知見は以下として再利用する。

- 段階ごとの声の違い
- CHINK / BARRIER 的な心の扉と防壁
- fixed memory
- 口調サンプル
- 関係の節目を保存する考え方
- AFFINITY 5後に深化タグ / hiddenベクトルを使うという思想

## 4. Hidden Vector Hold Policy

hidden深化ベクトルは初期βでは本格運用しない。

現時点での扱い:

- hiddenベクトルは将来の深化管理候補として保持する。
- 通常の関係進行メーターとしては使わない。
- Play Mode本文には軸名や数値を出さない。
- Save Modeでも、初期βでは原則として数値更新しない。
- 深い関係に到達したセッションで、関係の質を管理する必要が出た時に再検討する。

理由:

- inner-galgeではhiddenベクトルはAFFINITY 5到達後の運用だった。
- LILIAで最初からhiddenベクトルを動かすと、関係が数値ゲーム化しやすい。
- LILIAの初期価値は、数値ではなく記憶・声・距離・境界線の変化にある。

## 5. Text-Based Relationship State

関係変化は以下のファイルへ文字情報として残す。

| File | Responsibility |
|---|---|
| `lilia/main/memory.md` | 実際に起きた出来事、約束、拒否、保留、節目 |
| `lilia/main/relationship.md` | 距離、信頼、境界線、相互性、最近の変化 |
| `lilia/main/beliefs.md` | LILIA側の仮説、誤解、見直し、まだ疑っていること |
| `lilia/main/state.md` | 今だけの感情、照れ、迷い、警戒、疲労 |
| `lilia/main/voice.md` | 呼び方、沈黙、声の出方が継続的に変わった場合 |
| `current/hotset.md` | 次回1ターンに効く短い余韻、第一反応 |
| `current/event_card.md` | 今触れる可視イベント、言い残し、境界確認、次hook |

## 6. Audit Questions

Save Mode、AI Playtest、Integrity Auditでは以下を確認する。

### What Happened

- 実際に何が起きたか。
- ユーザーは何を言ったか、何をしたか。
- LILIAは何を見たか、何を聞いたか。
- 約束、拒否、保留、境界線、秘密共有、aftercareはあったか。

### How LILIA Received It

- LILIAはその出来事をどう受け取ったか。
- 信頼したのか、警戒したのか、保留したのか、誤解したのか。
- まだ確信していないことは何か。
- ユーザーの内面を断定していないか。

### What Remains

- memoryに残すべき実事実は何か。
- relationshipに残すべき距離や境界線の変化は何か。
- beliefsに残すべきLILIA側の仮説や誤解は何か。
- hotsetに戻すべき次回第一声や余韻は何か。

### Is the Change Too Fast

- 一回の優しい言葉だけで深い信頼や恋愛確定になっていないか。
- 初回sceneで過去・秘密・身体距離が進みすぎていないか。
- 拒否や保留を尊重しただけで即座に親密報酬化していないか。
- LILIAの人格、職業、過去、境界線に照らして早すぎないか。

### Is the Change Too Slow

- 重要な出来事があったのに、次回の声や距離に何も残っていないか。
- 約束を守った、拒否を尊重した、秘密を共有した、aftercareがあったのに、memory / relationship / beliefs が更新されていないか。
- 何度もsceneが進んでいるのに、関係の現在形が初期状態のままではないか。

## 7. Good Save Examples

### Waiting / Not Forcing

memory:

- ユーザーは、LILIAが話を止めた時に無理に聞き出さず、「待つ」と言った。

beliefs:

- LILIAは、ユーザーを「急かさない人かもしれない」と見直し始めている。ただし、まだ弱さを全部見せるほどではない。

relationship:

- 距離は少し柔らかくなった。次回は沈黙のあとに一言だけ本音が漏れる可能性がある。

hotset:

- 次回、LILIAは「昨日の、待つって言葉だけど」と切り出せる。

### Boundary Respected

memory:

- LILIAが触れないでと言った時、ユーザーはそれを尊重して距離を置いた。

relationship:

- 境界線が一度尊重された。信頼は少し戻ったが、すぐ親密化する段階ではない。

beliefs:

- LILIAは、ユーザーが踏み込むだけの人ではない可能性を持ち始めている。

### Overreach

memory:

- ユーザーは、LILIAが保留した話題をさらに聞こうとした。

relationship:

- 距離が一時的に硬くなった。境界線の再確認が必要。

beliefs:

- LILIAは、ユーザーが悪意ではなく焦りで踏み込んだ可能性を疑っている。

hotset:

- 次回、LILIAは同じ話題に入る前に「今日は、そこまで聞く？」と確認する。

## 8. Bad Save Examples

悪い:

relationship:

- LILIAはユーザーを深く信頼している。

理由:

- 何が起きたか分からない。
- なぜ信頼したか分からない。
- 次回どう出るか分からない。

悪い:

beliefs:

- ユーザーはLILIAのことを本気で愛している。

理由:

- ユーザーの内面を断定している。

悪い:

memory:

- LILIAはユーザーにすべてを話すことにした。

理由:

- 実際にsceneで起きていなければ捏造。
- 進行が早すぎる可能性が高い。

## 9. Failure Conditions

- 関係変化に出来事の根拠がない。
- 一回の行動で恋愛感情や信頼が急に深まりすぎる。
- 拒否や保留が報酬化されている。
- memoryに起きていないことが入っている。
- beliefsがユーザーの本心を断定している。
- relationshipが好感度説明になっている。
- hotsetだけ更新され、正本が更新されていない。
- 重要な出来事があったのに次回の声や距離に何も戻らない。
- hiddenベクトルを通常進行メーターとして動かしている。
- Play Modeに数値、タグ、内部軸が漏れている。

## 10. Passing Conditions

- 実際に起きた出来事がmemoryに残っている。
- LILIAの受け取り方がbeliefsに仮説として残っている。
- 距離・信頼・境界線の変化がrelationshipに理由つきで残っている。
- 次回の第一声や距離がhotsetに短く戻る。
- 関係変化が早すぎず、遅すぎず、人格と出来事に合っている。
- AFFINITY / bond を使わずに、関係の過程が読める。
- hiddenベクトルは初期βでは本格運用されていない。

## 11. Adopted From

- inner-galge: AFFINITY 5後に深化タグ / hiddenベクトルで関係の質を追う発想。
- LILIA: memory / relationship / beliefs / voice / state / hotset の責務分離。
- 花柳響氏の創作論: 物語は変化であり、sceneの入口と出口で何が変わったかを見る発想。

## 12. Not Adopted

- AFFINITY
- bond
- 好感度
- 攻略ルート
- 数値で恋愛成立を判定する運用
- hiddenベクトルを通常進行メーターとして使う運用
