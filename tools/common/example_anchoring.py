"""Example Anchoring Control loader.

Reads the canonical Example Anchoring Control section from prompt/core.md
and exposes it for embedding into generator prompts (profile, document, spine).

The single source of truth is prompt/core.md. This module exists so that
generator prompts can include the rule without duplicating its text.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORE_MD_PATH = ROOT / "prompt" / "core.md"
SECTION_HEADING = "## Example Anchoring Control"


class ExampleAnchoringLoadError(RuntimeError):
    """Raised when the Example Anchoring Control section cannot be located."""


def load_example_anchoring_control() -> str:
    """Return the body text of `## Example Anchoring Control` from core.md.

    The returned string starts at the section heading and ends just before
    the next `## ` heading. Trailing blank lines are stripped.

    Raises:
        ExampleAnchoringLoadError: if the section is missing or malformed.
    """

    text = CORE_MD_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()

    start_idx: int | None = None
    end_idx = len(lines)

    for i, line in enumerate(lines):
        if line.strip() == SECTION_HEADING:
            start_idx = i
            continue
        if start_idx is not None and line.startswith("## ") and line.strip() != SECTION_HEADING:
            end_idx = i
            break

    if start_idx is None:
        raise ExampleAnchoringLoadError(
            f"Section {SECTION_HEADING!r} not found in {CORE_MD_PATH}"
        )

    section_lines = lines[start_idx:end_idx]
    section = "\n".join(section_lines).rstrip()
    if not section:
        raise ExampleAnchoringLoadError(
            f"Section {SECTION_HEADING!r} is empty or malformed in {CORE_MD_PATH}"
        )
    return section
