"""Dependency-free fallback schema for character YAML material.

This exists only for environments without pydantic. The normal runtime uses
``tools.character.core.schema``; this fallback keeps the LLM YAML bridge usable
without depending on the retired profile template script.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re


@dataclass
class ToneExample:
    user: str = ""
    char: str = ""


@dataclass
class Tone:
    rule: str = ""
    examples: list[ToneExample] = field(default_factory=list)


@dataclass
class Appearance:
    hair_style: str | None = None
    hair_color: str | None = None
    eye_color: str | None = None
    body: str | None = None
    outfit: str | None = None
    notes: str | None = None


@dataclass
class Context:
    backstory: str | None = None
    current_situation: str | None = None


@dataclass
class CharacterSheet:
    name: str
    age: int | None = None
    occupation: str | None = None
    appearance: Appearance = field(default_factory=Appearance)
    tone: Tone = field(default_factory=Tone)
    personality: list[str] = field(default_factory=list)
    reactions: dict[str, str] = field(default_factory=dict)
    forbidden: list[str] = field(default_factory=list)
    context: Context = field(default_factory=Context)

    @classmethod
    def from_dict(cls, data: dict) -> "CharacterSheet":
        tone_data = data.get("tone") if isinstance(data.get("tone"), dict) else {}
        examples = tone_data.get("examples") if isinstance(tone_data, dict) else []
        if not isinstance(examples, list):
            examples = [{"char": str(examples)}]
        appearance_data = data.get("appearance") if isinstance(data.get("appearance"), dict) else {}
        context_data = data.get("context") if isinstance(data.get("context"), dict) else {}
        reactions = data.get("reactions") if isinstance(data.get("reactions"), dict) else {}
        personality = data.get("personality") if isinstance(data.get("personality"), list) else []
        forbidden = data.get("forbidden") if isinstance(data.get("forbidden"), list) else []
        age = _parse_age(data.get("age"))
        name = str(data.get("name") or "").strip()
        tone_rule = str(tone_data.get("rule") or "").strip()
        personality = [str(item).strip() for item in personality if str(item).strip()]
        if not name:
            raise ValueError("name is required")
        if not tone_rule:
            raise ValueError(f"[{name}] tone.rule is required")
        if not personality:
            raise ValueError(f"[{name}] personality must not be empty")
        return cls(
            name=name,
            age=age,
            occupation=str(data.get("occupation") or "").strip() or None,
            appearance=Appearance(
                hair_style=str(appearance_data.get("hair_style") or "").strip() or None,
                hair_color=str(appearance_data.get("hair_color") or "").strip() or None,
                eye_color=str(appearance_data.get("eye_color") or "").strip() or None,
                body=str(appearance_data.get("body") or "").strip() or None,
                outfit=str(appearance_data.get("outfit") or "").strip() or None,
                notes=str(appearance_data.get("notes") or "").strip() or None,
            ),
            tone=Tone(
                rule=tone_rule,
                examples=[
                    ToneExample(
                        user=str(item.get("user") or "").strip() if isinstance(item, dict) else "",
                        char=str(item.get("char") or item).strip() if isinstance(item, dict) else str(item).strip(),
                    )
                    for item in examples
                ],
            ),
            personality=personality,
            reactions={str(key).strip(): str(value).strip() for key, value in reactions.items()},
            forbidden=[str(item).strip() for item in forbidden if str(item).strip()],
            context=Context(
                backstory=str(context_data.get("backstory") or "").strip() or None,
                current_situation=str(context_data.get("current_situation") or "").strip() or None,
            ),
        )

    def model_dump(self, exclude_none: bool = False) -> dict:
        data = {
            "name": self.name,
            "age": self.age,
            "occupation": self.occupation,
            "appearance": {
                "hair_style": self.appearance.hair_style,
                "hair_color": self.appearance.hair_color,
                "eye_color": self.appearance.eye_color,
                "body": self.appearance.body,
                "outfit": self.appearance.outfit,
                "notes": self.appearance.notes,
            },
            "tone": {
                "rule": self.tone.rule,
                "examples": [example.__dict__ for example in self.tone.examples],
            },
            "personality": self.personality,
            "reactions": self.reactions,
            "forbidden": self.forbidden,
            "context": {
                "backstory": self.context.backstory,
                "current_situation": self.context.current_situation,
            },
        }
        if not exclude_none:
            return data
        return json.loads(
            json.dumps(data, ensure_ascii=False),
            object_hook=lambda obj: {key: value for key, value in obj.items() if value is not None},
        )


def load_simple_character_yaml(path: Path) -> dict:
    """Parse the compact character YAML shape without PyYAML."""

    data: dict[str, object] = {}
    current_top = ""
    current_example: dict[str, str] | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 0:
            current_example = None
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            current_top = key.strip()
            if value.strip():
                data[current_top] = _parse_simple_yaml_scalar(value)
            elif current_top in {"appearance", "tone", "context", "reactions"}:
                data[current_top] = {}
            elif current_top in {"personality", "forbidden"}:
                data[current_top] = []
            else:
                data[current_top] = {}
            continue

        if not current_top:
            continue

        if current_top in {"personality", "forbidden"} and line.startswith("- "):
            data.setdefault(current_top, [])
            assert isinstance(data[current_top], list)
            data[current_top].append(str(_parse_simple_yaml_scalar(line[2:]) or ""))
            continue

        if current_top in {"appearance", "context", "reactions"} and ":" in line:
            key, value = line.split(":", 1)
            data.setdefault(current_top, {})
            assert isinstance(data[current_top], dict)
            data[current_top][key.strip()] = _parse_simple_yaml_scalar(value)
            continue

        if current_top == "tone":
            data.setdefault("tone", {})
            assert isinstance(data["tone"], dict)
            if indent == 2 and ":" in line and not line.startswith("- "):
                key, value = line.split(":", 1)
                key = key.strip()
                if key == "examples":
                    data["tone"]["examples"] = []
                else:
                    data["tone"][key] = _parse_simple_yaml_scalar(value)
                continue
            if line.startswith("- "):
                item = line[2:]
                current_example = {}
                data["tone"].setdefault("examples", [])
                assert isinstance(data["tone"]["examples"], list)
                data["tone"]["examples"].append(current_example)
                if ":" in item:
                    key, value = item.split(":", 1)
                    current_example[key.strip()] = str(_parse_simple_yaml_scalar(value) or "")
                else:
                    current_example["char"] = str(_parse_simple_yaml_scalar(item) or "")
                continue
            if current_example is not None and ":" in line:
                key, value = line.split(":", 1)
                current_example[key.strip()] = str(_parse_simple_yaml_scalar(value) or "")

    return data


def _parse_simple_yaml_scalar(value: str) -> str | int | None:
    clean = value.strip()
    if clean in {"", "null", "None", "~"}:
        return None
    if re.fullmatch(r"\d+", clean):
        return int(clean)
    return clean.strip("'\"")


def _parse_age(value: object) -> int | None:
    if value is None or value == "":
        return None
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    return int(digits) if digits else None
