from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_opening_scene_has_reaction_dispersion_rule() -> None:
    text = (ROOT / "prompt/opening_scene.md").read_text(encoding="utf-8")

    assert "## ヒロインの反応情報の重複処理（重要）" in text
    assert "これは全部を順番に回収するためのチェックリストではない" in text


def test_core_has_reaction_dispersion_rule() -> None:
    text = (ROOT / "prompt/core.md").read_text(encoding="utf-8")

    assert "## ヒロインの反応情報の重複処理" in text
    assert "これは全部を順番に本文へ出すためのチェックリストではない" in text
