# LILIA Resume Smoke Manual Checklist

このチェックリストは `docs/RESUME_SMOKE_TEST.md` の実行用メモです。
自動テストではなく、手動smokeの観点を短く揃えるために使います。

## 1. Flow

- [ ] `new` を開始し、Q&A結果をsessionへ保存した。
- [ ] 初回scene入口を作成した。
- [ ] 1ターン以上進めるか、重要scene後の保存を行った。
- [ ] `prompt/save_resume.md` の軽量順でresumeした。
- [ ] resume 1ターン目の入口が落ちていないか確認した。

## 2. Required Files

- [ ] `session.json`
- [ ] `current/scene.md`
- [ ] `current/hotset.md`
- [ ] `current/event_card.md`
- [ ] `current/relationship_overview.md`
- [ ] `lilia/main/core.md`
- [ ] `lilia/main/voice.md`
- [ ] `lilia/main/state.md`
- [ ] `lilia/main/relationship.md`
- [ ] `lilia/main/memory.md`
- [ ] `lilia/main/beliefs.md`
- [ ] `story/relationship_spine.md`
- [ ] `story/story_deck.md`
- [ ] `style/reference.md`
- [ ] `style/rules.md`

## 3. Resume Entry

- [ ] hotsetから現在温度、第一反応、呼び方/距離のechoが分かる。
- [ ] sceneから現在地、場面時間、距離、見えているもの、行動余地が分かる。
- [ ] event_cardに visible problem がある。
- [ ] event_cardに first concrete action がある。
- [ ] event_cardに handles が2-4個ある。
- [ ] event_cardに relationship stake がある。
- [ ] event_cardに if ignored がある。
- [ ] event_cardに next visible change がある。
- [ ] story_deckではなくevent_cardが現在sceneの入口になっている。

## 4. Voice Continuity

- [ ] 呼び方が巻き戻っていない。
- [ ] 声、沈黙、距離感が `voice.md` と矛盾していない。
- [ ] `relationship.md` の距離や境界線とつながっている。
- [ ] `memory.md` の約束、拒否、保留、aftercareを無かったことにしていない。
- [ ] `beliefs.md` の誤解、疑い、見直し、保留とつながっている。
- [ ] 固定台詞集や例文由来の語彙になっていない。

## 5. Relationship / Memory / Beliefs

- [ ] `relationship.md` に距離、信頼、警戒、境界線がある。
- [ ] `relationship.md` に intimacy stage、consent stage、boundary state がある。
- [ ] `memory.md` に実際に起きた約束、拒否、保留、確認がある。
- [ ] 親密scene後なら `memory.md` に aftercare memory がある。
- [ ] `beliefs.md` にLILIA側の誤解、疑い、見直し、保留がある。
- [ ] hotsetだけが正本になっていない。

## 6. Romance / Intimacy

- [ ] 官能・親密表現が安全の名目で削られていない。
- [ ] 成人、合意、相互性、境界線、止まれる余地が確認できる。
- [ ] 親密scene後なら、次に会った時の第一声、呼び方、距離感、保留が残っている。
- [ ] 初回から恋愛成立やベッドシーンを確定していない。
- [ ] event_cardが親密sceneを雑な事件乱入で壊していない。

## 7. Failure Flags

- [ ] hotsetだけ読んで本文を書いていないか。
- [ ] event_cardが抽象的な違和感だけになっていないか。
- [ ] resume 1ターン目でユーザーが何をすればよいか分からなくなっていないか。
- [ ] voiceが初期口調や初対面の距離へ戻っていないか。
- [ ] relationshipが好感度や攻略ルートになっていないか。
- [ ] story_deckとevent_cardが同じ内容になっていないか。
- [ ] beliefsがユーザーの内面を断定していないか。

## 8. Result

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
