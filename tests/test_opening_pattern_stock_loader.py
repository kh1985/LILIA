from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.session.document_generator import load_sanitized_opening_pattern_stock


def test_opening_pattern_stock_loader_removes_observed_works() -> None:
    text = load_sanitized_opening_pattern_stock()

    assert "観察される作品" not in text
    assert "川端康成" not in text
    assert "Steins;Gate" not in text


def test_opening_pattern_stock_loader_keeps_all_pattern_names() -> None:
    text = load_sanitized_opening_pattern_stock()
    patterns = re.findall(r"^###\s+(O(?:[1-9]|1[0-5]))\.", text, flags=re.MULTILINE)

    assert patterns == [f"O{number}" for number in range(1, 16)]


def test_opening_pattern_stock_loader_keeps_structure_guidance() -> None:
    text = load_sanitized_opening_pattern_stock()

    assert "**形**:" in text
    assert "**使い時**:" in text
    assert "**注意**:" in text
