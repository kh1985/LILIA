"""Knowledge boundary helpers for LILIA session state.

This module keeps the "who knows what" rules small and reusable. It does not
write session files and does not decide story content by itself; callers use it
to classify and validate ``current/knowledge_state.md`` before generation,
validation, save, or resume work.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


GM = "GM"
PLAYER = "protagonist"
HEROINE = "heroine"

REQUIRED_FIELDS = {
    "key",
    "value",
    "fictional_status",
    "source",
    "known_to",
    "acquired_at",
    "weight",
}

VALID_STATUSES = {
    "meta",
    "observable",
    "shared",
    "gm_only",
    "meta-system",
}

VALID_WEIGHTS = {
    "low",
    "medium",
    "high",
}

SUSPICION_PATTERNS = (
    "疑",
    "推測",
    "仮説",
    "誤解",
    "可能性",
    "未確定",
    "察し",
)


@dataclass(frozen=True)
class KnowledgeItem:
    key: str
    value: str
    fictional_status: str
    source: str
    known_to: tuple[str, ...]
    acquired_at: str
    weight: str
    notes: str = ""

    def known_by(self, actor: str) -> bool:
        return actor in self.known_to


@dataclass(frozen=True)
class KnowledgeBoundary:
    items: tuple[KnowledgeItem, ...]
    gm_truth: tuple[KnowledgeItem, ...]
    player_known: tuple[KnowledgeItem, ...]
    heroine_known: tuple[KnowledgeItem, ...]
    shared_facts: tuple[KnowledgeItem, ...]
    observable_now: tuple[KnowledgeItem, ...]
    do_not_reveal_yet: tuple[KnowledgeItem, ...]
    heroine_beliefs_or_suspicions: tuple[KnowledgeItem, ...]


@dataclass(frozen=True)
class KnowledgeBoundaryReport:
    boundary: KnowledgeBoundary
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def assess_knowledge_boundary(markdown: str) -> KnowledgeBoundaryReport:
    """Parse, classify, and lightly validate ``knowledge_state.md`` content."""

    items, parse_errors = parse_knowledge_items(markdown)
    errors = list(parse_errors)
    warnings: list[str] = []

    for item in items:
        if item.fictional_status not in VALID_STATUSES:
            warnings.append(f"{item.key}: unknown fictional_status: {item.fictional_status}")
        if item.weight and item.weight not in VALID_WEIGHTS:
            warnings.append(f"{item.key}: unknown weight: {item.weight}")
        if item.fictional_status == "gm_only" and item.known_to != (GM,):
            errors.append(f"{item.key}: gm_only must be known_to [GM]")
        if item.fictional_status == "meta-system" and item.known_to != (GM,):
            errors.append(f"{item.key}: meta-system must be known_to [GM]")
        if item.fictional_status == "shared" and not (
            item.known_by(PLAYER) and item.known_by(HEROINE)
        ):
            warnings.append(f"{item.key}: shared should include protagonist and heroine")
        if not item.known_to:
            errors.append(f"{item.key}: known_to is empty")

    boundary = build_knowledge_boundary(items)
    if items and not boundary.gm_truth:
        warnings.append("knowledge_state has no GM-only truth/reveal item")
    if items and not boundary.player_known:
        warnings.append("knowledge_state has no player-known item")
    if items and not boundary.heroine_known:
        warnings.append("knowledge_state has no heroine-known item")
    if items and not (boundary.shared_facts or boundary.observable_now):
        warnings.append("knowledge_state has no shared or observable player-facing item")

    return KnowledgeBoundaryReport(
        boundary=boundary,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def build_knowledge_boundary(items: list[KnowledgeItem]) -> KnowledgeBoundary:
    normalized = tuple(items)
    return KnowledgeBoundary(
        items=normalized,
        gm_truth=tuple(item for item in normalized if _is_gm_truth(item)),
        player_known=tuple(item for item in normalized if item.known_by(PLAYER)),
        heroine_known=tuple(item for item in normalized if item.known_by(HEROINE)),
        shared_facts=tuple(
            item for item in normalized if item.known_by(PLAYER) and item.known_by(HEROINE)
        ),
        observable_now=tuple(item for item in normalized if item.fictional_status == "observable"),
        do_not_reveal_yet=tuple(item for item in normalized if _is_do_not_reveal_yet(item)),
        heroine_beliefs_or_suspicions=tuple(
            item for item in normalized if _is_heroine_belief_or_suspicion(item)
        ),
    )


def parse_knowledge_items(markdown: str) -> tuple[list[KnowledgeItem], list[str]]:
    block = extract_knowledge_yaml_block(markdown)
    if not block.strip():
        return [], ["knowledge_state YAML block is missing"]

    parsed, error = _parse_yaml_block(block)
    if error:
        return [], [error]

    raw_items = parsed.get("items") if isinstance(parsed, dict) else None
    if not isinstance(raw_items, list):
        return [], ["knowledge_state YAML has no items list"]

    items: list[KnowledgeItem] = []
    errors: list[str] = []
    for index, raw_item in enumerate(raw_items, start=1):
        if not isinstance(raw_item, dict):
            errors.append(f"item {index}: must be a mapping")
            continue

        missing = sorted(field for field in REQUIRED_FIELDS if field not in raw_item)
        key = str(raw_item.get("key") or f"item_{index}")
        if missing:
            errors.append(f"{key}: missing field(s): {', '.join(missing)}")
            continue

        items.append(
            KnowledgeItem(
                key=_string(raw_item.get("key")),
                value=_string(raw_item.get("value")),
                fictional_status=_string(raw_item.get("fictional_status")),
                source=_string(raw_item.get("source")),
                known_to=tuple(_known_to(raw_item.get("known_to"))),
                acquired_at=_string(raw_item.get("acquired_at")),
                weight=_string(raw_item.get("weight")),
                notes=_string(raw_item.get("notes")),
            )
        )

    return items, errors


def extract_knowledge_yaml_block(markdown: str) -> str:
    knowledge_match = re.search(
        r"^##\s+knowledge_state\s*$.*?```(?:yaml)?\s*\n(.*?)\n```",
        markdown,
        flags=re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    if knowledge_match:
        return knowledge_match.group(1)

    for match in re.finditer(r"```(?:yaml)?\s*\n(.*?)\n```", markdown, re.DOTALL | re.IGNORECASE):
        block = match.group(1)
        if re.search(r"^\s*items\s*:", block, re.MULTILINE):
            return block
    return ""


def _parse_yaml_block(block: str) -> tuple[dict[str, Any], str]:
    try:
        import yaml

        parsed = yaml.safe_load(block)
        return (parsed if isinstance(parsed, dict) else {}, "") if parsed is not None else ({}, "")
    except ModuleNotFoundError:
        parsed = _parse_knowledge_yaml_minimal(block)
        return (parsed, "") if parsed else ({}, "knowledge_state YAML block is not parseable")
    except Exception as exc:
        return {}, f"knowledge_state YAML block is not parseable: {exc}"


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


def _known_to(raw: Any) -> list[str]:
    if isinstance(raw, list):
        return [_string(item) for item in raw if _string(item)]
    value = _string(raw)
    if not value:
        return []
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    return [part.strip().strip('"').strip("'") for part in value.split(",") if part.strip()]


def _string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _is_gm_truth(item: KnowledgeItem) -> bool:
    return item.fictional_status == "gm_only" or (
        item.known_to == (GM,) and item.source == "story_spine"
    )


def _is_do_not_reveal_yet(item: KnowledgeItem) -> bool:
    return item.fictional_status in {"gm_only", "meta-system"} or (
        item.known_to == (GM,) and not item.known_by(PLAYER) and not item.known_by(HEROINE)
    )


def _is_heroine_belief_or_suspicion(item: KnowledgeItem) -> bool:
    if not item.known_by(HEROINE):
        return False
    if item.source == "inferred":
        return True
    text = f"{item.value} {item.notes}"
    return any(pattern in text for pattern in SUSPICION_PATTERNS)
