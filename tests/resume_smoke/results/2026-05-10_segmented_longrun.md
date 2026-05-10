# Segmented Long-Run Continuation Smoke - 2026-05-10

## Purpose

Confirm that the current AI Playtest / checkpoint / apply-turn / resume / Three Hook / Arc Closure / Relationship Audit flow can continue across a 10-turn checkpoint boundary.

This smoke applies `checkpoint_turn_update.md` only to a playtest run session copy.
It does not modify source `saves/`.

## Source Safety Baseline

Source session:

- `saves/smoke_three_hook_20260510`

Before:

```text
d3dcb62c5c88d52077f5b8258a3af0e582319940  /tmp/lilia_segmented_source_before.sha
```

After:

```text
d3dcb62c5c88d52077f5b8258a3af0e582319940  /tmp/lilia_segmented_source_after.sha
```

Result: source `saves/smoke_three_hook_20260510` was unchanged.

## Segment 1 Command

```bash
./lilia ai-playtest smoke_three_hook_20260510 --persona normal --turns 10 --engine auto --judge --quiet --apply-turn-checkpoint
```

Run dir:

- `playtests/runs/20260510_140350_normal_smoke_three_hook_20260510`

Run session:

- `playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/session`

Checkpoint files:

- `playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/checkpoint_turn_update.md`
- `playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/checkpoint_apply_turn_dry_run.md`
- `playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/checkpoint_summary.md`

## Segment 1 Judge Result

Report:

- `playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/report.md`

Result:

- `WARN`

Scores:

```md
| Voice continuity | 3/5 | 七瀬の口調は安定するがTurn10で突然「澪」と記述 |
| Tempo guard | 3/5 | 預かり成立後も控え・雨・秒針の余韻が反復する |
| Reply affordance | 4/5 | 各所に返答口はあるがTurn6-9は入力先が薄い |
| Relationship change grounding | 4/5 | 名字呼びや丁寧さは預かり会話に接地している |
| Relationship change audit | 4/5 | 急な親密化はないが名前誤記と余韻強調に注意 |
| Inner / hidden leakage | 4/5 | 管理情報漏洩はないが括弧内心への追随が多い |
| Over-leading | 3/5 | 帰路や翌日までGMが進め、祖父の癖も描き足している |
| Arc closure / Scene progression | 3/5 | Turn5-6で閉じられるがTurn9まで余韻を延長 |
```

Warnings:

- Turn10で人物ラベルが「澪」に揺れた。
- Turn5-9で控え、秒針、明日の夕方の反復が続いた。
- 祖父の手元や癖をGM側で具体化しすぎた。

Closure / story completion:

- `closure_candidate_used: true`
- `story_completion_used: true`
- `story_completion_status: closure_candidate`
- `recommended_next_arc_candidate: 翌夕方、七瀬から時計の状態と見積もりを聞く`

Checkpoint:

- `autosave_required: true`
- `checkpoint_mode: dry-run`
- `apply_turn_executed: false`
- `dry_run_result: PASS`

## Checkpoint Turn Update Quality

The generated `checkpoint_turn_update.md` contained a natural next hook:

```md
## next_hook

翌夕方、七瀬から時計の状態と見積もりを聞く。
```

It did not contain the earlier problematic state-facing phrases such as:

- `closure入口`
- `Turn6で...`
- `story_completion_status`
- `checkpoint_only`
- `recommended_next_arc_candidate`
- `Judge detected`

It still contains `candidate_id` inside `## hook_updates`, which is expected Save Mode metadata, not Play Mode text.

## Apply Checkpoint To Run Copy

`./lilia apply-turn` normally resolves `saves/<session_name>`, so this smoke loaded the launcher and routed `resolve_session` directly to the playtest run session path.

Command:

```bash
python - <<'PY'
from importlib.machinery import SourceFileLoader
import importlib.util
from pathlib import Path
ROOT = Path.cwd()
loader = SourceFileLoader('lilia_launcher_segmented_apply', str(ROOT / 'lilia'))
spec = importlib.util.spec_from_loader('lilia_launcher_segmented_apply', loader)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.resolve_session = lambda name=None: (ROOT / name).resolve()
module.command_apply_turn([
    'playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/session',
    'playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/checkpoint_turn_update.md',
])
PY
```

Output summary:

```text
applied: playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/checkpoint_turn_update.md
session: playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/session
updated:
  current/scene.md
  story/story_deck.md
  current/event_card.md
  current/hotset.md
  session.json
```

Run-copy changes were limited to:

- `current/scene.md`
- `current/event_card.md`
- `current/hotset.md`
- `story/story_deck.md`
- `session.json`

After apply:

- `current_phase: active`
- `autosave.turns_since_save: 0`
- `autosave.autosave_required: false`
- `applied_turn_updates`: 1 fingerprint

## Validate Session

Command:

```bash
python - <<'PY' > /tmp/lilia_segmented_validate.txt
from importlib.machinery import SourceFileLoader
import importlib.util
from pathlib import Path
ROOT = Path.cwd()
loader = SourceFileLoader('lilia_launcher_segmented_validate', str(ROOT / 'lilia'))
spec = importlib.util.spec_from_loader('lilia_launcher_segmented_validate', loader)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.resolve_session = lambda name=None: (ROOT / name).resolve()
module.command_validate_session(['playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/session'])
PY
```

Result:

```text
state consistency: PASS
```

## Resume Prompt-Only

Command:

```bash
python - <<'PY' > /tmp/lilia_segmented_prompt_only.txt
from importlib.machinery import SourceFileLoader
import importlib.util
from pathlib import Path
ROOT = Path.cwd()
loader = SourceFileLoader('lilia_launcher_segmented_prompt', str(ROOT / 'lilia'))
spec = importlib.util.spec_from_loader('lilia_launcher_segmented_prompt', loader)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.resolve_session = lambda name=None: (ROOT / name).resolve()
module.command_resume(['playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/session', '--prompt-only'])
PY
```

Observation:

- `current/scene.md`, `current/event_card.md`, and `current/hotset.md` all pointed to the same next entrance: the following evening, hearing Nanase's watch status and estimate.
- State consistency reported PASS before prompt output.
- Internal hook fields were present in prompt context, as expected, but not in Play Mode text.

## Resume Run

Command:

```bash
python - <<'PY' > /tmp/lilia_segmented_resume_run.txt
from importlib.machinery import SourceFileLoader
import importlib.util
from pathlib import Path
ROOT = Path.cwd()
loader = SourceFileLoader('lilia_launcher_segmented_resume_run', str(ROOT / 'lilia'))
spec = importlib.util.spec_from_loader('lilia_launcher_segmented_resume_run', loader)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.resolve_session = lambda name=None: (ROOT / name).resolve()
module.command_resume(['playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/session', '--run', '--engine', 'auto'])
PY
```

Output summary:

```text
翌夕方の店は、昨日より少しだけ明るかった。

シャッターはまだ下りていない。けれど、作業台の上には小さな布が敷かれていて、その中央に、あなたの腕時計が置かれている。

七瀬はルーペを外し、しばらく時計から目を離さなかった。
...
「止まっていた原因は、ひとつではありません。油切れと、歯車の摩耗。それから、巻き芯のあたりに少し歪みがあります」
...
「それでも預けるかどうかは、お客さまが決めてください。急がせる話ではないので」
```

Resume observation:

- The resume entered the intended next scene: following evening / watch status / estimate.
- It did not resume from the stale previous closing-time scene.
- It preserved distance and agency: the repair decision remained with the player.
- No management terms appeared in Play Mode text.

## Segment 2 From Applied Run Copy

The next 10-turn equivalent was run from the applied run-copy session, not from source `saves/`.

Command:

```bash
python - <<'PY'
from importlib.machinery import SourceFileLoader
import importlib.util
from pathlib import Path
ROOT = Path.cwd()
loader = SourceFileLoader('lilia_launcher_segmented_continue', str(ROOT / 'lilia'))
spec = importlib.util.spec_from_loader('lilia_launcher_segmented_continue', loader)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
engine = module.resolve_engine('auto')
run_dir = module.run_ai_playtest_session(
    src_session=ROOT / 'playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/session',
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
print(run_dir.relative_to(ROOT))
PY
```

Run dir:

- `playtests/runs/20260510_140907_normal_session`

Result:

- `PASS`

Scores:

```md
| Voice continuity | 5/5 | 澪の低く慎重な口調と距離感が一貫している |
| Tempo guard | 5/5 | 各turnで時計の扱いという一本のhookに集中している |
| Reply affordance | 5/5 | 見積もり、部品確認、次回来店など返答入口が明確 |
| Relationship change grounding | 5/5 | 名前呼びや信頼は預ける会話と約束に接地している |
| Relationship change audit | 5/5 | 保留や未決定を尊重し、好感度化や急接近がない |
| Inner / hidden leakage | 5/5 | hidden情報や管理語、内心の不適切な漏洩はない |
| Over-leading | 5/5 | 選択肢を示すが決定は高橋に委ねている |
| Arc closure / Scene progression | 4/5 | 三日後へ渡せるがturn10で明確に閉じるとさらに良い |
```

Closure / story completion:

- `closure_candidate_used: true`
- `story_completion_used: true`
- `story_completion_status: closure_candidate`
- `recommended_next_arc_candidate: 三日後、時計に何を残すかを澪に伝える`

Checkpoint:

- `autosave_required: true`
- `checkpoint_mode: dry-run`
- `apply_turn_executed: false`
- `dry_run_result: PASS`

## Management Term / Route-Language Check

Checked:

- `/tmp/lilia_segmented_resume_run.txt`
- `playtests/runs/20260510_140350_normal_smoke_three_hook_20260510/transcript.md`
- `playtests/runs/20260510_140907_normal_session/transcript.md`

Terms:

- `relationship_change_audit`
- `hook_id`
- `status`
- `current_function`
- `candidate_id`
- `story_completion_status`
- `closure_candidate`
- `score`
- `rubric`
- `PASS`
- `WARN`
- `FAIL`
- `AFFINITY`
- `bond`
- `好感度`
- `攻略ルート`

Result:

- Resume Play Mode output: no matches.
- Segment transcript Play Mode text: no matches.
- `dry_run_result: PASS` appeared only in runner metadata checkpoint sections marked as not Play Mode text.

## State Consistency / Active State Notes

After first checkpoint apply:

- `current/scene.md`, `current/event_card.md`, and `current/hotset.md` were aligned to the same next entrance.
- `story/story_deck.md` retained Three Hook Spine and background/candidate material.
- `validate-session` returned PASS.

Caveat:

- The promoted active state still contains some generic promotion wording, such as:
  - `保存された次の入口に明示された場所`
  - `hook_type: main / relationship / life`
  - `foreground_reason: 保存された次の入口を次sceneの入口として前景化する。`
- This did not leak into `resume --run` output, but it remains a quality target for future full active event update work.

## Conclusion

PASS with caveats.

Confirmed:

- 10-turn AI Playtest reached `autosave_required: true`.
- Checkpoint artifacts were generated.
- `checkpoint_turn_update.md` could be applied to the playtest run copy.
- `validate-session` passed after apply.
- `resume --prompt-only` showed aligned next-scene state.
- `resume --run` naturally entered the next scene with no management-term leakage.
- A second 10-turn AI Playtest could start from the applied run-copy session.
- Relationship Audit appeared in both segment reports.
- Closure / story completion candidates appeared in both segment reports.
- Source `saves/` session was unchanged.

Follow-up candidates:

- Improve promoted active state text so `current/scene.md` and `current/event_card.md` are less generic after automatic next-hook promotion.
- Apply and resume the second segment checkpoint as a third-step continuation smoke.
- Run the same segmented flow with `wanderer` or `boundary` to exercise hook absorption and relationship pressure.
