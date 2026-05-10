from __future__ import annotations

import importlib.util
import json
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_lilia():
    loader = SourceFileLoader("lilia_launcher", str(ROOT / "lilia"))
    spec = importlib.util.spec_from_loader("lilia_launcher", loader)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_growth_smoke_option_defaults() -> None:
    lilia = load_lilia()

    cleaned, persona, segments, turns, engine, judge, judge_engine, verbose, quiet = (
        lilia.parse_growth_smoke_options(["session_001"])
    )

    assert cleaned == ["session_001"]
    assert persona == "normal"
    assert segments == 3
    assert turns == 10
    assert engine == "auto"
    assert judge is True
    assert judge_engine is None
    assert verbose is False
    assert quiet is False


@pytest.mark.parametrize("args", [["s", "--segments", "0"], ["s", "--segments=-1"]])
def test_growth_smoke_segments_must_be_positive(args: list[str]) -> None:
    lilia = load_lilia()

    with pytest.raises(SystemExit):
        lilia.parse_growth_smoke_options(args)


@pytest.mark.parametrize(
    "args",
    [["s", "--turns-per-segment", "0"], ["s", "--turns-per-segment=-1"]],
)
def test_growth_smoke_turns_per_segment_must_be_positive(args: list[str]) -> None:
    lilia = load_lilia()

    with pytest.raises(SystemExit):
        lilia.parse_growth_smoke_options(args)


def test_growth_smoke_judge_flags_conflict() -> None:
    lilia = load_lilia()

    with pytest.raises(SystemExit):
        lilia.parse_growth_smoke_options(["s", "--judge", "--no-judge"])


def test_ai_playtest_judge_default_and_no_judge() -> None:
    lilia = load_lilia()

    assert lilia.parse_ai_playtest_options(["s"])[-1] is True
    assert lilia.parse_ai_playtest_options(["s", "--no-judge"])[-1] is False
    with pytest.raises(SystemExit):
        lilia.parse_ai_playtest_options(["s", "--judge", "--no-judge"])


def test_ai_playtest_accepts_wanderer_persona() -> None:
    lilia = load_lilia()

    cleaned, persona, turns, engine, verbose, quiet, scene_tick, apply_turn_checkpoint, judge = (
        lilia.parse_ai_playtest_options(
            ["s", "--persona", "wanderer", "--turns", "3", "--no-judge"]
        )
    )

    assert cleaned == ["s"]
    assert persona == "wanderer"
    assert turns == 3
    assert engine == "auto"
    assert verbose is False
    assert quiet is False
    assert scene_tick is True
    assert apply_turn_checkpoint is False
    assert judge is False


def test_ai_playtest_can_disable_scene_tick() -> None:
    lilia = load_lilia()

    cleaned, persona, turns, engine, verbose, quiet, scene_tick, apply_turn_checkpoint, judge = (
        lilia.parse_ai_playtest_options(["s", "--no-scene-tick"])
    )

    assert scene_tick is False
    assert apply_turn_checkpoint is False
    assert judge is True


def test_ai_playtest_accepts_apply_turn_checkpoint_flag() -> None:
    lilia = load_lilia()

    cleaned, persona, turns, engine, verbose, quiet, scene_tick, apply_turn_checkpoint, judge = (
        lilia.parse_ai_playtest_options(["s", "--apply-turn-checkpoint"])
    )

    assert cleaned == ["s"]
    assert scene_tick is True
    assert apply_turn_checkpoint is True
    assert judge is True


def test_ai_playtest_segment_ticks_run_session(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)

    session = tmp_path / "run_session"
    session.mkdir()
    (session / "session.json").write_text(
        json.dumps(
            {
                "session_name": "run_session",
                "autosave": {
                    "enabled": True,
                    "interval_turns": 10,
                    "turns_since_save": 0,
                    "autosave_required": False,
                },
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        lilia,
        "build_ai_playtest_gm_prompt",
        lambda session_path, history, player_boundary: "GM_PROMPT",
    )
    monkeypatch.setattr(
        lilia,
        "build_ai_playtest_player_prompt",
        lambda persona, history, last_gm_text: "PLAYER_PROMPT",
    )
    responses = iter(["gm 1", "player 1", "gm 2", "player 2"])
    monkeypatch.setattr(
        lilia,
        "run_engine_cli",
        lambda engine, prompt, timeout, root: next(responses),
    )

    transcript_md, transcript_jsonl, completed_turns, _ = lilia.run_ai_playtest_segment(
        run_dir=tmp_path / "run",
        session_path=session,
        transcript_title="Test Transcript",
        source_session_label="saves/source",
        run_session_label="playtests/runs/run/session",
        persona="normal",
        turns=2,
        requested_engine="auto",
        engine="codex",
        verbose=False,
        quiet=True,
        history=[],
    )

    assert completed_turns == 2
    data = json.loads((session / "session.json").read_text(encoding="utf-8"))
    assert data["autosave"]["turns_since_save"] == 2
    assert data["autosave"]["autosave_required"] is False
    transcript = transcript_md.read_text(encoding="utf-8")
    assert "scene_tick_enabled: true" in transcript
    assert "## Turn 1 - SCENE TICK" in transcript
    assert "- scene_tick: 1/10" in transcript
    assert "## Turn 2 - SCENE TICK" in transcript
    assert "- scene_tick: 2/10" in transcript
    jsonl = transcript_jsonl.read_text(encoding="utf-8")
    assert '"role": "scene_tick"' in jsonl


def test_ai_playtest_segment_stops_at_autosave_checkpoint(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)

    session = tmp_path / "run_session"
    session.mkdir()
    (session / "session.json").write_text(
        json.dumps(
            {
                "session_name": "run_session",
                "autosave": {
                    "enabled": True,
                    "interval_turns": 1,
                    "turns_since_save": 0,
                    "autosave_required": False,
                },
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        lilia,
        "build_ai_playtest_gm_prompt",
        lambda session_path, history, player_boundary: "GM_PROMPT",
    )
    monkeypatch.setattr(
        lilia,
        "build_ai_playtest_player_prompt",
        lambda persona, history, last_gm_text: "PLAYER_PROMPT",
    )
    calls: list[str] = []

    def fake_run_engine(engine: str, prompt: str, timeout: float, root: Path) -> str:
        calls.append(prompt)
        return "gm checkpoint"

    monkeypatch.setattr(lilia, "run_engine_cli", fake_run_engine)

    transcript_md, _, completed_turns, _ = lilia.run_ai_playtest_segment(
        run_dir=tmp_path / "run",
        session_path=session,
        transcript_title="Test Transcript",
        source_session_label="saves/source",
        run_session_label="playtests/runs/run/session",
        persona="normal",
        turns=3,
        requested_engine="auto",
        engine="codex",
        verbose=False,
        quiet=True,
        history=[],
    )

    assert completed_turns == 1
    assert calls == ["GM_PROMPT"]
    transcript = transcript_md.read_text(encoding="utf-8")
    assert "autosave_required: true" in transcript
    assert "apply_turn_executed: false" in transcript
    assert "## Turn 1 - PLAYER" not in transcript
    assert (tmp_path / "run" / "save_checkpoint.md").exists()
    jsonl = (tmp_path / "run" / "transcript.jsonl").read_text(encoding="utf-8")
    assert '"apply_turn_executed": false' in jsonl
    assert not (tmp_path / "run" / "checkpoint_turn_update.md").exists()
    data = json.loads((session / "session.json").read_text(encoding="utf-8"))
    assert data["autosave"]["turns_since_save"] == 1
    assert data["autosave"]["autosave_required"] is True


def test_ai_playtest_apply_turn_checkpoint_writes_dry_run_artifacts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)

    session = tmp_path / "run_session"
    session.mkdir()
    original_session_json = json.dumps(
        {
            "session_name": "run_session",
            "autosave": {
                "enabled": True,
                "interval_turns": 1,
                "turns_since_save": 0,
                "autosave_required": False,
            },
        },
        ensure_ascii=False,
    ) + "\n"
    (session / "session.json").write_text(original_session_json, encoding="utf-8")

    monkeypatch.setattr(
        lilia,
        "build_ai_playtest_gm_prompt",
        lambda session_path, history, player_boundary: "GM_PROMPT",
    )
    monkeypatch.setattr(
        lilia,
        "build_ai_playtest_player_prompt",
        lambda persona, history, last_gm_text: "PLAYER_PROMPT",
    )
    monkeypatch.setattr(
        lilia,
        "run_engine_cli",
        lambda engine, prompt, timeout, root: "gm checkpoint",
    )

    transcript_md, _, completed_turns, _ = lilia.run_ai_playtest_segment(
        run_dir=tmp_path / "run",
        session_path=session,
        transcript_title="Test Transcript",
        source_session_label="saves/source",
        run_session_label="playtests/runs/run/session",
        persona="normal",
        turns=3,
        requested_engine="auto",
        engine="codex",
        verbose=False,
        quiet=True,
        history=[],
        apply_turn_checkpoint=True,
    )

    assert completed_turns == 1
    run_dir = tmp_path / "run"
    candidate = run_dir / "checkpoint_turn_update.md"
    dry_run = run_dir / "checkpoint_apply_turn_dry_run.md"
    summary = run_dir / "checkpoint_summary.md"
    prompt = run_dir / "checkpoint_turn_update_prompt.md"
    assert candidate.exists()
    assert dry_run.exists()
    assert summary.exists()
    assert prompt.exists()
    assert "## state" in candidate.read_text(encoding="utf-8")
    dry_run_text = dry_run.read_text(encoding="utf-8")
    assert "dry_run_result: PASS" in dry_run_text
    assert "apply_turn_executed: false" in dry_run_text
    assert "lilia/main/state.md" in dry_run_text
    assert "This dry-run does not reset autosave counters." in dry_run_text
    checkpoint = (run_dir / "save_checkpoint.md").read_text(encoding="utf-8")
    assert "checkpoint_mode: dry-run" in checkpoint
    assert "turn_update_candidate:" in checkpoint
    assert "apply_turn_dry_run:" in checkpoint
    transcript = transcript_md.read_text(encoding="utf-8")
    assert "## Turn 1 - APPLY-TURN CHECKPOINT" in transcript
    assert "dry_run_result: PASS" in transcript
    data = json.loads((session / "session.json").read_text(encoding="utf-8"))
    assert data["autosave"]["turns_since_save"] == 1
    assert data["autosave"]["autosave_required"] is True
    assert "applied_turn_updates" not in data


def test_ai_playtest_apply_turn_checkpoint_uses_judge_closure_candidate(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "PLAYTESTS_DIR", tmp_path / "playtests")
    monkeypatch.setattr(
        lilia,
        "ai_playtest_run_dir",
        lambda persona, session_name: tmp_path / "playtests" / "runs" / "closure_run",
    )

    src_session = tmp_path / "saves" / "source_session"
    (src_session / "story").mkdir(parents=True)
    (src_session / "session.json").write_text(
        json.dumps(
            {
                "session_name": "source_session",
                "autosave": {
                    "enabled": True,
                    "interval_turns": 1,
                    "turns_since_save": 0,
                    "autosave_required": False,
                },
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (src_session / "story" / "story_deck.md").write_text(
        "# Story Deck\n\n## Candidate Next Hooks\n\n",
        encoding="utf-8",
    )

    judge_payload = {
        "result": "WARN",
        "summary": "closure candidate found",
        "scores": {
            "voice_continuity": {"score": 4, "notes": "ok"},
            "tempo_guard": {"score": 3, "notes": "drift"},
            "reply_affordance": {"score": 3, "notes": "thin"},
            "relationship_change_grounding": {"score": 4, "notes": "grounded"},
            "inner_hidden_leakage": {"score": 5, "notes": "none"},
            "over_leading": {"score": 4, "notes": "ok"},
            "arc_closure_scene_progression": {"score": 2, "notes": "closure drift"},
        },
        "warnings": [],
        "failures": [],
        "recommended_fixes": [],
        "notable_good_moments": [],
        "closure_candidates": [
            {
                "closure_candidate_turns": [1],
                "reason": "戸が閉まり、翌日電話の入口が成立した",
                "possible_next_hook_type": "relationship",
                "possible_next_question": "翌日昼過ぎ、澪からの電話にどう出るか",
                "risk_if_continued": "同じ余韻が続く",
                "recommended_closure_action": "次sceneを電話へ渡す",
            }
        ],
    }

    monkeypatch.setattr(
        lilia,
        "build_ai_playtest_gm_prompt",
        lambda session_path, history, player_boundary: "GM_PROMPT",
    )
    monkeypatch.setattr(
        lilia,
        "build_ai_playtest_player_prompt",
        lambda persona, history, last_gm_text: "PLAYER_PROMPT",
    )

    def fake_engine(engine: str, prompt: str, timeout: float, root: Path) -> str:
        if "AI Playtest Judge" in prompt:
            return "```json\n" + json.dumps(judge_payload, ensure_ascii=False) + "\n```"
        return "gm checkpoint"

    monkeypatch.setattr(lilia, "run_engine_cli", fake_engine)

    run_dir = lilia.run_ai_playtest_session(
        src_session=src_session,
        persona="normal",
        turns=3,
        requested_engine="auto",
        engine="codex",
        verbose=False,
        quiet=True,
        judge=True,
        apply_turn_checkpoint=True,
    )

    candidate = (run_dir / "checkpoint_turn_update.md").read_text(encoding="utf-8")
    assert "- closure_candidate_used: true" in candidate
    assert "## next_hook" in candidate
    assert "翌日昼過ぎ、澪からの電話にどう出るか" in candidate
    assert "## hook_updates" in candidate
    assert "- hook_type: relationship" in candidate
    assert "- update_target: candidate" in candidate
    assert "active stateへ昇格する" in candidate

    dry_run = (run_dir / "checkpoint_apply_turn_dry_run.md").read_text(encoding="utf-8")
    assert "dry_run_result: PASS" in dry_run
    assert "- next_hook" in dry_run
    assert "- hook_updates" in dry_run
    assert "current/scene.md" in dry_run
    assert "current/event_card.md" in dry_run
    assert "current/hotset.md" in dry_run
    assert "story/story_deck.md" in dry_run

    report = (run_dir / "report.md").read_text(encoding="utf-8")
    assert "## Closure Candidates / Next Active Hook Candidate" in report
    assert "- closure_candidate_used: true" in report
    assert "- hook_updates_candidate_included: true" in report
    assert "- apply_turn_executed: false" in report

    source_data = json.loads((src_session / "session.json").read_text(encoding="utf-8"))
    run_data = json.loads((run_dir / "session" / "session.json").read_text(encoding="utf-8"))
    assert source_data["autosave"]["autosave_required"] is False
    assert run_data["autosave"]["autosave_required"] is True
    assert "applied_turn_updates" not in run_data


def test_ai_playtest_closure_checkpoint_sanitizes_judge_heading_injection(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)

    session = tmp_path / "session"
    (session / "story").mkdir(parents=True)
    (session / "session.json").write_text(
        '{"session_name":"session","autosave":{"enabled":true,"interval_turns":1,"turns_since_save":1,"autosave_required":true}}\n',
        encoding="utf-8",
    )
    (session / "story" / "story_deck.md").write_text(
        "# Story Deck\n\n## Candidate Next Hooks\n\n",
        encoding="utf-8",
    )
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    transcript = run_dir / "transcript.md"
    transcript.write_text("# transcript\n\n## Turn 1 - GM\n本文\n", encoding="utf-8")
    (run_dir / "save_checkpoint.md").write_text(
        "# AI Playtest Save Checkpoint\n\n- turn: 1\n- scene_tick: 1/1\n- autosave_required: true\n",
        encoding="utf-8",
    )

    closure_candidate = {
        "closure_candidate_turns": ["1"],
        "reason": "閉じられる\n## memory\n- injected",
        "possible_next_hook_type": "relationship",
        "possible_next_question": "\n## memory\n- injected memory",
        "risk_if_continued": "# hidden heading",
        "recommended_closure_action": "\n## beliefs\n- injected belief",
    }

    artifacts = lilia.update_ai_playtest_checkpoint_with_closure_candidate(
        run_dir=run_dir,
        session_path=session,
        transcript_md=transcript,
        closure_candidate=closure_candidate,
        history=[{"turn": 1, "role": "gm", "text": "本文"}],
    )
    assert artifacts is not None

    candidate = (run_dir / "checkpoint_turn_update.md").read_text(encoding="utf-8")
    assert "\n## memory" not in candidate
    assert "\n## beliefs" not in candidate
    assert "review: hidden heading" in candidate
    assert "## next_hook" in candidate
    assert "## hook_updates" in candidate

    dry_run = (run_dir / "checkpoint_apply_turn_dry_run.md").read_text(encoding="utf-8")
    assert "dry_run_result: PASS" in dry_run
    assert "- next_hook" in dry_run
    assert "- hook_updates" in dry_run
    assert "- memory" not in dry_run
    assert "- beliefs" not in dry_run

    prompt = (run_dir / "checkpoint_turn_update_prompt.md").read_text(encoding="utf-8")
    assert "Recent transcript excerpt:" in prompt
    assert "### GM (turn 1)" in prompt


def test_ai_playtest_session_checkpoint_does_not_mutate_source_and_reports(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "PLAYTESTS_DIR", tmp_path / "playtests")
    monkeypatch.setattr(lilia, "ai_playtest_run_dir", lambda persona, session_name: tmp_path / "playtests" / "runs" / "checkpoint_run")

    src_session = tmp_path / "saves" / "source_session"
    src_session.mkdir(parents=True)
    source_session_json = json.dumps(
        {
            "session_name": "source_session",
            "autosave": {
                "enabled": True,
                "interval_turns": 1,
                "turns_since_save": 0,
                "autosave_required": False,
            },
        },
        ensure_ascii=False,
    ) + "\n"
    (src_session / "session.json").write_text(source_session_json, encoding="utf-8")
    (src_session / "marker.md").write_text("source marker\n", encoding="utf-8")

    monkeypatch.setattr(
        lilia,
        "build_ai_playtest_gm_prompt",
        lambda session_path, history, player_boundary: "GM_PROMPT",
    )
    monkeypatch.setattr(
        lilia,
        "build_ai_playtest_player_prompt",
        lambda persona, history, last_gm_text: "PLAYER_PROMPT",
    )
    monkeypatch.setattr(
        lilia,
        "run_engine_cli",
        lambda engine, prompt, timeout, root: "gm checkpoint",
    )

    run_dir = lilia.run_ai_playtest_session(
        src_session=src_session,
        persona="normal",
        turns=3,
        requested_engine="auto",
        engine="codex",
        verbose=False,
        quiet=True,
        judge=False,
        apply_turn_checkpoint=True,
    )

    assert (src_session / "session.json").read_text(encoding="utf-8") == source_session_json
    assert (src_session / "marker.md").read_text(encoding="utf-8") == "source marker\n"
    run_session_data = json.loads((run_dir / "session" / "session.json").read_text(encoding="utf-8"))
    assert run_session_data["autosave"]["autosave_required"] is True
    report = (run_dir / "report.md").read_text(encoding="utf-8")
    assert "## Save Checkpoint" in report
    assert "checkpoint_mode: dry-run" in report
    assert "apply_turn_executed: false" in report


def test_growth_run_dir_name(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    lilia = load_lilia()
    monkeypatch.setattr(lilia, "PLAYTESTS_DIR", tmp_path / "playtests")

    path = lilia.growth_run_dir("normal", "session_001")

    assert path.parent == tmp_path / "playtests" / "growth_runs"
    assert path.name.endswith("_normal_session_001")
    assert len(path.name.split("_")[0]) == 8


def test_growth_summary_minimal_rendering() -> None:
    lilia = load_lilia()

    body = lilia.render_growth_summary_md(
        result="PASS",
        source_session="saves/session_001",
        run_session="playtests/growth_runs/run/session",
        persona="normal",
        engine="codex",
        segments=1,
        turns_per_segment=1,
        judge_enabled=True,
        segment_rows=[
            {
                "segment": "001",
                "result": "PASS",
                "notes": "ok",
                "report": "segment_001/report.md",
            }
        ],
    )

    assert "# LILIA Growth Smoke Summary" in body
    assert "- Result: PASS" in body
    assert "| 001 | PASS | ok | segment_001/report.md |" in body
    assert "apply-turn / resume segment boundary" in body
