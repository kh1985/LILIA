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

    cleaned, persona, turns, engine, verbose, quiet, scene_tick, judge = (
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
    assert judge is False


def test_ai_playtest_can_disable_scene_tick() -> None:
    lilia = load_lilia()

    parsed = lilia.parse_ai_playtest_options(["s", "--no-scene-tick"])

    assert parsed[-2] is False
    assert parsed[-1] is True


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
    assert "## Turn 1 - PLAYER" not in transcript
    assert (tmp_path / "run" / "save_checkpoint.md").exists()
    data = json.loads((session / "session.json").read_text(encoding="utf-8"))
    assert data["autosave"]["turns_since_save"] == 1
    assert data["autosave"]["autosave_required"] is True


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
