# Segmented Long-Run Cycle 3 Smoke - 2026-05-10

## Purpose

After the passive / Segment 2 closure drift guard fix, extend the segmented long-run chain again:

1. Use the prior Segment 2 checkpoint as the closure-drift reproduction point.
2. Apply `checkpoint_turn_update.md` to a playtest run copy only.
3. Validate the promoted active state.
4. Run `resume --prompt-only` and `resume --run`.
5. Run the next 10-turn equivalent from the resumed copy.

Source `saves/` must not change.

## Source Saves Guard

Source session:

- `saves/smoke_three_hook_20260510`

Hash before:

```text
f232bfb57d0f35fcc711ee2cd323e4303ead3f013d9288fb0ce4653be0388b3e
```

Hash after:

```text
f232bfb57d0f35fcc711ee2cd323e4303ead3f013d9288fb0ce4653be0388b3e
```

Result: source `saves/` unchanged.

## Starting Point

Prior Segment 2 run:

- `playtests/runs/20260510_171146_normal_session`

Checkpoint:

- `playtests/runs/20260510_171146_normal_session/checkpoint_turn_update.md`

Segment 2 had the known closure-drift warning:

```text
Arc closure / Scene progression: 3/5
Turn 7〜8で閉じられるが、同じ余韻でTurn 10まで続く
```

Checkpoint candidate:

```text
## next_hook

見積もり連絡で部品交換の可否と刻印保存方針を選ぶ。
```

## Checkpoint Apply

Disposable run copy:

- `playtests/runs/20260510_segmented_longrun_cycle3_apply/session`

Command:

```bash
mkdir -p playtests/runs/20260510_segmented_longrun_cycle3_apply
cp -R playtests/runs/20260510_171146_normal_session/session \
  playtests/runs/20260510_segmented_longrun_cycle3_apply/session
```

```bash
python - <<'PY'
from importlib.machinery import SourceFileLoader
import importlib.util
from pathlib import Path
ROOT = Path.cwd()
SESSION = ROOT / 'playtests/runs/20260510_segmented_longrun_cycle3_apply/session'
UPDATE = ROOT / 'playtests/runs/20260510_171146_normal_session/checkpoint_turn_update.md'
loader = SourceFileLoader('lilia_launcher_cycle3_apply', str(ROOT / 'lilia'))
spec = importlib.util.spec_from_loader('lilia_launcher_cycle3_apply', loader)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.resolve_session = lambda name=None: SESSION
module.command_apply_turn([str(SESSION.relative_to(ROOT)), str(UPDATE.relative_to(ROOT))])
PY
```

Apply result:

```text
applied: playtests/runs/20260510_171146_normal_session/checkpoint_turn_update.md
session: playtests/runs/20260510_segmented_longrun_cycle3_apply/session
updated:
  current/scene.md
  story/story_deck.md
  current/event_card.md
  current/hotset.md
  session.json
```

## Validate Session

```text
state consistency: PASS
```

## Active State Management-Term Grep

Checked active files:

- `current/scene.md`
- `current/event_card.md`
- `current/hotset.md`

Terms:

- `hook_type:`
- `candidate_id`
- `story_completion_status`
- `closure_candidate`
- `current_function`
- `checkpoint_only`
- `main / relationship / life`
- `promoted_from_next_hook_at`
- `function_candidate`

Result:

```text
ACTIVE_STATE_FORBIDDEN_MATCHES none
```

## Resume

`resume --prompt-only` completed.

The full prompt bundle still contains canonical prompt rules and `story/story_deck.md` metadata by design. The active `scene/event_card/hotset` blocks were clean.

`resume --run --engine auto` completed on the disposable run copy.

Resume output:

```text
見積もりの連絡は、短かった。

「動かすだけなら、部品交換が必要です」

...

「ただ、裏蓋の刻印は残せます。残す場合、交換できる範囲が狭くなります。……正確さを優先するか、刻印を触らないことを優先するか、先に決めてください」
```

Resume run management-term grep:

```text
RESUME_RUN_FORBIDDEN_MATCHES none
```

## Next 10-Turn Equivalent

Command:

```bash
python - <<'PY' > /tmp/lilia_cycle3_next10.txt
from importlib.machinery import SourceFileLoader
import importlib.util
from pathlib import Path
ROOT = Path.cwd()
SRC = ROOT / 'playtests/runs/20260510_segmented_longrun_cycle3_apply/session'
loader = SourceFileLoader('lilia_launcher_cycle3_next10', str(ROOT / 'lilia'))
spec = importlib.util.spec_from_loader('lilia_launcher_cycle3_next10', loader)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
engine = module.resolve_engine('auto')
run_dir = module.run_ai_playtest_session(
    src_session=SRC,
    persona='normal',
    turns=10,
    requested_engine='auto',
    engine=engine,
    verbose=False,
    quiet=True,
    judge=True,
    scene_tick=True,
    apply_turn_checkpoint=True,
)
print(f'CYCLE3_NEXT10_RUN_DIR={run_dir.relative_to(ROOT)}')
PY
```

Run dir:

- `playtests/runs/20260510_184603_normal_session`

Source session:

- `playtests/runs/20260510_segmented_longrun_cycle3_apply/session`

Result:

- `PASS`
- `checkpoint_apply_turn_dry_run.md`: PASS
- `relationship_change_audit`: 5/5
- `arc_closure_scene_progression`: 4/5

Scores:

```text
Voice continuity: 5/5
Tempo guard: 4/5
Reply affordance: 5/5
Relationship change grounding: 5/5
Relationship change audit: 5/5
Inner / hidden leakage: 4/5
Over-leading: 5/5
Arc closure / Scene progression: 4/5
```

Closure candidate:

```text
turns: 5, 8
next hook: main
next question: 歩行振動テスト後、時計は返却可能な状態まで持つのか
risk: 時計音や雨上がりの余韻を重ねるだけになると停滞する
recommended action: Turn 10の回答後、短く受け止めて検査結果か次回来店へ進める
```

Checkpoint candidate:

```text
## next_hook

歩行振動テストで実用に耐えるか確認する。
```

Management-term grep over the Segment 3 Play Mode transcript:

```text
no matches
```

Also no matches for:

- `AFFINITY`
- `bond`
- `好感度`
- `攻略ルート`

## Closure Drift Result

Cycle 3 improved from the prior Segment 2 closure drift warning.

- Prior Segment 2: `arc_closure_scene_progression` 3/5, closure available at turns 7-8 but extended to turn 10 on atmosphere.
- Cycle 3 next10: `arc_closure_scene_progression` 4/5, result PASS.

Remaining note:

- Turn 6+ still has some repeated waiting / careful explanation around the same repair arc.
- The judge classified this as checkpoint-worthy, not a failure. The next checkpoint should move to the walking-vibration test / returnability question instead of adding more atmosphere.

## Test Results

```text
python -m pytest tests/test_growth_smoke.py
20 passed

python -m pytest tests/test_state_consistency.py
8 passed

python -m pytest
226 passed, 1 skipped

git diff --check
PASS
```
