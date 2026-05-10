# Active State Promotion Wording Smoke - 2026-05-10

## Purpose

Confirm that checkpoint / next_hook promotion no longer leaves generic management wording in active resume state after segmented long-run checkpoint apply.

The focus is `current/scene.md`, `current/event_card.md`, and `current/hotset.md`.
Report/debug artifacts and `story/story_deck.md` may still keep hook metadata.

## Source Run

- Source run: `playtests/runs/20260510_134945_normal_smoke_three_hook_20260510`
- Source checkpoint: `playtests/runs/20260510_134945_normal_smoke_three_hook_20260510/checkpoint_turn_update.md`
- Disposable run copy: `playtests/runs/20260510_active_state_promotion_wording_smoke/session`
- Source `saves/`: unchanged

Source saves hash:

```text
before: 356d0f3ad17b786cb8847daba05f1528073d64070cd9dab9190050d348781cc1
after:  356d0f3ad17b786cb8847daba05f1528073d64070cd9dab9190050d348781cc1
```

## Commands

```bash
cp -R playtests/runs/20260510_134945_normal_smoke_three_hook_20260510/session \
  playtests/runs/20260510_active_state_promotion_wording_smoke/session

python - <<'PY' > /tmp/lilia_active_state_promotion_wording_smoke.txt 2>&1
# Loaded ./lilia as a module, pointed resolve_session at the disposable run copy,
# then ran:
# - command_apply_turn(["active_state_wording", checkpoint_turn_update])
# - command_validate_session(["active_state_wording"])
# - command_resume(["active_state_wording", "--prompt-only"])
# - command_resume(["active_state_wording", "--run", "--engine", "auto"])
PY
```

Regression tests:

```bash
python -m pytest tests/test_state_consistency.py
python -m pytest tests/test_growth_smoke.py
python -m pytest
```

## Apply-Turn Result

```text
applied: playtests/runs/20260510_134945_normal_smoke_three_hook_20260510/checkpoint_turn_update.md
session: playtests/runs/20260510_active_state_promotion_wording_smoke/session
updated:
  current/scene.md
  story/story_deck.md
  current/event_card.md
  current/hotset.md
  session.json
```

## Validate-Session

```text
state consistency: PASS
```

## Active State Grep

Checked active files:

- `current/scene.md`
- `current/event_card.md`
- `current/hotset.md`

Forbidden management wording checked:

- `hook_type:`
- `candidate_id`
- `story_completion_status`
- `closure_candidate`
- `current_function`
- `checkpoint_only`
- `main / relationship / life`
- `promoted_from_next_hook_at`
- `次arc`

Result:

```text
ACTIVE_STATE_FORBIDDEN_MATCHES none
```

## Active Event Card Sample

The promoted active event now uses natural scene wording:

```text
## Active Hook

- 今触れる軸: 本筋の確認
- 前景化した理由: 預かり場面は閉じ、修理判断という次の確認へ渡せる状態
- 注: ここに置くのは今触れる1本だけ。3hookを選択肢UIとして並べない。

## Scene Function

- 場面の役割: 預けた時計の状態判明と、修理判断による次の約束形成
- 今の問い: 夕方の見積もり連絡で、修理に入るか保留するかを決める
```

## Resume Checks

`resume --prompt-only` completed and produced a prompt bundle for the disposable run copy.

`resume --run --engine auto` restarted naturally from the estimate / repair decision entrance.
The one-shot Play Mode output did not include:

- `hook_type`
- `candidate_id`
- `story_completion_status`
- `closure_candidate`
- `current_function`
- `checkpoint_only`
- `main / relationship / life`
- `promoted_from_next_hook_at`

Resume output summary:

```text
澪は夕方の見積もり連絡として、預かった時計の状態と修理に入るか保留するかを確認した。
修理には時間と費用がかかることを説明し、ユーザーが質問や判断を返せる入口を残した。
```

## Test Results

```text
tests/test_state_consistency.py: 8 passed
tests/test_growth_smoke.py: 20 passed
python -m pytest: 226 passed, 1 skipped
```

## Notes

- `story/story_deck.md` still keeps Candidate Hook metadata as a material shelf. This is expected and is not active state.
- The disposable run copy was under ignored `playtests/`; only this result file is committed.
- Source `saves/` was not modified.
