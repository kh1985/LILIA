# State Consistency / Next Hook Promotion Smoke - 2026-05-09

## Purpose

next_hook promotion / state consistency 修正後に、stale next_hook 状態を検出し、`apply-turn` によって next hook が active state へ昇格し、resume が矛盾した state をそのまま本文生成へ流さないことを確認した。

この結果は smoke 記録であり、WBS status は変更していない。

## Session / Fixture

- Fixture: `tests/fixtures/stale_next_hook_session/`
- Turn Update: `tests/fixtures/stale_next_hook_turn_update.md`
- Smoke session: `saves/smoke_state_consistency_20260509`
- Temporary output: `playtests/tmp/smoke_state_consistency_20260509_*`

`saves/` と `playtests/` は `.gitignore` 対象。既存の本番 session / saves は触っていない。

## Commands

```bash
./lilia validate-session smoke_state_consistency_20260509
./lilia apply-turn --dry-run smoke_state_consistency_20260509 playtests/tmp/smoke_state_consistency_20260509_turn_update.md
./lilia apply-turn smoke_state_consistency_20260509 playtests/tmp/smoke_state_consistency_20260509_turn_update.md
./lilia validate-session smoke_state_consistency_20260509
./lilia resume smoke_state_consistency_20260509 --prompt-only
./lilia resume smoke_state_consistency_20260509 --run --engine auto
python -m pytest tests/test_state_consistency.py
python -m pytest
```

## Validate Before Promotion

Result: expected failure.

```text
state consistency: FAIL
WARN: candidate_next_hook_not_active: current/event_card.md has a Next Hook, but current/event_card.md active fields do not reflect it [current/event_card.md, current/event_card.md]
FAIL: hotset_scene_event_mismatch: hotset/story_deck point at a next scene, but current/scene.md or current/event_card.md still looks stale [current/hotset.md, current/scene.md, current/event_card.md, current/event_card.md]
```

Exit code: `1`

This confirms the stale next_hook fixture is detected before resume.

## Apply-Turn Dry Run

Result: expected promotion plan.

```text
dry-run: applied: playtests/tmp/smoke_state_consistency_20260509_turn_update.md
session: saves/smoke_state_consistency_20260509
would update:
  current/scene.md
  current/event_card.md
  current/hotset.md
  story/story_deck.md
```

Dry run showed the correct active state targets without directly using Play Mode text.

## Apply-Turn Promotion

Result: applied.

```text
updated:
  current/scene.md
  story/story_deck.md
  current/event_card.md
  current/hotset.md
  session.json
```

Note: the minimal smoke fixture still produced a voice continuity warning:

```text
voice_continuity: core / voice が空である (core fixed の正本が無い)
```

This did not block promotion or state consistency. It is fixture noise from the small regression session, not a production save change.

## Validate After Promotion

Result: pass.

```text
state consistency: PASS
```

Exit code: `0`

## Active State Check

After promotion:

- `current/scene.md` points to the next scene: `翌日の夕方、依頼主に連絡がつかなかった件をもう一度確認に来てもらう。`
- `current/event_card.md` top active fields point to the same next scene.
- `current/event_card.md` includes `Grounding Guard`.
- `current/hotset.md` points to the same next scene.
- `story/story_deck.md` keeps the old event only as `Backgrounded Event Card` / material shelf.

The stale phrase `前日の閉店間際` remains only in `story/story_deck.md` as backgrounded material, not in active `current/event_card.md`.

Fixture-only forbidden clues were absent from promoted active files:

- `薄紙`
- `鉛筆`
- `店名`
- `住所`
- `写真の裏の文字`

## Resume Prompt Check

Command:

```bash
./lilia resume smoke_state_consistency_20260509 --prompt-only
```

Result:

- Exit code: `0`
- Header says `profile: omitted by default`.
- Active `current/scene.md`, `current/event_card.md`, and `current/hotset.md` contain the promoted next scene.
- `Grounding Guard` is present in the prompt through active `current/event_card.md`.
- `前日の閉店間際` appears only through backgrounded `story/story_deck.md`, not as the active event card.

The prompt contains general rules mentioning `profile.md`, `score`, `FAIL`, and `diff` as instruction text. These are not Play Mode output and are not the active scene state.

## Resume Run Check

Command:

```bash
./lilia resume smoke_state_consistency_20260509 --run --engine auto
```

Result:

- Exit code: `0`
- `resume --run` did not stop with state consistency failure.
- It resumed from the next hook: the next visit / confirmation about the unreachable requester.
- It did not introduce the original regression clues:
  - `薄紙`
  - `鉛筆`
  - `店名`
  - `住所`
  - `写真の裏の文字`
- It did not leak validator / score / FAIL / diff / file path management terms in the Play Mode output.

Summary of generated first response:

- LILIA waits at the shop in the evening.
- The unresolved photo remains present.
- The requester still cannot be reached.
- LILIA asks whether the item should remain held or whether the user can stay involved.
- The turn leaves the player an understandable reply point.

## Found Issues

The state integrity fix works, but `resume --run` still introduced small ungrounded operational details not present in the active state:

- `封筒`
- `手元のメモ`
- `番号`
- `昨日の控え`

These are less severe than the previous `薄紙` / `鉛筆` / `店名` / `住所` / `写真の裏の文字` failure, and they did not change the scene goal. However, they show that Grounding Guard reduces the stale next_hook bug but does not fully prevent LLMs from adding minor props during resume 1ターン目.

## Next Tasks

1. Strengthen resume 1ターン目 grounding so optional props such as memo, envelope, number, or receipt-like details are introduced only when present in active state or explicitly discovered in-scene.
2. Consider adding a resume-output grounding smoke that checks for newly introduced concrete nouns outside the active state, without turning fixture-only words into global forbidden terms.
3. Re-run TTY multi-turn interactive smoke in an external terminal after the environment allows a normal TTY.

## Test Results

```text
python -m pytest tests/test_state_consistency.py
4 passed
```

```text
python -m pytest
175 passed, 1 skipped
```

## Conclusion

The stale next_hook state is now detected before promotion and repaired by `apply-turn` into aligned `current/scene.md`, `current/event_card.md`, and `current/hotset.md` active state. `resume --run` no longer silently proceeds from a FAIL state and did not reproduce the original saved-state-specific clue hallucinations.

Residual grounding remains: resume output can still add small unstored props, so the next hardening task should focus on stricter first-turn grounding, not on character-specific wording.

## Follow-Up Run After Grounding Guard Strengthening

After strengthening the resume first-turn Grounding Guard, the same smoke session was run again.

Command:

```bash
./lilia resume smoke_state_consistency_20260509 --run --engine auto
```

Result:

- Exit code: `0`
- `resume --run` did not stop with state consistency failure.
- It resumed from the Next Hook: the next-day confirmation about the unreachable requester.
- It did not include the previous residual terms:
  - `手元のメモ`
  - `番号`
  - `昨日の控え`
- It did not include the original fixture regression terms:
  - `薄紙`
  - `鉛筆`
  - `店名`
  - `住所`
  - `写真の裏の文字`
- It did not leak Play Mode management terms such as `validator`, `FAIL`, `diff`, `score`, `state consistency`, file paths, or `Grounding Guard`.

Summary of generated first response:

- The scene resumes the next evening.
- LILIA thanks the user for coming.
- The requester still has not been reached.
- LILIA asks to decide how far to confirm before opening / checking further.
- She keeps the boundary: she will not move ahead on her own.

Observed nuance:

- The output still used light scene dressing such as glass, clock, counter, and fingers.
- These did not become clue-results or saved-state facts, but they show the guard distinguishes concrete clues from ordinary scene texture only by prompt pressure, not by a hard validator.
- `封筒` appeared again. The previous smoke already treated `封筒` as acceptable-leaning when it is the container for the saved unresolved photo. If stricter grounding is needed, future smoke should define allowed scene dressing versus clue-bearing props.

Conclusion:

The strengthened guard fixed the immediate residual terms seen in the previous run (`手元のメモ` / `番号` / `昨日の控え`) without turning those words into global forbidden terms. Remaining risk is mostly around harmless-looking scene dressing becoming clue-bearing if the model later attaches meaning to it.
