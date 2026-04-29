# LILIA MVP Playtest Manual Checklist

このチェックリストは、MVP Playtestで `new -> first scene -> save -> resume` を1周通すための実行用メモです。
新しい設計正本ではありません。
自動テスト、AI Harness、自動プレイ生成、大量ログ解析、launcher / CLI 実装は扱いません。

## 1. Scope

- [ ] 1人のLILIAで `new -> first scene -> save -> resume` を手動で1周通す。
- [ ] 関係、記憶、声、event_card、親密境界、story accumulation、crisis / ability が破綻していないかを見る。
- [ ] 合否は体験とstateの整合確認に絞り、網羅的な品質評価や自動採点にしない。
- [ ] 参照する正本は既存docsとpromptに委ね、このファイルに設計本文を増やさない。

## 2. Pre-check

- [ ] `docs/RESUME_SMOKE_TEST.md` を確認した。
- [ ] `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md` を確認した。
- [ ] `prompt/startup.md`、`prompt/newgame.md`、`prompt/save_resume.md` を確認した。
- [ ] `templates/session/` の必須ファイルが揃っている。
- [ ] `tests/resume_smoke/manual_checklist.md` を必要時に参照できる。

## 3. New Start

- [ ] `startup` で `new` として扱う入力から始めた。
- [ ] `newgame` のQ&Aを通した。
- [ ] Q&A回答を、core / voice / state / relationship / memory / beliefs / current / story / style に分けた。
- [ ] LILIAを所有物、攻略対象、ユーザー都合の最適化対象として作っていない。
- [ ] 初回から恋愛成立、ベッドシーン、巨大事件、full plotを確定していない。

## 4. First Scene

- [ ] `current/scene.md` から場所、場面時間、距離、見えているものが分かる。
- [ ] 初回sceneが設定説明だけで終わっていない。
- [ ] LILIAの第一声、沈黙、距離感が `voice.md` と矛盾していない。
- [ ] ユーザーが自由入力で触れる余地がある。

## 5. Event Card

- [ ] `current/event_card.md` に visible problem がある。
- [ ] first concrete action があり、今ユーザーが何に触れられるか分かる。
- [ ] handles 2-4 が行動余地として置かれている。
- [ ] relationship stake がLILIAとの関係に結びついている。
- [ ] if ignored と next visible change がある。
- [ ] event_cardが抽象的な違和感だけになっていない。
- [ ] story_deckではなくevent_cardが現在sceneの入口になっている。

## 6. Voice / Relationship / Memory / Beliefs

- [ ] voiceは固定台詞集ではなく、呼び方、沈黙、距離感、第一反応の方向になっている。
- [ ] relationshipは好感度、旧AFFINITY、攻略ルートになっていない。
- [ ] memoryには実際に起きたこと、約束、拒否、保留、確認だけが入っている。
- [ ] beliefsはLILIA側の仮説、誤解、疑い、見直しとして扱われている。
- [ ] unknownや未確定情報をmemoryの事実にしていない。
- [ ] ユーザーの内面を断定していない。

## 7. Romance / Intimacy Boundary

- [ ] 官能・親密表現を安全の名目で消していない。
- [ ] 成人、合意、相互性、境界線、止まれる余地を確認できる。
- [ ] `relationship.md` に intimacy stage、consent stage、boundary state がある。
- [ ] 親密scene後なら `memory.md` に aftercare memory が残る。
- [ ] 親密さを報酬、罰、攻略達成として扱っていない。
- [ ] event_cardが親密sceneを雑な襲撃や乱入で壊していない。

## 8. Story Accumulation

- [ ] Eventは今触れる点として扱われている。
- [ ] Storyは、反応と選択が memory / relationship / beliefs / voice に残る線として扱われている。
- [ ] `Story Residue` に、次回へ戻る保存候補が短く置かれている。
- [ ] `story_deck.md` は素材、圧、未回収札の棚になっている。
- [ ] `relationship_spine.md` は固定プロットや攻略ルートになっていない。
- [ ] full plotや巨大組織設定に寄っていない。

## 9. Crisis / Ability

- [ ] crisisがある場合、event_cardの visible problem として触れる入口がある。
- [ ] 戦うことだけを正解にしていない。
- [ ] 逃げる、守る、交渉する、隠す、耐える、助けを呼ぶ、あえて戦わない余地がある。
- [ ] abilityがある場合、can / cannot / condition / cost / trace / risk がある。
- [ ] abilityが万能解決ボタンになっていない。
- [ ] HP、ダメージ計算、部位管理、行動順、戦闘マップに寄っていない。
- [ ] 危機後の疲労、痕跡、関係リスクが必要なら state / story_deck に戻されている。

## 10. Growth Update

- [ ] scene後に、何が変わったかを確認した。
- [ ] 何も変わっていないファイルを無理に更新していない。
- [ ] stateには今だけの感情や疲労を置いた。
- [ ] relationshipには距離、信頼、境界線、相互性の変化だけを置いた。
- [ ] memoryには実際に起きたことだけを置いた。
- [ ] beliefsにはLILIA側の仮説や見直しだけを置いた。
- [ ] hotsetには次回1ターンに効く短い余韻だけを置いた。

## 11. Save

- [ ] `prompt/save_resume.md` の保存方針に従った。
- [ ] hotsetだけを更新して正本側を空にしていない。
- [ ] event_cardの進行状態、if ignored、next visible changeを必要に応じて更新した。
- [ ] story_deckへ戻す未回収札がある場合、短く整理した。
- [ ] 親密scene後なら aftercare、boundary、consent の変化を保存した。

## 12. Resume

- [ ] `prompt/save_resume.md` の軽量順でresumeした。
- [ ] hotsetを入口にしたが、hotsetだけで本文を書いていない。
- [ ] scene、event_card、relationship_overview、voice、state、relationship、memory、beliefsを必要分だけ確認した。
- [ ] story_deckは現在scene入口ではなく、未回収札や次候補として扱った。

## 13. Resume First Turn

- [ ] resume 1ターン目でLILIAの声が初期化されていない。
- [ ] 呼び方、沈黙、距離感が前回からつながっている。
- [ ] ユーザーが今触れるevent_card入口が戻っている。
- [ ] relationship / memory / beliefs の責務が混ざっていない。
- [ ] 親密scene後なら aftercare、境界線、次の第一声が戻っている。
- [ ] crisis / ability後なら痕跡、疲労、関係リスクが必要分だけ戻っている。

## 14. Integrity Cross-Check

- [ ] `docs/TECHNICAL_GAMEPLAY_INTEGRITY_CHECKS.md` の横断観点と矛盾していない。
- [ ] event_card / story_deck / relationship_spine の責務が分かれている。
- [ ] hotsetが正本化していない。
- [ ] memoryに推測やunknownが混ざっていない。
- [ ] beliefsでユーザーの内面を断定していない。
- [ ] romance / intimacy が境界線とaftercareを失っていない。
- [ ] crisis / ability が万能解決や重い数値戦闘になっていない。
- [ ] AI Harness、自動プレイ生成、大量ログ解析、launcher / CLIを必須にしていない。

## 15. Result

- session:
- date:
- pass/fail:
- new start:
- first scene:
- event_card:
- voice continuity:
- relationship / memory / beliefs:
- romance / intimacy boundary:
- story accumulation:
- crisis / ability:
- growth update:
- save:
- resume:
- resume first turn:
- integrity cross-check:
- notes:
