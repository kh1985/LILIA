from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.character import profile_validator


def test_profile_repetition_allows_character_yaml_visual_anchor() -> None:
    errors: list[str] = []

    profile_validator._check_repeated_phrases(
        "\n".join(
            [
                "outfit: 黒いテーパードパンツ",
                "- 視覚アンカー1: 黒いテーパードパンツ",
                "- アンカー3（軸 A）: 黒いテーパードパンツ",
            ]
        ),
        errors,
        character_yaml={
            "appearance": {
                "notes": "白いシャツに薄手のカーディガン、黒いテーパードパンツ。",
            },
        },
    )

    assert errors == []


def test_profile_repetition_still_rejects_ungrounded_phrase() -> None:
    errors: list[str] = []

    profile_validator._check_repeated_phrases(
        "\n".join(
            [
                "rule: 同じ説明を何度も繰り返す",
                "- アンカー1: 同じ説明を何度も繰り返す",
                "- アンカー2: 同じ説明を何度も繰り返す",
            ]
        ),
        errors,
        character_yaml={"appearance": {"notes": "黒いテーパードパンツ。"}},
    )

    assert errors == ["repeated phrase appears 6 times: `同じ説明を何度も繰り返す`"]
