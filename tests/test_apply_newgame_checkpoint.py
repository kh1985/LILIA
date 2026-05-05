from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys
from types import ModuleType
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_lilia_module() -> ModuleType:
    loader = SourceFileLoader("lilia_cli_checkpoint_test", str(ROOT / "lilia"))
    spec = importlib.util.spec_from_loader("lilia_cli_checkpoint_test", loader)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_session(tmp_path: Path, phase: str) -> Path:
    session = tmp_path / "checkpoint_case"
    (session / "lilia" / "main").mkdir(parents=True)
    (session / "current").mkdir(parents=True)
    (session / "story").mkdir(parents=True)
    (session / "session.json").write_text(
        f'{{"session_name": "checkpoint_case", "apply_newgame_phase": "{phase}"}}\n',
        encoding="utf-8",
    )
    return session


def write_answers(tmp_path: Path) -> Path:
    answers = tmp_path / "answers.md"
    answers.write_text(
        "\n\n".join(f"## Q{index}\n回答{index}" for index in range(1, 10)),
        encoding="utf-8",
    )
    return answers


def install_common_stubs(monkeypatch: pytest.MonkeyPatch, lilia: ModuleType) -> dict[str, int]:
    calls = {"character": 0, "profile": 0, "spines": 0, "documents": 0}

    monkeypatch.setattr(lilia, "resolve_engine", lambda requested: "claude")
    monkeypatch.setattr(
        lilia,
        "generate_character_yaml_data",
        lambda answers, requested_engine: (
            calls.__setitem__("character", calls["character"] + 1)
            or {"name": "テスト", "age": 24, "occupation": "検証係"},
            "claude",
            "generated via claude",
        ),
    )
    monkeypatch.setattr(
        lilia,
        "generate_profile_from_character_data",
        lambda answers, character_data, engine: (
            calls.__setitem__("profile", calls["profile"] + 1)
            or "# LILIA Persona Profile\n\n## 基礎情報\nname: テスト\n",
            {"engine": "claude", "validation_pass": True, "retry_count": 0, "sections_count": 1},
        ),
    )
    monkeypatch.setattr(
        lilia,
        "generate_downstream_session_documents",
        lambda **kwargs: {
            "documents": (
                calls.__setitem__("documents", calls["documents"] + 1)
                or {path: f"# {path}\n" for path in lilia.DOWNSTREAM_SESSION_DOCUMENT_FILES}
            ),
            "engine_used": "claude",
            "validation_retry_count": 0,
            "groups": {},
        },
    )
    monkeypatch.setattr(lilia, "render_ai_knowledge_state_document", lambda **kwargs: "# knowledge\n")

    from tools.character import profile_validator
    from tools.session import document_validator
    from tools.story import spine_generator

    monkeypatch.setattr(profile_validator, "validate_profile_output", lambda *args, **kwargs: (True, []))
    monkeypatch.setattr(document_validator, "validate_session_documents", lambda *args, **kwargs: (True, []))
    monkeypatch.setattr(
        spine_generator,
        "generate_story_and_relationship_spine",
        lambda **kwargs: {
            "story_spine_md": calls.__setitem__("spines", calls["spines"] + 1) or "# story\n",
            "relationship_spine_md": "# relationship\n",
            "engine_used": "claude",
            "validation_retry_count": 0,
        },
    )
    return calls


@pytest.mark.parametrize(
    ("phase", "expected_calls"),
    [
        ("pending", {"character": 1, "profile": 1, "spines": 1, "documents": 1}),
        ("character_yaml_generated", {"character": 0, "profile": 1, "spines": 1, "documents": 1}),
        ("profile_generated", {"character": 0, "profile": 0, "spines": 1, "documents": 1}),
        ("spines_generated", {"character": 0, "profile": 0, "spines": 0, "documents": 1}),
    ],
)
def test_apply_newgame_resumes_from_each_phase(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    phase: str,
    expected_calls: dict[str, int],
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path)
    session = write_session(tmp_path, phase)
    if phase in {"character_yaml_generated", "profile_generated", "spines_generated"}:
        lilia.write_session_file(session, "lilia/main/character.yaml", lilia.dump_character_yaml({"name": "テスト", "age": 24}))
    if phase in {"profile_generated", "spines_generated"}:
        lilia.write_session_file(session, "lilia/main/profile.md", "# LILIA Persona Profile\n\n## 基礎情報\nname: テスト\n")
    if phase == "spines_generated":
        lilia.write_session_file(session, "current/story_spine.md", "# story\n")
        lilia.write_session_file(session, "story/relationship_spine.md", "# relationship\n")
    answers = write_answers(tmp_path)
    calls = install_common_stubs(monkeypatch, lilia)

    lilia.command_apply_newgame(["checkpoint_case", str(answers), "--engine", "auto"])

    assert {key: calls[key] for key in expected_calls} == expected_calls
    assert lilia.read_session_json(session)["apply_newgame_phase"] == "complete"
    assert (session / "current" / "scene.md").exists()
    assert "phase: first_scene_ready" in capsys.readouterr().out


def test_apply_newgame_complete_refuses_without_force(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path)
    write_session(tmp_path, "complete")
    answers = write_answers(tmp_path)

    with pytest.raises(SystemExit):
        lilia.command_apply_newgame(["checkpoint_case", str(answers)])
