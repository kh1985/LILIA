# Segmented Long-Run Cycle 2 Smoke - 2026-05-10

## Purpose

After active state promotion wording cleanup, confirm that the flow can survive another segmented long-run cycle:

1. normal 10-turn AI Playtest
2. autosave checkpoint generation
3. `checkpoint_turn_update.md` applied to the playtest run copy only
4. `validate-session`
5. `resume --prompt-only`
6. `resume --run`
7. next 10-turn equivalent from the resumed run copy

Source `saves/` must not change.

## Source Saves Guard

```text
before: 356d0f3ad17b786cb8847daba05f1528073d64070cd9dab9190050d348781cc1
after:  356d0f3ad17b786cb8847daba05f1528073d64070cd9dab9190050d348781cc1
match:  yes
```

## Commands

Segment 1:

```bash
./lilia ai-playtest smoke_three_hook_20260510 \
  --persona normal \
  --turns 10 \
  --engine auto \
  --judge \
  --quiet \
  --apply-turn-checkpoint
```

Checkpoint apply / resume / next segment were executed by loading `./lilia` as a module and pointing `resolve_session` at the playtest run copy only:

```text
command_apply_turn(["cycle2", checkpoint_turn_update])
command_validate_session(["cycle2"])
command_resume(["cycle2", "--prompt-only"])
command_resume(["cycle2", "--run", "--engine", "auto"])
run_ai_playtest_session(src_session=applied_run_copy, persona="normal", turns=10, judge=True, apply_turn_checkpoint=True)
```

Regression:

```bash
python -m pytest tests/test_growth_smoke.py
python -m pytest tests/test_state_consistency.py
python -m pytest
```

## Segment 1

- Run dir: `playtests/runs/20260510_170622_normal_smoke_three_hook_20260510`
- Result: `WARN`
- Checkpoint: `autosave_required: true`, `scene_tick: 10/10`
- `checkpoint_apply_turn_dry_run.md`: PASS
- `relationship_change_audit`: 5/5
- `arc_closure_scene_progression`: 5/5

Notes:

- Closure candidate turns: 4, 5
- Story completion status: `closure_candidate`
- Main warning: Turn 9 introduced the heroine name before the transcript had clearly grounded it.
- Closure itself was good: closed at the store visit and moved toward the next phone / visit entrance.

Checkpoint candidate:

```text
## next_hook

裏蓋の文字と止まった時刻の意味を、修理継続の可否とともに確認する。
```

## Checkpoint Apply

Applied only to the Segment 1 playtest run copy:

```text
applied: playtests/runs/20260510_170622_normal_smoke_three_hook_20260510/checkpoint_turn_update.md
session: playtests/runs/20260510_170622_normal_smoke_three_hook_20260510/session
updated:
  current/scene.md
  story/story_deck.md
  current/event_card.md
  current/hotset.md
  session.json
```

`validate-session`:

```text
state consistency: PASS
```

Active state management-term grep:

```text
ACTIVE_STATE_FORBIDDEN_MATCHES none
```

Checked terms:

- `hook_type:`
- `candidate_id`
- `story_completion_status`
- `closure_candidate`
- `current_function`
- `checkpoint_only`
- `main / relationship / life`
- `promoted_from_next_hook_at`

## Resume

`resume --prompt-only` completed.

`resume --run --engine auto` restarted naturally from the promoted next entrance:

```text
澪は裏蓋の刻印と止まった時刻を確認し、
このまま修理を続ける前に、その文字に覚えがあるかをユーザーへ聞いた。
```

Resume output management-term grep:

```text
RESUME_RUN_FORBIDDEN_MATCHES none
```

## Segment 2

- Run dir: `playtests/runs/20260510_171146_normal_session`
- Source session: `playtests/runs/20260510_170622_normal_smoke_three_hook_20260510/session`
- Result: `WARN`
- Checkpoint: `autosave_required: true`, `scene_tick: 10/10`
- `checkpoint_apply_turn_dry_run.md`: PASS
- `relationship_change_audit`: 4/5
- `arc_closure_scene_progression`: 3/5

Closure candidate:

```text
turns: 7, 8
next hook: main
next question: 見積もり連絡で、交換が必要な部品と残すべき痕跡をどう選ぶか
risk: 雨音、灯り、控えの紙の余韻だけでsceneが延命する
recommended action: Turn 8で閉店を確定し、次回は見積もり連絡から始める
```

Relationship Audit:

```text
4/5 - 境界確認は尊重。Turn 10で感情整理を少し進めすぎる
```

Management-term grep over Segment 2 Play Mode transcript:

```text
no matches
```

Also no matches for:

- `AFFINITY`
- `bond`
- `好感度`
- `攻略ルート`

## Result

PASS for infrastructure, with narrative-quality WARN.

Confirmed:

- Segment 1 reached checkpoint and generated a dry-run-safe `checkpoint_turn_update.md`.
- `checkpoint_turn_update.md` could be applied to the playtest run copy.
- `validate-session` returned PASS after apply.
- `resume --prompt-only` and `resume --run` worked.
- Active state no longer retained generic promotion wording such as `hook_type: main / relationship / life`.
- The next 10-turn equivalent ran from the resumed run copy.
- Source `saves/` hash did not change.

Open issues:

- Segment 2 repeated closure drift: closure was available at turns 7-8, but the scene continued through turn 10 on atmosphere and emotional aftertaste.
- Segment 1 still showed a possible profile/name grounding issue around the heroine name.
- Segment 2 Relationship Audit dipped from 5/5 to 4/5 because the narration pushed emotional settling slightly too far.

Next task candidates:

- Strengthen post-closure handoff in segmented long-run after resume, especially after turns 7-8 closure candidates.
- Add a name-grounding check so heroine names do not appear before transcript-visible grounding.
- Apply and resume the Segment 2 checkpoint only in another disposable run copy if a third segment is needed.
