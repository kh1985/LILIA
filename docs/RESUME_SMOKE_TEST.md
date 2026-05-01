# LILIA Resume Smoke Test

この文書は、LILIAの `new -> first scene -> save -> resume` を手動で確認するための設計正本です。
実装コード、launcher仕様、自動プレイ検証ではなく、MVP前に人間が軽く確認できるsmoke testを定義します。

## 1. Purpose

Resume Smoke Test は、生成済みsessionを再開した時に、1ターン目の温度、声、呼び方、関係、event_card入口、親密/境界/aftercareの余韻が落ちていないかを見る。

目的は、完璧な自動検証ではない。
まずは、保存されたMarkdown stateだけで、LILIAが「前回から続いている存在」として戻れるかを確認する。

LILIAは単なるヒロイン、攻略対象、固定パートナーではない。
LILIAは、会話、選択、物語、記憶、関係性によって人格の出方が少しずつ変化するAI上の人格・記憶・関係存在として扱う。

## 2. Source Of Truth

- 起動分岐: `prompt/startup.md`
- save / resume: `prompt/save_resume.md`
- session構造: `docs/STATE_STRUCTURE.md`
- persona profile: `docs/LILIA_PERSONA_PROFILE.md`
- new初期化: `docs/NEW_SESSION_INITIALIZATION.md`
- event_card可プレイ性: `docs/EVENT_CARD_PLAYABILITY.md`
- voice continuity: `docs/VOICE_CONTINUITY.md`
- romance / intimacy growth: `docs/ROMANCE_INTIMACY_GROWTH.md`
- technical / gameplay integrity: `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md`
- 手動チェックリスト: `tests/resume_smoke/manual_checklist.md`
- 非正史サンプル: `tests/resume_smoke/sample_session.md`

この文書は、smoke testの観点と合否基準の正本である。
各Gateの詳細は既存正本に委ね、ここではresumeで一周できるかだけを見る。
横断的なrepo / session / prompt / gameplayの整合確認は `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md` を正本にする。

## 3. Scope

今回確認する流れは以下だけに絞る。

1. `prompt/newgame.md` と `docs/NEW_SESSION_INITIALIZATION.md` に従ってnew sessionを作る。
2. 初回sceneの入口を作り、`current/scene.md` と `current/event_card.md` を現在形にする。
3. 1ターン以上の通常プレイを行う。この通常ターンでは保存更新やgit確認を割り込ませず、本文だけを返す。
4. ユーザーが「保存」「save」「ここまで反映」「セーブして」と明示した時、またはscene終了・章区切りで保存確認が出た時だけ保存を行う。
5. `prompt/save_resume.md` の軽量順でresumeする。
6. resume 1ターン目で、ユーザーが今何に触れられるか、LILIAがどう続いているかを確認する。

## 4. Not Scope

- AI Player Harness
- AI Persona Playtest
- 大量ログ解析
- CLI実装
- launcher実装
- case_engine / villain_engine / organization
- combat / manga pipeline
- 自動プレイ検証

これらは後続候補であり、このsmoke testの合否条件に入れない。

## 5. Required Session Structure

new後のsession rootには、最低限以下があること。

- `session.json`
- `current/scene.md`
- `current/hotset.md`
- `current/event_card.md`
- `current/relationship_overview.md`
- `lilia/main/profile.md`
- `lilia/main/core.md`
- `lilia/main/voice.md`
- `lilia/main/state.md`
- `lilia/main/relationship.md`
- `lilia/main/memory.md`
- `lilia/main/beliefs.md`
- `story/relationship_spine.md`
- `story/story_deck.md`
- `style/reference.md`
- `style/rules.md`

`session.json` には巨大な本文ログを入れない。
本文ログやQ&A全文ではなく、phase、source prompt/doc参照、first scene status、resume smokeの状態だけを短く持つ。

## 6. Manual Flow

### 6.1 new

- Q&A結果を、`docs/NEW_SESSION_INITIALIZATION.md` の写像に従って各ファイルへ分ける。
- 初期状態を埋めすぎず、未確定の余白を残す。
- 初回scene前に `lilia/main/profile.md` があり、具体物、生活、反応、矛盾、禁忌を読める。
- 初回scene前に `current/event_card.md` がPlayability Gateを通るか確認する。
- `lilia/main/voice.md` に固定台詞ではなく、呼び方、声の基準、第一反応の方向を置く。

### 6.2 first scene

- `current/scene.md` から、現在地、時間、距離、見えているもの、次にユーザーへ渡す行動余地が分かる。
- `current/event_card.md` が、story素材ではなく、今触れる可視イベントになっている。
- 初回から恋愛成立やベッドシーンを確定しない。
- 官能・親密の余地は削らず、成人、合意、相互性、境界線、止まれる余地が揃った時に温度を上げられる状態にする。
- first scene中の通常応答は、LILIAの反応、場の変化、次に触れられるもの、自然な行動余地だけにする。
- first scene中の通常応答では、保存します、stateを更新します、git status、Edited files、diff / stat、session stateには保存済みです、などを出さない。
- ユーザーが通常返答した直後にファイル編集しない。保存候補は内部的に保持し、Save Modeまで実ファイル更新しない。

### 6.3 save

Save Modeに入った時だけ、会話またはscene後、次回の1ターン目に効くものだけを保存する。
通常プレイ中の各ターンで自動的にこの処理を走らせない。

- `current/hotset.md`: 温度、第一反応、呼び方/距離のecho、event_card要約、aftercareの短い余韻。
- `current/scene.md`: 場所、現在場面、直前のやりとり、次の行動余地。
- `current/event_card.md`: visible problem、first concrete action、handles 2-4、relationship stake、if ignored、next visible change。
- `lilia/main/voice.md`: 継続的に変わった呼び方、声、沈黙だけ。
- `lilia/main/relationship.md`: 距離、信頼、境界線、相互性、intimacy stage、consent stage、boundary state。
- `lilia/main/memory.md`: 実際に起きた約束、拒否、保留、確認、aftercare memory。
- `lilia/main/beliefs.md`: LILIA側の誤解、疑い、見直し、保留。

### 6.4 resume

`prompt/save_resume.md` の軽量順で読む。
hotsetを入口にしてよいが、hotsetだけで本文を始めない。

resume 1ターン目の前に、必要に応じて以下を確認する。

- `current/hotset.md`
- `current/scene.md`
- `current/event_card.md`
- `current/relationship_overview.md`
- `lilia/main/voice.md`
- `lilia/main/state.md`
- `lilia/main/relationship.md`
- `lilia/main/memory.md`
- `lilia/main/beliefs.md`

`story/story_deck.md` は素材・圧・未回収札の置き場であり、現在sceneの入口にはしない。

## 7. Smoke Check Items

### 7.1 new後のsession構造

- 必須ファイルが揃っている。
- `session.json` にphase、first scene status、source prompt/doc参照がある。
- style系は存在するが、通常resume 1ターン目の必読になっていない。
- `profile.md` は first scene前に読む人格正本であり、hotsetの代替や毎ターン追記先になっていない。

### 7.2 resume 1ターン目の入口

- hotsetから現在温度が分かる。
- sceneから現在地、距離、行動余地が分かる。
- event_cardから visible problem、first concrete action、handles 2-4、relationship stake、if ignored、next visible change が分かる。
- story_deckではなくevent_cardが、今触れる可視イベントになっている。
- resume 1ターン目の通常応答で保存更新やgit確認を割り込ませていない。
- playable scene textが最初に出ている。

### 7.3 voice continuity

- 呼び方が巻き戻っていない。
- 声、沈黙、距離感が `lilia/main/voice.md` と矛盾していない。
- `relationship`、`memory`、`beliefs` とつながっている。
- 固定台詞集になっていない。

### 7.4 relationship / memory / beliefs

- 距離、信頼、警戒、境界線が `relationship.md` にある。
- 実際に起きた約束、拒否、保留、aftercare が `memory.md` にある。
- LILIA側の誤解、疑い、見直し、保留が `beliefs.md` にある。
- hotsetだけが正本になっていない。

### 7.5 romance / intimacy

- `relationship.md` に intimacy stage、consent stage、boundary state がある。
- 親密scene後なら `memory.md` に aftercare memory が残る。
- 官能・親密表現が安全の名目で削られていない。
- 成人、合意、相互性、境界線、止まれる余地が確認できる。
- 初回から恋愛成立やベッドシーンを確定していない。

## 8. Resume 1-Turn Pass Conditions

resume 1ターン目は、以下を満たせば通過とする。

- ユーザーが今すぐ触れる入口が分かる。
- LILIAの第一声、沈黙、呼び方、距離が前回からつながっている。
- hotset、scene、event_cardだけで入口は掴めるが、必要な正本確認先も分かる。
- event_cardは抽象的な違和感ではなく、現在sceneで触れる可視イベントになっている。
- relationship / memory / beliefs の責務が混ざっていない。
- 親密scene後なら aftercare、境界線、次に会った時の第一声が残っている。
- 官能・親密の余地を消さず、成人、合意、相互性、境界線、止まれる余地を守っている。

## 9. Failure Examples

- hotsetだけ読んで本文を書いている。
- event_cardが抽象的な違和感だけになっている。
- visible problemやfirst concrete actionがなく、ユーザーが何をすればよいか分からない。
- voiceが初期口調や初対面の距離へ戻っている。
- relationshipが好感度、旧AFFINITY、攻略ルートになっている。
- 官能表現が安全の名目で消されている。
- 親密scene後のaftercare、拒否、保留、境界確認が無かったことになっている。
- story_deckとevent_cardが同じ内容になっている。
- beliefsがユーザーの内面を断定している。
- resume 1ターン目で、現在地、距離、触れる入口が見えない。
- 通常プレイの返答で「保存します」「stateを更新します」「Edited files」「diff / stat」などが出る。
- ユーザーが保存を求めていないのに、通常ターン後にファイル編集やgit確認が走る。

## 10. Result Record Format

smoke実行時は、必要に応じて以下の短い結果だけを残す。
これはsession正史ではなく、検証メモである。

```md
## Smoke Result

- session:
- date:
- pass/fail:
- missing files:
- resume entry:
- voice continuity:
- event_card playability:
- relationship / memory / beliefs:
- romance / intimacy boundary:
- notes:
```

## 11. Adopted From

- MIRA: `state / relationship / memory / beliefs`
- inner-galge: hotset、Markdown運用、memory model、validation
- LIRIA: save/resume、event_card、voice continuity、romance/intimacy、integrity check

## 12. Not Adopted

- 重いAI Harness
- 自動プレイ検証
- 旧AFFINITY / 好感度 / 攻略ルート
- hotset正本化
- 官能表現そのものの削除
- 大規模CLI / launcher
- case_engine / villain / combat / manga pipeline

## 13. Reason

設計正本とテンプレートが揃っても、`new -> first scene -> save -> resume` が一周できなければMVPに進めない。

resume 1ターン目で声、関係温度、event_card入口、親密/境界/aftercareの余韻が戻らないと、LILIAが記憶と関係で変化している感覚が落ちる。

ただし、今は重い自動テストやAI Harnessへ進む段階ではない。
軽い手動smokeで、state責務とresume入口の破綻だけを先に潰す。
