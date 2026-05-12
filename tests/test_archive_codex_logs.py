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
    loader = SourceFileLoader("lilia_cli_archive_codex_logs_test", str(ROOT / "lilia"))
    spec = importlib.util.spec_from_loader("lilia_cli_archive_codex_logs_test", loader)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_rollout(
    home: Path,
    rel_path: str,
    cwd: Path | str | None,
    *,
    extra_line: dict | None = None,
) -> Path:
    rollout = home / ".codex" / "sessions" / rel_path
    rollout.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    if cwd is not None:
        lines.append(
            {
                "timestamp": "2026-05-06T01:02:03.000Z",
                "type": "session_meta",
                "payload": {
                    "id": "rollout-test",
                    "timestamp": "2026-05-06T01:02:03.000Z",
                    "cwd": str(cwd),
                },
            }
        )
    if extra_line is not None:
        lines.append(extra_line)
    rollout.write_text("\n".join(json.dumps(line) for line in lines) + "\n", encoding="utf-8")
    return rollout


def write_invalid_rollout(home: Path, rel_path: str, content: str) -> Path:
    rollout = home / ".codex" / "sessions" / rel_path
    rollout.parent.mkdir(parents=True, exist_ok=True)
    rollout.write_text(content, encoding="utf-8")
    return rollout


def prepare(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> tuple[ModuleType, Path]:
    lilia = load_lilia_module()
    home = tmp_path / "home"
    home.mkdir()

    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    monkeypatch.setattr(lilia.Path, "home", lambda: home)
    return lilia, home


def discover_rollouts(lilia: ModuleType) -> list[tuple[Path, Path]]:
    return lilia.find_codex_rollouts_for_repo()


def test_no_codex_sessions_returns_empty(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia, _home = prepare(monkeypatch, tmp_path)

    assert discover_rollouts(lilia) == []


def test_matching_cwd_only(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia, home = prepare(monkeypatch, tmp_path)
    matching = write_rollout(home, "2026/05/06/rollout-matching.jsonl", tmp_path)
    write_rollout(home, "2026/05/06/rollout-other.jsonl", tmp_path / "other")

    rollouts = discover_rollouts(lilia)

    assert rollouts == [(matching, Path("2026/05/06/rollout-matching.jsonl"))]


def test_other_cwd_skipped(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia, home = prepare(monkeypatch, tmp_path)
    write_rollout(home, "2026/05/06/rollout-other.jsonl", tmp_path / "other")

    assert discover_rollouts(lilia) == []


def test_invalid_json_and_non_session_meta_skipped(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia, home = prepare(monkeypatch, tmp_path)
    write_invalid_rollout(home, "2026/05/06/rollout-invalid.jsonl", "{not json}\n")
    write_rollout(
        home,
        "2026/05/06/rollout-event-only.jsonl",
        None,
        extra_line={"timestamp": "2026-05-06T01:02:03.000Z", "type": "response_item", "payload": {}},
    )

    assert discover_rollouts(lilia) == []


def test_command_prints_relative_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia, home = prepare(monkeypatch, tmp_path)
    source = write_rollout(home, "2026/05/06/rollout-relative.jsonl", tmp_path)

    lilia.command_archive_codex_logs([])

    captured = capsys.readouterr()
    assert str(Path("2026/05/06/rollout-relative.jsonl")) in captured.out
    assert str(source) not in captured.out


def test_discovery_returns_codex_relative_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia, home = prepare(monkeypatch, tmp_path)
    source = write_rollout(home, "2026/05/06/rollout-relative-path.jsonl", tmp_path)

    assert discover_rollouts(lilia) == [
        (source, Path("2026/05/06/rollout-relative-path.jsonl"))
    ]


def test_command_no_matches_prints_no_rollouts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia, home = prepare(monkeypatch, tmp_path)
    (home / ".codex" / "sessions").mkdir(parents=True)

    lilia.command_archive_codex_logs([])

    captured = capsys.readouterr()
    assert "no codex rollouts found whose cwd matches this LILIA repo." in captured.out


def test_command_rejects_session_argument(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia, _home = prepare(monkeypatch, tmp_path)

    with pytest.raises(SystemExit):
        lilia.command_archive_codex_logs(["archive_case"])


def test_command_copies_and_second_run_skips_idempotently(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia, home = prepare(monkeypatch, tmp_path)
    source = write_rollout(home, "2026/05/06/rollout-copy.jsonl", tmp_path)

    lilia.command_archive_codex_logs([])
    first = capsys.readouterr()

    archived = tmp_path / "logs" / "codex_rollouts" / "2026" / "05" / "06" / "rollout-copy.jsonl"
    assert archived.read_text(encoding="utf-8") == source.read_text(encoding="utf-8")
    assert "copied" in first.out

    lilia.command_archive_codex_logs([])
    second = capsys.readouterr()

    assert archived.read_text(encoding="utf-8") == source.read_text(encoding="utf-8")
    assert "skipped" in second.out
