from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_lilia_module() -> ModuleType:
    loader = SourceFileLoader("lilia_cli_autosave_prompt_test", str(ROOT / "lilia"))
    spec = importlib.util.spec_from_loader("lilia_cli_autosave_prompt_test", loader)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_session(root: Path, name: str, phase: str = "active") -> Path:
    session = root / "saves" / name
    session.mkdir(parents=True)
    (session / "session.json").write_text(
        f'{{"session_name": "{name}", "current_phase": "{phase}"}}\n',
        encoding="utf-8",
    )
    return session


def assert_hard_autosave_prompt(text: str, session_name: str | None = None) -> None:
    if session_name:
        assert f"must run ./lilia scene-tick {session_name}" in text
        assert f"run ./lilia apply-turn {session_name} <turn_update.md>" in text
    else:
        assert "must run ./lilia scene-tick <session>" in text
        assert "run ./lilia apply-turn <session> <turn_update.md>" in text

    assert "autosave_required: true" in text
    assert "enter save mode" in text
    assert "only changed sections" in text or "only the sections that actually changed" in text
    assert "(保存しました)" in text
    assert "bracketed line" in text
    assert "Do not expose internal save reasoning to the player." in text
    assert "may update" not in text
    assert "suggest saving but do not run apply-turn" not in text


def assert_resume_grounding_prompt(text: str) -> None:
    assert "resume first turn: do not introduce unstored concrete props" in text
    assert "documents, contact methods" in text
    assert "identifiers, prior records, or clue-results" in text
    assert "unless active state names them" in text
    assert "discovers them in-scene" in text


def test_codex_prompt_bundles_require_scene_tick_and_apply_turn(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_session(tmp_path, "prompt_case")

    assert_hard_autosave_prompt(lilia.build_codex_new_prompt_bundle(session))
    assert_hard_autosave_prompt(lilia.build_codex_resume_prompt_bundle(session))


def test_resume_prompt_bundles_include_first_turn_grounding(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_session(tmp_path, "grounding_case")
    prompt_path = tmp_path / "prompt.md"

    resume_bundle = lilia.build_resume_prompt_bundle(session, latest_user_input="少し近づく。")
    assert_resume_grounding_prompt(resume_bundle)
    assert "Reply Context Bundle" in resume_bundle
    assert resume_bundle.index("Heroine Reply Context") < resume_bundle.index("GM Control Context")
    assert "GM-only" in resume_bundle
    assert "first beat" in resume_bundle.lower() or "最初の一拍" in resume_bundle
    assert "current/hotset.md" in resume_bundle or "current\\hotset.md" in resume_bundle
    assert_resume_grounding_prompt(lilia.build_codex_resume_prompt_bundle(session))
    assert_resume_grounding_prompt(lilia.codex_interactive_instruction(prompt_path, "resume", session))


def test_codex_interactive_instruction_branches_require_autosave_chain(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    prompt_path = tmp_path / "prompt.md"

    new_session = write_session(tmp_path, "new_case")
    first_scene_session = write_session(tmp_path, "first_scene_case", "first_scene_pending")
    resume_session = write_session(tmp_path, "resume_case", "active")

    assert_hard_autosave_prompt(
        lilia.codex_interactive_instruction(prompt_path, "new", new_session),
        "new_case",
    )
    assert_hard_autosave_prompt(
        lilia.codex_interactive_instruction(prompt_path, "resume", first_scene_session),
        "first_scene_case",
    )
    assert_hard_autosave_prompt(
        lilia.codex_interactive_instruction(prompt_path, "resume", resume_session),
        "resume_case",
    )
