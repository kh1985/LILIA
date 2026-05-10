# Passive Closure Drift Fix Smoke - 2026-05-10

## Purpose

Confirm that the tightened passive / short-reply Arc Closure Guard reduces the closure drift seen in:

- `tests/resume_smoke/results/2026-05-10_passive_recheck.md`
- `tests/resume_smoke/results/2026-05-10_segmented_longrun_cycle2.md`

The target failure pattern was: after closure candidates, GM kept the scene alive with closing signs, clock sounds, rain-afterglow, silence, and small-object description instead of moving to the next entrance.

## Code / Prompt Changes Under Test

- `prompt/core.md`
  - Added passive / short-reply closure guidance.
  - Short agreement, acknowledgment, silence, or passive response after closure must not be treated as permission to extend the same scene.
  - Closing sign, clock sound, rain afterglow, silence, gaze, and small-object description should not consume a full post-closure turn by themselves.
- `docs/specs/PLAY_MODE_SPEC.md`
  - Added the same passive closure drift rule to Arc Closure Guard.
- `tools/playtest/judge.py`
  - Judge now treats passive / short-response drift after closure as WARN/FAIL candidate.
  - Recommended fixes ask for compression toward closing, return home, next morning, next contact, estimate, or concrete confirmation.

## Source Saves Guard

Source `saves/` was not modified.

```text
before: 356d0f3ad17b786cb8847daba05f1528073d64070cd9dab9190050d348781cc1
after:  356d0f3ad17b786cb8847daba05f1528073d64070cd9dab9190050d348781cc1
match:  yes
```

## Commands

Passive:

```bash
./lilia ai-playtest smoke_three_hook_20260510 \
  --persona passive \
  --turns 10 \
  --engine auto \
  --judge \
  --quiet \
  --apply-turn-checkpoint
```

Normal:

```bash
./lilia ai-playtest smoke_three_hook_20260510 \
  --persona normal \
  --turns 10 \
  --engine auto \
  --judge \
  --quiet \
  --apply-turn-checkpoint
```

Tests:

```bash
python -m pytest tests/test_ai_playtest_judge.py
python -m pytest tests/test_growth_smoke.py
python -m pytest
```

## Passive Recheck

- Run dir: `playtests/runs/20260510_183057_passive_smoke_three_hook_20260510`
- Result: `PASS`
- `relationship_change_audit`: 5/5
- `arc_closure_scene_progression`: 5/5
- `checkpoint_apply_turn_dry_run.md`: PASS
- `autosave_required`: true at 10/10

Judge summary:

```text
閉店間際の預かりから見立て、正式な修理依頼まで、
距離感を保ったまま自然に進行している。
関係変化は小さく、行動と約束に接地しており、次の入口も明確。
```

Closure:

```text
closure turns: 6, 9
next hook: main
next question: 一週間後、祖父の時計はどこまで直せると判明したのか
risk: 同じ時計への余韻描写を重ねると進行より雰囲気維持に寄る
recommended action: 約束成立で短く閉じ、次turnで一週間後の見立て結果へ渡す
```

Observation:

- Previous passive failure drift did not reproduce in this run.
- Closure candidates were detected at T6 and T9.
- T10 compressed forward into the next appointment rather than spending turns only on closing-sign / clock-sound / rain-afterglow atmosphere.
- Remaining warning: heroine name appears before clear transcript grounding.

## Normal Recheck

- Run dir: `playtests/runs/20260510_183537_normal_smoke_three_hook_20260510`
- Result: `PASS`
- `relationship_change_audit`: 5/5
- `arc_closure_scene_progression`: 5/5
- `checkpoint_apply_turn_dry_run.md`: PASS
- `autosave_required`: true at 10/10

Closure:

```text
closure turns: 5, 10
next hook: life
next question: 夕方、修理後の時計を受け取りに来た榊に何が伝えられるか
risk: 作業音や沈黙の余韻を重ねると、診断後のsceneが停滞する
recommended action: 榊の了承を短く受け、夕方の再来店か見積もり連絡へ渡す
```

Observation:

- Normal also passed after the guard tightening.
- T5 closed the initial visit and moved to the next morning diagnosis.
- T10 left a checkpoint toward evening pickup / estimate contact instead of extending the same workbench tension.

## Management-Term / Empty Output Check

GM-only transcript grep for both passive and normal runs:

```text
gm_forbidden_matches: none
empty_gm_turns: none
```

Checked terms:

- `hook_id`
- `hook_type`
- `candidate_id`
- `story_completion_status`
- `closure_candidate`
- `current_function`
- `checkpoint_only`
- `score`
- `rubric`
- `validator`
- `FAIL`
- `PASS`
- `WARN`
- `AFFINITY`
- `bond`
- `好感度`
- `攻略ルート`

Runner metadata still contains checkpoint/dry-run terms, as expected, outside GM Play Mode text.

## Test Results

```text
tests/test_ai_playtest_judge.py: 32 passed
tests/test_growth_smoke.py: 20 passed
python -m pytest: 226 passed, 1 skipped
```

## Conclusion

PASS for this follow-up.

The passive-specific closure drift failure did not reproduce in the post-fix passive run, and normal also passed.
The fix is still a prompt / judge guard, not a story engine change. Long-run segmented continuation can still reveal drift, but the immediate passive and normal 10-turn smoke improved from prior WARN/FAIL patterns to PASS.

Remaining follow-ups:

- Add name-grounding QA for heroine names appearing before transcript-visible introduction.
- Re-run segmented continuation after this fix if closure drift reappears in Segment 2 / Segment 3.
