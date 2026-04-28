# LILIA Handoff

このファイルは、別のGPTセッションでLILIA開発を再開する時に最初に読ませる引き継ぎ文書です。

## 1. LILIAとは

LILIAは、あなたとの会話・選択・物語を記憶し、関係性と人格の出方が少しずつ変化していくAI恋愛シミュレーションです。

## 2. 現在の決定事項

- 名前は LILIA。
- LILIAは「ヒロイン」「キャラ」「パートナー」ではなく、LILIAというAI上の人格・関係存在として扱う。
- 短いコピーは「あなたとの記憶で、関係が育つ。」
- ストーリーは主役ではなく、関係と人格の出方を変化させる装置として扱う。
- 最初は1人のLILIAとの関係が面白いことを優先する。
- 官能寄りの表現技法は削除しない。成人・合意・相互性・関係段階・境界線を守ったうえで、LILIAの重要な魅力として活かす。

## 3. 現在の実装状況

- `docs/CORE_CONCEPT.md` を作成済み。
- `templates/session/` を作成済み。
- `docs/STATE_STRUCTURE.md` を作成済み。startup / new / resume が参照する最小state scaffold、session配置、new時生成ファイル、resume時読込方針を定義済み。
- `docs/NEW_SESSION_INITIALIZATION.md` を作成済み。`prompt/newgame.md` のQ&A結果から `session.json`、`current/*`、`lilia/main/*`、`story/*`、`style/*` を初期生成する写像と順序を定義する正本。
- `docs/EVENT_CARD_PLAYABILITY.md` を作成済み。`current/event_card.md` を抽象的な違和感ではなく、今触れる可視イベントにするGateの正本。
- `docs/VOICE_CONTINUITY.md` を作成済み。LILIAの声、呼び方、距離感、信頼、誤解、記憶、境界線がnew/resume/重要sceneで巻き戻らないようにするGateの正本。
- `docs/ROADMAP.md` を作成済み。長期実装順とMVP境界の正本として、マイルストーン、現在地、次タスクを管理する。
- 旧LIRIA / inner-galge zip調査に基づき、`docs/ROADMAP.md` に Style Defaults / Intimacy Defaults Completion、New Session Initialization、Event Card Playability Gate、Voice Continuity Gate、Romance / Intimacy Growth Loop、World Autonomy / Pressure Loop、Crisis / Combat / Ability Constraint Loop、Integrity Checks、Launcher / CLI、Visual / Manga Pipeline の順番を反映済み。
- `prompt/style_reference.md` と `templates/session/style/` を作成済み。参照小説・参照作品から本文ではなく表現軸を抽出し、Light Story Reference Pass としてnew初回scene前や必要時だけ使う方針を定義済み。
- root `style/defaults/` を作成済み。romance / tension / warmth / loss / quiet / landscape の場面別Style Defaultsを、作者別メソッドの直接模倣ではなく表現技法・温度・視点距離・余白の参照棚として移植済み。
- `style/defaults/romance.md` は、官能そのものを削らず、ベッドシーン、身体距離、触れる/触れない境界、体温、呼吸、沈黙、余韻を、成人・合意・関係段階・境界線のもとで扱う方針へ補強済み。
- `prompt/core.md` を作成済み。
- `prompt/core.md` に `Example Anchoring Control` を追加済み。
- `prompt/core.md` の読み順は、`current/relationship_overview.md` と `beliefs` を含め、保存・再開の詳細は `prompt/save_resume.md` を正本にする形へ調整済み。
- `prompt/startup.md` を作成済み。起動直後の `new` / `resume` / `consult` / `unknown` 分岐を定義し、詳細は `prompt/newgame.md` と `prompt/save_resume.md` に委ねる。
- `prompt/newgame.md` を作成または更新済み。
- `prompt/newgame.md` は `docs/NEW_SESSION_INITIALIZATION.md` を参照し、Q&A結果から各ファイルへ反映する写像、Light Story Reference Pass、new直後resume可能な最小状態を明記済み。
- `prompt/save_resume.md` は作成済みで、保存・再開promptとしてレビュー済み。
- `prompt/save_resume.md` は、再開読み順に `current/relationship_overview.md`、`story/story_deck.md`、`lilia/main/beliefs.md` の必要箇所確認を含める軽量順へ調整済み。
- `prompt/save_resume.md` は、new直後のresume-ready確認として `session.json`、`hotset`、`scene`、`event_card`、`relationship_overview`、`state`、`relationship`、`memory`、`beliefs` の最小状態を確認する方針を追加済み。
- `prompt/core.md`、`prompt/newgame.md`、`prompt/save_resume.md` に Event Card Playability の短い実行ルールを反映済み。詳細は `docs/EVENT_CARD_PLAYABILITY.md` を正本にする。
- `prompt/core.md`、`prompt/newgame.md`、`prompt/save_resume.md`、`prompt/style_reference.md` に Voice Continuity の短い実行ルールを反映済み。詳細は `docs/VOICE_CONTINUITY.md` を正本にする。
- `templates/session/` は New Session Initialization に合わせて補強済み。`session.json` にphaseとprompt参照、`current/event_card.md` に visible problem / first concrete action / handles 2-4 / relationship stake / if ignored / next visible change、session style rulesに intimacy / boundary の欄を追加済み。
- Case / Event Card Playability Gate は設計仕様とテンプレート補強が完了済み。`current/event_card.md` は、今のsceneでユーザーが触れる入口、放置時の小さな変化、次に見える変化、LILIAとの関係に残るものを持つ。
- Relationship / Character Voice Continuity Gate は設計仕様とテンプレート補強が完了済み。`core fixed`、`historical fixed`、`echo`、`volatile` をLILIA向けに軽量採用し、`voice`、`relationship`、`memory`、`beliefs` の責務分離と重要scene前の確認を固定済み。

prompt内の `current/...`、`lilia/main/...`、`story/...`、`archive/...` は、生成されたセッションルートからの相対パスとして扱う。テンプレート上では `templates/session/` 配下に対応する。

## 4. 採用元

- MIRA: 人格構造 `core / voice / state / relationship / memory / beliefs`、特に voice / memory / beliefs
- inner-galge: キャラ中心、hotset、Markdown運用、style defaults、romance/intimacy運用、memory model、validation、voice continuity、command導線
- LIRIA: session構造、event_card、save/resume、archive、story_reference / Light Story Reference Pass、style defaults、case/runtimeの運用知見、Visible Request Gate、Truth Hiding Boundary、Mid-Story Activation Gate、integrity check

combat / villain / visual / manga / AI Harness は、長期ROADMAP上の参照候補であり、初期MVP、New Session Initialization、Event Card Playability Gateには採用しない。

## 5. 採用しないもの

- proxy / web research / bench
- harem名称
- 複数キャラ前提
- case_engine / villain_engine / organization
- 漫画化 / AI Harness
- 巨大prompt分割
- 参照小説本文や固有文体の保存・直接模倣
- style系を通常resumeの毎回必読にする重い運用
- 安全の名目で官能表現そのものを削り、親密場面を薄める運用
- 旧AFFINITY数値、bond、好感度、攻略ルートを正本にする運用
- 固定台詞集でLILIAの声を管理する運用
- hotsetを正本として扱う運用
- 抽象的な違和感だけでevent_cardを進める運用
- 親密sceneを雑な事件乱入で壊す運用
- 最初から重いcase_engine / villain / combat / manga pipelineを全部MVP必須にすること

## 6. 次にやること

- ROADMAP上の直前項目は Relationship / Character Voice Continuity Gate。現状は設計仕様とテンプレート補強が完了済み。launcher / CLIによる実生成コードは後続。
- 次の実作業は Romance / Intimacy Growth Loop。
- event_card は「抽象的な違和感」ではなく「今触れる可視イベント」として扱う。真相は隠してよいが、visible problem、first concrete action、handles 2-4、relationship stake、if ignored、next visible change は隠さない。
- voice continuity は「固定台詞」ではなく、呼び方、声、距離、信頼、誤解、記憶、境界線が前回からつながっているかとして扱う。
- 長期実装順は `docs/ROADMAP.md` を正本とし、このファイルには直近の現在地と引き継ぎだけを残す。

## 7. 今後の判断基準

- 1人のLILIAとの関係が面白くなるか。
- LILIAの人格の核を壊していないか。
- ユーザーに迎合しすぎていないか。
- 記憶が次回の会話温度に効いているか。
- ストーリーが事件処理ではなく関係変化に効いているか。
- 例文やテンプレに引っ張られていないか。

## 8. HANDOFF更新ルール

- このファイルは開発の引き継ぎ正本である。
- 設計判断、prompt追加、session構造変更、採用方針変更、次タスク変更があったら更新する。
- マイルストーンが進んだ場合は、長期実装順の正本である `docs/ROADMAP.md` も更新する。
- 別GPTセッションで再開する時は、まずこのファイルを読ませる。
