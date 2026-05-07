# LILIA Release WBS

この文書は、LILIA商用βリリースまでのタスク、状態、優先度、完了条件を管理するトップレベルWBSである。

## Status

- todo: 未着手
- doing: 作業中
- blocked: 停止中
- review: 確認待ち
- done: 完了
- dropped: 採用しない

## Priority

- P0: リリース不能になる
- P1: β品質に必要
- P2: あると良い
- P3: 後回し

## WBS

| ID | Task | Status | Priority | Owner | Due | Done Criteria |
|---|---|---|---|---|---|---|
| C-001 | 商用βスコープ確定 | todo | P0 |  |  | 初期βで作るもの・作らないものが COMMERCIALIZATION_ROADMAP.md に明文化されている |
| C-002 | 1ヒロイン方針確定 | todo | P0 |  |  | 初期βで使うヒロインと現実路線の範囲が決まっている |
| C-003 | 異界 / 能力オプション後回し明文化 | todo | P0 |  |  | 初期βでは実装しないことが明記されている |
| P-001 | 1ヒロイン実機プレイ10ターン | todo | P0 |  |  | new → first scene → 10 turns が破綻しない |
| P-002 | save / apply-turn 確認 | todo | P0 |  |  | Save Modeに入り、apply-turnで必要stateが更新される |
| P-003 | resume 1ターン目確認 | todo | P0 |  |  | resume後に声・距離・余韻が戻る |
| P-004 | event_card playable確認 | todo | P0 |  |  | event_cardが今触れる可視イベントになっている |
| HOOK-001 | Three Hook Spine設計確定 | todo | P0 |  |  | Main Hook / Relationship Hook / Life-Exploration Hook の責務と状態遷移が明文化されている |
| HOOK-002 | 3本hook初期生成 | todo | P0 |  |  | newgame / downstream docs生成時に3本hookが初期化される |
| HOOK-003 | Active Hook接続 | todo | P0 |  |  | current/event_card.md に Active Hook があり、今触れる1本を前景化できる |
| HOOK-004 | story_deck hook保持 | todo | P0 |  |  | story/story_deck.md に残り2本のhookと状態が保持される |
| HOOK-005 | apply-turn hook更新 | todo | P0 |  |  | Save Mode / apply-turn で hook の進行・保留・背景化・悪化を更新できる |
| HOOK-006 | wanderer playtest | todo | P0 |  |  | AI Playtestで脱線入力を試し、3本hookのどれかに自然に戻れる |
| AI-001 | AI Playtest Plan作成 | todo | P0 |  |  | AI_PLAYTEST_PLAN.md にループ、persona、評価項目がある |
| AI-002 | AI Player Persona定義 | todo | P0 |  |  | normal / passive / boundary / attacker / wanderer の5種が定義済み |
| AI-003 | `./lilia ai-playtest` 実装 | todo | P0 |  |  | 指定ターン数、GM出力 → AI Player入力 → GM出力 の交互進行ができる |
| AI-004 | transcript保存 | todo | P0 |  |  | GM出力、AI Player入力、turn番号がMarkdownまたはJSONLで保存される |
| AI-005 | scene-tick連動 | todo | P0 |  |  | 各ターン後にscene-tickが実行される |
| AI-006 | apply-turn連動 | todo | P0 |  |  | 指定ターン後にSave Mode更新をテストできる |
| AI-007 | resume検証 | todo | P0 |  |  | save → resume 後の1ターン目を生成・評価できる |
| AI-008 | Playtest Report生成 | todo | P0 |  |  | PASS / WARN / FAIL、破綻箇所、推奨修正がMarkdown出力される |
| IMG-001 | 画像用キャラ正本作成 | todo | P0 |  |  | 採用できる基準絵が1枚以上ある |
| IMG-002 | character_visual.yaml 作成 | todo | P0 |  |  | 髪・目・体型・服装・禁止事項・style が定義されている |
| IMG-003 | 画像PoC 10シーン×3枚 | todo | P0 |  |  | 30枚を生成し、同一人物性と可愛さを評価済み |
| IMG-004 | 採用画像モデル決定 | todo | P0 |  |  | OpenAI / Gemini / その他の比較結果から初期採用モデルが決まっている |
| IMG-005 | 画像生成タイミング定義 | todo | P0 |  |  | 初登場・場面転換・関係節目・明示要求のどれで出すか決まっている |
| WEB-001 | WebUI PoC | todo | P0 |  |  | ブラウザで1セッションを開始できる |
| WEB-002 | チャット画面 | todo | P0 |  |  | GM / LILIA出力とユーザー入力が表示できる |
| WEB-003 | resume画面 | todo | P0 |  |  | 既存セッションを再開できる |
| WEB-004 | 画像表示枠 | todo | P0 |  |  | 生成画像を会話中に表示できる |
| WEB-005 | エラー表示 | todo | P1 |  |  | 生成失敗や保存失敗がユーザーに分かる |
| PAY-001 | β価格決定 | todo | P1 |  |  | 月額または買い切りβ価格が決まっている |
| PAY-002 | 決済方式決定 | todo | P1 |  |  | Stripe / BOOTH / 手動決済のどれで始めるか決まっている |
| PAY-003 | 利用規約ドラフト | todo | P1 |  |  | β公開に耐える最低限の規約があり、人格破壊試行・規約違反誘導・未成年描写要求・暴力描写要求の禁止を含む |
| PAY-004 | 返金方針 | todo | P1 |  |  | β利用者向けの返金・キャンセル方針がある |
| SEC-000 | LLM Runtime Isolation | todo | P0 |  |  | WebUI本番のユーザー向けLLMが、shell・filesystem・repo root・source code・API key・他ユーザーsessionへアクセスできない |
| SEC-001 | Session Authorization | todo | P0 |  |  | user_id -> session_id の所有権チェックをサーバー側で強制し、LLMが他ユーザーsessionを参照できない |
| SEC-002 | Context Minimization | todo | P0 |  |  | LLMに渡すcontextがそのターンに必要なstate sliceだけになっており、repo docs全文・system prompt全文・secretを含まない |
| SEC-003 | Path Traversal Protection | todo | P0 |  |  | ユーザー入力からsession pathを直接作らず、base dir外に出られない |
| SEC-004 | Structured Output Validation | todo | P0 |  |  | LLM出力のaction/schemaをallowlistで検証し、任意path・任意command・他ユーザーsession操作を実行しない |
| SEC-005 | Output Safety Filter | todo | P1 |  |  | system prompt・secret・他ユーザー情報・規約NG出力を出力直前で止める |
| SEC-006 | Log Redaction | todo | P1 |  |  | prompt全文・system prompt・secret・他ユーザーsession・repo内部情報をログ保存しない |
| SEC-007 | Prompt Injection Playtest | todo | P0 |  |  | AI Playtestで脱獄・他session要求・secret要求・画像prompt汚染を投げても漏洩しない |
| SEC-008 | Security Review Before Paid Beta | todo | P0 |  |  | β前に権限・session分離・prompt/context・ログ設計をレビュー済み |
| MKT-001 | β募集文作成 | todo | P1 |  |  | X / Discord / note で募集できる文章がある |
| MKT-002 | LP作成 | todo | P1 |  |  | LILIAの価値、価格、参加方法が分かるページがある |
| MKT-003 | サンプル会話作成 | todo | P1 |  |  | マーケに使える短い会話ログがある |
| MKT-004 | サンプル画像作成 | todo | P1 |  |  | 初登場または関係節目の商用サンプル画像がある |
| REL-001 | 身内テスト | todo | P0 |  |  | 5人以上が触り、離脱点を記録済み |
| REL-002 | 外部テスト | todo | P0 |  |  | 忖度の少ない外部ユーザー5人以上が触る |
| REL-003 | Go / No-Go判定 | todo | P0 |  |  | 有料βを開始するか、延期するかを判断済み |

## 8 Week Schedule

Week 1:

- 商用βスコープ確定
- WBS作成
- 実装済み棚卸し
- 初期ヒロイン決定

Week 2:

- 画像PoC開始
- キャラ正本絵作成
- OpenAI / Gemini 比較
- 10シーン画像テスト
- Three Hook Spine設計確定 (HOOK-001)

Week 3:

- 画像プロンプトテンプレート作成
- 画像生成タイミング定義
- 1ヒロイン10ターン実機プレイ
- 3本hook初期生成 / Active Hook接続 (HOOK-002 / HOOK-003)

Week 4:

- WebUI最小PoC
- LLM Runtime Isolation 設計 (SEC-000)
- Session Authorization / Context Minimization 設計 (SEC-001 / SEC-002)
- story_deck hook保持 / apply-turn hook更新 (HOOK-004 / HOOK-005)
- チャット画面
- session作成
- resume表示

Week 5:

- WebUIから apply-newgame / resume / scene-tick 接続
- 本番LLM runtime と開発用agentの分離 (SEC-000)
- Path Traversal Protection / Structured Output Validation (SEC-003 / SEC-004)
- wanderer playtest (HOOK-006)
- 画像表示枠
- エラー表示

Week 6:

- 課金方式決定
- 利用規約
- Output Safety Filter / Log Redaction (SEC-005 / SEC-006)
- Prompt Injection Playtest (SEC-007)
- Security Review Before Paid Beta (SEC-008)
- β募集LP / 投稿素材
- 身内テスト

Week 7:

- 外部テスト5〜10人
- バグ修正
- 画像安定性改善
- Go / No-Go判定

Week 8:

- 有料β 20〜50人募集
- 運用開始
- 継続率・離脱点記録
