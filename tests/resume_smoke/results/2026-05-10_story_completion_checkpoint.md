# Story Completion Checkpoint Smoke - 2026-05-10

## Purpose

ARC-001 / ARC-002 minimal check.

Verify that AI Playtest can report lightweight Story Completion Status and a single Next Story Arc Candidate, then carry the candidate into `checkpoint_turn_update.md` / `apply-turn --dry-run` without applying it to source saves.

## Command

```bash
./lilia ai-playtest smoke_three_hook_20260510 --persona normal --turns 10 --engine auto --judge --quiet --apply-turn-checkpoint
```

## Run

- run_dir: `playtests/runs/20260510_113104_normal_smoke_three_hook_20260510`
- source_session: `saves/smoke_three_hook_20260510`
- run_session: `playtests/runs/20260510_113104_normal_smoke_three_hook_20260510/session`
- persona: `normal`
- turns_completed: 10
- engine: `codex`

## Report Result

- judge_result: `FAIL`
- reason: Arc Closure / Scene Progression failed because Turn 5-6 had enough closure signals, but the scene continued through Turn 10 with repeated afterglow.
- story_completion_status: `closure_candidate`
- recommended_next_arc_candidate: `翌朝七時半の受け取りと時計の状態確認`
- suggested_active_hook_type: `life`
- suggested_story_function: `約束の履行と信頼の初期確認`
- should_apply_now: `false`
- checkpoint_only: `true`

## Closure Candidate

- closure_candidate_turns: `5, 6`
- possible_next_hook_type: `life`
- possible_next_question: `翌朝七時半、佐伯は呼び鈴を押して時計を受け取れるか`
- recommended_closure_action: `Turn6で夜を閉じ、次GMは翌朝の店前から始める`

## Checkpoint Artifacts

- `checkpoint_turn_update.md`: created.
- `checkpoint_apply_turn_dry_run.md`: created.
- `checkpoint_summary.md`: created.
- `report.md`: includes Story Completion / Next Story Arc Candidate section and Save Checkpoint summary.

`checkpoint_turn_update.md` included:

- `closure_candidate_used: true`
- `story_completion_used: true`
- `## next_hook`
- `## hook_updates`
- `story_completion_status: closure_candidate`
- `next_arc_candidate: 翌朝七時半の受け取りと時計の状態確認`

## Dry Run

- dry_run_result: `PASS`
- apply_turn_executed: `false`
- dry_run: `true`

Would update:

- `current/scene.md`
- `current/event_card.md`
- `current/hotset.md`
- `story/story_deck.md`

No real `apply-turn` was executed.

## Source Save Safety

- The source session under `saves/smoke_three_hook_20260510` was not modified by the checkpoint.
- The autosave counter and checkpoint files were produced under the playtest run copy only.

## Observations

- Story Completion Status is now present in the AI Playtest report.
- Next Story Arc Candidate is a single candidate, not a 3-choice UI.
- The candidate is checkpoint-only and does not automatically switch Active Hook.
- The checkpoint candidate can be checked by dry-run before any human-reviewed real apply-turn.
- Play Mode transcript did not expose `story_completion_status`, `next_arc_candidate`, or hook management fields as player-facing text.

## Follow-Up

- ARC-001 / ARC-002 can move to `review` candidate status because lightweight detection and checkpoint candidate generation now have test and smoke evidence.
- Full story arc application remains intentionally unimplemented.
- A later task should verify a human-reviewed real `turn_update.md` followed by resume first turn.
