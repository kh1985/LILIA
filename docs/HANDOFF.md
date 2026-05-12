# LILIA Handoff

このファイルは、別セッションでLILIA開発を再開する時の直近引き継ぎ専用メモです。
長期履歴、βタスク表、商用判断、詳細仕様はここに統合しません。

## 1. LILIAとは

LILIAは、あなたとの会話・選択・物語を記憶し、関係性と人格の出方が少しずつ変化していくAI恋愛シミュレーションです。

LILIAを所有物、攻略対象、ユーザーに都合よく最適化される存在として扱わない。
ストーリーは主役ではなく、関係と人格の出方を変化させるための装置として扱う。

## 2. 現在地

現在地の正本は `PROJECT_CONTROL.md` です。
このセクションは再開時の短い要約だけを置きます。

- CLI中心のMVP基盤はあります。`new` / Q1-Q9 / AI profile / story spine / downstream docs / `scene-tick` / `apply-turn` / resume系validator / growth smoke は到達済みです。
- 商用βとしては未到達です。WebUI、画像PoC、課金、利用規約、β募集導線、ユーザー向けLLM runtime分離、安全対策、外部テストが残っています。
- β前P0は、実プレイの保存再開、Three Hook Spine、Story Continuation / Travel Branch、AI Playtest Smoke、WebUI、安全分離、画像PoCに集中します。
- `STATUS_DASHBOARD.html` は人間用ビューであり、正本ではありません。Markdown正本をHTMLに置き換えません。

## 3. 直近の整理状況

ドキュメント整理の流れ:

- Phase 1: `PROJECT_CONTROL.md` を追加し、`AGENTS.md` を `PROJECT_CONTROL.md` へ誘導する入口に短縮しました。
- Phase 2-A: `docs/DOCUMENT_REORGANIZATION_PLAN.md` を追加し、トップレベルMarkdownと `docs/` 配下の配置計画を作りました。
- Phase 2-B: トップレベルMarkdownを `docs/specs/`、`docs/testing/`、`docs/release/`、`docs/archive/` へ整理しました。
- Phase 2-C: `STATUS_DASHBOARD.html` を `PROJECT_CONTROL.md` 中心の人間用司令室へ刷新しました。
- Phase 3-A: `docs/DOCUMENT_DEDUPLICATION_PLAN.md` を追加し、`HANDOFF` / `ROADMAP` / release docs / Dashboard の重複整理計画を作りました。
- Phase 3-B: このファイルを直近引き継ぎ専用に短縮しています。

直近の設計判断:

- `docs/tasks/KNOWLEDGE_BOUNDARY_IMPLEMENTATION_DESIGN.md` を追加し、GMが真相 / プレイヤー既知 / ヒロイン既知 / 共有済み / 観察可能 / 未開示を裁定する `Knowledge Boundary Gate` を設計しました。
- `tools/session/knowledge_boundary.py` を追加し、`current/knowledge_state.md` の分類と漏洩検査を validator から使える最小基盤として実装しました。
- AI Playtest Judge に `knowledge_boundary_player_orientation` を追加し、判断材料不足、GM-only/meta漏洩、ヒロインの知り得ない情報断定を、Story Causality不足と分けて評価する方針にしました。
- group_a deterministic fallback が `手元の具体物` を Active Hook にして作業ログ化する事故を防ぐため、物品リストを可視問題へ圧縮し、genericな主人公理由を validator で落とす方針にしました。
- `tools/session/opening_seed.py` を追加し、初回sceneの `hook_id` / `hook_type` / `status` / `Scene Function` / `Player Orientation` など、AIに空欄化させてはいけない制御値をコード側で先に固定する方針にしました。
- `./lilia new` 後に codex engine で開始する場合、`codex exec` のone-shot first sceneではなく `codex-resume` 相当の対話プレイへ渡す方針にしました。
- AI Playtest Judge に `story_causality_scene_drive` を追加し、確認手順だけが続いて不可逆変化 / Choice Tension / Next Curiosity が弱いrunを検出する方針にしました。
- AI Playtest の `--turns` は最大ターン数であり、autosave checkpointを越える自動継続ではありません。checkpoint到達時は `complete` ではなく `checkpoint reached` と表示し、開発メニューでも事前noticeを出します。
- `--continue-through-checkpoints` を追加し、checkpointごとにrun session側だけへ fresh `turn_update.md` を生成・dry-run確認・適用して30ターン級の連続観察をできるようにしました。元の `saves/` session は変更しません。
- `tools/session/reply_context.py` を追加し、resume / Play Mode生成直前に Heroine Reply Context、Pressure Context、GM Control Context を分離する方針にしました。圧とevent_cardは残すが、ヒロイン本文の根拠はヒロインが知覚・記憶・推測できる情報へ限定します。
- `current/event_card.md` template に Pressure / Agency、Observable Pressure、Heroine Initiative Candidate、Pressure Conversion Rule を追加し、Relationship Stake / Scene Functionをヒロイン主観へ混ぜない方針にしました。

今回の方針:

- 長い実装済み一覧は `docs/ROADMAP.md` と `docs/archive/IMPLEMENTATION_HISTORY.md` に逃がします。
- β前P0の一覧とstatusは `docs/release/RELEASE_WBS.md` に逃がします。
- 商用β方針、Go / No-Go、画像・Security方針は `docs/release/COMMERCIALIZATION_ROADMAP.md` に逃がします。
- 人間が見やすい現在地は `STATUS_DASHBOARD.html` へ置けますが、正本扱いしません。

## 4. 次にやること

ドキュメント整理の次順:

1. Phase 3-B: `docs/HANDOFF.md` 短縮差分を確認し、直近引き継ぎ専用として完了扱いにする。
2. Phase 3-C: `docs/ROADMAP.md` を履歴中心へ寄せ、現在地や次タスクの重複を `PROJECT_CONTROL.md` / `docs/HANDOFF.md` へ逃がす。
3. Phase 3-D: release docs の重複整理を行い、`docs/release/RELEASE_WBS.md` は表、`docs/release/COMMERCIALIZATION_ROADMAP.md` は商用方針、`PROJECT_CONTROL.md` は要約へ分ける。
4. ドキュメント整理後に、AI Playtest Judge / save-resume smoke / event_card確認へ戻る。

実装系へ戻る時の優先順:

1. `HOOK-006`: wanderer playtestで脱線入力を試し、Main / Relationship / Life-Exploration のどれかへ自然に戻れるか確認する。`HOOK-005` は最小実装済みだが、WBS status判断は `docs/release/RELEASE_WBS.md` を優先する。
2. `P-002` / `P-003`: 外部TTYで `save` / `apply-turn` / `resume` の実機確認を完了する。
3. `ARC-002〜007`: Story Continuation / Travel Branch MVPへ進む。
4. `AI-005〜007`: AI Playtestへscene-tick / apply-turn / resume連動を追加する。
5. WebUI前のSecurity設計を固める。

## 5. 参照すべき正本リンク

再開時は、まず `PROJECT_CONTROL.md` を読み、作業に必要な正本だけを読む。

| 読みたいもの | 正本 / 参照先 |
|---|---|
| 現在地、優先順位、正本一覧 | `PROJECT_CONTROL.md` |
| LILIAの中核思想 | `docs/CORE_CONCEPT.md` |
| 長期実装順、MVP境界、保留判断 | `docs/ROADMAP.md` |
| βまでのタスク、status、priority、done criteria | `docs/release/RELEASE_WBS.md` |
| 商用MVP境界、Go / No-Go、画像・安全方針 | `docs/release/COMMERCIALIZATION_ROADMAP.md` |
| 完了済みWaveと実装履歴の台帳 | `docs/archive/IMPLEMENTATION_HISTORY.md` |
| Phase 2-Aの文書配置計画 | `docs/DOCUMENT_REORGANIZATION_PLAN.md` |
| Phase 3-Aの重複整理計画 | `docs/DOCUMENT_DEDUPLICATION_PLAN.md` |
| Play Mode品質、Tempo、Arc Closure | `docs/specs/PLAY_MODE_SPEC.md` |
| AI Playtestのpersona、loop、judge、report | `docs/testing/AI_PLAYTEST_PLAN.md` |
| 人間用の現在地ビュー | `STATUS_DASHBOARD.html` |

## 6. Codex / Claudeへの注意

- `docs/HANDOFF.md` は直近引き継ぎであり、長期履歴の正本ではありません。
- 実装履歴は `docs/ROADMAP.md` と `docs/archive/IMPLEMENTATION_HISTORY.md` を見ます。
- βタスクは `docs/release/RELEASE_WBS.md` を見ます。
- 商用判断は `docs/release/COMMERCIALIZATION_ROADMAP.md` を見ます。
- Dashboardは人間用ビューであり、正本ではありません。
- Markdown正本をHTMLへ置き換えません。
- `prompt/core.md` の `Example Anchoring Control` は全prompt共通原則です。例文は選択肢でも正本でもなく、語彙を人格へ固定する材料でもありません。
- Play Mode / Save Mode を分離します。通常プレイ中にファイル編集、diff、保存更新ログを割り込ませません。
- `scene-tick` はターン数を進めるだけです。`apply-turn` が Save Mode の実更新を行い、勝手な自動保存はしません。
- 初期MVPに AFFINITY / bond / harem / heavy case engine / villain engine / manga pipeline を戻しません。
- `PROJECT_CONTROL.md` の現在地・優先順位と矛盾する場合は、`PROJECT_CONTROL.md` を優先し、必要に応じてこのファイルを短く直します。
- prompt / generator / validator / tests から参照される仕様docsは、整理目的だけで削らないでください。

## 7. 削った重複の逃がし先

| HANDOFFから外したもの | 逃がし先 |
|---|---|
| Wave 1〜16、Wave Y-F / Y-H、Growth Smokeなどの長い実装履歴 | `docs/ROADMAP.md`, `docs/archive/IMPLEMENTATION_HISTORY.md` |
| β前P0、P1、SEC、WEB、IMG、RELなどのタスク一覧 | `docs/release/RELEASE_WBS.md` |
| Three Hook Spine、Story Continuation / Travel Branch の商用β上の意味 | `docs/release/COMMERCIALIZATION_ROADMAP.md` |
| Play Mode品質、Lightweight Tempo Guard、Arc Closure Guardの詳細 | `docs/specs/PLAY_MODE_SPEC.md` |
| AI Playtest persona / judge / report の詳細 | `docs/testing/AI_PLAYTEST_PLAN.md` |
| 現在地の見やすいカード表示 | `STATUS_DASHBOARD.html` |

## 8. HANDOFF更新ルール

- このファイルは短く保つ。
- 直近作業、次タスク、再開時の注意だけを更新する。
- 長期実装順を変えたら `docs/ROADMAP.md` を更新する。
- βタスクのstatusを変えたら `docs/release/RELEASE_WBS.md` を更新する。
- 商用判断を変えたら `docs/release/COMMERCIALIZATION_ROADMAP.md` を更新する。
- 主要な設計判断をした時も、ここでは要約とリンクだけに留める。
