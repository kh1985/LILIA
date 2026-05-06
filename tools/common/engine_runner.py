"""Shared LLM CLI runner for LILIA generation tools."""

from __future__ import annotations

import atexit
from collections.abc import Callable
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import threading


SUPPORTED_ENGINES = ("codex", "claude")
DEFAULT_TIMEOUT_SECONDS = 600

# Codex auto-loads files under --cd into context. Pointing it at the LILIA
# repo can balloon small prompts by tens of thousands of tokens, so codex gets
# a process-wide empty cwd instead.
_CODEX_NEUTRAL_CWD: Path = Path(tempfile.mkdtemp(prefix="lilia_codex_neutral_"))


@atexit.register
def _cleanup_codex_neutral_cwd() -> None:
    try:
        shutil.rmtree(_CODEX_NEUTRAL_CWD, ignore_errors=True)
    except Exception:
        pass


class EngineRunnerError(RuntimeError):
    """Raised when an engine CLI fails to produce usable output."""


class EngineTimeoutError(EngineRunnerError):
    """Raised when an engine CLI exceeds its timeout."""


class EngineUnavailableError(EngineRunnerError):
    """Raised when a requested engine CLI is unavailable."""


def available_engines() -> list[str]:
    """Return supported engine CLIs available on PATH."""

    return [engine for engine in SUPPORTED_ENGINES if shutil.which(engine) is not None]


def resolve_engine(requested: str) -> str | None:
    """Resolve a requested engine to one available CLI, or ``None``."""

    if requested == "auto":
        candidates = engine_candidates(requested)
        return candidates[0] if candidates else None
    if requested in SUPPORTED_ENGINES and shutil.which(requested):
        return requested
    return None


def engine_candidates(requested: str) -> list[str]:
    """Return candidate engines in fallback order."""

    if requested not in {"auto", *SUPPORTED_ENGINES}:
        raise EngineUnavailableError("engine must be one of: codex, claude, auto")
    if requested != "auto":
        return [requested] if shutil.which(requested) is not None else []

    return _default_engine_priority()


def run_with_fallback(
    engines: list[str],
    prompt: str,
    *,
    timeout: float,
    root: Path,
    on_failure: Callable[[str, Exception], None] | None = None,
) -> tuple[str, str]:
    """Run candidate engines in order and return ``(stdout, engine_used)``."""

    last_error: Exception | None = None
    for engine in engines:
        try:
            return run_engine(engine, prompt, timeout=timeout, root=root), engine
        except Exception as exc:
            last_error = exc
            if on_failure is not None:
                on_failure(engine, exc)
    if last_error is None:
        raise EngineUnavailableError("no engine candidates were provided")
    raise last_error


def run_engine(engine: str, prompt: str, *, timeout: float, root: Path) -> str:
    """Run one LLM CLI with prompt on stdin and return stripped stdout."""

    command = _build_engine_command(engine, root)
    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []
    creationflags = 0
    popen_kwargs: dict[str, object] = {}
    if os.name == "posix":
        popen_kwargs["start_new_session"] = True
    elif os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)

    try:
        proc = subprocess.Popen(
            command,
            cwd=root,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            creationflags=creationflags,
            **popen_kwargs,
        )
    except FileNotFoundError as exc:
        raise EngineUnavailableError(f"{engine} command was not found") from exc

    stdout_thread = threading.Thread(target=_read_stream, args=(proc.stdout, stdout_chunks), daemon=True)
    stderr_thread = threading.Thread(target=_read_stream, args=(proc.stderr, stderr_chunks), daemon=True)
    stdout_thread.start()
    stderr_thread.start()

    try:
        if proc.stdin is not None:
            proc.stdin.write(prompt)
            proc.stdin.close()
        proc.wait(timeout=timeout)
    except BrokenPipeError:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        _terminate_process_group(proc)
        _join_readers(stdout_thread, stderr_thread)
        raise EngineTimeoutError(f"{engine} generation timed out after {timeout:g} seconds") from exc

    _join_readers(stdout_thread, stderr_thread)
    stdout = "".join(stdout_chunks).strip()
    stderr = "".join(stderr_chunks).strip()
    if proc.returncode != 0:
        detail = stderr or "(no stderr)"
        raise EngineRunnerError(f"{engine} CLI failed: {detail}")
    if not stdout:
        detail = stderr or "empty stdout"
        raise EngineRunnerError(f"{engine} CLI returned empty output: {detail}")
    return stdout


def _default_engine_priority() -> list[str]:
    env = os.environ.get("LILIA_DEFAULT_ENGINE", "").strip().lower()
    if env == "claude":
        priority = ["claude", "codex"]
    elif env == "codex":
        priority = ["codex", "claude"]
    else:
        # Long profile/spine/downstream prompts are more stable on codex in
        # current LILIA operation; character YAML keeps its own claude-first
        # route in tools.character.core.master.
        priority = ["codex", "claude"]
    return [engine for engine in priority if shutil.which(engine) is not None]


def _build_engine_command(engine: str, root: Path) -> list[str]:
    if engine == "claude":
        return ["claude", "-p", "--permission-mode", "dontAsk"]
    if engine == "codex":
        effort = os.environ.get("LILIA_CODEX_REASONING_EFFORT", "low").strip() or "low"
        return [
            "codex",
            "exec",
            "--cd",
            str(_CODEX_NEUTRAL_CWD),
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "--color",
            "never",
            "-c",
            f"model_reasoning_effort={effort}",
            "-",
        ]
    raise EngineUnavailableError(f"unsupported engine: {engine}")


def _read_stream(stream: object, chunks: list[str]) -> None:
    if stream is None:
        return
    for chunk in stream:
        chunks.append(chunk)


def _join_readers(*threads: threading.Thread) -> None:
    for thread in threads:
        thread.join(timeout=5)


def _terminate_process_group(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    if os.name == "posix":
        try:
            pgid = os.getpgid(proc.pid)
            os.killpg(pgid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            proc.wait(timeout=5)
            return
        except subprocess.TimeoutExpired:
            try:
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                return
            proc.wait(timeout=5)
    elif os.name == "nt":
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
    else:  # pragma: no cover - defensive fallback
        proc.kill()
        proc.wait(timeout=5)


def engine_timeout_seconds() -> float:
    """Return configured generation timeout seconds."""

    raw = os.environ.get("LILIA_ENGINE_TIMEOUT_SECONDS")
    if not raw:
        return float(DEFAULT_TIMEOUT_SECONDS)
    try:
        value = float(raw)
    except ValueError as exc:
        raise EngineRunnerError("LILIA_ENGINE_TIMEOUT_SECONDS must be a number") from exc
    if value <= 0:
        raise EngineRunnerError("LILIA_ENGINE_TIMEOUT_SECONDS must be positive")
    return value
