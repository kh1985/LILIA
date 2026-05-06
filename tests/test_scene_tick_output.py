from __future__ import annotations

import importlib.util
import json
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_lilia_module() -> ModuleType:
    loader = SourceFileLoader("lilia_cli_scene_tick_test", str(ROOT / "lilia"))
    spec = importlib.util.spec_from_loader("lilia_cli_scene_tick_test", loader)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_session(root: Path, turns_since_save: int) -> Path:
    session = root / "saves" / "tick_case"
    session.mkdir(parents=True)
    (session / "session.json").write_text(
        json.dumps(
            {
                "session_name": "tick_case",
                "autosave": {
                    "enabled": True,
                    "interval_turns": 10,
                    "turns_since_save": turns_since_save,
                    "autosave_required": False,
                },
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return session


def test_scene_tick_prints_save_required_at_threshold(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_session(tmp_path, 9)

    lilia.command_scene_tick(["tick_case"])

    output = capsys.readouterr().out
    assert "scene tick: 10/10" in output
    assert "autosave_required: true" in output
    assert "SAVE REQUIRED" in output
    assert "GM must enter save mode now" in output
    assert "Do not return the next play response until save completes" in output
    assert "save recommended" not in output

    data = json.loads((session / "session.json").read_text(encoding="utf-8"))
    assert data["autosave"]["turns_since_save"] == 10
    assert data["autosave"]["autosave_required"] is True


def test_scene_tick_keeps_required_true_after_threshold(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_session(tmp_path, 10)

    lilia.command_scene_tick(["tick_case"])

    output = capsys.readouterr().out
    assert "scene tick: 10/10" in output
    assert "autosave_required: true" in output
    assert "SAVE REQUIRED" in output

    data = json.loads((session / "session.json").read_text(encoding="utf-8"))
    assert data["autosave"]["turns_since_save"] == 11
    assert data["autosave"]["autosave_required"] is True
