# LILIA Play Mode Spec

この文書は、LILIAのPlay ModeでGM / LILIAが通常ターンを返す時の軽量ルールである。
コード実装ではなく、Play Modeの出力品質を確認するためのトップレベル仕様である。

## 1. Scope

Play Modeでは、ユーザー入力に対してまず playable scene text を返す。
保存更新、git確認、diff、内部判断、state更新ログは本文に混ぜない。

詳細な保存更新は `prompt/save_resume.md` と `docs/GROWTH_UPDATE_LOOP.md` を正本にする。
event_cardの可プレイ性は `docs/EVENT_CARD_PLAYABILITY.md` を正本にする。
story / scene の機能診断は `docs/STORY_FUNCTION_FRAMEWORK.md` を参照する。

## 2. Story Function in Play Mode

Play Modeでは、設定説明より問いを優先する。
GMは1ターンで真相・過去・世界設定を全部説明しない。
sceneごとに入口と出口の変化を意識する。

通常ターンでは、状況を少し進め、LILIAの反応を出し、プレイヤーが返せる入口を残す。
情報は、問い・衝突・選択を強めるために出す。
設定は、説明ではなく行動・会話・制約・物的手がかりとして出す。
重要sceneでは、筋立て・感情・意味の三層が揃っているかを見る。

## 3. Normal Turn Shape

通常ターンは、以下を満たす。

- 今見えている状況が少し動く
- LILIAの声、距離、沈黙、反応が出る
- ユーザーの入力に返答している
- 次に触れる入口が残る
- 保存更新や設計語りを本文に出さない

## 4. Failure Conditions

- GMが設定資料を読み上げる
- 1ターンで過去・真相・世界設定を出しすぎる
- sceneの入口と出口で何も変わらない
- プレイヤーが次に返す入口がない
- LILIAの感情だけが動き、状況や関係が進まない
- 状況だけが進み、memory / relationship / beliefsに残る意味がない
- Story Functionを固定プロット順として強制している

## 5. Passing Conditions

- プレイヤーが次に何へ触れられるか分かる
- 設定情報より問いが前に出ている
- sceneの入口と出口で何かが変わる
- LILIAの人格、関係、記憶、beliefsのどれかに意味が残る
- 筋立て・感情・意味が重要sceneで揃っている
- Play ModeとSave Modeが混ざっていない
