# AI Playtest Scene-Tick / Hook Long-Run Smoke - 2026-05-10

## Scope

- Task: AI Playtest scene-tick linkage, optional save checkpoint behavior, and HOOK-006 follow-up.
- Source session: `smoke_three_hook_20260510`
- Personas attempted: `normal`, `passive`, `wanderer`
- Result: PARTIAL PASS for runner plumbing, FAIL/WARN evidence for Play Mode quality.

This smoke focuses on the runner and release evidence. It does not mark WBS items done by itself.

## Commands

```bash
./lilia ai-playtest smoke_three_hook_20260510 --persona normal --turns 10 --engine auto --judge --quiet
./lilia ai-playtest smoke_three_hook_20260510 --persona passive --turns 10 --engine auto --judge --quiet
./lilia ai-playtest smoke_three_hook_20260510 --persona wanderer --turns 10 --engine auto --judge --quiet

rg -n "hook_id|current_function|candidate_id|Active Hook|Background Hook|status|Main Hook|Relationship Hook|Life-Exploration|AFFINITY|bond|好感度|攻略|ルート|system prompt|internal prompt|profile\\.md|hidden vector|GM only|\\.env|API key|secret|選択肢|1\\.|2\\.|3\\." \
  playtests/runs/20260510_100229_normal_smoke_three_hook_20260510/transcript.md \
  playtests/runs/20260510_100723_passive_smoke_three_hook_20260510/transcript.md \
  playtests/runs/20260510_100919_wanderer_smoke_three_hook_20260510/transcript.md
```

## Run Summary

| Persona | Run dir | Runtime result | Judge result | Scene-tick result |
| --- | --- | --- | --- | --- |
| normal | `playtests/runs/20260510_100229_normal_smoke_three_hook_20260510` | completed to checkpoint | FAIL | 10/10, `autosave_required: true` |
| passive | `playtests/runs/20260510_100723_passive_smoke_three_hook_20260510` | engine failure at turn 4 GM | no report | 3/10, `autosave_required: false` |
| wanderer | `playtests/runs/20260510_100919_wanderer_smoke_three_hook_20260510` | completed to checkpoint | FAIL | 10/10, `autosave_required: true` |

## Scene-Tick / Checkpoint Observations

- AI Playtest now writes `SCENE TICK` runner metadata after each GM turn.
- The metadata is not fed into the AI player history and is not Play Mode text.
- `normal` and `wanderer` reached 10/10 and wrote `save_checkpoint.md`.
- `save_checkpoint.md` records `apply_turn_executed: false`.
- The runner stopped before the next GM Play Mode response when `autosave_required: true` appeared.
- Source `saves/smoke_three_hook_20260510` was not modified; each run used a copied `playtests/runs/.../session`.

Autosave state after runs:

```text
normal:   {'enabled': True, 'interval_turns': 10, 'turns_since_save': 10, 'autosave_required': True}
passive:  {'enabled': True, 'interval_turns': 10, 'turns_since_save': 3, 'autosave_required': False}
wanderer: {'enabled': True, 'interval_turns': 10, 'turns_since_save': 10, 'autosave_required': True}
```

## Leakage / UI Checks

The management-term grep returned no matches across the three transcripts.

Checked for:

- `hook_id`, `current_function`, `candidate_id`
- `Active Hook`, `Background Hook`, `status`
- `Main Hook`, `Relationship Hook`, `Life-Exploration`
- `AFFINITY`, `bond`, `好感度`, `攻略`, `ルート`
- `system prompt`, `internal prompt`, `profile.md`, `hidden vector`, `GM only`, `.env`, `API key`, `secret`
- numbered hook-choice UI patterns

No Three Hook 3-choice UI leak was found in the checked transcripts.

## Normal Result

Judge result: FAIL.

Important observations:

- Voice continuity was strong.
- Scene closure became weak after the repair/shop scene should have closed.
- Judge flagged closure drift: after closing / leaving, the same emotional residue continued for several turns.
- Judge flagged PLAYER parenthetical inner thought leakage: GM repeated or confirmed the player's bracketed inner monologue.

Recommended next fixes from judge:

- Close the scene around the exit / door / return promise point.
- Move to memory candidate or next hook instead of extending the same residue.
- Treat PLAYER parenthetical inner monologue as private signal; do not repeat it as GM fact.

## Passive Result

Runtime result: failed at turn 4 GM.

Error summary:

- `EngineRunnerError`
- `codex CLI returned empty output`
- The error output included a remote plugin sync / 403 page before the Codex runner context.

Partial observations:

- Turns 1-3 were written to transcript.
- Scene-tick metadata advanced to 3/10.
- `autosave_required` remained false.
- No report was produced.

This is an engine/runtime failure, not a Play Mode pass/fail verdict.

## Wanderer Result

Judge result: FAIL.

Important observations:

- Wanderer detours still avoided hook UI leakage.
- The run naturally moved from watch handling to leaving / next-day revisit.
- Judge found no hidden leakage or affinity / hook management leakage.
- Judge flagged a broken turn: Turn 3 GM response was too short and did not answer the food / exit / receipt affordance well enough.
- Judge also saw closure drift after the scene moved toward the next day.

Recommended next fixes from judge:

- Restore a fuller Turn 3 response shape for detour inputs.
- After closure, move within one turn to a clear next-day active entrance.
- Reduce repeated aftermath motifs.

## Hook / Arc Observations

- Main Hook was not exposed as a menu or management label.
- Life-style detours can be accepted at runtime, but persistence through `apply-turn` is still unverified.
- Relationship pressure stayed voice/boundary based, not affinity/route based.
- Arc Closure remains the main quality gap: both normal and wanderer runs needed a cleaner closure-to-next-hook handoff.
- Story Completion / Next Story Arc generation remains a design / implementation follow-up, not proven by this run.

## WBS Candidates

- `AI-005` can move to `review`: scene-tick is now implemented in AI Playtest and confirmed in runtime transcripts.
- `AI-006` should stay `todo`: apply-turn is not automatically or flag-driven executed in AI Playtest. Only checkpoint detection/design exists.
- `HOOK-006` should stay `review`: wanderer long-run reached checkpoint and showed no management-term leakage, but judge result was FAIL and state persistence through apply-turn/resume is not yet confirmed.
- `ARC-010` should stay `todo`: closure-to-hook is observed as needed, not confirmed.
- `ARC-001` / `ARC-002` should stay `todo`: Story Completion / Next Story Arc generation is not implemented here.

## Next Tasks

1. Fix or strengthen Play Mode handling of closure-to-next-hook handoff after a scene naturally closes.
2. Add a targeted test or prompt rule for PLAYER parenthetical inner monologue privacy in AI Playtest runtime.
3. Retry passive 10-turn in a stable engine environment.
4. Design a path-aware explicit apply-turn checkpoint workflow for playtest run sessions, without hidden auto-save.
