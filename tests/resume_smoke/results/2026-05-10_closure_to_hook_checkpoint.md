# AI Playtest Closure-to-Hook Checkpoint Smoke - 2026-05-10

## Scope

- Task: ARC-010 checkpoint bridge from closure candidate to `turn_update` candidate.
- Source session: `smoke_three_hook_20260510`
- Persona: `normal`
- Result: PASS for checkpoint candidate generation and dry-run safety.

This smoke verifies review artifacts only.
It does not apply `turn_update.md`, switch Active Hook, or generate a story arc.

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

- Run dir: `playtests/runs/20260510_110939_normal_smoke_three_hook_20260510`
- Transcript: `playtests/runs/20260510_110939_normal_smoke_three_hook_20260510/transcript.md`
- Report: `playtests/runs/20260510_110939_normal_smoke_three_hook_20260510/report.md`
- Candidate: `playtests/runs/20260510_110939_normal_smoke_three_hook_20260510/checkpoint_turn_update.md`
- Dry-run: `playtests/runs/20260510_110939_normal_smoke_three_hook_20260510/checkpoint_apply_turn_dry_run.md`

## Judge / Closure Candidate

- Judge result: `PASS`
- `arc_closure_scene_progression`: `4/5`
- Closure candidate turn: `7`
- Next hook type: `main`
- Next question: `八時三十一分の非通知は、時計停止とどう繋がるのか`
- Recommended action: `次の着信か記録完了を契機に、帰路または翌日の連絡へ渡す`

## Checkpoint Candidate

`checkpoint_turn_update.md` was regenerated after judge and includes:

- `closure_candidate_used: true`
- `## next_hook`
- `## hook_updates`
- `update_target: candidate`
- `promotion_condition`: active stateへ昇格するのは、人間が transcript を確認し、scene / event_card / hotset が同じ入口へ揃う時だけ
- `grounding_guard`: Candidateのままではactive eventとして使わない。保存にない具体手がかりを足さない

The candidate is still a review skeleton and says not to apply it as-is.

## Dry-Run Result

- `dry_run_result: PASS`
- Sections detected:
  - `next_hook`
  - `hook_updates`
- Would update:
  - `current/scene.md`
  - `current/event_card.md`
  - `current/hotset.md`
  - `story/story_deck.md`
- `apply_turn_executed: false`

The dry-run did not reset autosave counters, did not write memory / relationship / beliefs / event_card / hook state, and did not mutate the source `saves/smoke_three_hook_20260510` session.

## Report Fields

`report.md` includes:

- `closure_candidate_used: true`
- `next_hook_candidate_path: playtests/runs/20260510_110939_normal_smoke_three_hook_20260510/checkpoint_turn_update.md`
- `hook_updates_candidate_included: true`
- `dry_run_result: PASS`
- `apply_turn_executed: false`

## Boundary Checks

- Play Mode transcript does not expose `closure_candidate`, `hook_updates`, `hook_id`, `current_function`, or `candidate_id`.
- Checkpoint metadata appears only after `scene_tick` as runner metadata.
- The candidate uses one next hook candidate, not a 3-hook choice UI.
- The candidate does not perform automatic Active Hook switching.
- The candidate does not auto-generate a story arc.

## Remaining Work

- Replace review skeleton with a human-reviewed Save Mode update before real apply-turn.
- Verify real apply-turn / resume first turn in a separate smoke.
- Implement runtime closure-to-hook handoff only after scene / event_card / hotset active state can be generated safely.
