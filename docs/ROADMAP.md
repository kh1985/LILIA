# LILIA Roadmap

この文書は、LILIA開発の長期実装順とMVP境界を管理する正本である。
思想・中核概念は `docs/CORE_CONCEPT.md`、直近の引き継ぎは `docs/HANDOFF.md`、state構造は `docs/STATE_STRUCTURE.md` を正本にする。

## 1. Goal

LILIAを、`new` / `resume` で実際に遊べて、記憶・関係・人格の変化が保存される最小プレイ可能版にする。

LILIAは単なるヒロイン、キャラ、攻略対象、固定パートナーではなく、会話・選択・物語・記憶・関係性によって人格の出方が少しずつ変化するAI上の人格・記憶・関係存在として扱う。

## 2. Current Position

- save/resume 軽量読み順: 完了
- startup分岐: 完了
- state scaffold: 完了
- style reference scaffold: 完了
- style defaults: 完了
- 次は new開始時の初期生成

## 3. Milestones

1. Concept / Growth Basis
   - `docs/CORE_CONCEPT.md` を正本として、LILIAの中核、価値提供、記憶、人格、設計原則を固定する。
   - Status: 完了

2. Save / Resume Reading Order
   - `prompt/save_resume.md` を正本として、保存対象と再開時の軽量読み順を固定する。
   - Status: 完了

3. Startup Flow
   - `prompt/startup.md` を正本として、起動直後の `new` / `resume` / `consult` / `unknown` 分岐を固定する。
   - Status: 完了

4. State Scaffold
   - `docs/STATE_STRUCTURE.md` と `templates/session/` で、最小state / memory / relationship / story構造を固定する。
   - Status: 完了

5. Style Reference Scaffold
   - `prompt/style_reference.md`、root `style/defaults/`、`templates/session/style/` で、参照小説・参照作品を本文コピーではなく表現軸へ分解する運用を固定する。
   - root `style/defaults/` は場面別の共通参照棚、`templates/session/style/` はsession初期生成用テンプレートとして分ける。
   - Status: 完了

6. New Session Initialization
   - `prompt/newgame.md` のQ&A結果から `session.json`、`current/*`、`lilia/main/*`、`story/*`、`style/*` を初期生成するルールを固める。
   - Status: 次に着手

7. Resume Smoke Test
   - 生成済みsessionを `resume` で軽量に読み、1ターン目の温度が落ちないか確認する。
   - Status: 未着手

8. Growth Update Loop
   - 会話後に `state`、`relationship`、`memory`、`beliefs`、`hotset`、`event_card` をどう更新するかを実運用できる形にする。
   - Status: 未着手

9. Personality / Relationship Reflection
   - LILIAの核を壊さず、関係変化が口調、第一反応、距離感、誤解、信頼に反映される流れを検証する。
   - Status: 未着手

10. Story Loop / Event Card
   - `event_card` と `story_deck` を、事件処理ではなく関係と人格の出方を動かすために運用する。
   - Status: 未着手

11. Memory Compression / Archive
    - 記憶が肥大化した時の圧縮、`archive/beats/` への節目保存、過去ログとの切り分けを設計する。
    - Status: 未着手

12. Launcher / CLI
    - `new` / `resume` を実際に起動する最小launcherまたはCLIを設計する。
    - Status: 未着手

13. MVP Playtest
    - 1人のLILIAで、開始、再開、関係変化、保存更新が一連の体験として成立するか検証する。
    - Status: 未着手

14. Extensions
    - export、セッション一覧、複数LILIA、UI、外部連携などをMVP後に検討する。
    - Status: 後続

## 4. Update Rules

- マイルストーンが進んだら `docs/ROADMAP.md` を更新する。
- `docs/HANDOFF.md` は直近作業・次タスク・引き継ぎに限定する。
- 小さな文言修正だけなら `docs/ROADMAP.md` は更新しなくてよい。
- 実装順を変えた場合は理由を短く残す。
- `prompt/core.md` の `Example Anchoring Control` を維持し、例文を本文生成へ流用しない。

## 5. Next Task

次タスクは New Session Initialization。

`prompt/newgame.md` のQ&A結果から `session.json`、`current/*`、`lilia/main/*`、`story/*`、`style/*` を初期生成するルールを固める。

## 6. 採用元

- MIRA: `core / voice / state / relationship / memory / beliefs`
- inner-galge: キャラ中心 / hotset / Markdown運用
- LIRIA: session構造 / event_card / save/resume / archive
- style reference: LIRIAの story_reference / Light Story Reference Pass / style rules / 作者別・場面別defaults と inner-galgeの抽象化手順

## 7. 採用しなかったもの

- LILIAを単なるヒロイン、攻略対象、固定パートナーとして扱う設計
- Handoffに長期ロードマップを全部詰め込む運用
- 起動時・再開時に全ファイルを総読みする重い運用
- example文を本文生成へ流用する運用
- 参照小説本文や固有文体を保存・直接模倣する運用
- style系を通常resumeの毎回必読にする重い運用
- 今回いきなりlauncher / CLIへ進むこと

## 8. 理由

HANDOFFは直近引き継ぎ、ROADMAPは長期実装順として分けた方が更新しやすいため。

LILIAの成長基盤、開始、再開、更新ループ、launcherの順番を見失わないようにするため。

実装順が共有されていないと、CodexがCLIや拡張機能へ早く進みすぎるリスクがあるため。

LILIAはAI上の人格・記憶・関係存在なので、成長基盤とnew/resumeの接続を優先する必要があるため。
