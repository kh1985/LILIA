"""Validation helpers for AI-generated LILIA session documents."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re
import sys
from typing import Any

from tools.session.knowledge_boundary import assess_knowledge_boundary


ROOT = Path(__file__).resolve().parents[2]

GROUPS = {
    "A": [
        "current/scene.md",
        "current/event_card.md",
        "current/hotset.md",
        "current/relationship_overview.md",
        "story/story_deck.md",
    ],
    "B": [
        "lilia/main/core.md",
        "lilia/main/voice.md",
        "lilia/main/state.md",
        "lilia/main/relationship.md",
        "lilia/main/memory.md",
        "lilia/main/beliefs.md",
    ],
    "C": [
        "current/protagonist.md",
        "current/knowledge_state.md",
    ],
}

DOWNSTREAM_SESSION_DOCUMENT_FILES = [
    "current/scene.md",
    "current/event_card.md",
    "current/hotset.md",
    "current/relationship_overview.md",
    "story/story_deck.md",
    "lilia/main/core.md",
    "lilia/main/voice.md",
    "lilia/main/state.md",
    "lilia/main/relationship.md",
    "lilia/main/memory.md",
    "lilia/main/beliefs.md",
    "current/protagonist.md",
    "current/knowledge_state.md",
]

TEMPLATE_PATHS = {
    "current/scene.md": "current/scene.md",
    "current/event_card.md": "current/event_card.md",
    "current/hotset.md": "current/hotset.md",
    "current/relationship_overview.md": "current/relationship_overview.md",
    "story/story_deck.md": "story/story_deck.md",
    "lilia/main/core.md": "lilia/main/core.md",
    "lilia/main/voice.md": "lilia/main/voice.md",
    "lilia/main/state.md": "lilia/main/state.md",
    "lilia/main/relationship.md": "lilia/main/relationship.md",
    "lilia/main/memory.md": "lilia/main/memory.md",
    "lilia/main/beliefs.md": "lilia/main/beliefs.md",
    "current/protagonist.md": "protagonist.md",
    "current/knowledge_state.md": "knowledge_state.md",
}

GROUP_A_PATHS = {
    "current/scene.md",
    "current/event_card.md",
    "current/hotset.md",
    "current/relationship_overview.md",
    "story/story_deck.md",
}

PROTAGONIST_KEYS = {
    "protagonist_call_name",
    "protagonist_gender",
    "protagonist_height",
    "protagonist_build",
    "protagonist_style",
    "protagonist_occupation",
}

HEROINE_REVEAL_KEYS = {
    "heroine_name",
    "heroine_occupation",
    "heroine_visual_anchor",
    "heroine_background_truth",
    "reveal_ladder_stage_1",
    "reveal_ladder_stage_2",
    "reveal_ladder_stage_3",
    "session_constraints",
}

FORBIDDEN_TEMPLATE_EXPRESSIONS = [
    "次の行動の判断について、急かさず短く聞く",
    "{ヒロイン名}が自分で決めるまで待つ",
    "{ヒロイン名}に名乗る / 名前を聞く",
]

PLACEHOLDER_ENDINGS = [
    "から導出する場面時間",
    "が次の入口として残る",
    "を抱えたまま次の行動へ移る",
]


def validate_session_documents(
    documents: dict[str, str],
    answers: dict,
    story_spine_md: str = "",
    expected_paths: list[str] | None = None,
    template_root: Path | None = None,
    original_knowledge_state_md: str = "",
) -> tuple[bool, list[str]]:
    """Validate generated downstream session documents."""

    errors: list[str] = []
    expected = expected_paths or DOWNSTREAM_SESSION_DOCUMENT_FILES
    root = template_root or (ROOT / "templates" / "session")

    for rel_path in expected:
        content = documents.get(rel_path, "")
        if not isinstance(content, str) or not content.strip():
            errors.append(f"{rel_path}: missing or empty")
            continue
        _check_required_sections(rel_path, content, root, errors)

    _check_template_identity(documents, expected, root, errors)
    _check_unresolved_placeholder_markers(documents, expected, errors)
    _check_text_collapse(documents, expected, errors)
    _check_template_expressions(documents, expected, errors)
    _check_duplicate_copy(documents, expected, errors)
    _check_answer_verbatim(documents, expected, answers, errors)
    if story_spine_md:
        _check_gm_only_leak(documents, story_spine_md, errors)
    _check_protagonist_document(documents.get("current/protagonist.md", ""), answers, errors)
    _check_knowledge_state(
        documents.get("current/knowledge_state.md", ""),
        answers,
        errors,
        original_knowledge_state_md=original_knowledge_state_md,
    )
    _check_scene_player_orientation(documents, errors)
    _check_story_deck_three_hook_spine(documents, errors)
    _check_event_card_playability(documents, errors)
    _check_opening_plan_consistency(documents)

    return not errors, errors


OPENING_PATTERN_GROUPS = {
    **{f"O{number}": "A" for number in range(1, 5)},
    **{f"O{number}": "B" for number in range(5, 9)},
    **{f"O{number}": "C" for number in range(9, 13)},
    **{f"O{number}": "D" for number in range(13, 16)},
}


def validate_opening_plan_consistency(scene_md: str) -> list[str]:
    """Return soft warnings for ``current/scene.md`` Opening Plan consistency."""

    warnings: list[str] = []
    section = _section_body(scene_md, "Opening Plan")
    if section is None:
        warnings.append("current/scene.md: Opening Plan section is missing")
        return warnings

    patterns = _opening_plan_patterns(section)
    if not patterns:
        warnings.append("current/scene.md: Opening Plan selected_patterns is missing or empty")
    if len(patterns) > 3:
        warnings.append("current/scene.md: Opening Plan selects more than 3 patterns")

    invalid = [pattern for pattern in patterns if pattern not in OPENING_PATTERN_GROUPS]
    for pattern in invalid:
        warnings.append(f"current/scene.md: Opening Plan has unknown pattern: {pattern}")

    valid_patterns = [pattern for pattern in patterns if pattern in OPENING_PATTERN_GROUPS]
    groups = [OPENING_PATTERN_GROUPS[pattern] for pattern in valid_patterns]
    if groups.count("A") != 1:
        warnings.append("current/scene.md: Opening Plan must select exactly one A-group pattern (O1-O4)")
    if groups.count("D") != 1:
        warnings.append("current/scene.md: Opening Plan must select exactly one D-group pattern (O13-O15)")
    if groups.count("B") + groups.count("C") > 1:
        warnings.append("current/scene.md: Opening Plan may select at most one optional B/C pattern")
    for group in ["A", "B", "C", "D"]:
        if groups.count(group) > 1:
            warnings.append(f"current/scene.md: Opening Plan selects multiple patterns from group {group}")

    for field in ["hook", "orientation", "agency", "unresolved"]:
        if not _yaml_like_field_has_value(section, field):
            warnings.append(f"current/scene.md: Opening Plan 4_jobs.{field} is missing")
    if not _list_block_has_item(section, "must_include"):
        warnings.append("current/scene.md: Opening Plan must_include is missing")
    for field in ["protagonist_role", "protagonist_purpose", "location_function", "heroine_relation"]:
        if not _yaml_like_field_has_value(section, field):
            warnings.append(f"current/scene.md: Opening Plan clarity_anchors.{field} is missing")
    return warnings


def _check_opening_plan_consistency(documents: dict[str, str]) -> None:
    scene_md = documents.get("current/scene.md")
    if not scene_md:
        return
    for warning in validate_opening_plan_consistency(scene_md):
        print(f"[opening_plan] warning: {warning}", file=sys.stderr)


def _section_body(markdown: str, heading: str) -> str | None:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return None
    next_heading = re.search(r"^##\s+.+?\s*$", markdown[match.end() :], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(markdown)
    return markdown[match.end() : end].strip()


def _opening_plan_patterns(section: str) -> list[str]:
    match = re.search(r"^selected_patterns\s*:\s*(.+)$", section, flags=re.MULTILINE)
    if not match:
        return []
    return re.findall(r"\bO(?:[1-9]|1[0-5])\b|\bO\d+\b", match.group(1))


def _yaml_like_field_has_value(section: str, field: str) -> bool:
    match = re.search(rf"^[ \t]*{re.escape(field)}[ \t]*:[ \t]*(.*)$", section, flags=re.MULTILINE)
    if not match:
        return False
    value = match.group(1).strip()
    return bool(value and value not in {"-", "未設定", "TODO", "placeholder"})


def _list_block_has_item(section: str, field: str) -> bool:
    match = re.search(rf"^[ \t]*{re.escape(field)}[ \t]*:[ \t]*$", section, flags=re.MULTILINE)
    if not match:
        inline = re.search(rf"^[ \t]*{re.escape(field)}[ \t]*:[ \t]*(.+)$", section, flags=re.MULTILINE)
        return bool(inline and inline.group(1).strip())
    following = section[match.end() :]
    next_field = re.search(r"^\S[^:\n]*:\s*", following, flags=re.MULTILINE)
    block = following[: next_field.start()] if next_field else following
    return any(
        line.strip().startswith("-") and line.strip() not in {"-", "- 未設定", "- TODO"}
        for line in block.splitlines()
    )


def _check_required_sections(rel_path: str, content: str, template_root: Path, errors: list[str]) -> None:
    template_rel = TEMPLATE_PATHS.get(rel_path)
    if not template_rel:
        return
    template_path = template_root / template_rel
    if not template_path.exists():
        errors.append(f"{rel_path}: template not found at {template_path}")
        return

    expected = _headings(template_path.read_text(encoding="utf-8"))
    actual = _headings(content)
    if expected != actual:
        missing = [heading for heading in expected if heading not in actual]
        extra = [heading for heading in actual if heading not in expected]
        if missing:
            errors.append(f"{rel_path}: missing section(s): {', '.join(missing)}")
        if extra:
            errors.append(f"{rel_path}: unexpected section(s): {', '.join(extra)}")
        if not missing and not extra:
            errors.append(f"{rel_path}: section order differs from template")


def _headings(markdown: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"^##\s+(.+?)\s*$", markdown, re.MULTILINE)]


def _check_template_identity(
    documents: dict[str, str],
    expected: list[str],
    template_root: Path,
    errors: list[str],
) -> None:
    for rel_path in expected:
        template_rel = TEMPLATE_PATHS.get(rel_path)
        if not template_rel:
            continue
        template_path = template_root / template_rel
        if not template_path.exists():
            continue
        content = documents.get(rel_path, "")
        template = template_path.read_text(encoding="utf-8")
        if _normalize_template_identity(content) == _normalize_template_identity(template):
            errors.append(f"{rel_path}: still identical to session template")


def _normalize_template_identity(content: str) -> str:
    return re.sub(r"\s+", "", content or "")


def _check_unresolved_placeholder_markers(
    documents: dict[str, str],
    expected: list[str],
    errors: list[str],
) -> None:
    for rel_path in expected:
        content = documents.get(rel_path, "")
        for line_number, raw_line in enumerate(content.splitlines(), 1):
            line = raw_line.strip()
            if re.search(r"雛形|TODO|PLACEHOLDER|placeholder", line, flags=re.IGNORECASE):
                errors.append(f"{rel_path}:{line_number}: unresolved placeholder marker remains")
            if re.search(r"(^|[\s:：])\(?未設定\)?(\s*$|[\s。、,.)）])", line):
                errors.append(f"{rel_path}:{line_number}: unresolved 未設定 marker remains")


def _check_text_collapse(documents: dict[str, str], expected: list[str], errors: list[str]) -> None:
    for rel_path in expected:
        content = documents.get(rel_path, "")
        for line_number, raw_line in enumerate(content.splitlines(), 1):
            line = raw_line.strip()
            if not line:
                continue
            if line.endswith("…") or line.endswith("...") or line.endswith(".."):
                errors.append(f"{rel_path}:{line_number}: line ends with unfinished ellipsis")
            if any(line.endswith(ending) or ending in line for ending in PLACEHOLDER_ENDINGS):
                errors.append(f"{rel_path}:{line_number}: placeholder-like ending detected")
            if _looks_like_field_concat(line):
                errors.append(f"{rel_path}:{line_number}: likely multi-field concatenation")
            if re.search(r"未確定:\s*profile/answers\s*から再推論", line):
                errors.append(f"{rel_path}:{line_number}: old profile placeholder residue detected")


def _looks_like_field_concat(line: str) -> bool:
    if "声 / 沈黙 / 呼び方 / 距離に出る変化" in line:
        return False
    if ".md /" in line:
        return False
    if line.count(" / ") < 2:
        return False
    if not re.match(r"^\s*(?:[-*]|\d+[.)]|[A-Za-z0-9_ /]+:|[^:：]{1,30}:)", line):
        return False
    return len(line) >= 45


def _check_template_expressions(documents: dict[str, str], expected: list[str], errors: list[str]) -> None:
    patterns = [
        re.compile(r"次の行動の判断について、急かさず短く聞く"),
        re.compile(r"自分で決めるまで待つ"),
        re.compile(r"に名乗る\s*/\s*名前を聞く"),
        re.compile(r"に触れず、扱い方だけを提案する"),
    ]
    for rel_path in expected:
        content = documents.get(rel_path, "")
        for literal in FORBIDDEN_TEMPLATE_EXPRESSIONS:
            if literal in content:
                errors.append(f"{rel_path}: forbidden template expression: {literal}")
        for pattern in patterns:
            if pattern.search(content):
                errors.append(f"{rel_path}: forbidden template expression pattern: {pattern.pattern}")


def _check_duplicate_copy(documents: dict[str, str], expected: list[str], errors: list[str]) -> None:
    occurrences: dict[str, set[str]] = defaultdict(set)
    for rel_path in expected:
        for unit in _duplicate_units(documents.get(rel_path, "")):
            occurrences[unit].add(rel_path)

    for unit, paths in sorted(occurrences.items()):
        if len(paths) >= 3:
            errors.append(
                "duplicate 30+ char string appears in 3+ files: "
                + f"{unit[:60]}... ({', '.join(sorted(paths))})"
            )
            return


def _duplicate_units(content: str) -> set[str]:
    units: set[str] = set()
    for raw_line in content.splitlines():
        line = _normalize_unit(raw_line)
        if len(line) < 30:
            continue
        if line.startswith("#") or line.startswith("```"):
            continue
        if any(skip in line for skip in ["このファイル", "LILIAは", "Save Mode", "apply-turn"]):
            continue
        units.add(line)
    return units


def _normalize_unit(text: str) -> str:
    text = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", text.strip())
    text = re.sub(r"\s+", "", text)
    return text


def _check_answer_verbatim(
    documents: dict[str, str],
    expected: list[str],
    answers: dict,
    errors: list[str],
) -> None:
    combined = "\n".join(documents.get(path, "") for path in expected)
    for number in (1, 6):
        answer_text = _answer_text(answers, number)
        if _contains_long_verbatim(combined, answer_text):
            errors.append(f"Q{number} appears verbatim for 30+ continuous characters")
    q8 = _answer_text(answers, 8)
    for path in ("current/protagonist.md", "current/knowledge_state.md"):
        if _contains_long_verbatim(documents.get(path, ""), q8):
            errors.append(f"{path}: Q8 appears verbatim for 30+ continuous characters")


def _answer_text(answers: dict, number: int) -> str:
    keys = (number, str(number), f"q{number}", f"Q{number}", f"Q{number}.")
    for key in keys:
        value = answers.get(key)
        if value:
            return str(value)
    needle = f"q{number}"
    for key, value in answers.items():
        key_text = str(key).lower()
        if key_text == str(number) or key_text.startswith(needle) or needle in key_text:
            return str(value)
    return ""


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


def _check_gm_only_leak(documents: dict[str, str], story_spine_md: str, errors: list[str]) -> None:
    sections = _markdown_sections(story_spine_md)
    background_truth = sections.get("background truth", "") or sections.get("background truth gm only", "")
    reveal_text = sections.get("reveal ladder", "")
    reveal_pending = "\n".join(
        re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", line).strip()
        for line in reveal_text.splitlines()
        if "[pending]" in line
    )
    for rel_path in sorted(GROUP_A_PATHS):
        content = documents.get(rel_path, "")
        if background_truth and _contains_long_verbatim(content, background_truth):
            errors.append(f"{rel_path}: Background Truth leaked verbatim")
        if reveal_pending and _contains_long_verbatim(content, reveal_pending):
            errors.append(f"{rel_path}: pending Reveal Ladder leaked verbatim")
        if "[pending]" in content:
            errors.append(f"{rel_path}: contains [pending] marker")


def _markdown_sections(markdown: str) -> dict[str, str]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", markdown, re.MULTILINE))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        key = match.group(1).strip().lower()
        key = re.sub(r"\s*\(.+?\)\s*", "", key)
        sections[key] = markdown[start:end].strip()
    return sections


def _check_protagonist_document(content: str, answers: dict, errors: list[str]) -> None:
    if not content.strip():
        return
    required = ["性別", "身長感", "体格", "仕事 / 立場", "服装"]
    for label in required:
        if not re.search(rf"{re.escape(label)}\s*[:：]", content):
            errors.append(f"current/protagonist.md: missing protagonist field: {label}")
    q8 = _answer_text(answers, 8)
    style_section = _markdown_sections(content).get("スタイル", "")
    if _contains_long_verbatim(style_section, q8):
        errors.append("current/protagonist.md: style/clothes contains Q8 verbatim")


def _check_knowledge_state(
    content: str,
    answers: dict,
    errors: list[str],
    *,
    original_knowledge_state_md: str = "",
) -> None:
    if not content.strip():
        return
    if _items_block_before_knowledge_state(content):
        errors.append("current/knowledge_state.md: items block appears before ## knowledge_state")
    if len(re.findall(r"^\s*items\s*:", content, flags=re.MULTILINE)) != 1:
        errors.append("current/knowledge_state.md: must contain exactly one YAML items block")
    parsed = _parse_knowledge_yaml(content)
    if parsed is None:
        errors.append("current/knowledge_state.md: YAML items block is not parseable")
        return
    items = parsed.get("items") if isinstance(parsed, dict) else None
    if not isinstance(items, list):
        errors.append("current/knowledge_state.md: YAML has no items list")
        return

    boundary_report = assess_knowledge_boundary(content)
    for error in boundary_report.errors:
        errors.append(f"current/knowledge_state.md: {error}")

    by_key: dict[str, Any] = {}
    for item in items:
        if isinstance(item, dict) and item.get("key"):
            by_key[str(item["key"])] = item
    missing_protagonist = sorted(PROTAGONIST_KEYS - set(by_key))
    if missing_protagonist:
        errors.append("current/knowledge_state.md: missing protagonist key(s): " + ", ".join(missing_protagonist))
    missing_heroine = sorted(HEROINE_REVEAL_KEYS - set(by_key))
    if missing_heroine:
        errors.append("current/knowledge_state.md: missing heroine/reveal key(s): " + ", ".join(missing_heroine))

    q8 = _answer_text(answers, 8)
    for key in PROTAGONIST_KEYS:
        item = by_key.get(key)
        if not isinstance(item, dict):
            continue
        value = str(item.get("value", ""))
        if _contains_long_verbatim(value, q8):
            errors.append(f"current/knowledge_state.md: {key} contains Q8 verbatim")

    if original_knowledge_state_md:
        original = _parse_knowledge_yaml(original_knowledge_state_md)
        original_items = original.get("items") if isinstance(original, dict) else None
        if isinstance(original_items, list):
            original_by_key = {
                str(item["key"]): item
                for item in original_items
                if isinstance(item, dict) and item.get("key")
            }
            for key in HEROINE_REVEAL_KEYS:
                if key in original_by_key and key in by_key and by_key[key] != original_by_key[key]:
                    errors.append(f"current/knowledge_state.md: heroine/reveal key changed unexpectedly: {key}")


def _check_event_card_playability(documents: dict[str, str], errors: list[str]) -> None:
    """current/event_card.md のプレイ可能性ゲートを検査する。

    `docs/EVENT_CARD_PLAYABILITY.md` の §4 Required Fields と §5 Gate Conditions に基づく。
    """

    content = documents.get("current/event_card.md", "")
    if not content.strip():
        return

    sections = _markdown_sections(content)
    _check_event_card_hook_scaffold(sections, errors)
    _check_event_card_reveal_control(sections, errors)

    unfilled_marker_sections = [
        "表の出来事",
        "Relationship Stake",
        "If Ignored",
        "Next Visible Change",
        "揺れるLILIA",
        "その出来事がLILIAに刺さる理由",
        "関係に残る変化",
    ]
    for heading in unfilled_marker_sections:
        body = sections.get(heading.lower(), "")
        if re.search(r"^[ \t]*-[ \t]*未設定[ \t]*$", body, flags=re.MULTILINE):
            errors.append(f"current/event_card.md: 未設定 が ## {heading} に残存している")

    visible_problem = sections.get("visible problem", "")
    _check_event_card_subline_group(
        visible_problem,
        [
            "誰が困っているか",
            "何が止まりそうか",
            "何に触れると入口になるか",
        ],
        "Visible Problem",
        errors,
    )

    first_action = sections.get("first concrete action", "")
    _check_event_card_subline_group(
        first_action,
        [
            "誰に / 何に",
            "どう触るか",
            "初回sceneで重すぎない一手",
        ],
        "First Concrete Action",
        errors,
    )

    handles = sections.get("handles 2-4", "")
    handle_labels = [
        "handle 1",
        "handle 2",
        "handle 3 optional",
        "handle 4 optional",
    ]
    handle_values = [
        _extract_subline_value(handles, re.escape(label))
        for label in handle_labels
        if _event_card_subline_present(handles, re.escape(label))
    ]
    if handle_values:
        handle_count = sum(1 for value in handle_values if value is not None)
    else:
        handle_count = _count_freeform_handles(handles)
    if handle_count < 2:
        errors.append("current/event_card.md: Handles 2-4 が 2 個未満しか埋まっていない")

    next_visible_change = sections.get("next visible change", "")
    _check_event_card_subline_group(
        next_visible_change,
        ["声 / 沈黙 / 呼び方 / 距離に出る変化"],
        "Next Visible Change",
        errors,
    )

    story_residue = sections.get("story residue", "")
    residue_labels = [
        "memoryに残るもの",
        "relationshipに残るもの",
        "beliefsに残るもの",
        "voiceに残るもの",
    ]
    residue_values = [
        _extract_subline_value(story_residue, re.escape(label))
        for label in residue_labels
        if _event_card_subline_present(story_residue, re.escape(label))
    ]
    if residue_values and not any(value is not None for value in residue_values):
        errors.append("current/event_card.md: Story Residue の memory/relationship/beliefs/voice すべてが空である")
    elif not residue_values and not _has_event_card_freeform_content(story_residue):
        errors.append("current/event_card.md: Story Residue の memory/relationship/beliefs/voice すべてが空である")


def _check_scene_player_orientation(documents: dict[str, str], errors: list[str]) -> None:
    content = documents.get("current/scene.md", "")
    if not content.strip():
        return
    sections = _markdown_sections(content)
    section_name, section = _find_section(
        sections,
        [
            r"\bplayer\s+orientation\b",
            r"プレイヤー.*(?:オリエンテーション|現在地|案内|理解)",
        ],
    )
    if not section:
        return

    required = [
        (
            "protagonist reason",
            [
                r"\bprotagonist[_\s-]*(?:reason|purpose)\b",
                r"主人公.*(?:理由|目的)",
                r"なぜ.*(?:いる|関わる|動く)",
            ],
        ),
        (
            "current player knowledge",
            [
                r"\bcurrent[_\s-]*player[_\s-]*knowledge\b",
                r"\bplayer[_\s-]*knowledge\b",
                r"プレイヤー.*(?:知って|既知|知識|わかって)",
                r"現在.*プレイヤー.*(?:知って|既知|知識|わかって)",
                r"主人公.*(?:知って|既知|知識|わかって)",
            ],
        ),
        (
            "opening must-show",
            [
                r"\bopening[_\s-]*must[_\s-]*show\b",
                r"\bmust[_\s-]*(?:show|include)\b",
                r"冒頭.*(?:見せる|必ず)",
                r"初回.*(?:見せる|必ず)",
            ],
        ),
    ]
    _check_required_labeled_values(
        section,
        required,
        f"current/scene.md: {section_name}",
        errors,
    )


def _check_event_card_reveal_control(sections: dict[str, str], errors: list[str]) -> None:
    matched = [
        (name, body)
        for name, body in sections.items()
        if re.search(r"\bknowledge\s+boundary\b|\breveal\s+control\b|知識境界|開示制御", name, re.IGNORECASE)
    ]
    if not matched:
        return
    player_facing_entrance = sections.get("player-facing entrance", "")
    location_parts = [f"## {name}" for name, _body in matched]
    if player_facing_entrance:
        location_parts.insert(0, "## player-facing entrance")
    location = "current/event_card.md: " + " / ".join(location_parts)
    section_parts = [player_facing_entrance] if player_facing_entrance else []
    section_parts.extend(body for _name, body in matched)
    section = "\n".join(section_parts)
    required = [
        (
            "player-facing entrance",
            [
                r"\bplayer[_\s-]*facing[_\s-]*(?:entrance|entry)\b",
                r"\bvisible[_\s-]*(?:entrance|entry)\b",
                r"プレイヤー.*入口",
                r"表.*入口",
                r"見せる入口",
            ],
        ),
        (
            "do-not-hide judgment material",
            [
                r"\bdo[_\s-]*not[_\s-]*hide[_\s-]*judg(?:e)?ment[_\s-]*material\b",
                r"\bjudg(?:e)?ment[_\s-]*material\b",
                r"隠してはいけない.*判断材料",
                r"判断材料",
            ],
        ),
        (
            "reveal conditions",
            [
                r"\breveal[_\s-]*conditions?\b",
                r"開示条件",
                r"開示.*条件",
            ],
        ),
        (
            "do-not-reveal-yet",
            [
                r"\bdo[_\s-]*not[_\s-]*reveal[_\s-]*yet\b",
                r"まだ.*開示しない",
                r"未開示",
                r"隠してよい真相",
            ],
        ),
    ]
    _check_required_labeled_values(section, required, location, errors)


def _check_story_deck_three_hook_spine(documents: dict[str, str], errors: list[str]) -> None:
    content = documents.get("story/story_deck.md", "")
    if not content.strip():
        return

    sections = _markdown_sections(content)
    spine = sections.get("three hook spine", "")
    if not spine:
        return

    required_by_hook = {
        "Main Hook": [
            "hook_id",
            "status",
            "current_function",
            "current_question",
            "visible_handle",
            "pressure",
            "exit_condition",
            "next_candidate",
        ],
        "Relationship Hook": [
            "hook_id",
            "status",
            "current_function",
            "current_question",
            "relationship_stake",
            "boundary_or_trust_issue",
            "exit_condition",
            "next_candidate",
        ],
        "Life-Exploration Hook": [
            "hook_id",
            "status",
            "current_function",
            "current_question",
            "available_scope",
            "travel_or_life_option",
            "heroine_attendance",
            "exit_condition",
            "next_candidate",
        ],
    }

    for hook_name, fields in required_by_hook.items():
        hook_body = _markdown_subsection(spine, hook_name)
        if not hook_body:
            errors.append(f"story/story_deck.md: Three Hook Spine missing {hook_name}")
            continue
        _check_required_field_values(
            hook_body,
            fields,
            f"story/story_deck.md: Three Hook Spine {hook_name}",
            errors,
        )

    relationship = _markdown_subsection(spine, "Relationship Hook")
    if re.search(r"好感度|攻略|ルート|bond|AFFINITY", relationship, flags=re.IGNORECASE):
        errors.append("story/story_deck.md: Relationship Hook must not become affinity/route tracking")

    active_status_count = sum(
        1
        for hook_name in required_by_hook
        if _extract_subline_value(_markdown_subsection(spine, hook_name), "status") == "active"
    )
    if active_status_count > 1:
        errors.append("story/story_deck.md: Three Hook Spine must not mark multiple hooks active")

    event_sections = _markdown_sections(documents.get("current/event_card.md", ""))
    active_hook = event_sections.get("active hook", "")
    event_hook_id = _extract_subline_value(active_hook, "hook_id")
    event_hook_type = _extract_subline_value(active_hook, "hook_type")
    story_hook_ids = {
        "main": _extract_subline_value(_markdown_subsection(spine, "Main Hook"), "hook_id"),
        "relationship": _extract_subline_value(_markdown_subsection(spine, "Relationship Hook"), "hook_id"),
        "life": _extract_subline_value(_markdown_subsection(spine, "Life-Exploration Hook"), "hook_id"),
    }
    known_story_hook_ids = {
        hook_id
        for hook_id in story_hook_ids.values()
        if hook_id and not _placeholder_value(hook_id)
    }
    if (
        event_hook_id
        and not _placeholder_value(event_hook_id)
        and event_hook_id != "promoted_next_hook"
        and known_story_hook_ids
        and event_hook_id not in known_story_hook_ids
    ):
        errors.append("current/event_card.md: Active Hook hook_id must exist in story/story_deck.md")
    if event_hook_id and event_hook_type in story_hook_ids:
        story_hook_id = story_hook_ids[event_hook_type]
        if story_hook_id and not _placeholder_value(story_hook_id) and event_hook_id != story_hook_id:
            errors.append("current/event_card.md: Active Hook hook_id must match story/story_deck.md hook_id")

    _check_story_deck_hook_shelves(sections, errors)


def _check_story_deck_hook_shelves(sections: dict[str, str], errors: list[str]) -> None:
    background_hooks = sections.get("background hooks", "")
    candidate_hooks = sections.get("candidate next hooks", "")

    if _hook_shelf_has_real_content(background_hooks):
        if _hook_shelf_marks_active(background_hooks):
            errors.append("story/story_deck.md: Background Hooks must not mark hooks active")
        if _hook_shelf_copies_event_card(background_hooks):
            errors.append("story/story_deck.md: Background Hooks must not copy current/event_card.md active fields")

    if _hook_shelf_has_real_content(candidate_hooks):
        if _hook_shelf_marks_active(candidate_hooks):
            errors.append("story/story_deck.md: Candidate Next Hooks must not mark hooks active before promotion")
        if _hook_shelf_copies_event_card(candidate_hooks):
            errors.append("story/story_deck.md: Candidate Next Hooks must not be formatted as an active event_card")


def _hook_shelf_has_real_content(section: str) -> bool:
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("注"):
            continue
        if line in {"-", "- 未設定", "未設定", "- TODO", "TODO"}:
            continue
        if re.match(r"^[-*]\s*[^:：]+[:：]\s*$", line):
            continue
        return True
    return False


def _hook_shelf_marks_active(section: str) -> bool:
    return bool(re.search(r"^\s*[-*]?\s*status\s*[:：]\s*active\s*$", section, flags=re.MULTILINE))


def _hook_shelf_copies_event_card(section: str) -> bool:
    active_field_labels = [
        "Visible Problem",
        "First Concrete Action",
        "Handles 2-4",
        "Relationship Stake",
        "If Ignored",
        "Next Visible Change",
    ]
    return sum(1 for label in active_field_labels if label in section) >= 3


def _check_event_card_hook_scaffold(sections: dict[str, str], errors: list[str]) -> None:
    active_hook = sections.get("active hook", "")
    scene_function = sections.get("scene function", "")

    _check_required_field_values(
        active_hook,
        ["hook_id", "hook_type", "status", "foreground_reason"],
        "current/event_card.md: Active Hook",
        errors,
    )
    hook_type = _extract_subline_value(active_hook, "hook_type")
    if hook_type and hook_type not in {"main", "relationship", "life"}:
        errors.append("current/event_card.md: Active Hook hook_type must be main / relationship / life")
    status = _extract_subline_value(active_hook, "status")
    if status and status != "active":
        errors.append("current/event_card.md: Active Hook status must be active")

    _check_required_field_values(
        scene_function,
        ["function", "current_question", "entry_state", "exit_condition", "change_delta", "next_hook_candidate"],
        "current/event_card.md: Scene Function",
        errors,
    )


def _check_required_field_values(
    section: str,
    fields: list[str],
    location: str,
    errors: list[str],
) -> None:
    for field in fields:
        value = _extract_subline_value(section, re.escape(field))
        if value is None or _placeholder_value(value):
            errors.append(f"{location}: {field} is empty")


def _find_section(sections: dict[str, str], heading_patterns: list[str]) -> tuple[str, str]:
    for name, body in sections.items():
        if any(re.search(pattern, name, flags=re.IGNORECASE) for pattern in heading_patterns):
            return f"## {name}", body
    return "", ""


def _check_required_labeled_values(
    section: str,
    required: list[tuple[str, list[str]]],
    location: str,
    errors: list[str],
) -> None:
    for field_name, label_patterns in required:
        value = _extract_labeled_value_by_patterns(section, label_patterns)
        if value is None or _placeholder_value(value):
            errors.append(f"{location}: {field_name} is empty")


def _extract_labeled_value_by_patterns(section: str, label_patterns: list[str]) -> str | None:
    lines = section.splitlines()
    for index, raw_line in enumerate(lines):
        match = re.match(r"^[ \t]*(?:[-*][ \t]*)?([^:：\n]{1,100})[ \t]*[:：][ \t]*(.*)$", raw_line)
        if not match:
            continue
        label = match.group(1).strip()
        if not any(re.search(pattern, label, flags=re.IGNORECASE) for pattern in label_patterns):
            continue
        value = match.group(2).strip()
        if value:
            return value
        nested_value = _nested_value_after_label(lines, index)
        if nested_value:
            return nested_value
    return None


def _nested_value_after_label(lines: list[str], label_index: int) -> str | None:
    label_line = lines[label_index]
    label_indent = len(label_line) - len(label_line.lstrip(" \t"))
    collected: list[str] = []
    for raw_line in lines[label_index + 1 :]:
        stripped = raw_line.strip()
        if not stripped:
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" \t"))
        if indent <= label_indent:
            break
        normalized = stripped.lstrip("-* \t").strip()
        if normalized and not _placeholder_value(normalized):
            collected.append(normalized)
    return " ".join(collected).strip() or None


def _markdown_subsection(markdown: str, heading: str) -> str:
    pattern = re.compile(rf"^###\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return ""
    next_heading = re.search(r"^###\s+.+?\s*$", markdown[match.end() :], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(markdown)
    return markdown[match.end() : end].strip()


def _placeholder_value(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized in {"", "未設定", "todo", "placeholder", "n/a", "none", "-"}


def _items_block_before_knowledge_state(content: str) -> bool:
    marker = re.search(r"^##\s+knowledge_state\s*$", content, flags=re.MULTILINE | re.IGNORECASE)
    if not marker:
        return False
    before = content[: marker.start()]
    return bool(re.search(r"^\s*items\s*:", before, flags=re.MULTILINE))


def _parse_knowledge_yaml(content: str) -> dict[str, Any] | None:
    block = _extract_knowledge_yaml_block(content)
    if not block.strip():
        return None
    try:
        import yaml

        parsed = yaml.safe_load(block)
        return parsed if isinstance(parsed, dict) else None
    except ModuleNotFoundError:
        return _parse_knowledge_yaml_minimal(block)
    except Exception:
        return None


def _extract_knowledge_yaml_block(content: str) -> str:
    knowledge_match = re.search(
        r"^##\s+knowledge_state\s*$.*?```(?:yaml)?\s*\n(.*?)\n```",
        content,
        flags=re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    if knowledge_match:
        return knowledge_match.group(1)
    for match in re.finditer(r"```(?:yaml)?\s*\n(.*?)\n```", content, re.DOTALL | re.IGNORECASE):
        block = match.group(1)
        if re.search(r"^\s*items\s*:", block, re.MULTILINE):
            return block
    return ""


def _parse_knowledge_yaml_minimal(block: str) -> dict[str, Any] | None:
    items: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        key_match = re.match(r"\s*-\s+key:\s*(.+?)\s*$", line)
        if key_match:
            current = {"key": key_match.group(1).strip().strip('"')}
            items.append(current)
            continue
        field_match = re.match(r"\s+([A-Za-z0-9_]+):\s*(.*?)\s*$", line)
        if field_match and current is not None:
            current[field_match.group(1)] = field_match.group(2).strip().strip('"')
    return {"items": items} if items else None


def _check_event_card_subline_group(
    section_body: str,
    labels: list[str],
    section_name: str,
    errors: list[str],
) -> None:
    present_labels = [
        label
        for label in labels
        if _event_card_subline_present(section_body, re.escape(label))
    ]
    if present_labels:
        labels_to_check = labels
    elif _has_event_card_freeform_content(section_body):
        return
    else:
        labels_to_check = labels
    for label in labels_to_check:
        if _extract_subline_value(section_body, re.escape(label)) is None:
            errors.append(f"current/event_card.md: {section_name} の '{label}' が空である")


def _extract_subline_value(section_body: str, key_pattern: str) -> str | None:
    match = re.search(rf"^[ \t]*-[ \t]*{key_pattern}[ \t]*:[ \t]*(.*)$", section_body, flags=re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def _event_card_subline_present(section_body: str, key_pattern: str) -> bool:
    return bool(re.search(rf"^[ \t]*-[ \t]*{key_pattern}[ \t]*:", section_body, flags=re.MULTILINE))


def _has_event_card_freeform_content(section_body: str) -> bool:
    for raw_line in section_body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.match(r"^-\s*未設定\s*$", line):
            continue
        if re.match(r"^-\s*[^:：]+[:：]\s*$", line):
            continue
        if line == "- 注: handlesは選択肢ではなく行動余地。":
            continue
        return True
    return False


def _count_freeform_handles(section_body: str) -> int:
    count = 0
    for raw_line in section_body.splitlines():
        line = raw_line.strip()
        if not line or line == "- 注: handlesは選択肢ではなく行動余地。":
            continue
        if re.match(r"^-\s*[^:：]+[:：]\s*$", line):
            continue
        count += 1
    return count
