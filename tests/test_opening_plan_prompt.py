from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.session import document_generator


def test_group_a_prompt_requires_opening_plan_and_sanitized_stock() -> None:
    prompt = document_generator._build_group_a_prompt(
        {
            "answers": {"3": "銀の鍵", "5": "古い約束", "6": "初対面、路地裏で発見", "9": "停滞を避けたい"},
            "character_yaml": {"name": "テスト"},
            "profile_md": "# profile",
            "story_spine_md": "## Background Truth\n秘密\n\n## Drift Guard\n銀の鍵\n",
            "relationship_spine_md": "# relationship",
            "engine": "auto",
            "lilia_name": "テスト",
            "session_name": "test",
        }
    )

    assert "## Opening Pattern Stock" in prompt
    assert "## Opening Plan" in prompt
    assert "selected_patterns" in prompt
    assert "clarity_anchors" in prompt
    assert "A群（O1-O4）から1つ、D群（O13-O15）から1つ" in prompt
    assert "観察される作品" not in prompt
