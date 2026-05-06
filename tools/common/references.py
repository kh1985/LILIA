"""Reference markdown loading and sanitizing helpers."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def sanitize_reference_md(text: str) -> str:
    """Remove concrete work observations while preserving structural guidance."""

    lines = text.splitlines()
    sanitized: list[str] = []
    skip_heading_level: int | None = None
    skip_until_blank = False

    for line in lines:
        heading_match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        heading_level = len(heading_match.group(1)) if heading_match else None
        heading_text = heading_match.group(2).strip() if heading_match else ""

        if skip_heading_level is not None:
            if heading_match and heading_level is not None and heading_level <= skip_heading_level:
                skip_heading_level = None
            else:
                continue

        if skip_until_blank:
            if not line.strip():
                skip_until_blank = False
            continue

        if heading_match and _is_concrete_reference_heading(heading_text):
            skip_heading_level = heading_level
            continue

        stripped = line.strip()
        if not stripped:
            sanitized.append(line)
            continue

        if stripped.startswith("**観察される作品**") or stripped.startswith("**観察される作品**:"):
            continue
        if stripped.startswith("**例"):
            skip_until_blank = True
            continue
        if _looks_like_concrete_example_line(stripped):
            continue
        if _contains_reference_work_observation(stripped):
            continue

        sanitized.append(line)

    compact = "\n".join(sanitized)
    compact = re.sub(r"\n{3,}", "\n\n", compact).strip()
    return compact


def load_sanitized_reference(rel_path: str) -> str:
    return sanitize_reference_md((ROOT / rel_path).read_text(encoding="utf-8"))


def _is_concrete_reference_heading(heading_text: str) -> bool:
    return any(marker in heading_text for marker in ["当てはめ例", "例", "出典"])


def _looks_like_concrete_example_line(line: str) -> bool:
    return bool(
        re.match(r"^-+\s*\[?(ヒロイン|ユーザー|主人公)", line)
        or re.match(r"^####\s*\[?ヒロイン", line)
        or re.match(r"^-+\s*厚い防壁", line)
        or re.match(r"^-+\s*静かな日常", line)
        or re.match(r"^-+\s*大きな転機", line)
    )


def _contains_reference_work_observation(line: str) -> bool:
    return "（" in line and "）" in line and any(token in line for token in ["Before", "Normal", "Monster"])
