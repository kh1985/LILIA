from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_opening_scene_has_required_clarity_sections() -> None:
    text = (ROOT / "prompt/opening_scene.md").read_text(encoding="utf-8")

    assert "## 冒頭の4つの仕事の必須要件" in text
    assert "## clarity_anchors の必須織り込み要件" in text
    assert "## 出力前の最終チェック（必須）" in text


def test_opening_scene_no_longer_uses_minimum_two_job_language() -> None:
    text = (ROOT / "prompt/opening_scene.md").read_text(encoding="utf-8")

    assert "最低2つ" not in text
