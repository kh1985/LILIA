from __future__ import annotations

import importlib.util
import json
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class TTYBuffer:
    def __init__(self) -> None:
        self.text = ""

    def isatty(self) -> bool:
        return True

    def write(self, text: str) -> int:
        self.text += text
        return len(text)

    def flush(self) -> None:
        pass


def load_lilia_module() -> ModuleType:
    loader = SourceFileLoader("lilia_cli_launch_recording_test", str(ROOT / "lilia"))
    spec = importlib.util.spec_from_loader("lilia_cli_launch_recording_test", loader)
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


def prepare_launch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> tuple[ModuleType, Path, list[list[str]], TTYBuffer]:
    lilia = load_lilia_module()
    session = write_session(tmp_path)
    calls: list[list[str]] = []
    stdout = TTYBuffer()

    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    monkeypatch.setattr(lilia.sys, "stdin", TTYBuffer())
    monkeypatch.setattr(lilia.sys, "stdout", stdout)
    monkeypatch.setattr(
        lilia.subprocess,
        "run",
        lambda cmd, cwd: calls.append(cmd) or SimpleNamespace(returncode=0),
    )
    return lilia, session, calls, stdout


def test_maybe_launch_records_with_script_when_available(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia, session, calls, stdout = prepare_launch(monkeypatch, tmp_path)

    monkeypatch.setattr(lilia.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(lilia.sys, "platform", "darwin")

    lilia.maybe_launch_codex_interactive(tmp_path / "prompt.md", "resume", session, record=True)

    assert calls
    assert calls[0][:3] == ["script", "-q", str(calls[0][2])]
    assert calls[0][2].startswith(str(session / "archive" / "logs"))
    assert calls[0][2].endswith(".log")
    assert calls[0][3] == "codex"
    assert (session / "archive" / "logs").is_dir()
    assert "recording terminal: saves/session_006/archive/logs/" in stdout.text


def test_maybe_launch_skips_recording_when_record_false(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia, session, calls, stdout = prepare_launch(monkeypatch, tmp_path)

    monkeypatch.setattr(lilia.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(lilia.sys, "platform", "darwin")

    lilia.maybe_launch_codex_interactive(tmp_path / "prompt.md", "resume", session, record=False)

    assert calls
    assert calls[0][0] == "codex"
    assert "recording terminal:" not in stdout.text


def test_maybe_launch_warns_and_continues_when_script_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia, session, calls, stdout = prepare_launch(monkeypatch, tmp_path)

    def which(name: str) -> str | None:
        return "/usr/bin/codex" if name == "codex" else None

    monkeypatch.setattr(lilia.shutil, "which", which)
    monkeypatch.setattr(lilia.sys, "platform", "darwin")

    lilia.maybe_launch_codex_interactive(tmp_path / "prompt.md", "resume", session, record=True)

    assert calls
    assert calls[0][0] == "codex"
    assert "terminal recording unavailable" in stdout.text
    assert "launching Codex interactive now." in stdout.text
