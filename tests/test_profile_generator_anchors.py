from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.character import profile_generator


def _prompt() -> str:
    return profile_generator._build_generation_prompt(
        answers={
            "1": "テスト、喫茶店の店主、物静かだが線引きははっきりしている",
            "2": "黒髪、灰色の目、暗いワンピース",
            "4": "表は穏やか、内側は判断が鋭い",
        },
        character_yaml={
            "name": "テスト",
            "occupation": "喫茶店の店主",
            "appearance": {"hair": "黒髪", "eyes": "灰色"},
        },
        attempt_index=0,
        previous_error="",
    )


def test_profile_generator_prompt_has_multi_axis_description_structure() -> None:
    prompt = _prompt()

    assert "Visual Identifier" in prompt
    assert "Sensual Two-Axis Design" in prompt
    assert "Manifestation Anchors" in prompt
    assert "Restraint Guideline" in prompt
    assert "いやらしくない。だが目が離せない" in prompt


def test_profile_generator_prompt_forbids_literal_example_reuse() -> None:
    prompt = _prompt()

    assert "例文の扱い" in prompt
    assert "literal に流用しない" in prompt
    assert "そのヒロインだけに合う言葉" in prompt
    assert "Q&A・character.yaml・職業・状況・人格から" in prompt


def test_profile_generator_prompt_embeds_core_example_anchoring_control() -> None:
    prompt = _prompt()

    assert "## トップレイヤーの共通原則（必読）" in prompt
    assert "## Example Anchoring Control" in prompt
    assert "prompt内の例文" in prompt
    assert "LILIAの人格は、例文からではなく" in prompt
    assert "描写の軸・Manifestation Anchors・仕草・匂い・声・身体表現" in prompt
