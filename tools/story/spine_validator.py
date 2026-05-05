"""Validation helpers for generated story spine Markdown.

The validator is intentionally stdlib-only so it can run in launcher and
prompt-support contexts without pulling in the character generation stack.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata


STORY_REQUIRED_SECTIONS = (
    "Main Question",
    "Reveal Ladder",
    "Background Truth",
    "Pressure Direction",
    "Heroine Tie",
    "if ignored",
    "Drift Guard",
)

RELATIONSHIP_REQUIRED_SECTIONS = (
    "育てたいテーマ",
    "最初の摩擦",
    "LILIAが守るもの",
    "LILIAが避けるもの",
    "ユーザー側に問うこと",
    "関係が変化する方向",
)

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_MEDIA_TITLE_RE = re.compile(r"^\s*\d+\.\s+\*\*(.+?)\*\*")
_PATTERN_OBSERVATION_RE = re.compile(r"^\s*\*\*観察される作品\*\*:\s*(.+)")
_LIST_PREFIX_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s*")
_STATUS_RE = re.compile(r"^\s*\[(?:pending|in_progress|revealed|closed|standing|fired|recurring)\]\s*", re.IGNORECASE)
_LATIN_WORD_RE = re.compile(r"[a-z][a-z0-9'_-]*", re.IGNORECASE)
_CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
_PLACEHOLDER_TOKEN_RE = re.compile(
    r"未設定|TODO|TBD|FIXME|placeholder|汎用テンプレ|"
    r"未確定\s*[:：]\s*進行で決める|"
    r"\[(?:ヒロイン|主人公|ユーザー|傷|選択肢|未解明|何|Q[1-9])[^]]*\]",
    re.IGNORECASE,
)
_TEMPLATE_BOILERPLATE_FRAGMENTS = (
    "この話が問うこと（1行）",
    "newgame の q&a から ai が生成する",
    "プレイ進行で書き換え可能",
    "q5 を自動的に",
    "ai が選択したパターン名",
    "謎・関係・真相の段階開示",
    "newgame で初期3段階",
    "main question の選択パターン",
    "この話の真相。本文には出さない",
    "references/story_pattern_stock.md",
    "newgame で最低限の骨だけ生成",
    "ユーザーが放置・脱線・無視した時",
    "全部同時に動かさない",
    "関係者全員が欲する1つのもの",
    "profile.md / relationship_spine.md から抽出",
    "放置時、1-3 scene 以内",
    "物語が霧にならないため",
    "形式: `物名",
)


@dataclass(frozen=True)
class _Section:
    heading: str
    content: str


def validate_spine_output(
    story_spine_md: str,
    relationship_spine_md: str,
    pattern_stock_path: Path,
    media_stock_path: Path,
    q1_text: str = "",
) -> tuple[bool, list[str]]:
    """Validate generated ``story_spine.md`` and ``relationship_spine.md``.

    Returns ``(ok, errors)``. The function never raises for normal validation
    failures; unreadable stock files are reported as errors so callers can show
    one consolidated quality-gate result.
    """

    errors: list[str] = []
    story_sections = _parse_markdown_sections(story_spine_md)
    relationship_sections = _parse_markdown_sections(relationship_spine_md)
    combined = f"{story_spine_md}\n\n{relationship_spine_md}"

    _check_required_sections("story_spine", story_sections, STORY_REQUIRED_SECTIONS, errors)
    _check_required_sections("relationship_spine", relationship_sections, RELATIONSHIP_REQUIRED_SECTIONS, errors)
    _check_unresolved_placeholders("story_spine", story_sections, errors)
    _check_unresolved_placeholders("relationship_spine", relationship_sections, errors)
    _check_ellipsis_endings("story_spine", story_sections, errors)
    _check_ellipsis_endings("relationship_spine", relationship_sections, errors)
    _check_repeated_phrases(combined, errors)
    _check_q1_verbatim(combined, q1_text, errors)

    forbidden_titles = _load_forbidden_titles(pattern_stock_path, media_stock_path, errors)
    _check_forbidden_titles(combined, forbidden_titles, errors)

    return not errors, errors


def _parse_markdown_sections(markdown: str) -> dict[str, _Section]:
    sections: dict[str, tuple[str, list[str]]] = {}
    current_key: str | None = None

    for line in markdown.splitlines():
        match = _HEADING_RE.match(line)
        if match:
            heading = _strip_markdown(match.group(2)).strip()
            key = _normalize_heading(heading)
            sections.setdefault(key, (heading, []))
            current_key = key
            continue
        if current_key is not None:
            sections[current_key][1].append(line)

    return {
        key: _Section(heading=heading, content="\n".join(lines).strip())
        for key, (heading, lines) in sections.items()
    }


def _check_required_sections(
    document_label: str,
    sections: dict[str, _Section],
    required_sections: tuple[str, ...],
    errors: list[str],
) -> None:
    for required in required_sections:
        section = _get_section(sections, required)
        if section is None:
            errors.append(f"{document_label}: missing required section `{required}`")
            continue
        if not _has_meaningful_content(section.content):
            errors.append(f"{document_label}: section `{section.heading}` is empty or placeholder-only")
            continue
        shape_error = _specific_section_shape_error(required, section.content)
        if shape_error:
            errors.append(f"{document_label}: section `{section.heading}` {shape_error}")


def _check_unresolved_placeholders(
    document_label: str,
    sections: dict[str, _Section],
    errors: list[str],
) -> None:
    for section in sections.values():
        bad_lines = _find_placeholder_lines(section.content)
        if bad_lines:
            preview = "; ".join(bad_lines[:3])
            more = "" if len(bad_lines) <= 3 else f"; +{len(bad_lines) - 3} more"
            errors.append(f"{document_label}: section `{section.heading}` has unresolved placeholder lines: {preview}{more}")


def _check_ellipsis_endings(
    document_label: str,
    sections: dict[str, _Section],
    errors: list[str],
) -> None:
    for section in sections.values():
        tail = _last_content_line(section.content)
        if tail.endswith(("…", "...")):
            errors.append(f"{document_label}: section `{section.heading}` ends with an unfinished ellipsis")


def _check_repeated_phrases(text: str, errors: list[str]) -> None:
    phrases = list(_iter_repetition_phrases(text))
    counts = Counter(phrases)
    repeated = [(phrase, count) for phrase, count in counts.items() if count >= 3]
    repeated.sort(key=lambda item: (-item[1], item[0]))
    if repeated:
        phrase, count = repeated[0]
        errors.append(f"repeated phrase appears {count} times: `{_shorten(phrase, 60)}`")


def _check_q1_verbatim(text: str, q1_text: str, errors: list[str]) -> None:
    copied = _find_verbatim_window(q1_text, text, minimum=30)
    if copied:
        errors.append(f"Q1 text copied verbatim for 30+ characters: `{_shorten(copied, 60)}`")


def _load_forbidden_titles(
    pattern_stock_path: Path,
    media_stock_path: Path,
    errors: list[str],
) -> dict[str, set[str]]:
    titles: dict[str, set[str]] = {}

    media_text = _read_text(media_stock_path, errors)
    if media_text:
        for raw_title in _extract_media_titles(media_text):
            _add_forbidden_title(titles, raw_title, "story_media_stock title")

    pattern_text = _read_text(pattern_stock_path, errors)
    if pattern_text:
        for raw_title in _extract_pattern_observation_titles(pattern_text):
            _add_forbidden_title(titles, raw_title, "story_pattern_stock observation")

    return titles


def _check_forbidden_titles(text: str, forbidden_titles: dict[str, set[str]], errors: list[str]) -> None:
    leaked: list[tuple[str, str]] = []
    for title, sources in sorted(forbidden_titles.items(), key=lambda item: (-len(item[0]), item[0])):
        if _contains_literal_title(text, title):
            leaked.append((title, ", ".join(sorted(sources))))
    if leaked:
        preview = "; ".join(f"`{title}` ({source})" for title, source in leaked[:5])
        more = "" if len(leaked) <= 5 else f"; +{len(leaked) - 5} more"
        errors.append(f"literal reference work/title leaked into spine output: {preview}{more}")


def _read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"could not read `{path}`: {exc}")
    except OSError as exc:
        errors.append(f"could not read `{path}`: {exc}")
    return ""


def _extract_media_titles(text: str) -> list[str]:
    titles: list[str] = []
    for line in text.splitlines():
        match = _MEDIA_TITLE_RE.match(line)
        if match:
            titles.extend(_title_variants(match.group(1)))
    return titles


def _extract_pattern_observation_titles(text: str) -> list[str]:
    titles: list[str] = []
    for line in text.splitlines():
        match = _PATTERN_OBSERVATION_RE.match(line)
        if not match:
            continue
        for entry in re.split(r"\s*,\s*|、", match.group(1)):
            titles.extend(_title_variants(entry))
    return titles


def _title_variants(raw_title: str) -> list[str]:
    title = _clean_title(raw_title)
    if not title:
        return []
    variants = [title]
    for part in re.split(r"\s*/\s*", title):
        clean = _clean_title(part)
        if clean:
            variants.append(clean)
    return variants


def _add_forbidden_title(titles: dict[str, set[str]], raw_title: str, source: str) -> None:
    title = _clean_title(raw_title)
    if not _is_title_worth_checking(title):
        return
    titles.setdefault(title, set()).add(source)


def _clean_title(raw_title: str) -> str:
    title = _strip_markdown(_nfkc(raw_title))
    title = re.sub(r"\s*[\(（][^()（）]*[\)）]\s*", "", title)
    title = title.strip(" \t\r\n-—:：,、.。")
    title = re.sub(r"\s+", " ", title)
    return title


def _is_title_worth_checking(title: str) -> bool:
    compact = re.sub(r"\s+", "", title)
    if len(compact) < 3:
        return False
    return bool(_CJK_RE.search(title) or _LATIN_WORD_RE.search(title) or re.search(r"\d", title))


def _contains_literal_title(text: str, title: str) -> bool:
    normalized_text = _nfkc(text)
    normalized_title = _nfkc(title).strip()
    if not normalized_title:
        return False
    if _CJK_RE.search(normalized_title):
        return normalized_title in normalized_text
    escaped = re.escape(normalized_title)
    escaped = re.sub(r"\\\s+", r"\\s+", escaped)
    pattern = rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])"
    return re.search(pattern, normalized_text, re.IGNORECASE) is not None


def _normalize_heading(heading: str) -> str:
    normalized = _nfkc(_strip_markdown(heading)).strip()
    while True:
        stripped = re.sub(r"\s*[\(（][^()（）]*[\)）]\s*$", "", normalized).strip()
        if stripped == normalized:
            break
        normalized = stripped
    normalized = re.sub(r"\s+", "", normalized)
    return normalized.casefold()


def _get_section(sections: dict[str, _Section], heading: str) -> _Section | None:
    key = _normalize_heading(heading)
    if key in sections:
        return sections[key]
    for candidate_key, section in sections.items():
        if candidate_key.startswith(key) or candidate_key.endswith(key) or key in candidate_key:
            return section
    return None


def _has_meaningful_content(content: str) -> bool:
    for line in content.splitlines():
        plain = _plain_line(line)
        if not plain:
            continue
        if _is_placeholder_line(line):
            continue
        if _is_template_boilerplate(plain):
            continue
        if len(re.sub(r"\s+", "", plain)) >= 4:
            return True
    return False


def _specific_section_shape_error(required_heading: str, content: str) -> str:
    key = _normalize_heading(required_heading)
    if key == "mainquestion":
        plain = _section_plain_text(content)
        if len(plain) < 12:
            return "is too short to be a character-specific question"
    if key == "revealladder":
        items = [
            item
            for item in _list_items(content, keep_status=True)
            if re.search(r"\[(?:pending|in_progress|revealed|closed)\]", item, re.IGNORECASE)
            and not _is_placeholder_line(item)
        ]
        if len(items) < 3:
            return "needs at least three non-placeholder reveal steps with state tags"
    if key == "pressuredirection":
        items = [
            item
            for item in _list_items(content, keep_status=True)
            if re.search(r"\[(?:standing|fired|recurring)\]", item, re.IGNORECASE)
            and not _is_placeholder_line(item)
        ]
        if len(items) < 3:
            return "needs three non-placeholder pressure items with state tags"
    if key == "ifignored":
        if not any(not _is_placeholder_line(item) for item in _list_items(content)):
            return "needs at least one concrete consequence"
    if key == "driftguard":
        items = [item for item in _list_items(content) if not _is_placeholder_line(item)]
        if not items:
            return "needs at least one concrete clue"
        if not any(("—" in item or " - " in item or " – " in item) for item in items):
            return "should use `物名 — Background Truth` clue shape"
    return ""


def _find_placeholder_lines(content: str) -> list[str]:
    bad_lines: list[str] = []
    for line in content.splitlines():
        if not line.strip():
            continue
        if _is_placeholder_line(line):
            bad_lines.append(_shorten(line.strip(), 80))
    return bad_lines


def _is_placeholder_line(line: str) -> bool:
    plain = _plain_line(line)
    if not plain:
        return True
    low = plain.casefold()
    compact = re.sub(r"\s+", "", plain)
    if compact in {"-", "--", "—", "...", "…", "なし", "空欄", "n/a", "na", "none", "null"}:
        return True
    if _PLACEHOLDER_TOKEN_RE.search(plain):
        return True
    if _is_bullet_or_numbered(line) and re.search(r"[:：]\s*$", plain):
        return True
    if low.startswith(("例（構造説明", "適用条件:", "構文:")):
        return True
    return False


def _is_bullet_or_numbered(line: str) -> bool:
    return re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", line) is not None


def _plain_line(line: str) -> str:
    plain = _strip_markdown(_nfkc(line)).strip()
    plain = re.sub(r"^\s*#{1,6}\s*", "", plain)
    plain = _LIST_PREFIX_RE.sub("", plain).strip()
    plain = _STATUS_RE.sub("", plain).strip()
    plain = re.sub(r"\s+", " ", plain)
    return plain


def _section_plain_text(content: str) -> str:
    lines = [
        _plain_line(line)
        for line in content.splitlines()
        if _plain_line(line) and not _is_placeholder_line(line) and not _is_template_boilerplate(_plain_line(line))
    ]
    return " ".join(lines).strip()


def _is_template_boilerplate(plain_line: str) -> bool:
    low = plain_line.casefold()
    return any(fragment in low for fragment in _TEMPLATE_BOILERPLATE_FRAGMENTS)


def _list_items(content: str, *, keep_status: bool = False) -> list[str]:
    items: list[str] = []
    for line in content.splitlines():
        if _is_bullet_or_numbered(line):
            item = _strip_markdown(_nfkc(line)).strip()
            item = _LIST_PREFIX_RE.sub("", item).strip()
            if not keep_status:
                item = _STATUS_RE.sub("", item).strip()
            item = re.sub(r"\s+", " ", item)
            if item:
                items.append(item)
    return items


def _last_content_line(content: str) -> str:
    for line in reversed(content.splitlines()):
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _iter_repetition_phrases(text: str) -> list[str]:
    phrases: list[str] = []
    for line in text.splitlines():
        plain = _plain_line(line)
        if not plain or _is_placeholder_line(line) or _is_template_boilerplate(plain):
            continue
        line_phrases: list[str] = []
        if _phrase_is_long_enough(plain):
            line_phrases.append(plain)
        for clause in re.split(r"[。.!?！？、,;；:：\n]", plain):
            clause = re.sub(r"\s+", " ", clause).strip()
            if _phrase_is_long_enough(clause):
                line_phrases.append(clause)
        phrases.extend(dict.fromkeys(line_phrases))

    words = [word.casefold() for word in _LATIN_WORD_RE.findall(_strip_markdown(text))]
    for size in range(3, 7):
        for index in range(0, max(len(words) - size + 1, 0)):
            phrase = " ".join(words[index : index + size])
            if len(phrase) >= 14:
                phrases.append(phrase)
    return phrases


def _phrase_is_long_enough(phrase: str) -> bool:
    compact = re.sub(r"\s+", "", phrase)
    if _CJK_RE.search(compact):
        return len(compact) >= 6
    return len(compact) >= 10


def _find_verbatim_window(source: str, target: str, minimum: int) -> str:
    source_norm = _normalize_for_verbatim(source)
    target_norm = _normalize_for_verbatim(target)
    if len(source_norm) < minimum or len(target_norm) < minimum:
        return ""
    seen: set[str] = set()
    for index in range(0, len(source_norm) - minimum + 1):
        window = source_norm[index : index + minimum]
        if window in seen:
            continue
        seen.add(window)
        if window in target_norm:
            return window
    return ""


def _normalize_for_verbatim(text: str) -> str:
    return re.sub(r"\s+", "", _nfkc(text)).strip()


def _strip_markdown(text: str) -> str:
    stripped = text.replace("`", "")
    stripped = stripped.replace("**", "").replace("__", "")
    stripped = stripped.replace("*", "")
    return stripped


def _nfkc(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def _shorten(text: str, limit: int) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 1]}…"
