from __future__ import annotations

import importlib.util
import re
from datetime import datetime, timezone
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_lilia_module() -> ModuleType:
    loader = SourceFileLoader("lilia_cli_recording_test", str(ROOT / "lilia"))
    spec = importlib.util.spec_from_loader("lilia_cli_recording_test", loader)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generate_codex_log_path_shape(tmp_path: Path) -> None:
    lilia = load_lilia_module()
    session = tmp_path / "saves" / "session_006"

    log_path = lilia.generate_codex_log_path(session)

    year = datetime.now(timezone.utc).astimezone().strftime("%Y")
    assert isinstance(log_path, Path)
    assert log_path.parent == session / "archive" / "logs" / year
    assert re.fullmatch(r"\d{8}_\d{6}\.log", log_path.name)


def test_wrap_codex_with_script_returns_original_when_script_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia_module()
    cmd = ["codex", "--no-alt-screen"]

    monkeypatch.setattr(lilia.shutil, "which", lambda name: None)

    assert lilia.wrap_codex_with_script(cmd, tmp_path / "log.log") is cmd


def test_wrap_codex_with_script_uses_bsd_script_on_darwin(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia_module()
    cmd = ["codex", "--cd", "/repo", "hello world"]
    log_path = tmp_path / "archive" / "logs" / "2026" / "session.log"

    monkeypatch.setattr(lilia.shutil, "which", lambda name: "/usr/bin/script")
    monkeypatch.setattr(lilia.sys, "platform", "darwin")

    wrapped = lilia.wrap_codex_with_script(cmd, log_path)

    assert wrapped == ["script", "-q", str(log_path), *cmd]
    assert log_path.parent.is_dir()


def test_wrap_codex_with_script_uses_util_linux_script_on_linux(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia_module()
    cmd = ["codex", "--cd", "/repo path", "hello world"]
    log_path = tmp_path / "archive" / "logs" / "2026" / "session.log"

    monkeypatch.setattr(lilia.shutil, "which", lambda name: "/usr/bin/script")
    monkeypatch.setattr(lilia.sys, "platform", "linux")

    wrapped = lilia.wrap_codex_with_script(cmd, log_path)

    assert wrapped == ["script", "-q", "-c", lilia.shlex.join(cmd), str(log_path)]
    assert log_path.parent.is_dir()


def test_wrap_codex_with_script_returns_original_on_unknown_platform(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia_module()
    cmd = ["codex", "--no-alt-screen"]
    log_path = tmp_path / "archive" / "logs" / "2026" / "session.log"

    monkeypatch.setattr(lilia.shutil, "which", lambda name: "/usr/bin/script")
    monkeypatch.setattr(lilia.sys, "platform", "win32")

    assert lilia.wrap_codex_with_script(cmd, log_path) is cmd
    assert log_path.parent.is_dir()
