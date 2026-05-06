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
    loader = SourceFileLoader("lilia_cli_no_record_flag_test", str(ROOT / "lilia"))
    spec = importlib.util.spec_from_loader("lilia_cli_no_record_flag_test", loader)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_session(root: Path, name: str = "session_006") -> Path:
    session = root / "saves" / name
    session.mkdir(parents=True)
    (session / "session.json").write_text(
        json.dumps({"session_name": name, "current_phase": "active"}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return session


def test_codex_resume_no_record_flag_disables_recording(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia_module()
    session = write_session(tmp_path)
    calls: list[tuple[Path, str, Path, bool]] = []

    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    monkeypatch.setattr(lilia, "codex_prompt_path", lambda session_path, mode: tmp_path / f"{mode}.md")
    monkeypatch.setattr(
        lilia,
        "maybe_launch_codex_interactive",
        lambda prompt_path, mode, session_path, record=True: calls.append(
            (prompt_path, mode, session_path, record)
        ),
    )

    lilia.command_codex_resume(["session_006", "--no-record"])

    assert calls == [(tmp_path / "resume.md", "resume", session, False)]


def test_codex_resume_defaults_to_recording(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia_module()
    session = write_session(tmp_path)
    calls: list[tuple[Path, str, Path, bool]] = []

    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    monkeypatch.setattr(lilia, "codex_prompt_path", lambda session_path, mode: tmp_path / f"{mode}.md")
    monkeypatch.setattr(
        lilia,
        "maybe_launch_codex_interactive",
        lambda prompt_path, mode, session_path, record=True: calls.append(
            (prompt_path, mode, session_path, record)
        ),
    )

    lilia.command_codex_resume(["session_006"])

    assert calls == [(tmp_path / "resume.md", "resume", session, True)]


def test_codex_new_no_record_flag_is_removed_before_session_parsing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia_module()
    calls: list[tuple[Path, str, Path, bool]] = []

    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    monkeypatch.setattr(lilia, "codex_prompt_path", lambda session_path, mode: tmp_path / f"{mode}.md")
    monkeypatch.setattr(
        lilia,
        "maybe_launch_codex_interactive",
        lambda prompt_path, mode, session_path, record=True: calls.append(
            (prompt_path, mode, session_path, record)
        ),
    )

    lilia.command_codex_new(["new_case", "--no-record"])

    assert calls
    assert calls[0] == (tmp_path / "new.md", "new", tmp_path / "saves" / "new_case", False)
