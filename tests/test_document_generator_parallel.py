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
