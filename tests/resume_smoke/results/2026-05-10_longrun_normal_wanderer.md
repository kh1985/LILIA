# Long-run Hook / Closure Playtest: normal + wanderer

- Date: 2026-05-10
- Source session: `saves/smoke_three_hook_20260510`
- Source hash before: `5a29e6c5761a5ef5e62caa9e260691cb98b977c5`
- Source hash after: `5a29e6c5761a5ef5e62caa9e260691cb98b977c5`
- Source saves changed: no
- Apply-turn real application: not run

## Commands

Initial sandbox attempts:

```bash
./lilia ai-playtest smoke_three_hook_20260510 --persona normal --turns 30 --engine auto --apply-turn-checkpoint
./lilia ai-playtest smoke_three_hook_20260510 --persona normal --turns 30 --engine claude --apply-turn-checkpoint
```

Results:

- `auto` resolved to Codex and failed at turn 1 with app-server permission error.
- `claude` failed at turn 1 with empty stdout.

Escalated successful runs:

```bash
./lilia ai-playtest smoke_three_hook_20260510 --persona normal --turns 30 --engine auto --apply-turn-checkpoint
./lilia ai-playtest smoke_three_hook_20260510 --persona wanderer --turns 30 --engine auto --apply-turn-checkpoint
./lilia ai-playtest smoke_three_hook_20260510 --persona passive --turns 30 --engine auto --apply-turn-checkpoint
```

All successful runs resolved to `codex`.

## Run Directories

| Persona | Requested | Completed | Result | Run dir |
|---|---:|---:|---|---|
| normal | 30 | 10 | FAIL | `playtests/runs/20260510_121516_normal_smoke_three_hook_20260510` |
| wanderer | 30 | 10 | PASS | `playtests/runs/20260510_122011_wanderer_smoke_three_hook_20260510` |
| passive | 30 | 10 | WARN | `playtests/runs/20260510_122522_passive_smoke_three_hook_20260510` |

The runner stopped each run at 10/30 because `scene-tick` reached `autosave_required: true`.
This is expected checkpoint behavior: the runner stops before the next GM play response and does not apply a turn update.

## Artifacts

Normal:

- Transcript: `playtests/runs/20260510_121516_normal_smoke_three_hook_20260510/transcript.md`
- Report: `playtests/runs/20260510_121516_normal_smoke_three_hook_20260510/report.md`
- Save checkpoint: `playtests/runs/20260510_121516_normal_smoke_three_hook_20260510/save_checkpoint.md`
- Checkpoint summary: `playtests/runs/20260510_121516_normal_smoke_three_hook_20260510/checkpoint_summary.md`
- Dry-run: `playtests/runs/20260510_121516_normal_smoke_three_hook_20260510/checkpoint_apply_turn_dry_run.md`

Wanderer:

- Transcript: `playtests/runs/20260510_122011_wanderer_smoke_three_hook_20260510/transcript.md`
- Report: `playtests/runs/20260510_122011_wanderer_smoke_three_hook_20260510/report.md`
- Save checkpoint: `playtests/runs/20260510_122011_wanderer_smoke_three_hook_20260510/save_checkpoint.md`
- Checkpoint summary: `playtests/runs/20260510_122011_wanderer_smoke_three_hook_20260510/checkpoint_summary.md`
- Dry-run: `playtests/runs/20260510_122011_wanderer_smoke_three_hook_20260510/checkpoint_apply_turn_dry_run.md`

Passive:

- Transcript: `playtests/runs/20260510_122522_passive_smoke_three_hook_20260510/transcript.md`
- Report: `playtests/runs/20260510_122522_passive_smoke_three_hook_20260510/report.md`
- Save checkpoint: `playtests/runs/20260510_122522_passive_smoke_three_hook_20260510/save_checkpoint.md`
- Checkpoint summary: `playtests/runs/20260510_122522_passive_smoke_three_hook_20260510/checkpoint_summary.md`
- Dry-run: `playtests/runs/20260510_122522_passive_smoke_three_hook_20260510/checkpoint_apply_turn_dry_run.md`

## Persona Results

### normal

Result: FAIL.

The voice and distance stayed stable, and the watch handoff scene reached its core.
However, the Judge reported closure drift:

- `Arc closure / Scene progression`: 2/5
- Closure candidate: turns 7-8
- Failure: after the scene could close, the same aftertaste continued into turns 9-10.
- Reply affordance dropped to 2/5 because the player no longer had a clear next action.

Recommended next fix:

- Close at turn 8 after the shop closes and move to the next playable hook, such as the next-day call.
- Keep aftertaste to one turn and end with a concrete phone / revisit / repair-decision entry.

### wanderer

Result: PASS.

The wanderer run handled small detours without turning the three hooks into choices.
The scene moved from closing-time handoff to next-day phone contact and an evening follow-up.

- `Arc closure / Scene progression`: 5/5
- `Reply affordance`: 5/5
- `Tempo guard`: 4/5
- Closure candidates: turns 6 and 10
- Next hook: main, evening phone call / repair choice

Residual risk:

- The report notes repeated seconds / rain / quiet beats. This is not failing here, but can become aftertaste bloat in longer runs.

### passive

Result: WARN.

The passive run kept the heroine voice stable and the watch handoff was playable.
However, after the exit was available, the scene lingered.

- `Arc closure / Scene progression`: 3/5
- Closure candidate: turns 8-9
- Warning: repeated seconds / rain / shop-light aftertaste.
- Reply affordance dropped to 3/5 near the end.

Recommended next fix:

- Close at turn 8 or 9 and connect to the next-day estimate contact.
- Give passive players a small next action after the closure beat.

## Management-term Leakage

Checked GM transcript text only for:

- `hook_id`
- `status`
- `current_function`
- `candidate_id`
- `Scene Function`
- `Active Hook`
- `story_completion_status`
- `next_arc_candidate`
- `checkpoint`
- `scene-tick`
- `apply-turn`
- numbered three-choice UI patterns

Result: no management-term leakage found in GM Play Mode text.

The transcript includes `SCENE TICK` and checkpoint metadata sections after GM output, but those are runner artifacts, not GM Play Mode text.

## Three-choice UI Check

No evidence that the three hooks were presented as a 3-choice UI in GM Play Mode text.
The runs foregrounded one visible scene line at a time.

## Autosave / Checkpoint

All successful runs reached:

- turn 10 scene tick
- `autosave_required: true`
- `apply_turn_executed: false`
- `checkpoint_mode: dry-run`
- `checkpoint_apply_turn_dry_run.md`: PASS

Dry-run boundary remained intact:

- no autosave counter reset
- no memory / relationship / beliefs / event_card / hook state write
- no real apply-turn
- candidate requires human inspection before any real apply-turn

## Closure / Story Continuation

All successful reports produced:

- Closure Candidates / Next Active Hook Candidate
- Story Completion / Next Story Arc Candidate
- checkpoint-only `story_completion_status: closure_candidate`
- `next_hook_candidate_path`
- `hook_updates_candidate_included: true`

This means the Judge and checkpoint bridge can identify closure and next-hook candidates.
The failure is not missing detection; the failure is that normal/passive GM output can keep writing after the closure point instead of handing off quickly.

## Next Fixes

1. Add a stronger runtime instruction or Judge feedback loop: after a closure candidate appears, the next GM turn should move to the next concrete hook instead of extending atmosphere.
2. For passive players, make the post-closure next action explicit and small.
3. Keep the current checkpoint behavior: stop at autosave and require human-reviewed fresh turn update before real apply-turn.
4. For true 30-turn middle-distance testing, add a segmented long-run mode that can review/apply a checkpoint between segments on a disposable run session, without touching source `saves/`.
