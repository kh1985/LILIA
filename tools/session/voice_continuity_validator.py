"""Resume gate validation helpers for LILIA voice continuity."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any


REQUIRED_FILES = [
    "lilia/main/core.md",
    "lilia/main/voice.md",
    "lilia/main/relationship.md",
    "lilia/main/memory.md",
    "lilia/main/beliefs.md",
    "lilia/main/state.md",
    "current/hotset.md",
    "current/scene.md",
    "current/event_card.md",
]

HOTSET_DECISION_SECTIONS = [
    "未消化の感情",
    "言い残し / まだ言っていないこと",
    "未確定の余白",
]

DECISION_SECTIONS = {
    "約束": "約束（Promises）",
    "拒否": "拒否（Refusals）",
    "保留": "保留（Deferrals）",
}

DECISION_TRACE_WORDS = {
    "約束": ["約束", "次", "あと", "後", "守", "また", "予定"],
    "拒否": ["拒否", "しない", "触れない", "断", "境界", "止"],
    "保留": ["保留", "後で", "まだ", "未確定", "言い残し", "話していない"],
}

DECISION_PLACEHOLDER_LABELS = {
    "内容",
    "誰が誰に",
    "誰が",
    "期限 / 条件",
    "理由 (optional)",
    "戻る条件",
    "関係への影響",
}

DECISION_PLACEHOLDER_VALUES = {
    "active / fulfilled / broken / withdrawn",
    "active / withdrawn",
    "pending / resolved / abandoned",
}

INITIAL_RELATIONSHIP_WORDS = ["初期", "未開始", "未成立"]

PROGRESSED_RELATIONSHIP_WORDS = [
    "キス",
    "同棲",
    "告白",
    "肉体関係",
    "結婚",
    "付き合っている",
    "恋人",
    "彼氏",
    "彼女として",
]

GM_ONLY_TARGETS = [
    "current/hotset.md",
    "current/event_card.md",
    "current/scene.md",
    "current/relationship_overview.md",
]

WARNING_PREFIX = "voice_continuity: warning:"


def validate_voice_continuity(
    session_root: Path,
) -> list[str]:
    """Resume gate 観点で session の voice / relationship / memory / beliefs / hotset / state / event_card の継続性を検査する。

    Returns:
        errors のリスト。空リストなら pass。
    """

    errors: list[str] = []
    root = Path(session_root)

    _check_required_files(root, errors)

    core_md = _read_text(root / "lilia/main/core.md")
    voice_md = _read_text(root / "lilia/main/voice.md")
    hotset_md = _read_text(root / "current/hotset.md")
    relationship_md = _read_text(root / "lilia/main/relationship.md")

    _check_calling_basis(voice_md, hotset_md, errors)
    _check_core_fixed_basis(core_md, voice_md, errors)
    _check_decision_hotset_trace(root, hotset_md, errors)
    _check_relationship_stage(relationship_md, hotset_md, errors)
    _check_gm_only_leak(root, errors)

    return errors


def _check_required_files(session_root: Path, errors: list[str]) -> None:
    for rel_path in REQUIRED_FILES:
        if not (session_root / rel_path).exists():
            errors.append(f"voice_continuity: missing required file: {rel_path}")


def _check_calling_basis(voice_md: str, hotset_md: str, errors: list[str]) -> None:
    voice_calling = _section_containing(voice_md, "呼び方")
    hotset_calling = _section_containing(hotset_md, "呼び方")
    if not _has_section_body(voice_calling) and not _has_section_body(hotset_calling):
        errors.append("voice_continuity: 呼び方の根拠が voice.md と hotset.md の両方にない")


def _check_core_fixed_basis(core_md: str, voice_md: str, errors: list[str]) -> None:
    if not _has_h2_sections(core_md) or not _has_h2_sections(voice_md):
        errors.append("voice_continuity: core / voice が空である (core fixed の正本が無い)")


def _check_decision_hotset_trace(session_root: Path, hotset_md: str, errors: list[str]) -> None:
    decision_path = session_root / "current/decision_index.md"
    if not decision_path.exists():
        return

    decision_sections = _markdown_sections(_read_text(decision_path))
    hotset_trace = "\n".join(_section_by_heading(hotset_md, heading) for heading in HOTSET_DECISION_SECTIONS)

    for label, heading in DECISION_SECTIONS.items():
        section = _section_by_heading_from_sections(decision_sections, heading)
        if not _has_decision_record(section):
            continue
        if not _has_hotset_trace(hotset_trace, label):
            errors.append(f"{WARNING_PREFIX} decision_index に{label}があるが hotset に痕跡が無い")


def _check_relationship_stage(relationship_md: str, hotset_md: str, errors: list[str]) -> None:
    if not any(word in relationship_md for word in INITIAL_RELATIONSHIP_WORDS):
        return
    progressed_words = [word for word in PROGRESSED_RELATIONSHIP_WORDS if word in hotset_md]
    if progressed_words:
        errors.append("voice_continuity: relationship が初期段階だが hotset に進行語彙がある")


def _check_gm_only_leak(session_root: Path, errors: list[str]) -> None:
    story_spine_path = session_root / "current/story_spine.md"
    if not story_spine_path.exists():
        return

    story_spine = _read_text(story_spine_path)
    sections = _markdown_sections(story_spine)
    background_truth = (
        _section_by_heading_from_sections(sections, "Background Truth")
        or _section_by_heading_from_sections(sections, "Background Truth (GM only)")
    )
    if not background_truth.strip():
        return

    for rel_path in GM_ONLY_TARGETS:
        target_path = session_root / rel_path
        if not target_path.exists():
            continue
        if _contains_long_verbatim(_read_text(target_path), background_truth):
            errors.append(
                f"voice_continuity: gm_only_leak: {rel_path} に Background Truth が30文字以上連続して含まれる"
            )


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _markdown_sections(markdown: str) -> dict[str, str]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", markdown, re.MULTILINE))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections[_normalize_heading(match.group(1))] = markdown[start:end].strip()
    return sections


def _section_by_heading(markdown: str, heading: str) -> str:
    return _section_by_heading_from_sections(_markdown_sections(markdown), heading)


def _section_containing(markdown: str, heading_part: str) -> str:
    normalized_part = _normalize_heading(heading_part)
    sections = _markdown_sections(markdown)
    for heading, body in sections.items():
        if normalized_part in heading:
            return body
    return ""


def _section_by_heading_from_sections(sections: dict[str, str], heading: str) -> str:
    return sections.get(_normalize_heading(heading), "")


def _normalize_heading(heading: str) -> str:
    text = _as_text(heading)
    text = re.sub(r"\s*[（(].*?[）)]\s*", "", text)
    text = re.sub(r"\s+", "", text)
    return text.casefold()


def _as_text(value: Any) -> str:
    return "" if value is None else str(value)


def _has_h2_sections(markdown: str) -> bool:
    return bool(re.search(r"^##\s+.+?\s*$", markdown, re.MULTILINE))


def _has_section_body(section: str) -> bool:
    return bool(section.strip())


def _plain_line(line: str) -> str:
    text = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s*", "", line.strip())
    return re.sub(r"\s+", " ", text).strip()


def _has_decision_record(section: str) -> bool:
    for raw_line in section.splitlines():
        if not re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", raw_line):
            continue
        line = _plain_line(raw_line)
        if not line:
            continue
        if _is_decision_placeholder_line(line):
            continue
        return True
    return False


def _is_decision_placeholder_line(line: str) -> bool:
    if re.match(r"^(約束|拒否|保留)\d+\s*[:：]\s*$", line):
        return True
    if ":" in line or "：" in line:
        label, value = re.split(r"[:：]", line, maxsplit=1)
        label = label.strip()
        value = value.strip()
        if label in DECISION_PLACEHOLDER_LABELS and not value:
            return True
        if label == "状態" and (not value or value in DECISION_PLACEHOLDER_VALUES):
            return True
    return False


def _has_hotset_trace(hotset_trace: str, label: str) -> bool:
    if not hotset_trace.strip():
        return False
    return any(word in hotset_trace for word in DECISION_TRACE_WORDS.get(label, [label]))


def _contains_long_verbatim(haystack: str, needle: str, length: int = 30) -> bool:
    normalized_haystack = _normalize_verbatim(haystack)
    normalized_needle = _normalize_verbatim(needle)
    if len(normalized_needle) < length:
        return False
    for index in range(0, len(normalized_needle) - length + 1):
        chunk = normalized_needle[index : index + length]
        if chunk in normalized_haystack:
            return True
    return False


def _normalize_verbatim(text: str) -> str:
    return re.sub(r"\s+", "", str(text or ""))
