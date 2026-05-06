# LILIA Engine Runner

この文書は、LILIAのAI生成処理で使う共通 LLM CLI runner の責務を定義する設計正本である。
実装コードの詳細ではなく、`codex` / `claude` 呼び出しを各 generator へ散らさないための軽量ルールを固定する。

## 1. Purpose

Engine Runner は、character YAML、profile、story spine、downstream session documents などのAI生成で使う CLI 呼び出しの共通層である。

目的は、生成品質の判断をrunnerへ集めることではない。
CLIの選択、fallback、timeout、stdout取得、process終了だけを共通化し、各生成物の schema / validator / retry 判断はそれぞれの generator に残す。

Engine Runner は、物語エンジン、会話エンジン、AI Harness、自動プレイではない。

## 2. Source Of Truth

- 中核思想: `docs/CORE_CONCEPT.md`
- new初期化: `docs/NEW_SESSION_INITIALIZATION.md`
- save / resume: `prompt/save_resume.md`
- growth update: `docs/GROWTH_UPDATE_LOOP.md`
- launcher / CLI: `./lilia`
- 実行共通層: `tools/common/engine_runner.py`

この文書は、LLM CLI 実行境界の正本である。
生成物の内容責務は、profile / spine / session document 側の generator と validator を優先する。

## 3. Responsibilities

Engine Runner が担当するもの:

- `claude` / `codex` CLI の利用可否確認。
- `auto` 指定時の候補順決定。
- prompt を stdin で渡し、stdout を文字列として返す。
- stderr、空stdout、非0終了を error として扱う。
- timeout時に子processを残さない。
- engineごとのコマンド差分を隠す。

## 4. Public API

実装の公開 API は `tools/common/engine_runner.py` に置く。

- `class EngineRunnerError(RuntimeError)`
- `class EngineTimeoutError(EngineRunnerError)`
- `class EngineUnavailableError(EngineRunnerError)`
- `available_engines() -> list[str]`
- `resolve_engine(requested: str) -> str | None`
- `engine_candidates(requested: str) -> list[str]`
- `run_engine(engine: str, prompt: str, *, timeout: float, root: Path) -> str`
- `run_with_fallback(engines: list[str], prompt: str, *, timeout: float, root: Path, on_failure: Callable[[str, Exception], None] | None = None) -> tuple[str, str]`

generator 側はこの API を使い、独自の `subprocess.run(..., capture_output=True)` や engine command builder を持たない。

Engine Runner が担当しないもの:

- character YAML の schema 判断。
- profile / story spine / downstream docs の validator。
- Q&Aの解釈、人格設計、event_card生成。
- Play Mode中の通常応答生成。
- 保存更新判断。
- AI Harness、自動プレイ、大量ログ解析、bench。

## 5. Engine Selection

指定できる engine は以下だけにする。

- `claude`
- `codex`
- `auto`

`auto` は利用可能な CLI から順に試す。
候補は必ず `shutil.which()` で検出できた CLI だけにする。
未インストールの CLI は候補に含めない。
利用可能な CLI が1つだけなら、その CLI だけで実行する。
利用可能な CLI がない場合、候補は空になり、generator 側で明確なエラーとして扱う。

明示指定された engine は、その engine だけを使う。
明示指定の失敗を、勝手に別 engine の成功で覆い隠さない。
明示指定された engine が未インストールの場合も候補は空になる。

### engine 優先順位の決定

| 用途 | 環境変数 | デフォルト優先順位 |
| --- | --- | --- |
| 一般（profile / spine / downstream / interactive） | `LILIA_DEFAULT_ENGINE` | `codex -> claude` |
| character YAML 生成 | `LILIA_CHARACTER_ENGINE` | `claude -> codex` |

一般生成では、長プロンプト（profile / spine / downstream）で `claude` がハングするケースを避けるため、未設定時は `codex` を優先する。
character YAML は短プロンプトで `claude` が安定して速いため、`tools/character/core/master.py` の `engine="auto"` だけは `claude` を優先する。
どちらも、環境変数で先頭候補を切り替えられる。

## 6. Environment Variables

- `LILIA_DEFAULT_ENGINE`: 一般生成での `auto` 優先 engine。未設定時は `codex`。
- `LILIA_CHARACTER_ENGINE`: character YAML 生成での `auto` 優先 engine。未設定時は `claude`。
- `LILIA_CODEX_REASONING_EFFORT`: `codex exec` の reasoning effort。未設定時は `low`。
- `LILIA_ENGINE_TIMEOUT_SECONDS`: LLM CLI 呼び出し timeout 秒。未設定時は `600`。

`codex` は `codex exec --cd <empty-temp-dir> --skip-git-repo-check --sandbox read-only --color never -c model_reasoning_effort=<value> -` を使い、prompt は stdin から渡す。
`claude` は `claude -p --permission-mode dontAsk` を使い、prompt は stdin から渡す。

## codex の cwd 自動 context 読み込み問題

`codex exec --cd <path>` は、`--cd` 配下のファイルを自動で context に取り込む挙動がある。
`--cd` に LILIA repo root を渡すと、docs / prompt / templates の Markdown 群まで読み込まれ、数千トークンの生成promptが数万トークン規模に膨張する。
このため profile / spine / downstream の生成が極端に遅くなる。

対策として、`tools/common/engine_runner.py` はモジュールロード時に空の一時ディレクトリを1つだけ作成し、`codex exec --cd` には常にその空ディレクトリを渡す。
一時ディレクトリは process 終了時に `atexit` で削除する。
空ディレクトリは git repository ではないため、`codex exec` には `--skip-git-repo-check` も渡す。

副作用として、`codex` の sandbox は空ディレクトリを基準にするため、`codex` に LILIA repo 内のファイルを直接読ませる運用はできない。
LILIA の生成経路は prompt と stdin だけで完結する設計なので、この副作用は許容する。

## 7. Timeout / Failure

既定 timeout は軽量MVPでは 600 秒とする。
必要な場合だけ `LILIA_ENGINE_TIMEOUT_SECONDS` で変更する。

timeout、CLI未検出、空stdout、非0終了は区別して扱う。
generator はそれを受けて、再試行、fallback、hard-fail のどれにするかを判断する。

timeout時は、POSIX では process group 全体へ SIGTERM を送り、5秒後も残る場合は SIGKILL する。
親processだけでなく、孫processとして残りやすい実LLM呼び出しも終了対象にする。
生成に失敗した壊れた成果物は保存しない。

## 8. Generator Boundary

各 generator は、Engine Runner の出力をそのまま正本にしない。

最低限、以下を守る。

- stdoutを parse する。
- schema / required section / literal混入 / 文崩壊などを validator で見る。
- invalid時は必要に応じて再試行する。
- 3回失敗したら hard-fail し、壊れたファイルを保存しない。
- prompt本文やAI出力本文を巨大ログとして保存しない。

Engine Runner は「出力を得る」まで。
LILIAとして採用できるかは generator / validator が判断する。

## 9. apply-newgame Checkpoint

`./lilia apply-newgame` は `session.json` の `apply_newgame_phase` で再開位置を持つ。

- `pending`: character YAML 生成前。
- `character_yaml_generated`: `lilia/main/character.yaml` は保存済み。profile 生成から再開する。
- `profile_generated`: `lilia/main/profile.md` まで保存済み。spine 生成から再開する。
- `spines_generated`: `current/story_spine.md` と `story/relationship_spine.md` まで保存済み。downstream docs 生成から再開する。
- `documents_generated`: downstream docs を生成済み。最終完了直前の内部 phase。
- `complete`: 初期生成完了。やり直す場合は `--force` を使う。

各段階は成功直後にファイルを書き出し、phase を進める。
`--force` は既存生成物を消して `pending` から再実行する。

## 10. Play Mode Boundary

Play Mode中の通常入力に対して、Engine Runner を保存更新やstate編集のために勝手に起動しない。

起動してよい場面:

- `apply-newgame` の初期生成。
- Save Modeで明示された `apply-turn` 系の生成補助。
- 人間が明示した検証・再生成。

通常会話では、まずLILIA / GMの本文を返す。
Engine Runner の実行ログ、engine名、fallback事情、validator事情を作中本文に出さない。

## 11. 採用元

- MIRA: engine選択とAI生成補助の分離。
- inner-galge: Markdown stateを正本にし、生成物をvalidatorで確認してから採用する運用。
- LIRIA: session構造、apply-newgame、save/resume、archive/logの考え方。

## 12. 採用しないもの

- MIRAのproxy / web research / bench。
- inner-galgeの複数キャラ前提運用。
- LIRIAのAI Harness、自動プレイ、大量ログ解析、production CI。
- runner内で人格、関係、物語内容を判断すること。
- Play Mode中に毎ターンAI生成と保存更新を走らせること。

## 13. MVP Passing Conditions

- character / profile / spine / downstream docs が同じ runner を使える。
- `auto` の候補順と timeout が環境変数で最小調整できる。
- CLI timeout時に子processが残らない。
- generator側の validator / hard-fail 方針が保たれている。
- Play Mode / Save Mode の境界を壊していない。
