"""Shared LLM CLI runner for LILIA generation tools."""

from __future__ import annotations

from collections.abc import Callable
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import threading


SUPPORTED_ENGINES = ("claude", "codex")
DEFAULT_TIMEOUT_SECONDS = 600


class EngineRunnerError(RuntimeError):
    """Raised when an engine CLI fails to produce usable output."""


class EngineTimeoutError(EngineRunnerError):
    """Raised when an engine CLI exceeds its timeout."""


class EngineUnavailableError(EngineRunnerError):
    """Raised when a requested engine CLI is unavailable."""


def available_engines() -> list[str]:
    """Return supported engine CLIs available on PATH."""

    return [engine for engine in SUPPORTED_ENGINES if shutil.which(engine)]


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
        return [requested]

    default_engine = os.environ.get("LILIA_DEFAULT_ENGINE", "claude").strip() or "claude"
    priority = _priority_order(default_engine)
    available = set(available_engines())
    return [engine for engine in priority if engine in available]


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


def _priority_order(default_engine: str) -> list[str]:
    if default_engine not in SUPPORTED_ENGINES:
        default_engine = "claude"
    return [default_engine] + [engine for engine in SUPPORTED_ENGINES if engine != default_engine]


def _build_engine_command(engine: str, root: Path) -> list[str]:
    if engine == "claude":
        return ["claude", "-p", "--permission-mode", "dontAsk"]
    if engine == "codex":
        effort = os.environ.get("LILIA_CODEX_REASONING_EFFORT", "low").strip() or "low"
        return [
            "codex",
            "exec",
            "--cd",
            str(root),
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

