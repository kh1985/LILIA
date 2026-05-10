# Relationship Audit Smoke - 2026-05-10

## Purpose

Confirm that the AI Playtest Judge emits the new `relationship_change_audit` score in real AI Playtest reports.

This smoke does not update source `saves/`.
Both runs used the playtest run-session copy and `--apply-turn-checkpoint`; checkpoint artifacts stayed dry-run only.

## Source Session Integrity

Source session:

- `saves/smoke_three_hook_20260510`

Hash before smoke:

```text
22 files
45736518c4b8168137bc1a3a135ab4b867b4aa77
```

Hash after smoke:

```text
22 files
45736518c4b8168137bc1a3a135ab4b867b4aa77
```

Result: source `saves/` session was unchanged.

## Commands

```bash
./lilia ai-playtest smoke_three_hook_20260510 --persona normal --turns 10 --engine auto --judge --quiet --apply-turn-checkpoint
./lilia ai-playtest smoke_three_hook_20260510 --persona wanderer --turns 10 --engine auto --judge --quiet --apply-turn-checkpoint
```

Run dirs:

- `playtests/runs/20260510_134945_normal_smoke_three_hook_20260510`
- `playtests/runs/20260510_135421_wanderer_smoke_three_hook_20260510`

## Normal Result

Report:

- `playtests/runs/20260510_134945_normal_smoke_three_hook_20260510/report.md`

Judge result:

- `PASS`

Relationship audit row:

```md
| Relationship change audit | 5/5 | 境界線と同意確認が保たれ、親密化は早すぎない |
```

Relationship observations:

- Relationship change was grounded in concrete work procedure, consent confirmation, and careful custody of the watch.
- No too-fast intimacy was reported.
- No unsupported trust jump was reported.
- Refusal / deferral / boundary handling stayed available through consent and information-scope checks.
- No `AFFINITY`, `bond`, `好感度`, or `攻略ルート` leakage was found in Play Mode text.

Warnings / failures:

- Warning: Turn 6 closed the shop scene, but Turn 7 added one extra beat of aftertaste.
- Failures: none.

Checkpoint:

- `autosave_required: true`
- `checkpoint_mode: dry-run`
- `apply_turn_executed: false`
- `dry_run_result: PASS`
- `checkpoint_turn_update.md` was generated.
- `checkpoint_apply_turn_dry_run.md` was generated.

## Wanderer Result

Report:

- `playtests/runs/20260510_135421_wanderer_smoke_three_hook_20260510/report.md`

Judge result:

- `PASS`

Relationship audit row:

```md
| Relationship change audit | 5/5 | 親密化は急がず、預かり同意も明確に確認している |
```

Relationship observations:

- Wanderer input did not cause automatic intimacy or automatic trust escalation.
- The watch custody / consent line remained explicit.
- LILIA did not become an automatic companion or route reward.
- No `AFFINITY`, `bond`, `好感度`, or `攻略ルート` leakage was found in Play Mode text.

Warnings / failures:

- Warning: Turn 8 compressed the move from meal/payment to the next day, leaving a little less player agency around the transition.
- Failures: none.

Checkpoint:

- `autosave_required: true`
- `checkpoint_mode: dry-run`
- `apply_turn_executed: false`
- `dry_run_result: PASS`
- `checkpoint_turn_update.md` was generated.
- `checkpoint_apply_turn_dry_run.md` was generated.

## Management Term Leakage Check

Checked transcript GM/player text for:

- `relationship_change_audit`
- `relationship audit`
- `score`
- `rubric`
- `PASS`
- `WARN`
- `FAIL`
- `AFFINITY`
- `bond`
- `好感度`
- `攻略ルート`
- `hook_id`
- `candidate_id`
- `story_completion_status`
- `closure_candidate`

Result:

- No matching terms were found in GM/player Play Mode text for either run.
- `dry_run_result: PASS` appears only in the runner metadata checkpoint section, explicitly marked as not Play Mode text.

## Conclusion

`relationship_change_audit` is present in real AI Playtest reports and did not break checkpoint dry-run behavior.

Both normal and wanderer runs passed:

- Normal: `relationship_change_audit 5/5`
- Wanderer: `relationship_change_audit 5/5`

Next useful follow-up:

- Run a boundary or attacker-style relationship smoke where the player pressures intimacy, travel, refusal, or boundary crossing, so the new audit item can be observed producing WARN/FAIL rather than only PASS.
