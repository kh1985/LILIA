"""Reply context separation for LILIA Play Mode resume prompts.

This module is intentionally read-only. It separates heroine-facing material,
pressure material, and GM-only control material immediately before Play Mode
generation. It does not migrate sessions and does not update save files.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Literal, cast

from tools.session.knowledge_boundary import assess_knowledge_boundary


PressureSource = Literal[
    "protagonist_initiated",
    "heroine_initiated",
    "gm_world_pressure",
    "npc_pressure",
    "environment_pressure",
    "ambient_drift",
    "ignored_event_return",
    "none",
]

VALID_PRESSURE_SOURCES = {
    "protagonist_initiated",
    "heroine_initiated",
    "gm_world_pressure",
    "npc_pressure",
    "environment_pressure",
    "ambient_drift",
    "ignored_event_return",
    "none",
}


@dataclass(frozen=True)
class HeroineReplyContext:
    latest_user_action: str = ""
    latest_user_inner_monologue_gm_only: str = ""

    heroine_known_facts: list[str] = field(default_factory=list)
    shared_facts: list[str] = field(default_factory=list)
    observable_now: list[str] = field(default_factory=list)

    current_physical_situation: list[str] = field(default_factory=list)
    recent_visible_exchange: list[str] = field(default_factory=list)

    voice_rules: list[str] = field(default_factory=list)
    current_state: list[str] = field(default_factory=list)
    relationship_temperature: list[str] = field(default_factory=list)
    memory_echo: list[str] = field(default_factory=list)
    beliefs_or_suspicions: list[str] = field(default_factory=list)

    immediate_reaction_priority: list[str] = field(default_factory=list)
    defense_patterns: list[str] = field(default_factory=list)
    embarrassment_patterns: list[str] = field(default_factory=list)
    distance_patterns: list[str] = field(default_factory=list)

    can_say: list[str] = field(default_factory=list)
    must_not_say: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PressureContext:
    source: PressureSource = "none"

    player_facing_entry: list[str] = field(default_factory=list)
    observable_pressure: list[str] = field(default_factory=list)
    heroine_possible_initiative: list[str] = field(default_factory=list)
    handles: list[str] = field(default_factory=list)
    if_ignored: list[str] = field(default_factory=list)
    next_visible_change: list[str] = field(default_factory=list)

    must_convert_to_observable: list[str] = field(default_factory=list)
    must_not_expose: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GMControlContext:
    active_hook: list[str] = field(default_factory=list)
    scene_function: list[str] = field(default_factory=list)
    relationship_stake: list[str] = field(default_factory=list)
    hidden_truth: list[str] = field(default_factory=list)
    story_pressure: list[str] = field(default_factory=list)
    next_hook: list[str] = field(default_factory=list)
    save_candidates: list[str] = field(default_factory=list)
    do_not_reveal: list[str] = field(default_factory=list)
    forbidden_direct_terms: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ReplyContextBundle:
    latest_user_input: str = ""
    heroine: HeroineReplyContext = field(default_factory=HeroineReplyContext)
    pressure: PressureContext = field(default_factory=PressureContext)
    gm: GMControlContext = field(default_factory=GMControlContext)
    warnings: list[str] = field(default_factory=list)


def build_reply_context_bundle(
    session_root: Path,
    latest_user_input: str = "",
) -> ReplyContextBundle:
    """Build a read-only bundle from a session directory."""

    root = Path(session_root)
    heroine = extract_heroine_context(root, latest_user_input)
    event_card_md = read_text(root / "current/event_card.md")
    pressure, gm = extract_event_card_context(event_card_md)

    knowledge_md = read_text(root / "current/knowledge_state.md")
    warnings: list[str] = []
    if knowledge_md.strip():
        report = assess_knowledge_boundary(knowledge_md)
        warnings.extend(f"knowledge_boundary: {item}" for item in report.errors)
        warnings.extend(f"knowledge_boundary: {item}" for item in report.warnings)
        gm = _merge_gm_context(
            gm,
            hidden_truth=[item.value for item in report.boundary.gm_truth],
            do_not_reveal=[item.value for item in report.boundary.do_not_reveal_yet],
        )
    else:
        warnings.append("current/knowledge_state.md is missing or empty")

    story_spine_md = read_text(root / "current/story_spine.md")
    story_deck_md = read_text(root / "story/story_deck.md")
    gm = _merge_gm_context(
        gm,
        hidden_truth=_story_spine_hidden_truth(story_spine_md),
        story_pressure=_story_pressure(story_spine_md, story_deck_md),
        next_hook=_story_next_hooks(event_card_md, story_deck_md),
        save_candidates=_story_save_candidates(story_spine_md, story_deck_md),
    )

    if event_card_md.strip():
        raw_source = extract_raw_pressure_source(event_card_md)
        if raw_source and raw_source not in VALID_PRESSURE_SOURCES:
            warnings.append(f"invalid pressure_source: {raw_source}")
        if not _section(parse_markdown_sections(event_card_md), "Pressure / Agency"):
            warnings.append("current/event_card.md is missing Pressure / Agency")
    else:
        warnings.append("current/event_card.md is missing or empty")

    if pressure.source == "gm_world_pressure" and not pressure.observable_pressure:
        warnings.append("gm_world_pressure requires Observable Pressure")
    if pressure.source == "heroine_initiated" and not _heroine_initiative_has_basis(pressure, heroine):
        warnings.append(
            "heroine_initiated pressure requires state / relationship / memory / beliefs basis"
        )

    return ReplyContextBundle(
        latest_user_input=latest_user_input,
        heroine=heroine,
        pressure=pressure,
        gm=gm,
        warnings=_unique(warnings),
    )


def render_reply_context_bundle(bundle: ReplyContextBundle) -> str:
    """Render the bundle as Markdown for insertion before raw session files."""

    heroine = bundle.heroine
    pressure = bundle.pressure
    gm = bundle.gm
    parts = [
        "# Reply Context Bundle",
        "",
        "## Latest User Input",
        "",
        bundle.latest_user_input.strip() or "(none provided / 未指定)",
        "",
        "## Heroine Reply Context",
        "",
        "This is the primary basis for heroine dialogue and behavior.",
        "The heroine may only speak from what she can observe, remember, feel, infer, or misunderstand.",
        "ヒロイン本文の主材料。ヒロインが知覚・記憶・推測・誤解できる情報だけを根拠にする。",
        "",
        "### Latest Player-Visible Action",
        "",
        _render_value(heroine.latest_user_action),
        "",
        "### Heroine Known Facts",
        "",
        _render_list(heroine.heroine_known_facts),
        "",
        "### Shared Facts",
        "",
        _render_list(heroine.shared_facts),
        "",
        "### Observable Now",
        "",
        _render_list(heroine.observable_now),
        "",
        "### Current Physical Situation",
        "",
        _render_list(heroine.current_physical_situation),
        "",
        "### Recent Visible Exchange",
        "",
        _render_list(heroine.recent_visible_exchange),
        "",
        "### Voice / State / Relationship / Memory / Beliefs",
        "",
        _render_labeled_lists(
            [
                ("Voice", heroine.voice_rules),
                ("State", heroine.current_state),
                ("Relationship", heroine.relationship_temperature),
                ("Memory", heroine.memory_echo),
                ("Beliefs or Suspicions (heroine-side inference, not fact)", heroine.beliefs_or_suspicions),
            ]
        ),
        "",
        "### Reaction Patterns",
        "",
        _render_labeled_lists(
            [
                ("Immediate Reaction Priority", heroine.immediate_reaction_priority),
                ("Defense", heroine.defense_patterns),
                ("Embarrassment", heroine.embarrassment_patterns),
                ("Distance", heroine.distance_patterns),
            ]
        ),
        "",
        "### Can Say",
        "",
        _render_list(heroine.can_say),
        "",
        "### Must Not Say",
        "",
        _render_list(heroine.must_not_say),
        "",
        "## Pressure Context",
        "",
        "Pressure is not heroine knowledge.",
        "Pressure must be converted into observable situation, silence, gesture, hesitation, physical cue, or player-facing entrance.",
        "圧はヒロインの知識ではない。観測可能な状況・沈黙・所作・ためらい・物理手がかり・返せる入口へ変換して使う。",
        "",
        "### Pressure Source",
        "",
        f"- {pressure.source}",
        "",
        "### Player-Facing Entry",
        "",
        _render_list(pressure.player_facing_entry),
        "",
        "### Observable Pressure",
        "",
        _render_list(pressure.observable_pressure),
        "",
        "### Heroine Possible Initiative",
        "",
        _render_list(pressure.heroine_possible_initiative),
        "",
        "### Handles",
        "",
        _render_list(pressure.handles),
        "",
        "### If Ignored",
        "",
        _render_list(pressure.if_ignored),
        "",
        "### Next Visible Change",
        "",
        _render_list(pressure.next_visible_change),
        "",
        "### Pressure Conversion Rule",
        "",
        _render_list(pressure.must_convert_to_observable),
        "",
        "### Must Not Expose",
        "",
        _render_list(pressure.must_not_expose),
        "",
        "## GM Control Context",
        "",
        "GM-only.",
        "The heroine does not know this as written.",
        "Do not expose these labels or internal concepts in dialogue or narration.",
        "これはGM専用制御情報である。ヒロインはこの情報をこの形では知らない。",
        "本文では、圧、間、沈黙、観測可能な物理状況、次に返せる入口を整えるためだけに使う。",
        "",
        "### Active Hook",
        "",
        _render_list(gm.active_hook),
        "",
        "### Scene Function",
        "",
        _render_list(gm.scene_function),
        "",
        "### Relationship Stake",
        "",
        _render_list(gm.relationship_stake),
        "",
        "### Hidden Truth / Do Not Reveal",
        "",
        _render_labeled_lists(
            [
                ("Hidden Truth", gm.hidden_truth),
                ("Do Not Reveal", gm.do_not_reveal),
            ]
        ),
        "",
        "### Story Pressure",
        "",
        _render_list(gm.story_pressure),
        "",
        "### Next Hook",
        "",
        _render_list(gm.next_hook),
        "",
        "### Save Candidates",
        "",
        _render_list(gm.save_candidates),
        "",
        "### Forbidden Direct Terms",
        "",
        _render_list(gm.forbidden_direct_terms),
        "",
        "## Output Contract",
        "",
        "- The first beat must respond to the latest player-visible action or speech.",
        "- 最初の一拍は、必ずユーザーの直近の可視行動・発言への反応にする。",
        "- Do not start from event_card, scene function, relationship stake, hidden truth, next hook, or save candidate.",
        "- The heroine must speak only from Heroine Reply Context.",
        "- Use GM Control Context only to shape pacing, observable pressure, interruption, silence, or future affordance.",
        "- Convert pressure into observable situation, gesture, silence, physical cue, or heroine-like dialogue.",
        "- Leave one natural entrance the player can answer or act on.",
    ]
    if bundle.warnings:
        parts.extend(["", "## Bundle Warnings", "", _render_list(bundle.warnings)])
    return "\n".join(parts).rstrip() + "\n"


def parse_markdown_sections(markdown: str) -> dict[str, str]:
    """Return level-2 Markdown sections by their visible heading text."""

    matches = list(re.finditer(r"^##\s+(.+?)\s*$", markdown or "", re.MULTILINE))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        heading = match.group(1).strip()
        sections[heading] = markdown[start:end].strip()
    return sections


def extract_pressure_source(event_card_md: str) -> PressureSource:
    raw = extract_raw_pressure_source(event_card_md)
    if raw in VALID_PRESSURE_SOURCES:
        return cast(PressureSource, raw)
    return "none"


def extract_raw_pressure_source(event_card_md: str) -> str:
    sections = parse_markdown_sections(event_card_md)
    body = _section(sections, "Pressure / Agency")
    if not body:
        return ""
    match = re.search(r"pressure_source\s*[:：]\s*([A-Za-z0-9_-]+)", body)
    if match:
        return match.group(1).strip()
    return ""


def extract_event_card_context(event_card_md: str) -> tuple[PressureContext, GMControlContext]:
    sections = parse_markdown_sections(event_card_md)
    pressure_source = extract_pressure_source(event_card_md)
    reveal_control = _section(sections, "Knowledge Boundary / Reveal Control")
    truth_boundary = _section(sections, "Truth Hiding Boundary")

    pressure = PressureContext(
        source=pressure_source,
        player_facing_entry=_merge_lines(
            _section_lines(sections, "Player-Facing Entrance"),
            _section_lines(sections, "Visible Problem"),
            _section_lines(sections, "First Concrete Action"),
        ),
        observable_pressure=_section_lines(sections, "Observable Pressure"),
        heroine_possible_initiative=_section_lines(sections, "Heroine Initiative Candidate"),
        handles=_section_lines(sections, "Handles 2-4"),
        if_ignored=_section_lines(sections, "If Ignored"),
        next_visible_change=_section_lines(sections, "Next Visible Change"),
        must_convert_to_observable=_section_lines(sections, "Pressure Conversion Rule"),
        must_not_expose=[
            "pressure_source / scene function / relationship stake / hidden truth / next hook",
            "GM内部圧を管理語のまま本文へ出さない",
        ],
    )

    gm = GMControlContext(
        active_hook=_section_lines(sections, "Active Hook"),
        scene_function=_section_lines(sections, "Scene Function"),
        relationship_stake=_section_lines(sections, "Relationship Stake"),
        hidden_truth=_hidden_truth_lines(reveal_control) + _hidden_truth_lines(truth_boundary),
        story_pressure=_section_lines(sections, "Pressure / Agency"),
        next_hook=_section_lines(sections, "Next Hook"),
        save_candidates=_section_lines(sections, "Save Candidates"),
        do_not_reveal=_do_not_reveal_lines(reveal_control) + _do_not_reveal_lines(truth_boundary),
        forbidden_direct_terms=[
            "event_card",
            "scene function",
            "relationship stake",
            "hidden truth",
            "story_spine Background Truth",
            "next hook",
            "save candidate",
            "GM-only",
            "meta-system",
        ],
    )
    return pressure, gm


def extract_heroine_context(
    session_root: Path,
    latest_user_input: str,
) -> HeroineReplyContext:
    root = Path(session_root)
    latest_action, latest_inner = split_latest_user_input(latest_user_input)

    knowledge_md = read_text(root / "current/knowledge_state.md")
    heroine_known: list[str] = []
    shared: list[str] = []
    observable: list[str] = []
    beliefs_or_suspicions: list[str] = []
    must_not_say: list[str] = [
        "GM-only information",
        "meta-system information",
        "hidden truth / unrevealed truth",
        "scene function",
        "relationship stake",
        "next hook / save candidate",
    ]
    if knowledge_md.strip():
        report = assess_knowledge_boundary(knowledge_md)
        suspicion_values = {item.value for item in report.boundary.heroine_beliefs_or_suspicions}
        heroine_known = [
            item.value
            for item in report.boundary.heroine_known
            if item.fictional_status not in {"gm_only", "meta-system"} and item.value not in suspicion_values
        ]
        shared = [
            item.value
            for item in report.boundary.shared_facts
            if item.fictional_status not in {"gm_only", "meta-system"}
        ]
        observable = [
            item.value
            for item in report.boundary.observable_now
            if item.fictional_status not in {"gm_only", "meta-system"}
        ]
        beliefs_or_suspicions = [
            f"推測/疑い: {item.value}"
            for item in report.boundary.heroine_beliefs_or_suspicions
            if item.fictional_status not in {"gm_only", "meta-system"}
        ]

    scene_sections = parse_markdown_sections(read_text(root / "current/scene.md"))
    hotset_sections = parse_markdown_sections(read_text(root / "current/hotset.md"))
    relationship_overview_sections = parse_markdown_sections(
        read_text(root / "current/relationship_overview.md")
    )

    return HeroineReplyContext(
        latest_user_action=latest_action,
        latest_user_inner_monologue_gm_only=latest_inner,
        heroine_known_facts=_unique(heroine_known),
        shared_facts=_unique(shared),
        observable_now=_unique(observable),
        current_physical_situation=_merge_lines(
            _section_lines(scene_sections, "今いる場所"),
            _section_lines(scene_sections, "現在時刻または場面時間"),
            _section_lines(scene_sections, "今この場で見えているもの"),
            _section_lines(scene_sections, "今の場面"),
            _section_lines(scene_sections, "Player Orientation"),
        ),
        recent_visible_exchange=_merge_lines(
            _section_lines(scene_sections, "直前のやりとり"),
            _section_lines(hotset_sections, "最新scene後のecho"),
            _section_lines(hotset_sections, "現在のイベント要約"),
        ),
        voice_rules=_section_lines(parse_markdown_sections(read_text(root / "lilia/main/voice.md")), ""),
        current_state=_section_lines(parse_markdown_sections(read_text(root / "lilia/main/state.md")), ""),
        relationship_temperature=_merge_lines(
            _section_lines(parse_markdown_sections(read_text(root / "lilia/main/relationship.md")), ""),
            _section_lines(relationship_overview_sections, ""),
        ),
        memory_echo=_merge_lines(
            _section_lines(parse_markdown_sections(read_text(root / "lilia/main/memory.md")), ""),
            _section_lines(hotset_sections, "言い残し / まだ言っていないこと"),
        ),
        beliefs_or_suspicions=_merge_lines(
            beliefs_or_suspicions,
            _section_lines(parse_markdown_sections(read_text(root / "lilia/main/beliefs.md")), ""),
        ),
        immediate_reaction_priority=_merge_lines(
            _section_lines(hotset_sections, "次に会った時の第一反応"),
            ["latest user inputへの第一反応を最優先する"] if latest_action else [],
        ),
        defense_patterns=_keyword_lines(
            read_text(root / "lilia/main/voice.md") + "\n" + read_text(root / "lilia/main/state.md"),
            ("防御", "警戒", "拒否", "線引き", "守る"),
        ),
        embarrassment_patterns=_keyword_lines(
            read_text(root / "lilia/main/voice.md") + "\n" + read_text(root / "lilia/main/state.md"),
            ("照れ", "恥", "赤", "言い淀"),
        ),
        distance_patterns=_keyword_lines(
            read_text(root / "lilia/main/voice.md")
            + "\n"
            + read_text(root / "lilia/main/relationship.md"),
            ("距離", "呼び方", "沈黙", "近づ", "離れ"),
        ),
        can_say=_unique(shared + observable + heroine_known),
        must_not_say=_unique(must_not_say),
    )


def split_latest_user_input(latest_user_input: str) -> tuple[str, str]:
    text = latest_user_input.strip()
    if not text:
        return "", ""
    action_match = re.search(
        r"\[PLAYER_ACTION\]\s*(.*?)\s*\[END_PLAYER_ACTION\]",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    inner_match = re.search(
        r"\[PLAYER_INNER(?:_MONOLOGUE)?\]\s*(.*?)\s*\[END_PLAYER_INNER(?:_MONOLOGUE)?\]",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if action_match:
        return action_match.group(1).strip(), inner_match.group(1).strip() if inner_match else ""

    visible_lines: list[str] = []
    inner_lines: list[str] = []
    for line in text.splitlines():
        visible, inner = split_line_inner_monologue(line)
        inner_lines.extend(inner)
        if visible.strip():
            visible_lines.append(visible)
    return "\n".join(visible_lines).strip(), "\n".join(inner_lines).strip()


def split_line_inner_monologue(line: str) -> tuple[str, list[str]]:
    """Split line-leading inner monologue from visible player action."""

    rest = line
    inner: list[str] = []
    while True:
        match = re.match(r"^(\s*)[（(]([^）)]*)[）)](.*)$", rest)
        if not match:
            break
        inner_text = match.group(2).strip()
        if inner_text:
            inner.append(inner_text)
        rest = match.group(1) + match.group(3).lstrip()
    return rest, inner


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _merge_gm_context(
    gm: GMControlContext,
    *,
    hidden_truth: list[str] | None = None,
    story_pressure: list[str] | None = None,
    next_hook: list[str] | None = None,
    save_candidates: list[str] | None = None,
    do_not_reveal: list[str] | None = None,
) -> GMControlContext:
    return GMControlContext(
        active_hook=gm.active_hook,
        scene_function=gm.scene_function,
        relationship_stake=gm.relationship_stake,
        hidden_truth=_merge_lines(gm.hidden_truth, hidden_truth or []),
        story_pressure=_merge_lines(gm.story_pressure, story_pressure or []),
        next_hook=_merge_lines(gm.next_hook, next_hook or []),
        save_candidates=_merge_lines(gm.save_candidates, save_candidates or []),
        do_not_reveal=_merge_lines(gm.do_not_reveal, do_not_reveal or []),
        forbidden_direct_terms=gm.forbidden_direct_terms,
    )


def _story_spine_hidden_truth(story_spine_md: str) -> list[str]:
    sections = parse_markdown_sections(story_spine_md)
    return _merge_lines(
        _section_lines(sections, "Background Truth"),
        _section_lines(sections, "Background Truth GM Only"),
        _section_lines(sections, "Reveal Ladder"),
    )


def _story_pressure(story_spine_md: str, story_deck_md: str) -> list[str]:
    story_spine = parse_markdown_sections(story_spine_md)
    story_deck = parse_markdown_sections(story_deck_md)
    return _merge_lines(
        _section_lines(story_spine, "Pressure Direction"),
        _section_lines(story_deck, "Three Hook Spine"),
        _section_lines(story_deck, "Background Hooks"),
        _section_lines(story_deck, "Candidate Next Hooks"),
    )


def _story_next_hooks(event_card_md: str, story_deck_md: str) -> list[str]:
    event_card = parse_markdown_sections(event_card_md)
    story_deck = parse_markdown_sections(story_deck_md)
    return _merge_lines(
        _section_lines(event_card, "Next Hook"),
        _section_lines(story_deck, "Candidate Next Hook"),
        _section_lines(story_deck, "Candidate Next Hooks"),
    )


def _story_save_candidates(story_spine_md: str, story_deck_md: str) -> list[str]:
    story_spine = parse_markdown_sections(story_spine_md)
    story_deck = parse_markdown_sections(story_deck_md)
    return _merge_lines(
        _section_lines(story_spine, "Save Candidates"),
        _section_lines(story_deck, "Story Residue Candidates"),
    )


def _section(sections: dict[str, str], heading: str) -> str:
    if not heading:
        return "\n\n".join(sections.values()).strip()
    target = _normalize_heading(heading)
    for key, body in sections.items():
        if _normalize_heading(key) == target:
            return body
    return ""


def _section_lines(sections: dict[str, str], heading: str) -> list[str]:
    return _meaningful_lines(_section(sections, heading))


def _normalize_heading(heading: str) -> str:
    heading = re.sub(r"\s+-\s+.*$", "", heading.strip())
    heading = re.sub(r"\s*\(.+?\)\s*", "", heading)
    return re.sub(r"\s+", " ", heading).lower()


def _meaningful_lines(text: str) -> list[str]:
    lines: list[str] = []
    pending_label: str | None = None
    for raw_line in (text or "").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("```"):
            continue
        stripped = re.sub(r"^\s*[-*]\s*", "", stripped).strip()
        if _placeholder_value(stripped):
            continue
        label_match = re.match(r"^([^:：]{1,80})[:：]\s*(.*)$", stripped)
        if label_match:
            label = label_match.group(1).strip()
            value = label_match.group(2).strip()
            if value and not _placeholder_value(value):
                lines.append(f"{label}: {value}")
                pending_label = None
            else:
                pending_label = label
            continue
        if pending_label:
            lines.append(f"{pending_label}: {stripped}")
            pending_label = None
        else:
            lines.append(stripped)
    return _unique(lines)


def _placeholder_value(value: str) -> bool:
    normalized = re.sub(r"\s+", "", value.strip().lower())
    return normalized in {"", "-", "未設定", "todo", "placeholder", "n/a", "none"}


def _hidden_truth_lines(section: str) -> list[str]:
    lines = _meaningful_lines(section)
    selected = [
        line
        for line in lines
        if re.search(r"hidden|truth|真相|隠してよい|gmだけ|知らない|言語化できない", line, re.IGNORECASE)
    ]
    return selected or []


def _do_not_reveal_lines(section: str) -> list[str]:
    lines = _meaningful_lines(section)
    return [
        line
        for line in lines
        if re.search(r"do-not-reveal|do not reveal|まだ|未開示|隠して|書かない|言わせない", line, re.IGNORECASE)
    ]


def _keyword_lines(text: str, keywords: tuple[str, ...]) -> list[str]:
    return [
        line
        for line in _meaningful_lines(text)
        if any(keyword.lower() in line.lower() for keyword in keywords)
    ][:8]


def _heroine_initiative_has_basis(pressure: PressureContext, heroine: HeroineReplyContext) -> bool:
    joined = "\n".join(pressure.heroine_possible_initiative).lower()
    if any(token in joined for token in ["state", "relationship", "memory", "beliefs", "根拠"]):
        return True
    return bool(
        heroine.current_state
        or heroine.relationship_temperature
        or heroine.memory_echo
        or heroine.beliefs_or_suspicions
    )


def _merge_lines(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    for group in groups:
        merged.extend(group)
    return _unique(merged)


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        text = re.sub(r"\s+", " ", str(item or "")).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _render_value(value: str) -> str:
    return value.strip() or "- (none)"


def _render_list(items: list[str]) -> str:
    if not items:
        return "- (none)"
    return "\n".join(f"- {item}" for item in items)


def _render_labeled_lists(groups: list[tuple[str, list[str]]]) -> str:
    lines: list[str] = []
    for label, items in groups:
        lines.append(f"- {label}:")
        if items:
            lines.extend(f"  - {item}" for item in items)
        else:
            lines.append("  - (none)")
    return "\n".join(lines)
