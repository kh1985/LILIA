from __future__ import annotations

from dataclasses import fields, is_dataclass
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.session.reply_context import (  # noqa: E402
    build_reply_context_bundle,
    render_reply_context_bundle,
    split_latest_user_input,
)


def _write(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def _knowledge_doc(yaml_block: str) -> str:
    return f"""# Knowledge State

## knowledge_state

```yaml
{yaml_block.strip()}
```
"""


def _event_card(extra: str = "") -> str:
    return f"""# Event Card

## Active Hook

- hook_id: main_test

## Scene Function

- function: 関係の入口を作る

## Visible Problem

- 主人公が今触れられる小さな問題。

## First Concrete Action

- 声をかける。

## Handles 2-4

- 声をかける。
- 待つ。

## Relationship Stake

- 主人公がヒロインを頼れるかが賭けになる。

{extra.strip()}

## If Ignored

- 約束が曖昧なまま残る。

## Next Visible Change

- ヒロインの沈黙が少し長くなる。
"""


def _session(tmp_path: Path, *, event_card: str = "", knowledge_state: str = "") -> Path:
    root = tmp_path / "session"
    _write(root, "current/event_card.md", event_card or _event_card())
    _write(root, "current/knowledge_state.md", knowledge_state or _knowledge_doc("items: []"))
    _write(
        root,
        "current/scene.md",
        """# Scene

## 今この場で見えているもの

- 喫茶店のテーブル。

## 直前のやりとり

- 主人公が短く声をかけた。
""",
    )
    _write(root, "current/hotset.md", "# Hotset\n\n## 次に会った時の第一反応\n\n- まず声に反応する。")
    _write(root, "current/relationship_overview.md", "# Relationship\n\n## Overview\n\n- まだ距離がある。")
    for rel in [
        "lilia/main/voice.md",
        "lilia/main/state.md",
        "lilia/main/relationship.md",
        "lilia/main/memory.md",
        "lilia/main/beliefs.md",
    ]:
        _write(root, rel, "# Test\n\n## Notes\n\n- 短く反応する。")
    _write(root, "current/story_spine.md", "# Story Spine\n\n## Background Truth\n\n- GMだけの背景。")
    _write(root, "story/story_deck.md", "# Story Deck\n\n## Candidate Next Hooks\n\n- 次の入口。")
    return root


def _contains(value: object, needle: str) -> bool:
    if isinstance(value, str):
        return needle in value
    if isinstance(value, (list, tuple)):
        return any(_contains(item, needle) for item in value)
    if is_dataclass(value):
        return any(_contains(getattr(value, field.name), needle) for field in fields(value))
    return False


def test_hidden_truth_does_not_enter_heroine_reply_context(tmp_path: Path) -> None:
    hidden = "ヒロインがまだ知らない真相"
    session = _session(
        tmp_path,
        knowledge_state=_knowledge_doc(
            f"""
items:
  - key: hidden_truth
    value: {hidden}
    fictional_status: gm_only
    source: story_spine
    known_to: [GM]
    acquired_at: pre_play
    weight: high
"""
        ),
    )

    bundle = build_reply_context_bundle(session)

    assert not _contains(bundle.heroine, hidden)
    assert hidden not in bundle.heroine.heroine_known_facts
    assert hidden not in bundle.heroine.shared_facts
    assert hidden not in bundle.heroine.observable_now
    assert _contains(bundle.gm.hidden_truth, hidden) or _contains(bundle.gm.do_not_reveal, hidden)


def test_meta_system_does_not_enter_heroine_reply_context(tmp_path: Path) -> None:
    meta = "ヒロインは主人公の内心を読まない"
    session = _session(
        tmp_path,
        knowledge_state=_knowledge_doc(
            f"""
items:
  - key: session_constraints
    value: {meta}
    fictional_status: meta-system
    source: protagonist
    known_to: [GM]
    acquired_at: pre_play
    weight: low
"""
        ),
    )

    bundle = build_reply_context_bundle(session)

    assert not _contains(bundle.heroine, meta)
    assert _contains(bundle.gm.do_not_reveal, meta)


def test_relationship_stake_does_not_enter_heroine_reply_context(tmp_path: Path) -> None:
    session = _session(tmp_path)

    bundle = build_reply_context_bundle(session)

    assert not _contains(bundle.heroine, "頼れるかが賭け")
    assert _contains(bundle.gm.relationship_stake, "頼れるか")


def test_observable_pressure_enters_pressure_context(tmp_path: Path) -> None:
    session = _session(
        tmp_path,
        event_card=_event_card(
            """
## Pressure / Agency

- pressure_source: gm_world_pressure

## Observable Pressure

- 喫茶店の明かりがまだ点いている。
- 雨が強くなっている。
"""
        ),
    )

    bundle = build_reply_context_bundle(session)

    assert _contains(bundle.pressure.observable_pressure, "喫茶店の明かり")
    assert _contains(bundle.pressure.observable_pressure, "雨が強く")


def test_render_order_places_heroine_before_gm(tmp_path: Path) -> None:
    bundle = build_reply_context_bundle(_session(tmp_path))

    rendered = render_reply_context_bundle(bundle)

    assert rendered.index("Heroine Reply Context") < rendered.index("GM Control Context")


def test_render_contains_first_beat_contract(tmp_path: Path) -> None:
    bundle = build_reply_context_bundle(_session(tmp_path), latest_user_input="少し近づく。")

    rendered = render_reply_context_bundle(bundle)

    assert "first beat" in rendered.lower() or "最初の一拍" in rendered
    assert "latest user" in rendered.lower() or "直近" in rendered


def test_split_latest_user_input_handles_line_leading_japanese_parentheses() -> None:
    action, inner = split_latest_user_input("（本当は早くしてほしい）「読めるところだけで構いません」")

    assert action == "「読めるところだけで構いません」"
    assert inner == "本当は早くしてほしい"
