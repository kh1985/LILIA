from __future__ import annotations

from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.common import example_anchoring


def test_load_example_anchoring_control_reads_core_section() -> None:
    section = example_anchoring.load_example_anchoring_control()

    assert isinstance(section, str)
    assert "## Example Anchoring Control" in section
    assert "prompt内の例文" in section
    assert "LILIAの人格は、例文からではなく" in section


def test_example_anchoring_control_includes_descriptive_categories() -> None:
    section = example_anchoring.load_example_anchoring_control()

    for keyword in (
        "性格類型",
        "関係類型",
        "イベント類型",
        "描写の軸",
        "Manifestation Anchors",
        "仕草",
        "匂い",
        "声",
        "身体表現",
    ):
        assert keyword in section


def test_load_example_anchoring_control_raises_when_section_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_core = tmp_path / "core.md"
    fake_core.write_text("# Core\n\n## Other\n\ntext\n", encoding="utf-8")
    monkeypatch.setattr(example_anchoring, "CORE_MD_PATH", fake_core)

    with pytest.raises(example_anchoring.ExampleAnchoringLoadError):
        example_anchoring.load_example_anchoring_control()
