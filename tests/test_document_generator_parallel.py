from __future__ import annotations

import time
from pathlib import Path
import sys
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.session import document_generator


def _minimal_args() -> dict[str, Any]:
    return {
        "answers": {"1": "テスト"},
        "character_yaml": {"name": "テスト", "age": 24},
        "profile_md": "# profile",
        "story_spine_md": "# story",
        "relationship_spine_md": "# relationship",
        "engine": "auto",
    }


def test_generate_session_documents_runs_groups_in_parallel(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_generate_group(**kwargs: Any) -> dict[str, Any]:
        group_name = kwargs["group_name"]
        calls.append(group_name)
        time.sleep(0.2)
        return {
            "documents": {path: f"# {path}\n" for path in kwargs["rel_paths"]},
            "meta": {"engine_used": "stub", "validation_retry_count": 0},
        }

    monkeypatch.setattr(document_generator, "_generate_group", fake_generate_group)
    monkeypatch.setattr(document_generator, "validate_session_documents", lambda *args, **kwargs: (True, []))

    start = time.perf_counter()
    result = document_generator.generate_session_documents(**_minimal_args())
    elapsed = time.perf_counter() - start

    assert set(calls) == {"group_a", "group_b", "group_c"}
    assert elapsed < 0.45
    assert set(result["documents"]) == set(document_generator.ALL_PATHS)


def test_generate_session_documents_propagates_first_group_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_generate_group(**kwargs: Any) -> dict[str, Any]:
        if kwargs["group_name"] == "group_b":
            raise document_generator.DocumentGenerationError("group_b exploded")
        time.sleep(0.2)
        return {
            "documents": {path: f"# {path}\n" for path in kwargs["rel_paths"]},
            "meta": {"engine_used": "stub", "validation_retry_count": 0},
        }

    monkeypatch.setattr(document_generator, "_generate_group", fake_generate_group)

    with pytest.raises(document_generator.DocumentGenerationError, match="group_b exploded"):
        document_generator.generate_session_documents(**_minimal_args())


def test_group_a_uses_deterministic_fallback_after_invalid_generation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    template_root = ROOT / "templates" / "session"

    def template_for(path: str) -> str:
        template_path = template_root / path
        return template_path.read_text(encoding="utf-8")

    def invalid_group_a_output(*args: Any, **kwargs: Any) -> str:
        return "\n".join(
            f"===FILE: {path}===\n{template_for(path)}"
            for path in document_generator.GROUP_A_PATHS
        )

    monkeypatch.setattr(document_generator, "engine_candidates", lambda engine: ["stub"])
    monkeypatch.setattr(document_generator, "run_engine", invalid_group_a_output)

    result = document_generator._generate_group(
        group_name="group_a",
        rel_paths=document_generator.GROUP_A_PATHS,
        prompt="group a prompt",
        answers={"1": "おまかせ", "8": "おまかせ"},
        story_spine_md=(
            "## Main Question\n"
            "主人公は相手の境界を待てるか\n\n"
            "## Background Truth\n"
            "これは本文に出さない真相。\n"
        ),
        engine="codex",
        context={
            "answers": {"1": "おまかせ", "8": "おまかせ"},
            "character_yaml": {"name": "三枝 玲奈", "occupation": "小さな店の店主"},
            "profile_md": (
                "# Profile\n"
                "name: 三枝 玲奈\n"
                "occupation: 小さな店の店主\n\n"
                "## Initial Scene Anchors\n"
                "- 場所と状況: 閉店前の小さな店\n"
                "- 手元の具体物: 伝票と銀の鍵\n"
                "- 最初の距離: 初対面で、カウンター越しに向き合う\n"
                "- 会話の入口: 玲奈が伝票から目を上げる\n"
            ),
            "story_spine_md": "## Main Question\n主人公は相手の境界を待てるか\n",
            "relationship_spine_md": "## 育てたいテーマ\n近づくことと明かすことは同じではない。\n",
            "session_name": "test",
        },
    )

    assert result["meta"]["validation"] == "deterministic_fallback"
    assert result["documents"]["current/event_card.md"].count("hook_id: main_initial_contact") == 1
    assert "未設定" not in "\n".join(result["documents"].values())
