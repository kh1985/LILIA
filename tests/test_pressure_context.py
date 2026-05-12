from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.session.reply_context import build_reply_context_bundle  # noqa: E402
from tools.session.state_consistency import event_card_pressure_issues  # noqa: E402


def _write(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def _session(tmp_path: Path, event_card: str) -> Path:
    root = tmp_path / "session"
    _write(root, "current/event_card.md", event_card)
    _write(root, "current/knowledge_state.md", "# Knowledge State\n\n## knowledge_state\n\n```yaml\nitems: []\n```")
    _write(root, "current/scene.md", "# Scene\n\n## 今この場で見えているもの\n\n- 店内の明かり。")
    _write(root, "current/hotset.md", "# Hotset\n")
    _write(root, "current/relationship_overview.md", "# Relationship\n")
    for rel in [
        "lilia/main/voice.md",
        "lilia/main/state.md",
        "lilia/main/relationship.md",
        "lilia/main/memory.md",
        "lilia/main/beliefs.md",
    ]:
        _write(root, rel, "# Test\n\n## Notes\n\n- 根拠になる短い状態。")
    _write(root, "current/story_spine.md", "# Story Spine\n")
    _write(root, "story/story_deck.md", "# Story Deck\n")
    return root


def _event_card(pressure_sections: str) -> str:
    return f"""# Event Card

## Scene Function

- function: 関係の入口

## Relationship Stake

- 頼れるかが賭けになる。

{pressure_sections.strip()}
"""


def test_protagonist_initiated_pressure_source(tmp_path: Path) -> None:
    session = _session(
        tmp_path,
        _event_card(
            """
## Pressure / Agency

- pressure_source: protagonist_initiated
"""
        ),
    )

    bundle = build_reply_context_bundle(session)

    assert bundle.pressure.source == "protagonist_initiated"


def test_heroine_initiated_pressure_source_with_candidate(tmp_path: Path) -> None:
    session = _session(
        tmp_path,
        _event_card(
            """
## Pressure / Agency

- pressure_source: heroine_initiated

## Heroine Initiative Candidate

- ヒロインが自分から「少し寄る？」と聞く。
- 発火条件: ユーザーが迷っている。
- その動きの根拠になる state / relationship / memory / beliefs:
  - state: 気まずさを避けたい
"""
        ),
    )

    bundle = build_reply_context_bundle(session)

    assert bundle.pressure.source == "heroine_initiated"
    assert bundle.pressure.heroine_possible_initiative


def test_gm_world_pressure_requires_observable_pressure(tmp_path: Path) -> None:
    session = _session(
        tmp_path,
        _event_card(
            """
## Pressure / Agency

- pressure_source: gm_world_pressure

## Observable Pressure

- 閉店時間が近づいている。
"""
        ),
    )

    bundle = build_reply_context_bundle(session)

    assert bundle.pressure.source == "gm_world_pressure"
    assert any("閉店時間" in item for item in bundle.pressure.observable_pressure)


def test_invalid_pressure_source_reports_issue() -> None:
    issues = event_card_pressure_issues(
        _event_card(
            """
## Pressure / Agency

- pressure_source: forced_plot
"""
        )
    )

    assert any(issue.code == "invalid_pressure_source" for issue in issues)
