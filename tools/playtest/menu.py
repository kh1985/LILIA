"""Pure helpers for the LILIA dev menu.

Anything that touches the filesystem, sessions, or LLM CLIs lives in the
``lilia`` launcher itself. This module only owns the small, easily-tested
pieces: keyword → action resolution and default value helpers.
"""

from __future__ import annotations


# Action identifiers exposed by the menu.
MENU_ACTIONS: tuple[str, ...] = (
    "new",       # 1. 新規テストセッション自動作成 (MVP: TODO表示)
    "playtest",  # 2. 既存セッションでAIプレイテスト
    "smoke",     # 3. まとめてSmokeテスト
    "last",      # 4. 最新のテスト結果を見る
    "clean",     # 5. playtests/runs を掃除する
    "saves",     # 6. saves の不要セッション候補を見る
    "list",      # 7. セッション一覧
    "growth",    # 8. 関係成長の長期テスト
    "quit",      # 0. 終了
)


# Order matters. Each tuple is (action, keywords). The resolver checks the
# list top-to-bottom so earlier entries take priority on substring conflicts.
# Keywords are matched case-insensitively for ASCII; CJK keywords are kept
# as-is.
MENU_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("quit",     ("0", "q", "quit", "exit", "終了", "やめる", "おわり", "中止")),
    ("new",      ("1", "new", "新規", "作成", "新セッション")),
    ("playtest", ("2", "test", "playtest", "テスト", "プレイテスト")),
    ("growth",   ("8", "growth", "long", "成長", "長期", "long-growth", "growth-smoke")),
    ("smoke",    ("3", "smoke", "スモーク", "まとめて")),
    ("last",     ("4", "last", "result", "report", "最新", "結果", "レポート")),
    ("clean",    ("5", "clean", "cleanup", "掃除", "クリーン", "クリーンアップ")),
    ("saves",    ("6", "saves", "セーブ")),
    ("list",     ("7", "list", "sessions", "一覧", "セッション")),
)


def resolve_menu_action(text: str) -> str | None:
    """Map free-form user input (number / keyword / Japanese) to a menu action.

    Returns the action name (one of ``MENU_ACTIONS``) or ``None`` if the
    input doesn't match any keyword. The function is intentionally permissive:
    exact match wins, otherwise the first substring match in keyword order.
    """

    if text is None:
        return None
    normalized = text.strip().lower()
    if not normalized:
        return None

    # Exact match first — handles single-digit menu numbers and short tokens.
    for action, keywords in MENU_KEYWORDS:
        if normalized in {kw.lower() for kw in keywords}:
            return action

    # Substring match — handles e.g. "テストして" → playtest. We require the
    # keyword to be at least 2 chars to avoid matching the digit "1" inside
    # longer numbers.
    for action, keywords in MENU_KEYWORDS:
        for kw in keywords:
            if len(kw) >= 2 and kw.lower() in normalized:
                return action

    return None


def parse_turns_or_default(raw: str | None, default: int) -> int:
    """Parse a turns input, falling back to ``default`` for empty/blank input.

    Raises ``ValueError`` for non-integer or non-positive values, so callers
    can re-prompt cleanly.
    """

    if raw is None:
        return default
    text = raw.strip()
    if not text:
        return default
    value = int(text)
    if value < 1:
        raise ValueError("turns must be a positive integer")
    return value


def parse_yes_no(raw: str | None, default: bool) -> bool:
    """Parse a yes/no prompt response. Empty/blank uses ``default``."""

    if raw is None:
        return default
    text = raw.strip().lower()
    if not text:
        return default
    if text in {"y", "yes", "はい", "ok", "true", "1"}:
        return True
    if text in {"n", "no", "いいえ", "ng", "false", "0"}:
        return False
    return default


PERSONA_CHOICES: tuple[tuple[str, str], ...] = (
    ("1", "normal"),
    ("2", "passive"),
    ("3", "boundary"),
    ("4", "wanderer"),
)

ENGINE_CHOICES: tuple[tuple[str, str], ...] = (
    ("1", "auto"),
    ("2", "codex"),
    ("3", "claude"),
)


def resolve_choice(raw: str | None, choices: tuple[tuple[str, str], ...], default_index: int = 0) -> str | None:
    """Resolve a numeric or named choice against a (number, value) table.

    Empty input → ``choices[default_index][1]``. Returns the chosen value, or
    ``None`` if the input does not match any number or value.
    """

    default_value = choices[default_index][1]
    if raw is None:
        return default_value
    text = raw.strip().lower()
    if not text:
        return default_value
    for number, value in choices:
        if text == number or text == value.lower():
            return value
    return None
