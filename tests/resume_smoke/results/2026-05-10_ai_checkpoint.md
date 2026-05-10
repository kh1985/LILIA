# AI Playtest Apply-Turn Checkpoint Smoke - 2026-05-10

## Scope

- Task: AI-006 apply-turn checkpoint mode.
- Source session: `smoke_three_hook_20260510`
- Persona: `normal`
- Result: PASS for checkpoint plumbing, with Save Mode still requiring human-reviewed turn_update before real apply.

This smoke verifies checkpoint artifacts and dry-run safety only.
It does not mark save/resume or full apply-turn behavior done.

## Command

```bash
./lilia ai-playtest smoke_three_hook_20260510 \
  --persona normal \
  --turns 10 \
  --engine auto \
  --no-judge \
  --quiet \
  --apply-turn-checkpoint
```

## Run

- Run dir: `playtests/runs/20260510_103046_normal_smoke_three_hook_20260510`
- Transcript: `playtests/runs/20260510_103046_normal_smoke_three_hook_20260510/transcript.md`
- JSONL: `playtests/runs/20260510_103046_normal_smoke_three_hook_20260510/transcript.jsonl`

## Checkpoint Result

- `scene-tick` reached `10/10`.
- `autosave_required: true` was recorded.
- The runner stopped before the next GM Play Mode response.
- `apply_turn_executed: false` was recorded in transcript, JSONL, `save_checkpoint.md`, and `report.md`.
- No real `apply-turn` was executed.

Run session autosave after smoke:

```text
{'enabled': True, 'interval_turns': 10, 'turns_since_save': 10, 'autosave_required': True}
```

Source session autosave after smoke:

```text
{'enabled': True, 'interval_turns': 10, 'turns_since_save': 0, 'autosave_required': False}
```

The source `saves/smoke_three_hook_20260510` session was not updated.

## Generated Artifacts

- `save_checkpoint.md`
- `checkpoint_turn_update_prompt.md`
- `checkpoint_turn_update.md`
- `checkpoint_apply_turn_dry_run.md`
- `checkpoint_summary.md`
- `report.md`

`checkpoint_turn_update.md` is a review skeleton, not a finished save update.
It contains only a minimal `## state` review-required section so the dry-run path can be exercised safely.

## Dry-Run Result

- Result: PASS
- Candidate: `playtests/runs/20260510_103046_normal_smoke_three_hook_20260510/checkpoint_turn_update.md`
- Dry-run result: `playtests/runs/20260510_103046_normal_smoke_three_hook_20260510/checkpoint_apply_turn_dry_run.md`
- Would update: `lilia/main/state.md`
- Did not reset autosave counter.
- Did not write memory / relationship / beliefs / event_card / hook state.
- Did not add `applied_turn_updates` to `session.json`.

## Transcript / Boundary Check

- Scene tick metadata appears as runner metadata, not Play Mode text.
- Apply-turn checkpoint metadata appears after the final scene tick, not inside GM output.
- The turn 10 GM output ends before checkpoint metadata.
- No PLAYER turn is written after checkpoint.
- A grep for management terms matched only runner metadata lines such as `checkpoint`, `apply-turn`, `scene-tick`, `dry_run_result`, not GM / PLAYER Play Mode text.

## Interpretation

AI-006 now has a safe checkpoint mode:

- Default mode still stops at `autosave_required: true` without real apply-turn.
- `--apply-turn-checkpoint` adds review artifacts and a dry-run result.
- Real save application remains a human-reviewed follow-up.

## Remaining Work

- Generate a high-quality fresh `turn_update.md` from checkpoint transcript content instead of using the review skeleton.
- Decide whether future automation should call an LLM to draft the candidate, still behind an explicit flag.
- Connect checkpoint flow to resume validation only after a reviewed update is applied.
- Keep WBS `P-002` / `P-003` unchanged until real apply-turn and resume first voice are verified.
