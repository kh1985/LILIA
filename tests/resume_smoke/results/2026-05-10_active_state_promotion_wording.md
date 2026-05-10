# Active State Promotion Wording Smoke - 2026-05-10

## Purpose

Confirm that checkpoint / next_hook promotion no longer leaves management wording in active resume state after a segmented long-run checkpoint apply.

The focus is `current/scene.md`, `current/event_card.md`, and `current/hotset.md`.
Report/debug artifacts and `story/story_deck.md` may still keep hook metadata.

## Source Safety

Source session:

- `saves/smoke_three_hook_20260510`

Disposable run copy:

- `playtests/runs/20260510_active_state_promotion_wording_v2/session`

Checkpoint used:

- `playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/checkpoint_turn_update.md`

Source saves hash before / after:

```text
97fd54f43077bd8507e021d3f5a6a395270f5d70  saves/smoke_three_hook_20260510/session.json
b75caf456ce2f677ceef412d17eb86040efff0d3  saves/smoke_three_hook_20260510/current/scene.md
4e5aca6ba4ed4b122702c66038ceb7bff4c94552  saves/smoke_three_hook_20260510/current/event_card.md
baf65e3f86611c36720aeb41de8156c737f3b3e6  saves/smoke_three_hook_20260510/current/hotset.md
cf0310b917812b41eeb66898119733c1b374b178  saves/smoke_three_hook_20260510/story/story_deck.md
```

Result: source `saves/` was unchanged.

## Commands

```bash
mkdir -p playtests/runs/20260510_active_state_promotion_wording_v2
cp -R saves/smoke_three_hook_20260510 playtests/runs/20260510_active_state_promotion_wording_v2/session
```

```bash
python - <<'PY'
from importlib.machinery import SourceFileLoader
import importlib.util
from pathlib import Path
ROOT = Path.cwd()
SESSION = ROOT / 'playtests/runs/20260510_active_state_promotion_wording_v2/session'
UPDATE = ROOT / 'playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/checkpoint_turn_update.md'
loader = SourceFileLoader('lilia_launcher_active_state_apply_v2', str(ROOT / 'lilia'))
spec = importlib.util.spec_from_loader('lilia_launcher_active_state_apply_v2', loader)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.resolve_session = lambda name=None: SESSION
module.command_apply_turn([str(SESSION.relative_to(ROOT)), str(UPDATE.relative_to(ROOT))])
PY
```

```bash
python -m pytest tests/test_growth_smoke.py
python -m pytest tests/test_state_consistency.py
python -m pytest
git diff --check
```

## Apply-Turn Result

```text
applied: playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/checkpoint_turn_update.md
session: playtests/runs/20260510_active_state_promotion_wording_v2/session
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

## Active State Grep

Checked active files:

- `current/scene.md`
- `current/event_card.md`
- `current/hotset.md`

Forbidden management wording checked:

- `hook_type: main / relationship / life`
- `candidate_id`
- `story_completion_status`
- `closure_candidate`
- `current_function`
- `checkpoint_only`
- `promoted_from_next_hook_at`
- `handoff_main`
- `function_candidate`
- `3hook`
- `Save Mode`
- `active event_card`
- `current/scene.md`
- `story/story_deck.md`

Result:

```text
ACTIVE_STATE_FORBIDDEN_MATCHES none
```

## Active Event Card Sample

```text
## Active Hook

- 今触れる軸: 本筋の確認
- 前景化した理由: 時計預かりsceneは閉じられ、見積もり確認の次の確認へ接続できる
- 注: 次の返答では、この出来事だけを前景化する。

## Scene Function

- 場面の役割: 預けた時計の診断結果を提示し、修理可否と選択を開く
- 今の問い: 翌夕方、七瀬から時計の状態と見積もりを聞く
- 次に残す入口: 必要になった時だけ、次の保存時に短く残す。
```

The promoted `Grounding Guard` also avoids file-path/debug wording and uses natural scene-facing guidance:

```text
再開1ターン目では、保存済みの場面、出来事、温度、記憶、思い込みに明示されたものだけを場面の具体手がかりとして使う。
素材棚に残る背景情報を、今この場の新しい証拠として前景化しない。
```

## Resume Checks

`resume --prompt-only` completed for the disposable run copy.
The full prompt bundle still contains canonical prompt rules and story_deck metadata by design, but the active state blocks were clean.

`resume --run --engine auto` initially failed in the sandbox with an app-server permission error, then passed with escalated execution on the disposable run copy.

Play Mode output did not include:

- `hook_type`
- `candidate_id`
- `story_completion_status`
- `closure_candidate`
- `current_function`
- `checkpoint_only`
- `main / relationship / life`
- `promoted_from_next_hook_at`

Resume output opened naturally from the estimate / repair decision entrance:

```text
翌夕方の店は、前の夜より少しだけ明るかった。
...
「先に、状態を見ますか。それとも、見積もりから聞きますか」
```

## Test Results

```text
python -m pytest tests/test_state_consistency.py
8 passed

python -m pytest tests/test_growth_smoke.py
20 passed

python -m pytest
226 passed, 1 skipped

git diff --check
PASS
```

## Notes

- `story/story_deck.md` still keeps Candidate Hook metadata as a material shelf. This is expected and is not active state.
- The disposable run copy is under ignored `playtests/`; only this result file is tracked.
- Source `saves/` was not modified.
