# Checkpoint Turn Update Quality Smoke - 2026-05-10

## Purpose

Improve the pre-human-review quality of `checkpoint_turn_update.md` so that applying a checkpoint candidate to a playtest run copy does not leave mechanical wording in active resume state.

This smoke verifies:

- `checkpoint_turn_update.md` uses natural Save Mode wording for state-facing values.
- `closure入口`, `Turn6...`, `story_completion_status`, `recommended_next_arc_candidate`, and related management wording do not enter active state.
- `apply-turn` is only applied to a playtest run copy, never to source `saves/`.
- `validate-session`, `resume --prompt-only`, and `resume --run` still work after applying the checkpoint candidate to the run copy.

## Source Session Safety

Source session:

- `saves/smoke_three_hook_20260510`

Source hash was captured before the run:

```bash
find saves/smoke_three_hook_20260510 -type f -print0 | sort -z | xargs -0 shasum > /tmp/lilia_source_saves_before.sha
```

After checkpoint generation and run-copy apply-turn checks:

```bash
find saves/smoke_three_hook_20260510 -type f -print0 | sort -z | xargs -0 shasum > /tmp/lilia_source_saves_after_apply.sha
diff -u /tmp/lilia_source_saves_before.sha /tmp/lilia_source_saves_after_apply.sha
```

Result:

- No diff.
- Source `saves/` was not changed.

## AI Playtest Checkpoint Run

Command:

```bash
./lilia ai-playtest smoke_three_hook_20260510 --persona normal --turns 10 --engine auto --judge --quiet --apply-turn-checkpoint
```

Run dir:

- `playtests/runs/20260510_120729_normal_smoke_three_hook_20260510`

Artifacts:

- `checkpoint_turn_update.md`
- `checkpoint_apply_turn_dry_run.md`
- `checkpoint_summary.md`
- `report.md`
- `transcript.md`
- `transcript.jsonl`

Checkpoint candidate excerpt:

```md
## next_hook

翌朝、七瀬から時計の内部状態について電話が来る。

## hook_updates

- candidate_id: handoff_main_4_5_6
- hook_type: main
- update_target: candidate
- status: pending
- function_candidate: 預けた時計の問題を明らかにし、修理方針を選ばせる
- visible_entry: 翌朝、七瀬から時計の内部状態について電話が来る。
- promotion_condition: 人間が直近のやりとりを確認し、scene / event_card / hotset が同じ入口へ揃う時だけactive stateへ昇格する。
- grounding_guard: Candidateのままではactive eventとして使わない。保存にない具体手がかりを足さない。
- reason: 時計を預けるsceneの核は成立し、次は見立て電話へ渡せる。
- risk_if_continued: 同じ余韻と内省が続き、進行量が薄くなる。
```

Candidate grep:

```bash
rg -n "closure入口|Turn[0-9]|story_completion_status|checkpoint_only|recommended_next_arc_candidate|next_arc_candidate|closure_candidate_used|story_completion_used|Judge detected|review:" \
  playtests/runs/20260510_120729_normal_smoke_three_hook_20260510/checkpoint_turn_update.md
```

Result:

- No matches.

Dry-run result:

- `dry_run_result: PASS`
- Sections: `next_hook`, `hook_updates`
- Would update:
  - `current/scene.md`
  - `current/event_card.md`
  - `current/hotset.md`
  - `story/story_deck.md`

## Run-Copy Apply-Turn Smoke

Because the CLI accepts normal session names, the smoke used the existing test pattern of temporarily overriding `resolve_session` so a playtest run copy can be targeted directly.

Run-copy session:

- `playtests/runs/20260510_120729_normal_smoke_three_hook_20260510/session_quality_reapply_v4`

Setup:

```bash
RUN=playtests/runs/20260510_120729_normal_smoke_three_hook_20260510
TARGET="$RUN/session_quality_reapply_v4"
rm -rf "$TARGET"
mkdir -p "$TARGET"
rsync -a saves/smoke_three_hook_20260510/ "$TARGET"/
```

Apply / validate:

```bash
python - <<'PY'
from importlib.machinery import SourceFileLoader
import importlib.util
from pathlib import Path

ROOT = Path.cwd()
run = Path("playtests/runs/20260510_120729_normal_smoke_three_hook_20260510")
session = run / "session_quality_reapply_v4"
loader = SourceFileLoader("lilia_checkpoint_quality_reapply_v4", str(ROOT / "lilia"))
spec = importlib.util.spec_from_loader("lilia_checkpoint_quality_reapply_v4", loader)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.resolve_session = lambda name=None: (ROOT / str(name)).resolve()
module.command_apply_turn([str(session), str(run / "checkpoint_turn_update.md")])
module.command_validate_session([str(session)])
PY
```

Output summary:

```text
applied: playtests/runs/20260510_120729_normal_smoke_three_hook_20260510/checkpoint_turn_update.md
session: playtests/runs/20260510_120729_normal_smoke_three_hook_20260510/session_quality_reapply_v4
updated:
  current/scene.md
  story/story_deck.md
  current/event_card.md
  current/hotset.md
  session.json
state consistency: PASS
```

## Active State Check

Active state grep:

```bash
rg -n "closure入口|Turn[0-9]|story_completion_status|checkpoint_only|recommended_next_arc_candidate|next_arc_candidate|closure_candidate|review:|Judge detected|保存済みnext_hook|next_hookに明示|next_hook候補|保存済みのnext_hook" \
  "$TARGET/current/scene.md" \
  "$TARGET/current/event_card.md" \
  "$TARGET/current/hotset.md" \
  "$TARGET/story/story_deck.md"
```

Result:

- No matches.

Active state now uses natural wording:

- `保存された次の入口`
- `前sceneは一度閉じ、保存された次の入口から再開する`
- `保存された次の入口を次sceneの入口として前景化する`

The promoted `event_card` also includes the stronger Grounding Guard:

```text
電話や訪問などの入口でも、保存にない着信表示、連絡先の識別、場所の固有情報、控え類、手元の補助記録をresume 1ターン目の既存情報として描写しない。
```

## Resume Checks

Prompt-only command:

```bash
python - <<'PY' > /tmp/lilia_checkpoint_quality_resume_prompt_v4.txt
from importlib.machinery import SourceFileLoader
import importlib.util
from pathlib import Path

ROOT = Path.cwd()
loader = SourceFileLoader("lilia_checkpoint_quality_resume_prompt_v4", str(ROOT / "lilia"))
spec = importlib.util.spec_from_loader("lilia_checkpoint_quality_resume_prompt_v4", loader)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.resolve_session = lambda name=None: (ROOT / str(name)).resolve()
module.command_resume(["playtests/runs/20260510_120729_normal_smoke_three_hook_20260510/session_quality_reapply_v4", "--prompt-only"])
PY
```

Prompt-only grep:

```bash
rg -n "closure入口|Turn[0-9]|story_completion_status|checkpoint_only|recommended_next_arc_candidate|next_arc_candidate|closure_candidate|review:|Judge detected|保存済みnext_hook|next_hookに明示|next_hook候補|保存済みのnext_hook" \
  /tmp/lilia_checkpoint_quality_resume_prompt_v4.txt
```

Result:

- No matches.

Resume run command:

```bash
python - <<'PY' > /tmp/lilia_checkpoint_quality_resume_run_v4.txt
from importlib.machinery import SourceFileLoader
import importlib.util
from pathlib import Path

ROOT = Path.cwd()
loader = SourceFileLoader("lilia_checkpoint_quality_resume_run_v4", str(ROOT / "lilia"))
spec = importlib.util.spec_from_loader("lilia_checkpoint_quality_resume_run_v4", loader)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.resolve_session = lambda name=None: (ROOT / str(name)).resolve()
module.command_resume(["playtests/runs/20260510_120729_normal_smoke_three_hook_20260510/session_quality_reapply_v4", "--run", "--engine", "auto"])
PY
```

Resume output summary:

- Started from the next entrance: a morning call about the watch state.
- Did not expose validator / score / diff / hook management terms.
- Did not include the previously problematic thin props:
  - `手元のメモ`
  - `番号`
  - `昨日の控え`
  - `店名`
  - `住所`
  - `鉛筆`
  - `薄紙`
  - `写真の裏`

Grep:

```bash
rg -n "closure入口|Turn[0-9]|story_completion_status|checkpoint_only|recommended_next_arc_candidate|next_arc_candidate|closure_candidate|candidate_id|hook_id|current_function|validator|FAIL|diff|score|rubric|review:|Judge detected|保存済みnext_hook|next_hookに明示|next_hook候補|保存済みのnext_hook" \
  /tmp/lilia_checkpoint_quality_resume_run_v4.txt

rg -n "手元のメモ|番号|昨日の控え|店名|住所|鉛筆|薄紙|写真の裏|着信画面|登録名" \
  /tmp/lilia_checkpoint_quality_resume_run_v4.txt
```

Result:

- No matches.

## Notes

An intermediate v2 check still produced `まだ登録されていない番号` from the phone-call entrance. The implementation was tightened by making the promoted active event_card forbid unsaved call-screen, contact-identity, place-identity, and hand-note details as existing resume-turn-1 facts. The v4 retry was clean.

The checkpoint candidate is still a review candidate. It is safer to inspect before applying, but if a human does apply it to a playtest run copy, the active state no longer receives the previous mechanical wording.

## Next Work

- Keep source `saves/` protected; checkpoint apply should stay run-copy only unless a human explicitly chooses a real save update.
- Continue monitoring resume 1st turn for thin inferred props when contact/travel/checking scenes are generated.
- If thin props recur, add a lightweight resume-output QA grep for `番号 / 店名 / 住所 / 控え / メモ` to checkpoint smoke.
