"""Validation helpers for generated LILIA Persona Profile Markdown.

The validator is stdlib-only so launcher code can use it without importing the
character YAML stack. It validates the Wave 12.1 ``profile.md`` shape produced
by ``tools.character.profile_generator``.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re
import unicodedata


REQUIRED_SECTIONS = (
    "基礎情報",
    "appearance",
    "tone",
    "personality",
    "values",
    "everyday anchors",
    "memories",
    "contradictions",
    "unspoken",
    "reactions",
    "sensuality / body distance",
    "forbidden",
    "context",
    "描写の縛り",
    "Initial Scene Anchors",
    "fixed memory",
    "5層構造 / Self-Understanding",
    "voice by relationship stage",
    "人格設計",
    "Relationship Progression",
    "Multi-Relationship / Jealousy Profile",
    "Ability / Intimacy Resonance",
    "Deepening Tags",
    "Do Not Predefine",
)

DEEPENING_TAGS = (
    "境界線を尊重された",
    "自分から頼った",
    "自分から断った",
    "呼び方が変わった",
    "沈黙を共有した",
    "小さな約束が残った",
    "誤解を修正した",
    "摩擦を処理した",
    "秘密の一部を共有した",
    "親密後のaftercareが残った",
    "他者との関係について確認した",
    "離れる自由を確認した",
    "能力との相互作用を確認した",
)

DO_NOT_PREDEFINE = (
    "完成された恋愛感情",
    "ユーザーへの好意",
    "攻略トリガー",
    "親密成立",
    "重い過去を説明で全部出すこと",
    "固定台詞集",
    "ハーレム展開の強制",
    "能力反応の即時発火",
)

REQUIRED_SUBFIELDS: dict[str, tuple[str, ...]] = {
    "基礎情報": ("name", "age", "occupation", "role", "appearance", "body", "outfit"),
    "appearance": ("hair_style", "hair_color", "eye_color", "body", "outfit", "notes"),
    "tone": ("rule", "examples"),
    "personality": ("行動で見える性格", "困った時の出方", "褒められた時の反応", "怒った時の反応", "頼る / 断る / 待つ の傾向"),
    "everyday anchors": ("生活の場所", "仕事 / 用事 / 習慣", "よく触る物", "初回sceneで使える具体物"),
    "contradictions": ("表の態度", "内側の反応", "表の態度と内側の矛盾", "頼りたい / 頼れない", "近づきたい / 距離を守りたい"),
    "reactions": ("能力や異常性に触れた相手には", "弱っている相手には", "急かされたとき", "感謝されたとき", "踏み込まれたとき", "待ってもらえたとき", "助けられすぎたとき", "軽く扱われたとき"),
    "sensuality / body distance": ("初期距離", "近づいてよい条件", "止まる合図", "触れられた時の出方", "親密さを急がないための制約"),
    "context": ("初回scene開始時点の状況", "ユーザーとの関係位置", "表と内の差", "内面に持っているもの", "今日なぜそこにいるか", "初回sceneの生活上の用事"),
    "描写の縛り": ("必ず入れる質感1", "必ず入れる質感2"),
    "Initial Scene Anchors": ("場所と状況", "手元の具体物", "最初の距離", "会話の入口"),
    "fixed memory": ("core fixed", "historical fixed"),
    "5層構造 / Self-Understanding": ("Layer 1", "Layer 2", "Layer 3", "Layer 4", "Layer 5"),
    "voice by relationship stage": ("Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage 5"),
    "人格設計": ("骨", "境遇", "価値観", "欠点", "口調", "壁", "秘密", "開示条件", "拒否トリガー", "育つ部分", "性格の発見", "ユーザーとの関係変化", "個人ストーリーの種"),
    "Relationship Progression": ("rapport", "intimacy", "consent", "boundary", "self-understanding"),
    "Multi-Relationship / Jealousy Profile": ("status", "揺れやすい条件", "揺れにくい条件", "表に出る反応", "禁止"),
    "Ability / Intimacy Resonance": ("status", "能力が導入された場合に見ること", "初期sceneでは使わない", "能力が導入された時だけ有効化する"),
}

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_LIST_PREFIX_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s*")
_CHECKBOX_RE = re.compile(r"^\s*-\s+\[(?P<mark>[ xX])\]\s+(?P<label>.+?)\s*$")
_LATIN_WORD_RE = re.compile(r"[a-z][a-z0-9'_-]*", re.IGNORECASE)
_CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
_PLACEHOLDER_RE = re.compile(
    r"未設定|未確定|TODO|TBD|FIXME|placeholder|汎用テンプレ|"
    r"ここに|入力してください|N/A|null|None|"
    r"\[(?:ヒロイン|主人公|ユーザー|名前|年齢|職業|何|Q[1-9])[^]]*\]",
    re.IGNORECASE,
)
_FORBIDDEN_WORDS_RE = re.compile(r"AFFINITY|bond|ルート", re.IGNORECASE)
_LATIN_REPETITION_STOPWORDS = {
    "stage",
    "voice",
    "by",
    "lilia",
    "user",
    "profile",
    "scene",
    "memory",
    "relationship",
    "beliefs",
}
_LABEL_ONLY_ALLOWED = {
    "examples",
    "corefixed",
    "historicalfixed",
    "layer3",
    "layer4",
    "layer5",
    "chinkトリガー",
    "barrier強化",
    "骨",
    "壁",
    "育つ部分",
    "rapport",
    "intimacy",
    "consent",
    "boundary",
    "self-understanding",
    "揺れやすい条件",
    "揺れにくい条件",
    "表に出る反応",
    "禁止",
    "能力が導入された場合に見ること",
}


@dataclass(frozen=True)
class _Section:
    heading: str
    content: str
    level: int


def validate_profile_output(profile_md: str, answers: dict, character_yaml: dict) -> tuple[bool, list[str]]:
    """Validate a generated Wave 12.1 ``profile.md``.

    Returns ``(ok, errors)`` and does not raise for normal validation failures.
    ``answers`` and ``character_yaml`` are used only for copy and minimum
    grounding checks.
    """

    errors: list[str] = []
    if not isinstance(profile_md, str) or not profile_md.strip():
        return False, ["profile_md is empty"]
    if not isinstance(answers, dict):
        errors.append("answers must be a dict")
        answers = {}
    if not isinstance(character_yaml, dict):
        errors.append("character_yaml must be a dict")
        character_yaml = {}

    sections = _parse_markdown_sections(profile_md)
    _check_required_sections(sections, errors)
    _check_required_subfields(sections, errors)
    _check_placeholder_remnants(profile_md, sections, errors)
    _check_ellipsis_field_lines(sections, errors)
    _check_repeated_phrases(profile_md, errors)
    _check_q1_verbatim(profile_md, answers, errors)
    _check_deepening_tags(sections, errors)
    _check_do_not_predefine(sections, errors)
    _check_basic_grounding(sections, character_yaml, errors)
    return not errors, errors


def _parse_markdown_sections(markdown: str) -> dict[str, _Section]:
    sections: dict[str, tuple[str, int, list[str]]] = {}
    current_key: str | None = None
    current_level = 0

    for line in markdown.splitlines():
        match = _HEADING_RE.match(line)
        if match:
            level = len(match.group(1))
            heading = _strip_markdown(match.group(2)).strip()
            key = _normalize_heading(heading)
            if level <= 2:
                sections.setdefault(key, (heading, level, []))
                current_key = key
                current_level = level
                continue
        if current_key is not None:
            sections[current_key][2].append(line)

    return {
        key: _Section(heading=heading, level=level, content="\n".join(lines).strip())
        for key, (heading, level, lines) in sections.items()
        if current_level or level
    }


def _check_required_sections(sections: dict[str, _Section], errors: list[str]) -> None:
    for required in REQUIRED_SECTIONS:
        section = _get_section(sections, required)
        if section is None:
            errors.append(f"missing required section `{required}`")
            continue
        if not _has_meaningful_content(section.content):
            errors.append(f"section `{section.heading}` is empty or placeholder-only")


def _check_required_subfields(sections: dict[str, _Section], errors: list[str]) -> None:
    for heading, fields in REQUIRED_SUBFIELDS.items():
        section = _get_section(sections, heading)
        if section is None:
            continue
        for field in fields:
            if not _section_has_field(section.content, field):
                errors.append(f"section `{section.heading}` is missing subfield `{field}`")

    tone = _get_section(sections, "tone")
    if tone is not None and len(_list_items(_subsection_after_label(tone.content, "examples"))) < 2:
        errors.append("section `tone` needs at least two tone examples")

    for heading in ("values", "memories", "unspoken", "forbidden"):
        section = _get_section(sections, heading)
        if section is not None and len(_list_items(section.content)) < 2:
            errors.append(f"section `{section.heading}` needs at least two list items")


def _check_placeholder_remnants(profile_md: str, sections: dict[str, _Section], errors: list[str]) -> None:
    if _FORBIDDEN_WORDS_RE.search(profile_md):
        errors.append("profile contains forbidden route/affinity vocabulary")
    for section in sections.values():
        bad_lines = [
            _shorten(line.strip(), 90)
            for line in section.content.splitlines()
            if line.strip() and _is_placeholder_line(line)
        ]
        if bad_lines:
            preview = "; ".join(bad_lines[:3])
            more = "" if len(bad_lines) <= 3 else f"; +{len(bad_lines) - 3} more"
            errors.append(f"section `{section.heading}` has placeholder remnants: {preview}{more}")


def _check_ellipsis_field_lines(sections: dict[str, _Section], errors: list[str]) -> None:
    for section in sections.values():
        for line in section.content.splitlines():
            stripped = line.strip()
            if not stripped or not _looks_like_field_line(stripped):
                continue
            value = re.split(r"[:：]", stripped, maxsplit=1)[-1].strip()
            if value.endswith(("…", "...", "。…")):
                errors.append(f"section `{section.heading}` has ellipsis-ending field line: `{_shorten(stripped, 80)}`")


def _check_repeated_phrases(text: str, errors: list[str]) -> None:
    counts = Counter(_iter_repetition_phrases(text))
    repeated = [(phrase, count) for phrase, count in counts.items() if count >= 3]
    repeated.sort(key=lambda item: (-item[1], item[0]))
    if repeated:
        phrase, count = repeated[0]
        errors.append(f"repeated phrase appears {count} times: `{_shorten(phrase, 70)}`")


def _check_q1_verbatim(profile_md: str, answers: dict, errors: list[str]) -> None:
    q1_text = _answer_text(answers, 1)
    copied = _find_verbatim_window(q1_text, profile_md, minimum=30)
    if copied:
        errors.append(f"Q1 text copied verbatim for 30+ characters: `{_shorten(copied, 70)}`")


def _check_deepening_tags(sections: dict[str, _Section], errors: list[str]) -> None:
    section = _get_section(sections, "Deepening Tags")
    if section is None:
        return
    checkboxes = _checkbox_items(section.content)
    labels = tuple(label for mark, label in checkboxes)
    checked = [label for mark, label in checkboxes if mark.strip()]
    if labels != DEEPENING_TAGS:
        errors.append("Deepening Tags must be exactly the Wave 12.1 13 unchecked tags in order")
    if checked:
        errors.append("Deepening Tags must all be unchecked")


def _check_do_not_predefine(sections: dict[str, _Section], errors: list[str]) -> None:
    section = _get_section(sections, "Do Not Predefine")
    if section is None:
        return
    items = tuple(_plain_line(item) for item in _list_items(section.content))
    if items != DO_NOT_PREDEFINE:
        errors.append("Do Not Predefine must be exactly the Wave 12.1 8 items in order")


def _check_basic_grounding(
    sections: dict[str, _Section],
    character_yaml: dict,
    errors: list[str],
) -> None:
    basic = _get_section(sections, "基礎情報")
    if basic is None:
        return
    name = str(character_yaml.get("name", "")).strip()
    if name and name not in basic.content:
        errors.append("section `基礎情報` does not include character_yaml name")


def _answer_text(answers: dict, number: int) -> str:
    keys = (number, str(number), f"q{number}", f"Q{number}", f"Q{number}.")
    for key in keys:
        value = answers.get(key)
        if value:
            return str(value)
    number_text = str(number)
    for key, value in answers.items():
        key_text = str(key).lower()
        if key_text == number_text or key_text.startswith(f"q{number}") or f"q{number}" in key_text:
            return str(value)
    return ""


def _get_section(sections: dict[str, _Section], heading: str) -> _Section | None:
    key = _normalize_heading(heading)
    return sections.get(key)


def _normalize_heading(heading: str) -> str:
    normalized = _nfkc(_strip_markdown(heading)).strip()
    normalized = re.sub(r"\s*[\[［(（].*?[\]］)）]\s*$", "", normalized).strip()
    normalized = re.sub(r"\s+", "", normalized)
    return normalized.casefold()


def _has_meaningful_content(content: str) -> bool:
    for line in content.splitlines():
        plain = _plain_line(line)
        if not plain or _is_placeholder_line(line):
            continue
        if len(re.sub(r"\s+", "", plain)) >= 4:
            return True
    return False


def _section_has_field(content: str, field: str) -> bool:
    normalized_field = _normalize_field(field)
    for line in content.splitlines():
        plain = _plain_line(line)
        if not plain:
            continue
        if _normalize_field(plain).startswith(normalized_field):
            if normalized_field in _LABEL_ONLY_ALLOWED and re.search(r"[:：]\s*$", plain):
                return True
            return not _is_placeholder_line(line)
    return False


def _normalize_field(text: str) -> str:
    text = _nfkc(_strip_markdown(text))
    text = _LIST_PREFIX_RE.sub("", text).strip()
    text = re.split(r"[:：]", text, maxsplit=1)[0].strip()
    text = re.sub(r"\s+", "", text)
    return text.casefold()


def _subsection_after_label(content: str, label: str) -> str:
    lines = content.splitlines()
    normalized_label = _normalize_field(label)
    for index, line in enumerate(lines):
        if _normalize_field(line) == normalized_label:
            return "\n".join(lines[index + 1 :])
    return ""


def _is_placeholder_line(line: str) -> bool:
    plain = _plain_line(line)
    if not plain:
        return True
    compact = re.sub(r"\s+", "", plain)
    if compact in {"-", "--", "—", "...", "…", "なし", "空欄", "n/a", "na", "none", "null"}:
        return True
    if _PLACEHOLDER_RE.search(plain):
        return True
    if _looks_like_field_line(plain):
        field_name = _normalize_field(plain)
        if _is_allowed_label_only(field_name) and re.search(r"[:：]\s*$", plain):
            return False
        value = re.split(r"[:：]", plain, maxsplit=1)[-1].strip()
        if not value or _PLACEHOLDER_RE.fullmatch(value):
            return True
    return False


def _looks_like_field_line(line: str) -> bool:
    plain = _plain_line(line)
    return ":" in plain or "：" in plain


def _list_items(content: str) -> list[str]:
    items: list[str] = []
    for line in content.splitlines():
        if re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", line):
            item = _plain_line(line)
            if item:
                items.append(item)
    return items


def _checkbox_items(content: str) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for line in content.splitlines():
        match = _CHECKBOX_RE.match(line)
        if match:
            items.append((match.group("mark"), _plain_line(match.group("label"))))
    return items


def _plain_line(line: str) -> str:
    plain = _strip_markdown(_nfkc(line)).strip()
    plain = re.sub(r"^\s*#{1,6}\s*", "", plain)
    plain = _LIST_PREFIX_RE.sub("", plain).strip()
    plain = re.sub(r"^\[[ xX]\]\s*", "", plain).strip()
    plain = re.sub(r"\s+", " ", plain)
    return plain


def _iter_repetition_phrases(text: str) -> list[str]:
    phrases: list[str] = []
    for line in text.splitlines():
        plain = _plain_line(line)
        if not plain or _is_placeholder_line(line):
            continue
        if _looks_like_field_line(plain):
            plain = re.split(r"[:：]", plain, maxsplit=1)[-1].strip()
        if plain and _phrase_is_long_enough(plain):
            phrases.append(plain)
        for clause in re.split(r"[。.!?！？、,;；\n]", plain):
            clause = re.sub(r"\s+", " ", clause).strip()
            if _phrase_is_long_enough(clause):
                phrases.append(clause)

    words = [word.casefold() for word in _LATIN_WORD_RE.findall(_strip_markdown(text))]
    for size in range(3, 7):
        for index in range(0, max(len(words) - size + 1, 0)):
            phrase = " ".join(words[index : index + size])
            if len(phrase) >= 14 and not set(phrase.split()).issubset(_LATIN_REPETITION_STOPWORDS):
                phrases.append(phrase)
    return phrases


def _is_allowed_label_only(field_name: str) -> bool:
    return any(field_name == allowed or field_name.startswith(allowed) for allowed in _LABEL_ONLY_ALLOWED)


def _phrase_is_long_enough(phrase: str) -> bool:
    compact = re.sub(r"\s+", "", phrase)
    if _CJK_RE.search(compact):
        return len(compact) >= 8
    return len(compact) >= 12


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
    return text.replace("`", "").replace("**", "").replace("__", "").replace("*", "")


def _nfkc(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def _shorten(text: str, limit: int) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 1]}…"
