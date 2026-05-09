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
    loader = SourceFileLoader("lilia_cli_first_scene_phase_test", str(ROOT / "lilia"))
    spec = importlib.util.spec_from_loader("lilia_cli_first_scene_phase_test", loader)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_session(root: Path, name: str, *, phase: str, first_scene_status: str) -> Path:
    session = root / "saves" / name
    session.mkdir(parents=True)
    (session / "session.json").write_text(
        json.dumps(
            {
                "session_name": name,
                "current_phase": phase,
                "initialization": {
                    "qa_completed": True,
                    "first_scene_status": first_scene_status,
                },
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


def write_resume_bundle_files(lilia: ModuleType, root: Path, session: Path) -> None:
    for rel_path in ["prompt/core.md", "prompt/save_resume.md"]:
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"# {rel_path}\n", encoding="utf-8")

    for rel_path in lilia.RESUME_SESSION_FILES:
        target = session / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"# {rel_path}\n", encoding="utf-8")

    profile = session / lilia.RESUME_PROFILE_FILE
    profile.parent.mkdir(parents=True, exist_ok=True)
    profile.write_text("# Profile\n\nPROFILE_SHOULD_ONLY_APPEAR_BEFORE_FIRST_SCENE\n", encoding="utf-8")


def test_apply_turn_moves_first_scene_ready_session_to_active(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_session(tmp_path, "phase_case", phase="first_scene_ready", first_scene_status="ready")
    update_path = tmp_path / "turn_update.md"
    update_path.write_text("## hotset\n\n- The first scene has begun.\n", encoding="utf-8")

    lilia.command_apply_turn(["phase_case", str(update_path)])
    capsys.readouterr()

    data = json.loads((session / "session.json").read_text(encoding="utf-8"))
    assert data["current_phase"] == "active"
    assert data["initialization"]["first_scene_status"] == "started"
    assert data["autosave"]["turns_since_save"] == 0
    assert data["autosave"]["autosave_required"] is False


def test_resume_profile_is_omitted_after_active_phase_even_with_legacy_ready_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_session(tmp_path, "active_case", phase="active", first_scene_status="ready")
    write_resume_bundle_files(lilia, tmp_path, session)

    assert lilia.resume_requires_profile(session) is False
    bundle = lilia.build_resume_prompt_bundle(session)

    assert "profile: omitted by default" in bundle
    assert "PROFILE_SHOULD_ONLY_APPEAR_BEFORE_FIRST_SCENE" not in bundle


def test_resume_profile_is_included_for_first_scene_ready_phase(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_session(tmp_path, "ready_case", phase="first_scene_ready", first_scene_status="ready")
    write_resume_bundle_files(lilia, tmp_path, session)

    assert lilia.resume_requires_profile(session) is True
    bundle = lilia.build_resume_prompt_bundle(session)

    assert "profile: included because first scene is ready/pending" in bundle
    assert "PROFILE_SHOULD_ONLY_APPEAR_BEFORE_FIRST_SCENE" in bundle
