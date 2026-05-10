# Wanderer Hook Playtest - 2026-05-10

## Scope

- Task: HOOK-006 wanderer playtest for Three Hook Spine absorption.
- Session: `smoke_three_hook_20260510`
- Runtime transcript: `playtests/runs/20260510_092943_wanderer_smoke_three_hook_20260510/transcript.md`
- Result: PARTIAL PASS.

This smoke verifies that `wanderer` persona can now run through `./lilia ai-playtest`, and that a short detour around food / leaving / next visit can be absorbed without exposing hook management terms or turning the three hooks into a choice UI.

It does not yet verify all listed wanderer inputs as forced runtime turns, and the current `ai-playtest` loop does not run `scene-tick` / `apply-turn` after each turn.

## Commands

```bash
./lilia validate-session smoke_three_hook_20260510
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_growth_smoke.py tests/test_dev_menu.py -q
./lilia ai-playtest smoke_three_hook_20260510 --persona wanderer --turns 3 --engine auto --no-judge --verbose
rg -n "hook_id|current_function|candidate_id|Active Hook|Background Hook|Candidate|status|validator|FAIL|PASS|score|rubric|Main Hook|Relationship Hook|Life-Exploration|選択肢|1\.|2\.|3\." playtests/runs/20260510_092943_wanderer_smoke_three_hook_20260510/transcript.md
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_ai_playtest_judge.py tests/test_state_consistency.py tests/test_session_document_validator.py -q
```

## Command Results

- `validate-session`: PASS.
- `tests/test_growth_smoke.py tests/test_dev_menu.py`: `75 passed`.
- `ai-playtest`: completed `3/3` turns with `persona=wanderer`, `engine=codex`.
- transcript management-term grep: no matches.
- `tests/test_ai_playtest_judge.py tests/test_state_consistency.py tests/test_session_document_validator.py`: `40 passed, 1 skipped`.

## Runtime Observations

| Turn | Wanderer input | Hook absorption | Observation |
| --- | --- | --- | --- |
| 1 | 明日また来る / 温かいものを食べて帰る | Main + Life | GM kept the stopped-watch check active, accepted the food detour as a time/life beat, and did not drop the repair decision. |
| 2 | 駅前で一人で入りやすい店を聞く | Life + Relationship | GM answered through Mio's practical voice and boundary, while continuing the ten-minute watch check. |
| 3 | 今日は持ち帰るかもしれない / 明日の昼休みに再訪確認 | Main background/defer + Life | Player naturally moved toward a possible next visit without closing the Main Hook or forcing intimacy. |

## Static Routing Matrix For Requested Inputs

These rows were not all forced through runtime in this smoke. They are the expected routing based on the current `story_deck`, `event_card`, and Three Hook Spine docs.

| Input | Expected Hook | Expected Handling |
| --- | --- | --- |
| 駅に戻ります | Life-Exploration | Allow leaving the shop; keep the watch decision as background/pending or candidate next hook. |
| 飯を食いに行く | Life-Exploration | Accept food/rest as a short decompression beat; do not create an unrelated arc. |
| 今日は帰る | Life-Exploration + Main background | Respect leaving; carry the repair decision as deferred/resolved/worsened, not forgotten. |
| 主人公だけ沖縄に行く | Life-Exploration | Solo travel is allowed as a player action, but should carry time/cost/return conditions and not erase active hooks. |
| 葵も一緒に来る？ | Relationship + Life | In this session the heroine is Mio, not Aoi; companion travel should be conditional/deferred/declined based on personality, work, trust, and timing. |
| 同居しよう | Relationship | Treat as a boundary/maturity negotiation, not instant intimacy or reward. |
| 異世界に行こう | Life-Exploration, reframed unless the session supports unreal elements | Treat as joke/metaphor/dream/event unless grounded by session state. |
| この件は置いて別の仕事に行く | Main background/worsened + Life | Main Hook must remain deferred/backgrounded rather than vanish. |
| 怖いから帰る | Relationship + Life | Respect fear and boundary; convert to aftercare/return promise instead of punishing the player. |
| 関係ない雑談をする | Relationship, sometimes Life | Small talk should reveal distance/voice and leave one concrete return path. |

## Three Hook / UI Checks

- Three hooks were not presented as a numbered or menu-like choice UI.
- Play text did not leak `hook_id`, `status`, `current_function`, `candidate_id`, `Main Hook`, `Relationship Hook`, or `Life-Exploration`.
- Relationship Hook did not become affinity, route progress, or instant intimacy.
- Life Hook did not become unlimited free travel in the runtime excerpt; it stayed tied to time, station vicinity, cold doorway, and returning later.
- Main Hook remained present through the watch check and "ten minutes" boundary.

## Active / Background / Candidate State

- Active Hook before the run: `main_stopped_watch_after_hours`.
- Background Hooks before the run:
  - `relationship_keep_counter_distance`
  - `life_after_closing_route`
- Candidate Next Hooks before the run include watch assessment, name/calling distance, and possible revisit.
- The runtime playtest copies the session into `playtests/runs/.../session` and does not update the source session.
- Because this run did not execute `scene-tick` or `apply-turn`, hook status persistence after the detour remains a follow-up.

## Issues / Follow-up

1. `wanderer` was present in the playtest plan but not accepted by the CLI/menu before this task. This smoke adds the minimal runtime persona support.
2. Current `ai-playtest` does not run `scene-tick` / `apply-turn` after each turn, so HOOK-006 only verifies output behavior, not hook state persistence across Save Mode.
3. The runtime covered food / leave / revisit detours, but did not force all listed inputs. A later targeted runner could feed fixed wanderer inputs one by one.
4. If the "南口側のうどん屋" detail becomes meaningful, Save Mode should preserve it as a life/detail candidate. It is not treated as a current failure because the player explicitly asked for a nearby food option and the Life Hook allowed a nearby rest beat.

## Next Task Candidate

- Add a targeted wanderer prompt runner or fixture that forces the listed detour inputs and checks for hook UI leakage / management-term leakage.
- Extend AI Playtest loop later to call `scene-tick` and optional `apply-turn` so hook status persistence can be verified, not only transcript behavior.
