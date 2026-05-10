# AI Playtest Arc Closure Candidate Smoke - 2026-05-10

## Scope

- Task: report closure candidate / next active hook candidate before Arc Closure / Story Continuation implementation.
- Source session: `smoke_three_hook_20260510`
- Persona: `normal`
- Result: PASS for reporting plumbing, FAIL evidence for actual closure drift.

This smoke records detection and reporting only.
It does not auto-generate a story arc, auto-switch Active Hook, or apply a turn update.

## Command

```bash
./lilia ai-playtest smoke_three_hook_20260510 \
  --persona normal \
  --turns 10 \
  --engine auto \
  --judge \
  --quiet \
  --apply-turn-checkpoint
```

## Run

- Run dir: `playtests/runs/20260510_104852_normal_smoke_three_hook_20260510`
- Transcript: `playtests/runs/20260510_104852_normal_smoke_three_hook_20260510/transcript.md`
- Report: `playtests/runs/20260510_104852_normal_smoke_three_hook_20260510/report.md`

## Report Result

- Judge result: `FAIL`
- `arc_closure_scene_progression`: `2/5`
- `autosave_required`: `true`
- `checkpoint_mode`: `dry-run`
- `apply_turn_executed`: `false`
- `apply-turn` dry-run result: `PASS`

## Closure Candidate Reporting

The report rendered the new section:

```text
## Closure Candidates / Next Active Hook Candidate
```

Recorded candidate:

| Closure turns | Reason | Next hook | Next question | Risk if continued | Recommended action |
|---|---|---|---|---|---|
| 6, 7 | 店を出て戸が閉まり、明日昼過ぎの電話という次入口が成立している | relationship | 翌日昼過ぎ、澪からの電話で時計の状態をどう告げられるか | 同じ余韻モチーフの反復で停滞し、次行動の入口がぼやける | Turn 6で退店を締め、次sceneを翌日の電話に送る |

The closure candidate turns are grouped, and the next Active Hook candidate is one hook only.
No automatic Active Hook switch or story arc generation was performed.

## Boundary Checks

- Report metadata includes closure candidate and checkpoint terms, as expected.
- Play Mode transcript did not expose `closure_candidate`, `possible_next_hook_type`, `hook_id`, `current_function`, or `candidate_id`.
- Checkpoint metadata remained runner metadata after the final scene tick, not GM Play Mode text.
- The run session is under `playtests/runs/.../session`; the source `saves/smoke_three_hook_20260510` session was not updated by this smoke.

## Observed Issues

- Closure drift remains a real Play Mode quality issue: Turn 6/7 could close, but the same scene residue continued until the 10-turn checkpoint.
- The report now identifies a possible relationship-hook handoff, but runtime does not yet close the scene or switch Active Hook automatically.

## Next Tasks

- Use the reported closure candidate as input for ARC-010: closure-to-hook connection.
- Keep Story Completion / Next Story Arc generation out of this step until closure handoff is stable.
- Continue to treat `apply-turn` checkpoint artifacts as review material only; do not apply automatically.
