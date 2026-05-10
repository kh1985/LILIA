from __future__ import annotations

import importlib.util
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

    cleaned, persona, turns, engine, verbose, quiet, judge = (
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
    assert judge is False


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
