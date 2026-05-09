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
    loader = SourceFileLoader("lilia_cli_apply_turn_duplicate_test", str(ROOT / "lilia"))
    spec = importlib.util.spec_from_loader("lilia_cli_apply_turn_duplicate_test", loader)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_session(root: Path, name: str) -> Path:
    session = root / "saves" / name
    session.mkdir(parents=True)
    (session / "session.json").write_text(
        json.dumps(
            {
                "session_name": name,
                "current_phase": "active",
                "autosave": {
                    "enabled": True,
                    "interval_turns": 10,
                    "turns_since_save": 4,
                    "autosave_required": True,
                },
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return session


def write_turn_update(path: Path) -> Path:
    path.write_text(
        "\n".join(
            [
                "## memory",
                "",
                "- 澪は、かねこさんが写真を急かさず待ったことを覚えた。",
                "",
                "## relationship",
                "",
                "- 信頼が一段だけ増えたが、距離はまだ店先に留まっている。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def read_session_json(session: Path) -> dict:
    return json.loads((session / "session.json").read_text(encoding="utf-8"))


def test_apply_turn_rejects_same_turn_update_hash_after_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_session(tmp_path, "duplicate_case")
    update_path = write_turn_update(tmp_path / "turn_update.md")

    lilia.command_apply_turn(["duplicate_case", str(update_path)])
    capsys.readouterr()

    first_data = read_session_json(session)
    expected_hash = lilia.turn_update_fingerprint(lilia.parse_turn_update(update_path))
    assert first_data["applied_turn_updates"][0]["sha256"] == expected_hash

    memory_path = session / "lilia/main/memory.md"
    assert memory_path.read_text(encoding="utf-8").count("写真を急かさず待った") == 1

    with pytest.raises(SystemExit) as exc:
        lilia.command_apply_turn(["duplicate_case", str(update_path)])

    captured = capsys.readouterr()
    assert exc.value.code == 1
    assert "turn_update already applied" in captured.err
    assert "Use --force only when intentional" in captured.err
    assert memory_path.read_text(encoding="utf-8").count("写真を急かさず待った") == 1

    second_data = read_session_json(session)
    assert len(second_data["applied_turn_updates"]) == 1
    assert second_data["autosave"]["turns_since_save"] == 0


def test_apply_turn_dry_run_warns_for_duplicate_without_reapplying(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_session(tmp_path, "dry_run_duplicate_case")
    update_path = write_turn_update(tmp_path / "turn_update.md")

    lilia.command_apply_turn(["dry_run_duplicate_case", str(update_path)])
    capsys.readouterr()

    lilia.command_apply_turn(["--dry-run", "dry_run_duplicate_case", str(update_path)])
    captured = capsys.readouterr()

    assert "warning: turn_update already applied" in captured.err
    assert "dry-run: applied" in captured.out
    memory = (session / "lilia/main/memory.md").read_text(encoding="utf-8")
    assert memory.count("写真を急かさず待った") == 1
    assert len(read_session_json(session)["applied_turn_updates"]) == 1


def test_apply_turn_dry_run_then_actual_apply_succeeds(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_session(tmp_path, "dry_run_first_case")
    update_path = write_turn_update(tmp_path / "turn_update.md")

    lilia.command_apply_turn(["--dry-run", "dry_run_first_case", str(update_path)])
    capsys.readouterr()
    assert "applied_turn_updates" not in read_session_json(session)

    lilia.command_apply_turn(["dry_run_first_case", str(update_path)])
    capsys.readouterr()

    data = read_session_json(session)
    assert len(data["applied_turn_updates"]) == 1
    memory = (session / "lilia/main/memory.md").read_text(encoding="utf-8")
    assert memory.count("写真を急かさず待った") == 1


def test_apply_turn_force_allows_intentional_reapply(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_session(tmp_path, "force_case")
    update_path = write_turn_update(tmp_path / "turn_update.md")

    lilia.command_apply_turn(["force_case", str(update_path)])
    capsys.readouterr()
    lilia.command_apply_turn(["--force", "force_case", str(update_path)])
    captured = capsys.readouterr()

    assert "warning: turn_update already applied" in captured.err
    memory = (session / "lilia/main/memory.md").read_text(encoding="utf-8")
    assert memory.count("写真を急かさず待った") == 2
    assert len(read_session_json(session)["applied_turn_updates"]) == 1


def test_apply_turn_duplicate_guard_is_session_scoped(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    first_session = write_session(tmp_path, "first_case")
    second_session = write_session(tmp_path, "second_case")
    update_path = write_turn_update(tmp_path / "turn_update.md")

    lilia.command_apply_turn(["first_case", str(update_path)])
    capsys.readouterr()
    lilia.command_apply_turn(["second_case", str(update_path)])
    capsys.readouterr()

    assert len(read_session_json(first_session)["applied_turn_updates"]) == 1
    assert len(read_session_json(second_session)["applied_turn_updates"]) == 1
    first_memory = (first_session / "lilia/main/memory.md").read_text(encoding="utf-8")
    second_memory = (second_session / "lilia/main/memory.md").read_text(encoding="utf-8")
    assert first_memory.count("写真を急かさず待った") == 1
    assert second_memory.count("写真を急かさず待った") == 1


def test_turn_update_fingerprint_is_path_independent(tmp_path: Path) -> None:
    lilia = load_lilia_module()
    first = write_turn_update(tmp_path / "first.md")
    second_path = tmp_path / "nested" / "second.md"
    second_path.parent.mkdir(parents=True)
    second = write_turn_update(second_path)

    assert lilia.turn_update_fingerprint(
        lilia.parse_turn_update(first)
    ) == lilia.turn_update_fingerprint(lilia.parse_turn_update(second))
