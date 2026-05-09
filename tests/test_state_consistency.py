from __future__ import annotations

import importlib.util
import json
import shutil
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/stale_next_hook_session"
FORBIDDEN_FIXTURE_CLUES = ["薄紙", "鉛筆", "店名", "住所"]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.session.state_consistency import (  # noqa: E402
    promote_next_hook_to_active_state,
    validate_state_consistency,
)


def load_lilia_module() -> ModuleType:
    loader = SourceFileLoader("lilia_cli_state_consistency_test", str(ROOT / "lilia"))
    spec = importlib.util.spec_from_loader("lilia_cli_state_consistency_test", loader)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_fixture(tmp_path: Path, name: str = "stale_case") -> Path:
    session = tmp_path / "saves" / name
    shutil.copytree(FIXTURE, session)
    data = json.loads((session / "session.json").read_text(encoding="utf-8"))
    data["session_name"] = name
    (session / "session.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return session


def test_state_consistency_detects_stale_next_hook_fixture(tmp_path: Path) -> None:
    session = copy_fixture(tmp_path)

    result = validate_state_consistency(session)

    assert result.status == "FAIL"
    assert any(issue.code == "candidate_next_hook_not_active" for issue in result.issues)
    assert any(issue.code == "hotset_scene_event_mismatch" for issue in result.issues)


def test_next_hook_promotion_aligns_active_scene_event_hotset(tmp_path: Path) -> None:
    session = copy_fixture(tmp_path)
    next_hook = "翌日の夕方、依頼主に連絡がつかなかった件をもう一度確認に来てもらう。"

    updated = promote_next_hook_to_active_state(session, next_hook, "2026-05-09T23:30:00+09:00")

    assert "current/scene.md" in updated
    assert "current/event_card.md" in updated
    assert "current/hotset.md" in updated
    assert "story/story_deck.md" in updated

    scene = (session / "current/scene.md").read_text(encoding="utf-8")
    event_card = (session / "current/event_card.md").read_text(encoding="utf-8")
    hotset = (session / "current/hotset.md").read_text(encoding="utf-8")
    story_deck = (session / "story/story_deck.md").read_text(encoding="utf-8")

    assert "翌日の夕方" in scene
    assert "翌日の夕方" in event_card
    assert "翌日の夕方" in hotset
    assert "Grounding Guard" in event_card
    assert "前日の閉店間際" not in event_card
    assert "Backgrounded Event Card" in story_deck

    combined = "\n".join([scene, event_card, hotset])
    for clue in FORBIDDEN_FIXTURE_CLUES:
        assert clue not in combined

    assert validate_state_consistency(session).status == "PASS"


def test_apply_turn_promotes_next_hook_when_active_sections_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = copy_fixture(tmp_path, "apply_promotion_case")
    update_path = tmp_path / "turn_update.md"
    update_path.write_text(
        "## next_hook\n\n翌日の夕方、依頼主に連絡がつかなかった件をもう一度確認に来てもらう。\n",
        encoding="utf-8",
    )

    lilia.command_apply_turn(["apply_promotion_case", str(update_path)])
    output = capsys.readouterr().out

    assert "current/scene.md" in output
    assert "current/event_card.md" in output
    assert "current/hotset.md" in output

    event_card = (session / "current/event_card.md").read_text(encoding="utf-8")
    assert "Visible Problem" in event_card
    assert "First Concrete Action" in event_card
    assert "Grounding Guard" in event_card
    assert "前日の閉店間際" not in event_card

    for clue in FORBIDDEN_FIXTURE_CLUES:
        assert clue not in event_card

    assert validate_state_consistency(session).status == "PASS"


def test_validate_session_command_fails_stale_fixture(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    copy_fixture(tmp_path, "validate_case")

    with pytest.raises(SystemExit) as exc:
        lilia.command_validate_session(["validate_case"])

    captured = capsys.readouterr()
    assert exc.value.code == 1
    assert "state consistency: FAIL" in captured.out
    assert "hotset_scene_event_mismatch" in captured.out
