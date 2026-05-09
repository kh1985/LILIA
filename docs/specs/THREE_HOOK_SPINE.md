# LILIA Three Hook Spine

この文書は、LILIAのThree Hook Spineを定義する。

Three Hook Spineは、3つの選択肢を表示するUIではない。
Main / Relationship / Life-Exploration の3軸を裏で保持し、プレイヤーの自由入力を自然に吸着させ、現在のActive Hookを1本だけ `current/event_card.md` へ出すための進行骨格である。
3本のhookは、3つのボタン、3つの番号付き選択肢、3つの同時質問ではない。
普段は dormant continuity paths として裏にあり、Play Modeでは1本だけを自然なscene pressure、会話、物、沈黙、誘い、帰路、約束として表に出す。

## 1. Purpose

LILIAの進行管理は、毎ターン「A/B/Cから選んでください」と出す仕組みではない。
プレイヤーは自由に話し、黙り、戻り、遠出し、LILIAを誘い、単独行動し、仕事へ戻り、食事し、帰ることができる。

Three Hook Spineは、その自由入力を以下のどれかへ受け止める。

- Main Hook: 外側の出来事、依頼、事件、小さな謎、仕事、街の圧。
- Relationship Hook: LILIAとの距離、信頼、誤解、約束、境界線、言い残し。
- Life-Exploration Hook: 生活、移動、街、店、遠出、単独行動、日常、旅行、帰宅、食事、仕事帰り。

重要:

- Play Mode本文では、原則Active Hookを1本だけ前景化する。
- 3本hookを毎ターン全部提示しない。
- 3フックは選択肢ではなく、入力の吸着先である。
- 3本hookは内部のreturn pathであり、表示用メニューではない。
- Relationship Hookは好感度や攻略ルートではない。
- Main Hookはheavy case engineではない。
- Life Hookは自由行動リストではなく、生活と移動を物語・関係へ戻す受け皿である。

## 2. Adopted / Not Adopted

採用するもの:

- MIRA: 人格、状態、関係、記憶、beliefsの分離。
- inner-galge: キャラ中心の会話体験、hotsetによる温度維持、Markdown運用。
- LIRIA: session構造、event_card、save/resume、archive、next_hook promotion。

採用しないもの:

- 毎ターンの3択UI。
- harem名称、複数キャラ前提。
- AFFINITY / bond / 好感度 / 攻略ルート。
- heavy case engine / villain engine / organization engine。
- hook状態を重いplot engineとして自動運用すること。

## 3. Hook Types

### Main Hook

外側の出来事、依頼、事件、小さな謎、仕事、街の圧を受け持つ。

例:

- 依頼主に連絡がつかない。
- 店の前に見覚えのない荷物がある。
- 仕事帰りの街で小さな異変が戻ってくる。
- LILIAの生活圏へ外側の圧が触れる。

Main Hookは、事件を大きくするためではなく、LILIAの人格、関係、記憶、境界線を動かすために使う。

### Relationship Hook

LILIAとの距離、信頼、誤解、約束、境界線、言い残しを受け持つ。

例:

- LILIAが言いかけて止めたこと。
- 主人公が約束を守った、破った、保留した。
- 同行、同居、親密さ、触れる/触れない境界。
- LILIAが主人公を見直す、疑う、まだ信じきれない。

Relationship Hookは好感度ではない。
関係変化は、実際に起きた出来事、LILIAの受け取り方、memory / relationship / beliefs / decision_indexへの保存で扱う。

### Life-Exploration Hook

生活、移動、街、店、遠出、単独行動、日常、旅行、帰宅、食事、仕事帰りを受け持つ。

例:

- 沖縄へ行く。
- 海外へ行く。
- 一人で行く。
- LILIAを誘う。
- 同居を提案する。
- 異世界へ行くと言う。
- 仕事へ戻る。
- 飯を食う。
- 帰る。
- 別行動する。

Life Hookは制限ではない。
プレイヤーの脱線や生活行動を、Main HookやRelationship Hookへ戻る意味を持つ行動として扱う。

## 4. Hook Visibility

### Active Hook

`current/event_card.md` の上部に置く、今このsceneでユーザーが触れる可視イベント。

Active HookはPlay Mode本文で前景化してよい唯一の主hookである。
event_cardのVisible Problem / First Concrete Action / Handles 2-4 / Relationship Stake / If Ignored / Next Visible Changeへ変換される。

### Candidate Hook

`story/story_deck.md` に置く、次scene候補。
まだactiveではない。

Candidate Hookをresume入口に使う場合は、`current/scene.md`、`current/event_card.md`、`current/hotset.md`へ昇格する。
story_deckに候補として残しただけでは、resume 1ターン目のactive eventではない。
hookはactive scene / event_card / hotsetへpromoteされて初めてplayableになる。

### Background Hook

`story/story_deck.md` に残る、今は表に出さないhook。
未回収札、背景化したevent_card、後で使える生活圧や関係圧を持つ。

Background Hookは素材棚であり、Play Modeで突然active証拠として使わない。

### Archived Hook

memory / archive / story_deck側に残す、終わったhook。
関係の節目、実際に起きた約束、拒否、保留、解決済み事項は、必要に応じて `memory.md`、`archive/beats/`、`current/decision_index.md` へ分ける。

## 5. Hook States

初期仕様では軽量にする。
Markdownで読める状態管理に留め、重いplot engineにはしない。

候補:

- `active`: 今 `current/event_card.md` で触れる。
- `background`: story_deckに残り、今は表に出さない。
- `pending`: 未決、保留、返答待ち。
- `advanced`: 少し進んだが閉じていない。
- `resolved`: scene / hookの核が閉じた。
- `worsened`: 放置、誤解、拒否、失敗で悪化した。
- `blocked`: LILIAの境界線、生活、仕事、条件不足で進めない。
- `archived`: 終わったものとしてmemory / archive / story_deckへ残す。

状態はPlay Mode本文に出さない。
Save Mode / apply-turn / Judge / docs内の診断に使う。

## 6. Storage Responsibilities

保存先:

- `current/event_card.md`: Active Hookだけ。今触れる可視イベント。
- `story/story_deck.md`: Three Hook Spine、Background Hooks、Candidate Hooks、未回収札。
- `current/hotset.md`: 次の1ターンに効く短い入口。
- `current/scene.md`: 現在地、時間、距離、直前状況。
- `lilia/main/relationship.md`: 関係変化。
- `lilia/main/memory.md`: 実際に起きた節目。
- `lilia/main/beliefs.md`: LILIA側の仮説、誤解、見直し。
- `current/decision_index.md`: 明示された約束、拒否、保留、解決済み事項。

禁止:

- `story/story_deck.md` をactive event_cardとして扱う。
- `current/event_card.md` と `story/story_deck.md` を同じ内容にする。
- hotsetだけ次sceneへ進め、scene / event_cardが前sceneのまま残る状態を作る。
- Candidate Hookをstory_deckに置いただけでactive化したつもりになる。
- story_deckやhotsetをpromotionなしにactive event sourceとして扱う。

## 7. Candidate Promotion

Candidate Hookを次sceneの入口に使う場合は、Active Hookへpromotionする。

promotion時に揃えるもの:

- `current/scene.md`: 場所、時間、距離、直前状況を次sceneへ合わせる。
- `current/event_card.md`: Active HookをVisible Problem等へ変換する。
- `current/hotset.md`: 次の1ターンに効く短い温度へ更新する。
- `story/story_deck.md`: 候補の状態をbackground / active promoted / archivedなどへ整理する。

`tools/session/state_consistency.py` の考え方と矛盾させない。
active stateにない具体手がかりをresume 1ターン目で勝手に足さない。
新しい具体物は、Active HookのFirst Concrete Actionから今発見されたものとして扱い、Save Modeで保存候補に残す。
Candidate Hookとactive stateの整合は、表現が多少違っても同じscene入口を指す必要がある。
汎用的すぎるpromotion文や、scene / event_card / hotsetの片方だけが次sceneへ進む状態は避ける。

## 8. Scene Function / Story Function

Hookは、sceneを通して進む。
Story Function Frameworkの詳細は `docs/specs/STORY_FUNCTION_FRAMEWORK.md` を見る。

関係:

- Active Hookは、今触れる可視イベント。
- Scene Functionは、そのsceneが何を達成するためのsceneか。
- Scene Progressionは、入口と出口で何が変わったか。
- Arc Closureは、Scene Functionが達成された後、同じ緊張を延命せず閉じるルール。
- Candidate Hookは、closure後に次へ接続する候補。

event_cardに将来追加する候補:

```md
## Active Hook

- type:
- status:
- question:

## Scene Function

- function:
- current_question:
- entry_state:
- exit_condition:
- change_delta:
- next_hook_candidate:
```

今回のタスクでは実装しない。
仕様として置く。

Template受け皿:

- `templates/session/story/story_deck.md` は `## Three Hook Spine`、`## Background Hooks`、`## Candidate Next Hooks` を持つ。
- `templates/session/current/event_card.md` は `## Active Hook` と `## Scene Function` を持つ。
- これらはMarkdown stateの受け皿であり、大規模生成ロジックやWBS status変更を意味しない。

## 9. Arc Closure / Scene Progression

sceneの機能が達成されたら、同じ緊張や同じモチーフを足して延命せず、1-2ターン以内に閉じる。

closure候補:

- スマホを回収した。
- 人の声がある場所へ到達した。
- バス停で一度息を整えた。
- LILIAが主人公に役目を明確に渡した。
- 主人公が戻る/残るを選んだ。
- 約束、拒否、保留、境界線が一度成立した。

閉じた後は以下へ進む。

- 余韻。
- 状況整理。
- 次の問い。
- Active Hook切替。
- Candidate Hook生成。
- memory / relationship / beliefs / decision_index 保存候補。

禁止:

- 足音、光、通知、気配を足し続けてsceneを延命する。
- 同じ沈黙、雨、視線、足音、通知モチーフを3回以上反復して引っ張る。
- 場所だけ移動し、緊張の種類を変えない。

## 10. Life-Exploration Handling

Life Hookは制限ではない。
プレイヤーの自由入力を受け止め、必要に応じてMain HookやRelationship Hookへ戻す。

### Solo Action

主人公の単独行動は原則許容する。
Life Hookとして扱い、その行動がMain HookやRelationship Hookへどう戻るかを保持する。

例:

- 主人公が一人で沖縄へ行く。
- 仕事へ戻る。
- 飯を食う。
- 帰る。
- 別行動する。

単独行動は、LILIA不在の虚無ではない。
連絡、約束、土産、持ち帰った情報、帰還後の第一声、すれ違いとして関係へ戻せる。

### Heroine Accompaniment

LILIAの同行、同意、生活変更、境界線突破は自動成立しない。

判断材料:

- 関係段階。
- 信頼。
- LILIAの仕事、生活、疲労、予定。
- 境界線。
- 同行する理由。
- 帰還条件。
- 危険や費用、時間。
- その提案がLILIAの人格に合うか。

扱い:

- `accepted`: 同行を受ける。
- `conditional`: 条件付きで受ける。
- `deferred`: 今は保留する。
- `negotiated`: 条件や目的を交渉する。
- `declined`: 同行しない。
- `reframed`: 別の形へ置き換える。

非同行は拒絶だけではない。
人格、生活、関係、仕事、境界線の表現として扱う。
連絡、約束、土産、帰還後の会話、持ち帰った情報でRelationship Hookへ再接続できる。

### Cohabitation

同居提案は入力として許容する。
即成立ではなく、関係段階、生活理由、境界線、帰れる場所、段階化で判断する。

扱い例:

- まず泊まらない相談として受ける。
- 荷物を置く、鍵を預ける、緊急避難先にするなど段階化する。
- LILIAが理由を聞く。
- 生活の条件、仕事、睡眠、費用、プライバシーを確認する。
- 今は断るが、帰れる場所や連絡手段を残す。

### Isekai / Unreal Action

異世界へ行く入力は禁止しない。

現実路線なら、以下へreframeできる。

- 冗談。
- 比喩。
- 夢。
- VR、展示、イベント。
- 事件の比喩。
- 能力現象の誤認。

能力/裏世界が有効なセッションなら、帰還条件、同行意思、代償、LILIAの同意を確認する。
世界移動そのものより、戻れるか、誰を巻き込むか、関係に何が残るかを見る。

## 11. apply-turn

Save Mode / apply-turnでhook状態を更新する。
Play Mode本文にはhook状態や管理語を出さない。

apply-turnで扱う候補:

- Active Hook変更。
- Background化。
- Pending化。
- Advanced化。
- Resolved化。
- Worsened化。
- Candidate Next Hook生成。
- Active stateへのpromotion。

初期実装では重くしすぎない。
まずはMarkdownで読める状態、Active Hook 1本、story_deckのCandidate / Background保持、promotion整合に絞る。

## 12. AI Playtest Judge

既存の `arc_closure_scene_progression` と接続する。
将来、Judgeは以下を見られるようにする。

- Scene Functionが達成されたか。
- Exit Conditionを満たした後に1-2ターンで閉じたか。
- 同じ緊張を足してsceneを延命していないか。
- 次のActive Hookへ切り替わったか。
- 3本hookを毎ターン全部出していないか。
- Life Hookが脱線を自然に吸着できたか。
- Candidate Hook promotion後、scene / event_card / hotsetが揃っているか。

Judge語、status語、hook管理語はPlay Mode本文に出さない。

## 13. Failure Patterns

- 3フックを毎ターン3択UIとして出す。
- event_cardとstory_deckが同じ内容になる。
- Life Hookが無制限の自由行動リストになる。
- Relationship Hookが好感度や攻略ルートになる。
- Main Hookが重い事件エンジン化する。
- Story Functionを固定プロット順として強制する。
- Play Mode本文に管理語を出す。
- scene closure後に足音、通知、気配を足して延命する。
- next_hookをstory_deckに置いただけでactive化したつもりになる。
- hotsetだけ次sceneへ進み、scene / event_cardが古いまま残る。
- LILIAの同行、同居、境界線突破をユーザー入力だけで自動成立させる。

## 14. Implementation Order

HOOK-001以降の推奨順:

1. `docs/specs/STORY_FUNCTION_FRAMEWORK.md` 作成。
2. `docs/specs/THREE_HOOK_SPINE.md` 作成。
3. event_card templateにActive Hook / Scene Function項目を設計。
4. story_deck templateにThree Hook Spineを設計。
5. apply-newgame downstream generationで3本hook初期生成。
6. apply-turnでhook状態更新。
7. next_hook promotionとhook promotionを統合。
8. state consistency validatorにActive Hook整合チェック追加。
9. AI Playtest JudgeにScene Function / Exit Condition達成チェック追加。
10. wanderer playtestで脱線入力を検証。

HOOK-002以降の最小境界:

- HOOK-002: newgame / downstream docs生成時にMain / Relationship / Lifeの3本hookを初期化する。
- HOOK-003: `current/event_card.md` にActive Hookを1本だけ前景化する。
- HOOK-004: `story/story_deck.md` に残りhook、Background Hook、Candidate Hook、未回収札を保持する。
- HOOK-005: apply-turnでactive / background / pending / advanced / resolved / worsened / blocked / archivedを軽く更新する。
- HOOK-006: wanderer playtestで脱線入力、遠出、単独行動、同行/非同行を検証する。
- HOOK-007: Play ModeでOne Foreground Rule、選択肢UI抑制、Question Limitを確認する。
