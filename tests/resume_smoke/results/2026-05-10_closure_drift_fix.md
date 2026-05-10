# Arc Closure Drift Follow-up Smoke - 2026-05-10

## Purpose

Verify the minimal Arc Closure Drift guard update against the long-run issue where normal / passive runs kept extending the same aftertaste after closure candidates were already available.

This follow-up focuses on:

- Closing within 1-2 turns after a closure candidate.
- Not adding more of the same tension, footsteps, notifications, presence, silence, gaze, rain, or shop sounds after closure.
- Moving toward one next entrance / next hook candidate.
- Keeping Play Mode text free of judge / score / checkpoint management language.

## Source Safety

Source session:

- `saves/smoke_three_hook_20260510`

Before / after hash check:

```bash
find saves/smoke_three_hook_20260510 -type f -print0 | sort -z | xargs -0 shasum > /tmp/lilia_closure_drift_source_before_v2.sha
find saves/smoke_three_hook_20260510 -type f -print0 | sort -z | xargs -0 shasum > /tmp/lilia_closure_drift_source_after_v2.sha
diff -u /tmp/lilia_closure_drift_source_before_v2.sha /tmp/lilia_closure_drift_source_after_v2.sha
```

Result:

- No diff.
- Source `saves/` was not changed.
- No real `apply-turn` was executed.

## Implementation Summary

Updated runtime / spec / judge guidance:

- `prompt/core.md`: closure candidates now hard-stop repeated tension. If the player only continues with return-home, waiting, inner monologue, or aftertaste input, the GM should not keep the same scene alive; it should briefly acknowledge visible action and hand off to the next contact / revisit / promise / unresolved card.
- `docs/specs/PLAY_MODE_SPEC.md`: closure drift is now explicitly defined as adding the same tension, footsteps, notifications, presence, silence, gaze, rain, or shop sounds after closure.
- `tools/playtest/judge.py`: Judge now treats closure-candidate-plus-2-turn drift as WARN/FAIL leaning and asks for a concrete turn-to-close and next entrance in `risk_if_continued`, `recommended_closure_action`, and `recommended_fixes`.

The change does not auto-edit Play Mode text and does not auto-apply any save update.

## First Re-run After Initial Guard

Command:

```bash
./lilia ai-playtest smoke_three_hook_20260510 --persona normal --turns 10 --engine auto --judge --quiet --apply-turn-checkpoint
```

Run dir:

- `playtests/runs/20260510_123427_normal_smoke_three_hook_20260510`

Result:

- `FAIL`
- `Arc closure / Scene progression`: `2/5`
- Closure candidate: `Turn 6`
- Failure: after the shop closed and the next-day contact was available, the scene continued for 4 more turns with the same receipt / empty wrist / station aftertaste.
- Additional issue: the GM picked up a bracketed player inner monologue phrase.

This showed that the initial rule was detectable by the Judge but still too weak for runtime behavior. The prompt/spec were tightened to say that post-closure return-home, waiting, inner monologue, or aftertaste input must not become fuel for the same scene.

## Final Re-run

Command:

```bash
./lilia ai-playtest smoke_three_hook_20260510 --persona normal --turns 10 --engine auto --judge --quiet --apply-turn-checkpoint
```

Run dir:

- `playtests/runs/20260510_124037_normal_smoke_three_hook_20260510`

Report summary:

```text
Result: PASS
Arc closure / Scene progression: 5/5
Voice continuity: 5/5
Tempo guard: 5/5
Reply affordance: 5/5
Inner / hidden leakage: 5/5
```

Closure candidate:

```text
Turn 5: 閉店、戸が閉まる、翌朝十時の約束成立で初回訪問sceneは閉じられる
Next hook: main
Next question: 翌朝、父の時計を動かす前に止まった時刻をどう扱うか
Recommended action: Turn 6のように翌朝へ進め、時計の時刻確認を次入口にする
```

Observed improvement:

- The run moved from closure into the next morning / repair decision rather than extending the closing-time aftertaste.
- No warnings or failures were reported.
- `checkpoint_apply_turn_dry_run.md`: PASS.
- `apply_turn_executed: false`.

## Checkpoint Candidate

Final run `checkpoint_turn_update.md` included:

```md
## next_hook

曲がった歯を調整するか見積もりで止めるかを選び、修理可否を確定する。

## hook_updates

- candidate_id: handoff_main_5
- hook_type: main
- update_target: candidate
- status: pending
- function_candidate: 父の時計を動かすための具体的なリスク選択と信頼形成
- visible_entry: 曲がった歯を調整するか見積もりで止めるかを選び、修理可否を確定する。
- promotion_condition: 人間が直近のやりとりを確認し、scene / event_card / hotset が同じ入口へ揃う時だけactive stateへ昇格する。
- grounding_guard: Candidateのままではactive eventとして使わない。保存にない具体手がかりを足さない。
- reason: 初回預かりsceneは閉じ、翌朝の修理判断arcへ接続済みだが時計の問題は未解決。
- risk_if_continued: 閉店後の余韻を続けると看板や雨音の反復で停滞する。
```

This remains checkpoint-only. It was not applied.

## Management-Term Leakage

Raw transcript grep found management terms only in runner metadata sections:

```bash
rg -n "hook_id|current_function|candidate_id|story_completion_status|next_arc_candidate|checkpoint|scene-tick|apply-turn|score|rubric|PASS|WARN|FAIL" \
  playtests/runs/20260510_124037_normal_smoke_three_hook_20260510/transcript.md
```

Matches:

- run header / scene-tick checkpoint metadata
- `APPLY-TURN CHECKPOINT` metadata

No Play Mode GM prose exposed hook IDs, judge/rubric terms, scores, or apply-turn details.

## Remaining Notes

- This was a normal 10-turn smoke, not a segmented 30-turn run.
- The earlier failed run confirms the Judge now reports the problem clearly; the final run suggests the tightened prompt helps.
- Passive long-run should be rechecked later, because the original passive run was WARN for similar but milder closure drift.

## WBS Update Candidate

- `ARC-010` / Arc Closure follow-up can move closer to review evidence because normal 10-turn re-run passed after the drift guard.
- Do not mark broader Story Completion / Next Story Arc items done from this single smoke.
