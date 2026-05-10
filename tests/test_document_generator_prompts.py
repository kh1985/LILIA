from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.session import document_generator


def _minimal_context() -> dict:
    return {
        "answers": {"1": "テスト", "9": "特になし"},
        "character_yaml": {"name": "テスト"},
        "profile_md": "# profile",
        "story_spine_md": "## Background Truth\n秘密\n\n## Drift Guard\n銀の鍵\n",
        "relationship_spine_md": "# relationship",
        "engine": "auto",
        "lilia_name": "テスト",
        "session_name": "test",
    }


def test_group_a_prompt_has_abstraction_level_separation_rule() -> None:
    prompt = document_generator._build_group_a_prompt(_minimal_context())

    assert "## ファイル間の抽象レベル分離（重要）" in prompt
    assert "current/scene.md `## 直前のやりとり`" in prompt
    assert "current/event_card.md `## First Concrete Action`" in prompt
    assert "current/hotset.md `## 次に会った時の第一反応`" in prompt
    assert "3 つのセクションの抽象レベルを必ず区別しろ" in prompt


def test_group_a_prompt_has_three_hook_initial_generation_rules() -> None:
    prompt = document_generator._build_group_a_prompt(_minimal_context())

    assert "Three Hook Spine" in prompt
    assert "Main Hook" in prompt
    assert "Relationship Hook" in prompt
    assert "Life-Exploration Hook" in prompt
    assert "Active Hook" in prompt
    assert "Scene Function" in prompt
    assert "### Main Hook" in prompt
    assert "### Relationship Hook" in prompt
    assert "### Life-Exploration Hook" in prompt
    assert "hook_id" in prompt
    assert "exit_condition" in prompt
    assert "change_delta" in prompt
    assert "material shelf" in prompt
    assert "candidate promotion" in prompt
    assert "Background Hooks" in prompt
    assert "Candidate Next Hooks" in prompt
    assert "current/scene.md / current/event_card.md / current/hotset.md" in prompt
    assert "candidate_id" in prompt
    assert "grounding_guard" in prompt
    assert "3択UIとして並べず" in prompt
    assert "Play Mode本文として説明しない" in prompt


def test_group_b_prompt_has_abstraction_level_separation_rule() -> None:
    prompt = document_generator._build_group_b_prompt(_minimal_context())

    assert "## ファイル間の抽象レベル分離（重要）" in prompt
    assert "lilia/main/voice.md `## 第一反応`" in prompt
    assert "lilia/main/state.md `## 第一反応`" in prompt
    assert "永続的な反応の癖" in prompt
    assert "今だけの気分" in prompt


def test_base_prompt_has_common_first_reaction_constraint() -> None:
    prompt = document_generator._build_base_prompt(
        context=_minimal_context(),
        rel_paths=["current/scene.md"],
        role="role",
        constraints="group constraints",
    )

    assert "9. 「第一反応」「最初の反応」「First Concrete Action」" in prompt
    assert "永続的な癖 / 今だけの気分 / 場面のトリガー / 再開キャッシュ / 物理事実" in prompt
