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


def test_opening_scene_has_multi_axis_heroine_density_rules() -> None:
    text = (ROOT / "prompt/opening_scene.md").read_text(encoding="utf-8")

    assert "## Part 2 で必ず織り込む描写（多軸・必須）" in text
    assert "Visual Identifier" in text
    assert "Sensual Two-Axis Design" in text
    assert "感覚チャンネルの横断" in text
    assert "### 色気・身体描写の抑制ガイド" in text
    assert "literal として真似しない" in text
    assert "literal に流用しない" in text
    assert "を**1つ**織り込む" not in text
