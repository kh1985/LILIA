"""Unit tests for tools/playtest/menu.py.

The menu module is intentionally pure (no filesystem / no LLM access). These
tests cover the keyword resolver and the small input-default helpers. The
``lilia`` launcher's interactive command_menu / dev-* commands are integration
glue and are smoke-checked via the launcher itself.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.playtest import menu


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("0", "quit"),
        ("1", "new"),
        ("2", "playtest"),
        ("3", "smoke"),
        ("4", "last"),
        ("5", "clean"),
        ("6", "saves"),
        ("7", "list"),
    ],
)
def test_resolve_menu_action_numeric(text: str, expected: str) -> None:
    assert menu.resolve_menu_action(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("テスト", "playtest"),
        ("プレイテスト", "playtest"),
        ("スモーク", "smoke"),
        ("まとめて", "smoke"),
        ("掃除", "clean"),
        ("クリーン", "clean"),
        ("一覧", "list"),
        ("セッション", "list"),
        ("最新", "last"),
        ("結果", "last"),
        ("レポート", "last"),
        ("新規", "new"),
        ("終了", "quit"),
        ("やめる", "quit"),
    ],
)
def test_resolve_menu_action_japanese(text: str, expected: str) -> None:
    assert menu.resolve_menu_action(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("q", "quit"),
        ("Q", "quit"),
        ("quit", "quit"),
        ("EXIT", "quit"),
        ("テストして", "playtest"),
        ("掃除して", "clean"),
        ("セッション一覧", "list"),
    ],
)
def test_resolve_menu_action_substring_and_case(text: str, expected: str) -> None:
    assert menu.resolve_menu_action(text) == expected


@pytest.mark.parametrize("text", ["", "   ", "ぴったり該当なし", "????"])
def test_resolve_menu_action_unknown_returns_none(text: str) -> None:
    assert menu.resolve_menu_action(text) is None


def test_resolve_menu_action_handles_none() -> None:
    assert menu.resolve_menu_action(None) is None  # type: ignore[arg-type]


# --- parse_turns_or_default -----------------------------------------------


@pytest.mark.parametrize(("raw", "default", "expected"), [
    (None, 10, 10),
    ("", 10, 10),
    ("   ", 10, 10),
    ("5", 10, 5),
    (" 12 ", 3, 12),
    ("", 3, 3),  # smoke default
])
def test_parse_turns_or_default(raw, default, expected) -> None:
    assert menu.parse_turns_or_default(raw, default) == expected


@pytest.mark.parametrize("raw", ["abc", "0", "-1"])
def test_parse_turns_or_default_invalid(raw: str) -> None:
    with pytest.raises(ValueError):
        menu.parse_turns_or_default(raw, 10)


# --- parse_yes_no ----------------------------------------------------------


@pytest.mark.parametrize(("raw", "default", "expected"), [
    (None, True, True),
    ("", True, True),
    ("", False, False),
    ("y", False, True),
    ("Y", False, True),
    ("yes", False, True),
    ("はい", False, True),
    ("n", True, False),
    ("No", True, False),
    ("いいえ", True, False),
    ("???", True, True),  # unknown → default
    ("???", False, False),
])
def test_parse_yes_no(raw, default, expected) -> None:
    assert menu.parse_yes_no(raw, default) is expected


# --- resolve_choice --------------------------------------------------------


def test_resolve_choice_default_for_empty() -> None:
    assert menu.resolve_choice("", menu.PERSONA_CHOICES) == "normal"
    assert menu.resolve_choice(None, menu.PERSONA_CHOICES) == "normal"


def test_resolve_choice_by_number() -> None:
    assert menu.resolve_choice("2", menu.PERSONA_CHOICES) == "passive"
    assert menu.resolve_choice("3", menu.PERSONA_CHOICES) == "boundary"


def test_resolve_choice_by_name_case_insensitive() -> None:
    assert menu.resolve_choice("BOUNDARY", menu.PERSONA_CHOICES) == "boundary"
    assert menu.resolve_choice("auto", menu.ENGINE_CHOICES) == "auto"
    assert menu.resolve_choice("CODEX", menu.ENGINE_CHOICES) == "codex"


def test_resolve_choice_unknown_returns_none() -> None:
    assert menu.resolve_choice("xyz", menu.PERSONA_CHOICES) is None
    assert menu.resolve_choice("99", menu.ENGINE_CHOICES) is None


# --- ordering / coverage --------------------------------------------------


def test_menu_keywords_cover_all_actions() -> None:
    """Every action declared in MENU_ACTIONS must have at least one keyword."""

    actions_with_kw = {action for action, _ in menu.MENU_KEYWORDS}
    assert actions_with_kw == set(menu.MENU_ACTIONS)
