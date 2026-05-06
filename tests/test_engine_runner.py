from __future__ import annotations

import os
from pathlib import Path
import sys
import textwrap
import time

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.common import engine_runner


def _which_for(*available: str):
    available_set = set(available)

    def fake_which(command: str) -> str | None:
        return f"/fake/bin/{command}" if command in available_set else None

    return fake_which


def test_codex_command_uses_neutral_cwd(tmp_path: Path) -> None:
    command = engine_runner._build_engine_command("codex", tmp_path)
    cd_index = command.index("--cd")

    assert command[cd_index + 1] == str(engine_runner._CODEX_NEUTRAL_CWD)
    assert command[cd_index + 1] != str(tmp_path)
    assert "--skip-git-repo-check" in command


def test_codex_neutral_cwd_exists_and_is_empty() -> None:
    neutral_cwd = engine_runner._CODEX_NEUTRAL_CWD

    assert neutral_cwd.exists()
    assert neutral_cwd.is_dir()
    assert list(neutral_cwd.iterdir()) == []


def test_engine_candidates_auto_defaults_to_codex(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LILIA_DEFAULT_ENGINE", raising=False)
    monkeypatch.setattr(engine_runner.shutil, "which", _which_for("claude", "codex"))

    assert engine_runner.engine_candidates("auto") == ["codex", "claude"]


def test_engine_candidates_auto_respects_default_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LILIA_DEFAULT_ENGINE", "claude")
    monkeypatch.setattr(engine_runner.shutil, "which", _which_for("claude", "codex"))

    assert engine_runner.engine_candidates("auto") == ["claude", "codex"]


def test_engine_candidates_explicit_returns_only_requested_when_available(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(engine_runner.shutil, "which", _which_for("claude"))

    assert engine_runner.engine_candidates("claude") == ["claude"]


def test_engine_candidates_filter_unavailable_clis(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LILIA_DEFAULT_ENGINE", raising=False)
    monkeypatch.setattr(engine_runner.shutil, "which", _which_for("claude"))
    assert engine_runner.engine_candidates("auto") == ["claude"]
    assert engine_runner.engine_candidates("codex") == []

    monkeypatch.setattr(engine_runner.shutil, "which", _which_for("codex"))
    assert engine_runner.engine_candidates("auto") == ["codex"]
    assert engine_runner.engine_candidates("claude") == []

    monkeypatch.setattr(engine_runner.shutil, "which", _which_for())
    assert engine_runner.engine_candidates("auto") == []
    assert engine_runner.engine_candidates("codex") == []
    assert engine_runner.engine_candidates("claude") == []


def test_run_engine_reads_stdout_from_dummy_command(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        engine_runner,
        "_build_engine_command",
        lambda engine, root: ["/bin/echo", "hello"],
    )

    assert engine_runner.run_engine("dummy", "ignored", timeout=5, root=tmp_path) == "hello"


def test_run_engine_timeout_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        engine_runner,
        "_build_engine_command",
        lambda engine, root: ["/bin/sleep", "30"],
    )

    with pytest.raises(engine_runner.EngineTimeoutError):
        engine_runner.run_engine("dummy", "ignored", timeout=0.1, root=tmp_path)


@pytest.mark.skipif(os.name != "posix", reason="process group kill assertion is POSIX-specific")
def test_run_engine_timeout_kills_process_group(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    child_pid_path = tmp_path / "child.pid"
    script = tmp_path / "spawn_child.py"
    script.write_text(
        textwrap.dedent(
            f"""
            import subprocess
            import time

            child = subprocess.Popen(["/bin/sleep", "30"])
            {str(child_pid_path)!r}
            with open({str(child_pid_path)!r}, "w", encoding="utf-8") as handle:
                handle.write(str(child.pid))
            time.sleep(30)
            """
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        engine_runner,
        "_build_engine_command",
        lambda engine, root: [sys.executable, str(script)],
    )

    with pytest.raises(engine_runner.EngineTimeoutError):
        engine_runner.run_engine("dummy", "ignored", timeout=0.5, root=tmp_path)

    deadline = time.time() + 5
    while not child_pid_path.exists() and time.time() < deadline:
        time.sleep(0.05)
    child_pid = int(child_pid_path.read_text(encoding="utf-8"))

    deadline = time.time() + 5
    while time.time() < deadline:
        try:
            os.kill(child_pid, 0)
        except ProcessLookupError:
            break
        time.sleep(0.05)
    else:
        pytest.fail(f"child process {child_pid} survived timeout process-group kill")
