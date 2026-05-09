# LILIA Release WBS

この文書は、LILIA商用βリリースまでのタスク、状態、優先度、完了条件を管理するトップレベルWBSである。

## Status

- todo: 未着手
- doing: 作業中
- blocked: 停止中
- review: 確認待ち / 実装または仕様は存在するが、β完了条件としては追加確認が必要
- done: 完了
- dropped: 採用しない

## Progress Semantics

このWBSでは、`done` は商用βのDone Criteriaを満たした状態だけに使う。
コードや設計文書が存在するが、手動smoke、長期run、β品質確認が残るものは `review` とする。

進捗判断は以下の3段階で分ける。

1. コード実装済み / 仕様文書作成済み
2. smoke確認済み
3. β完了条件達成

`ROADMAP.md` は開発waveの実装履歴、`RELEASE_WBS.md` は商用βに出せるかの判定表である。
そのため、ROADMAP上でdoneでも、β確認が未完了ならWBSでは `review` または `todo` のままにしてよい。

## Priority

- P0: リリース不能になる
- P1: β品質に必要
- P2: あると良い
- P3: 後回し

## WBS

| ID | Task | Status | Priority | Owner | Due | Done Criteria |
|---|---|---|---|---|---|---|
| C-001 | 商用βスコープ確定 | review | P0 |  |  | 初期βで作るもの・作らないものが COMMERCIALIZATION_ROADMAP.md に明文化されている |
| C-002 | 1ヒロイン方針確定 | review | P0 |  |  | 初期βで使うヒロインと現実路線の範囲が決まっている |
| C-003 | 異界 / 能力オプション後回し明文化 | review | P0 |  |  | 初期βでは実装しないことが明記されている |
| P-001 | 1ヒロイン実機プレイ10ターン | done | P0 |  |  | new → first scene → 10 turns が破綻しない |
| P-002 | save / apply-turn 確認 | review | P0 |  |  | Save Modeに入り、apply-turnで必要stateが更新される |
| P-003 | resume 1ターン目確認 | review | P0 |  |  | resume後に声・距離・余韻が戻る |
| P-004 | event_card playable確認 | review | P0 |  |  | event_cardが今触れる可視イベントになっている |
| HOOK-001 | Three Hook Spine設計確定 | todo | P0 |  |  | Main Hook / Relationship Hook / Life-Exploration Hook の責務と状態遷移が明文化されている |
| HOOK-002 | 3本hook初期生成 | todo | P0 |  |  | newgame / downstream docs生成時に3本hookが初期化される |
| HOOK-003 | Active Hook接続 | todo | P0 |  |  | current/event_card.md に Active Hook があり、今触れる1本を前景化できる |
| HOOK-004 | story_deck hook保持 | todo | P0 |  |  | story/story_deck.md に残り2本のhookと状態が保持される |
| HOOK-005 | apply-turn hook更新 | todo | P0 |  |  | Save Mode / apply-turn で hook の進行・保留・背景化・悪化を更新できる |
| HOOK-006 | wanderer playtest | todo | P0 |  |  | AI Playtestで脱線入力を試し、3本hookのどれかに自然に戻れる |
| HOOK-007 | Lightweight Tempo Guard | done | P0 |  |  | 1ターンに前景化するhookは原則1本、LILIAからの明示質問は原則1個、通常ターンの文字量目安、場面転換の上限、次に返せる入口、選択肢UIの抑制がPLAY_MODE_SPEC.mdに定義されている |
| TEMPO-001 | Tempo Guard詳細仕様追加 | done | P0 |  |  | PLAY_MODE_SPEC.md にTurn Budget / One Foreground Rule / Question Limit / Exit Shape が定義されている |
| TEMPO-002 | AI Playtest Tempo Guard追加 | review | P0 |  |  | AI_PLAYTEST_PLAN.md で質問過多・hook過多・説明過多・返答入口不明を評価できる |
| TEMPO-003 | Passive Player Tempo Test | todo | P1 |  |  | passive AI Playerが10turn回っても、返答先に迷わないか確認できる |
| TEMPO-004 | WebUI Readability Check | todo | P1 |  |  | 通常ターンがWebUI上で読みにくい長さになっていないか評価できる |
| TEMPO-005 | Choice UI Restraint Rule | todo | P1 |  |  | 毎ターン露骨な選択肢UIを出さず、必要時だけ補助表示する方針がある |
| ARC-001 | Story Completion判定 | todo | P0 |  |  | Reveal Ladder / event_card / story_deck から、現在のstoryが解決・保留・背景化・悪化・完了のどれか判定できる |
| ARC-002 | Next Story Arc生成 | todo | P0 |  |  | 現在storyが閉じた後、LILIAとの関係・記憶・未回収札から次のstory_spine / event_card候補を生成できる |
| ARC-003 | Travel / Location Branch | todo | P0 |  |  | 沖縄・鹿児島・ニューヨーク等の大移動宣言を即拒否せず、費用・時間・理由・LILIA同行可否を含むbranchとして扱える |
| ARC-004 | Heroine Agency on Travel | todo | P0 |  |  | 親密度や関係理由が薄い時、LILIAが同行しない・保留する・条件を出す判断を人格として返せる |
| ARC-005 | Open Arc Limit | todo | P0 |  |  | 未解決の遠出 / branch は最大2本まで保持し、3本目は既存arcの解決・保留・帰還を促す |
| ARC-006 | Long-run AI Playtest | todo | P0 |  |  | normal / wanderer で100ターン級smokeを実行し、story完了後の次arc生成とresumeが破綻しない |
| ARC-007 | High-intimacy Manual Run | todo | P0 |  |  | ユーザー本人が長期手動プレイし、関係が深まった後の声・境界線・同行判断・新story生成を確認する |
| STORY-001 | STORY_FUNCTION_FRAMEWORK.md 作成 | done | P1 |  |  | 15機能、三層構造、scene機能、LILIA用読み替えが定義されている |
| STORY-002 | story_spineへStory Function Position追加検討 | todo | P1 |  |  | current_function / next_function_candidate / do_not_jump_to の導入方針が決まっている |
| STORY-003 | event_cardへScene Function追加検討 | todo | P1 |  |  | scene_goal / obstacle / expected_change / withheld_information の導入方針が決まっている |
| STORY-004 | AI PlaytestへScene Change Check追加 | todo | P1 |  |  | 入口と出口で何が変わったかを評価できる |
| STORY-005 | PLAY_MODE_SPECへ「情報ではなく問い」ルール追加 | done | P0 |  |  | GMが設定説明より問い・行動・衝突を優先するルールがある |
| STORY-006 | Story Functionを固定プロット化しないルール追加 | done | P0 |  |  | 十五機能を順番強制せず、診断と生成補助に限定することが明文化されている |
| REL-LOGIC-001 | AFFINITY / bond 非採用方針の明文化 | done | P0 |  |  | LILIA初期βではAFFINITY / bondを採用しない理由が明記されている |
| REL-LOGIC-002 | hiddenベクトル本格運用の保留 | done | P0 |  |  | hiddenベクトルは初期βでは数値運用せず、将来の深化管理候補として保持すると明記されている |
| REL-LOGIC-003 | Relationship Change Audit正本作成 | done | P0 |  |  | docs/RELATIONSHIP_CHANGE_AUDIT.md に、関係変化の根拠・速度・保存先分離の監査ルールがある |
| REL-LOGIC-004 | AI PlaytestへRelationship Change Audit追加 | review | P1 |  |  | AI Playtestで早すぎる/遅すぎる/根拠なしの関係変化を検出できる |
| REL-LOGIC-005 | relationship templateへhidden保留方針追加 | done | P0 |  |  | templates/session/lilia/main/relationship.md に、初期βではhiddenを通常進行メーターにしない方針がある |
| AI-001 | AI Playtest Plan作成 | done | P0 |  |  | AI_PLAYTEST_PLAN.md にループ、persona、評価項目がある |
| AI-002 | AI Player Persona定義 | done | P0 |  |  | normal / passive / boundary / attacker / wanderer / traveler の6種が定義済み |
| AI-003 | `./lilia ai-playtest` 実装 | done | P0 |  |  | 指定ターン数、GM出力 → AI Player入力 → GM出力 の交互進行ができる |
| AI-004 | transcript保存 | done | P0 |  |  | GM出力、AI Player入力、turn番号がMarkdownまたはJSONLで保存される |
| AI-005 | scene-tick連動 | done | P0 |  |  | 各ターン後にscene-tickが実行される |
| AI-006 | apply-turn連動 | review | P0 |  |  | 指定ターン後にSave Mode更新をテストできる |
| AI-007 | resume検証 | review | P0 |  |  | save → resume 後の1ターン目を生成・評価できる |
| AI-008 | Playtest Report生成 | done | P0 |  |  | PASS / WARN / FAIL、破綻箇所、推奨修正がMarkdown出力される |
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
- 3本hook初期生成 / Active Hook接続 / Tempo Guard (HOOK-002 / HOOK-003 / HOOK-007)
- Story Completion判定 / Next Story Arc生成設計 (ARC-001 / ARC-002)

Week 4:

- WebUI最小PoC
- LLM Runtime Isolation 設計 (SEC-000)
- Session Authorization / Context Minimization 設計 (SEC-001 / SEC-002)
- story_deck hook保持 / apply-turn hook更新 (HOOK-004 / HOOK-005)
- Travel / Location Branch と Heroine Agency on Travel (ARC-003 / ARC-004)
- チャット画面
- session作成
- resume表示

Week 5:

- WebUIから apply-newgame / resume / scene-tick 接続
- 本番LLM runtime と開発用agentの分離 (SEC-000)
- Path Traversal Protection / Structured Output Validation (SEC-003 / SEC-004)
- wanderer playtest (HOOK-006)
- Open Arc Limit / Long-run AI Playtest (ARC-005 / ARC-006)
- 画像表示枠
- エラー表示

Week 6:

- 課金方式決定
- 利用規約
- Output Safety Filter / Log Redaction (SEC-005 / SEC-006)
- Prompt Injection Playtest (SEC-007)
- Security Review Before Paid Beta (SEC-008)
- High-intimacy Manual Run (ARC-007)
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
