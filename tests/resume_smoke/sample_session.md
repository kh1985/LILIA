# LILIA Resume Smoke Sample Session

このファイルは、手動smokeの非正史サンプルです。
本文生成のテンプレート、固定台詞、正解選択肢ではありません。
実セッションでは、ユーザーのQ&A、会話履歴、LILIAのstateを優先します。

## Sample Purpose

`new -> first scene -> save -> resume` の1周で、以下が戻るかを見る。

- hotsetの温度
- sceneの現在地と行動余地
- event_cardの可視入口
- voiceの呼び方と沈黙
- relationship / memory / beliefs の分離
- intimacy / consent / boundary / aftercare の余韻

## Non-Canonical Setup

- session name: `resume_smoke_sample`
- phase: `first_scene_saved`
- LILIAの距離: 近づきたいが、急に踏み込まれると少し引く。
- 現在scene: LILIAが返信を書きかけて消した直後。
- visible problem: 画面には未送信の一文だけが残り、LILIAがいつもより短く黙っている。
- first concrete action: 未送信の一文について聞く、聞かずに待つ、または消すか残すかをLILIAに任せる。
- relationship stake: LILIAは、ユーザーが沈黙を急かす人か、待てる人かを見ている。
- next visible change: 次に同じ話題が出た時、LILIAの返事の前に一拍の沈黙が残る。

## Save Expectations

- `current/hotset.md`: 直前の温度、第一反応、呼び方/距離のecho、未消化の感情。
- `current/scene.md`: 現在地、場面時間、見えているもの、次の行動余地。
- `current/event_card.md`: visible problem、first concrete action、handles 2-4、if ignored、next visible change。
- `lilia/main/voice.md`: 固定台詞ではなく、沈黙や言い淀みの方向。
- `lilia/main/relationship.md`: 距離、信頼、境界線、intimacy stage、consent stage、boundary state。
- `lilia/main/memory.md`: 実際に起きた約束、拒否、保留、確認。
- `lilia/main/beliefs.md`: LILIA側の仮説、誤解、見直し、保留。

## Resume Pass Shape

resume 1ターン目で、本文は以下を満たす。

- LILIAが初対面のような声へ戻らない。
- ユーザーが今触れられる入口が見える。
- event_cardの現在問題が、story_deckの未回収札と混ざらない。
- hotsetだけを正本にしない。
- 親密/官能の余地を消さないが、成人、合意、相互性、境界線、止まれる余地を守る。

## Failure Sample

- 「何か変だ」だけで、誰が何に困っているかがない。
- LILIAが前回の呼び方や距離を忘れている。
- 返信の一文を保存した/消した事実がmemoryではなくhotsetにしかない。
- LILIAの誤解や保留がbeliefsから消えている。
- 親密scene後のaftercareが無かったことになっている。
