# Checkpoint Apply-Turn Smoke - 2026-05-10

## Purpose

AI-007 / ARC follow-up.

Apply a generated `checkpoint_turn_update.md` to a playtest run session copy only, then verify `validate-session`, `resume --prompt-only`, and `resume --run`.

This smoke intentionally does **not** modify `saves/`.

## Target

- source_session: `saves/smoke_three_hook_20260510`
- run_dir: `playtests/runs/20260510_113104_normal_smoke_three_hook_20260510`
- run_session: `playtests/runs/20260510_113104_normal_smoke_three_hook_20260510/session`
- turn_update: `playtests/runs/20260510_113104_normal_smoke_three_hook_20260510/checkpoint_turn_update.md`

The target run is the ARC-001 / ARC-002 smoke that produced:

- `story_completion_status: closure_candidate`
- `recommended_next_arc_candidate: 翌朝七時半の受け取りと時計の状態確認`
- `closure_candidate_used: true`
- `story_completion_used: true`
- `dry_run_result: PASS`

## Source Safety Baseline

Before applying the checkpoint, source session hashes were recorded with:

```bash
find saves/smoke_three_hook_20260510 -type f -print | sort | xargs shasum -a 256 > /tmp/lilia_source_before.sha
```

After apply-turn and resume checks:

```bash
find saves/smoke_three_hook_20260510 -type f -print | sort | xargs shasum -a 256 > /tmp/lilia_source_after_resume.sha
diff -u /tmp/lilia_source_before.sha /tmp/lilia_source_after_resume.sha
```

Result: no diff. Source `saves/smoke_three_hook_20260510` was not modified.

## Apply-Turn Command

`./lilia apply-turn` currently resolves only `saves/<session_name>` style session names, so this smoke loaded the launcher and routed `resolve_session` directly to the playtest run session path.

```bash
python - <<'PY'
from importlib.machinery import SourceFileLoader
import importlib.util
from pathlib import Path

ROOT = Path.cwd()
loader = SourceFileLoader("lilia_launcher_smoke", str(ROOT / "lilia"))
spec = importlib.util.spec_from_loader("lilia_launcher_smoke", loader)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.resolve_session = lambda name=None: (ROOT / name).resolve()
module.command_apply_turn([
    "playtests/runs/20260510_113104_normal_smoke_three_hook_20260510/session",
    "playtests/runs/20260510_113104_normal_smoke_three_hook_20260510/checkpoint_turn_update.md",
])
PY
```

Output summary:

```text
applied: playtests/runs/20260510_113104_normal_smoke_three_hook_20260510/checkpoint_turn_update.md
session: playtests/runs/20260510_113104_normal_smoke_three_hook_20260510/session
updated:
  current/scene.md
  story/story_deck.md
  current/event_card.md
  current/hotset.md
  session.json
```

## Apply-Turn Result

`session.json` after apply:

- `current_phase: active`
- `initialization.first_scene_status: started`
- `autosave.turns_since_save: 0`
- `autosave.autosave_required: false`
- `applied_turn_updates`: contains one fingerprint for `checkpoint_turn_update.md`

Run session hash diff showed only the expected files changed:

- `current/scene.md`
- `current/event_card.md`
- `current/hotset.md`
- `story/story_deck.md`
- `session.json`

## Validate-Session

Command:

```bash
python - <<'PY'
from importlib.machinery import SourceFileLoader
import importlib.util
from pathlib import Path

ROOT = Path.cwd()
loader = SourceFileLoader("lilia_launcher_validate_smoke", str(ROOT / "lilia"))
spec = importlib.util.spec_from_loader("lilia_launcher_validate_smoke", loader)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.resolve_session = lambda name=None: (ROOT / name).resolve()
module.command_validate_session([
    "playtests/runs/20260510_113104_normal_smoke_three_hook_20260510/session"
])
PY
```

Result:

```text
state consistency: PASS
```

## Active State After Apply

### `current/scene.md`

The active scene was promoted from the checkpoint next hook:

- next scene: `翌朝七時半の受け取りと時計の状態確認`
- action room: confirm the situation / wait for LILIA's procedure / support the check / confirm boundaries
- `promoted_from_next_hook_at: 2026-05-10T11:55:07+09:00`

### `current/event_card.md`

The top active fields were replaced with a promoted next-hook event:

- `Visible Problem`: next morning 7:30 pickup / watch status check
- `First Concrete Action`: LILIA gives only the situation-confirmation entrance and does not add unstored clues
- `Handles 2-4`: ask / wait / support / boundary
- `Grounding Guard`: present

The old active event was not left at the top of `current/event_card.md`.

### `current/hotset.md`

Hotset points to the same next scene entrance as scene/event_card.

### `story/story_deck.md`

Story deck still contains the Three Hook Spine and Background Hooks.
The checkpoint candidate was added as:

- `Candidate Hook - 2026-05-10T11:55:07+09:00 - closure_life_5_6`
- `Candidate Next Hook - 2026-05-10T11:55:07+09:00`
- `Backgrounded Event Card - 2026-05-10T11:55:07+09:00`

The previous active event was backgrounded into `story/story_deck.md`, not left as the active event_card top.

## Resume Prompt-Only

Command:

```bash
python - <<'PY' > /tmp/lilia_checkpoint_prompt_only.txt
from importlib.machinery import SourceFileLoader
import importlib.util
from pathlib import Path

ROOT = Path.cwd()
loader = SourceFileLoader("lilia_launcher_resume_prompt_smoke", str(ROOT / "lilia"))
spec = importlib.util.spec_from_loader("lilia_launcher_resume_prompt_smoke", loader)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.resolve_session = lambda name=None: (ROOT / name).resolve()
module.command_resume([
    "playtests/runs/20260510_113104_normal_smoke_three_hook_20260510/session",
    "--prompt-only",
])
PY
```

Result:

- Prompt bundle includes the promoted next scene entrance.
- The prompt's current/hotset, current/scene, and current/event_card all point to the same next scene.
- Internal state documents still contain hook fields such as `hook_id` and `candidate_id`, as expected for prompt context.
- Those management terms are not meant to appear in Play Mode text.

## Resume Run

Command:

```bash
python - <<'PY' > /tmp/lilia_checkpoint_resume_run.txt
from importlib.machinery import SourceFileLoader
import importlib.util
from pathlib import Path

ROOT = Path.cwd()
loader = SourceFileLoader("lilia_launcher_resume_run_smoke", str(ROOT / "lilia"))
spec = importlib.util.spec_from_loader("lilia_launcher_resume_run_smoke", loader)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.resolve_session = lambda name=None: (ROOT / name).resolve()
module.command_resume([
    "playtests/runs/20260510_113104_normal_smoke_three_hook_20260510/session",
    "--run",
    "--engine",
    "auto",
])
PY
```

Output summary:

```text
翌朝の駅前は、夜の雨をまだ少しだけ敷石に残していた。

七時半。店のシャッターはまだ半分だけ下りていて、細い隙間から作業台の灯りが漏れている。
...
「……おはようございます」
...
「時計、確認してあります。中へどうぞ。まだ開店前なので、短くなりますけど」
...
作業台の上には、柔らかい布に乗せられた腕時計がひとつ、昨夜よりもまっすぐな向きで置かれていた。
```

Management term grep:

```bash
rg -n "hook_id|story_completion_status|closure_candidate|candidate_id|current_function|validator|FAIL|diff|score|rubric" /tmp/lilia_checkpoint_resume_run.txt
```

Result: no matches.

Resume quality observation:

- Next scene starts from the intended next-hook entrance: next morning / 7:30 / shop front / watch check.
- It does not expose `hook_id`, `story_completion_status`, `closure_candidate`, `candidate_id`, score/rubric, validator, or diff terms in Play Mode text.
- It does not resume from the stale previous closing-time event_card top.

## Issues Found

The checkpoint candidate was intentionally a review skeleton, and applying it as-is leaves some mechanically phrased active-state text:

- `closure入口`
- `Turn6で夜を閉じ...`
- `hook_type: main / relationship / life` in the promoted Active Hook field rather than a concrete single type

The resume output did not leak these management-ish phrases, but a production-quality real `turn_update.md` should be human-reviewed or generated fresh before apply.

Follow-up candidate:

- Generate a cleaner checkpoint apply candidate that removes judge/review phrasing before real apply.
- Let next-hook promotion use the explicit `hook_updates` hook type when available, instead of writing generic `main / relationship / life`.

## Test Results

```bash
python -m pytest tests/test_growth_smoke.py
# 20 passed

python -m pytest tests/test_state_consistency.py
# 7 passed

python -m pytest
# 220 passed, 1 skipped
```

## Conclusion

PASS with caveat.

- checkpoint_turn_update can be applied to the playtest run session copy.
- `validate-session` passes after apply.
- `resume --prompt-only` shows the promoted next scene entrance.
- `resume --run` naturally restarts from the next hook without management term leakage.
- Source `saves/smoke_three_hook_20260510` remained unchanged.
- The applied checkpoint skeleton is mechanically worded, so real release operation should use a cleaned, human-reviewed `turn_update.md`.
