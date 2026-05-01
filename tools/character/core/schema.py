"""
Minimal character YAML schema for LILIA persona material.

The generated YAML is not the LILIA source of truth. It is an external
character-material layer that is converted into lilia/main/profile.md before
the first scene.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class ToneExample(BaseModel):
    user: str = ""
    char: str

    @field_validator("user", "char", mode="before")
    @classmethod
    def stringify(cls, value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()


class Tone(BaseModel):
    rule: str
    examples: list[ToneExample] = Field(default_factory=list)

    @field_validator("rule", mode="before")
    @classmethod
    def normalize_rule(cls, value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @field_validator("examples", mode="before")
    @classmethod
    def normalize_examples(cls, value: Any) -> list[Any]:
        if value is None:
            return []
        if not isinstance(value, list):
            return [{"user": "", "char": str(value)}]

        normalized: list[Any] = []
        for item in value:
            if isinstance(item, str):
                normalized.append({"user": "", "char": item})
            elif isinstance(item, dict):
                normalized.append(item)
        return normalized


class Appearance(BaseModel):
    hair_style: str | None = None
    hair_color: str | None = None
    notes: str | None = None

    @field_validator("hair_style", "hair_color", "notes", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None


class Context(BaseModel):
    backstory: str | None = None
    current_situation: str | None = None

    @field_validator("backstory", "current_situation", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None


class CharacterSheet(BaseModel):
    name: str
    age: int | None = None
    occupation: str | None = None
    appearance: Appearance = Field(default_factory=Appearance)
    tone: Tone = Field(default_factory=lambda: Tone(rule=""))
    personality: list[str] = Field(default_factory=list)
    reactions: dict[str, str] = Field(default_factory=dict)
    forbidden: list[str] = Field(default_factory=list)
    context: Context = Field(default_factory=Context)

    @field_validator("name", "occupation", mode="before")
    @classmethod
    def normalize_text(cls, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @field_validator("age", mode="before")
    @classmethod
    def normalize_age(cls, value: Any) -> int | None:
        if value is None or value == "":
            return None
        if isinstance(value, int):
            return value
        digits = "".join(ch for ch in str(value) if ch.isdigit())
        return int(digits) if digits else None

    @field_validator("personality", "forbidden", mode="before")
    @classmethod
    def normalize_list(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        if not isinstance(value, list):
            return [str(value).strip()]
        return [str(item).strip() for item in value if str(item).strip()]

    @field_validator("reactions", mode="before")
    @classmethod
    def normalize_reactions(cls, value: Any) -> dict[str, str]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            return {"反応": str(value).strip()}
        return {
            str(key).strip(): str(reaction).strip()
            for key, reaction in value.items()
            if str(key).strip() and str(reaction).strip()
        }

    @model_validator(mode="after")
    def check_required_content(self) -> "CharacterSheet":
        if not self.name:
            raise ValueError("name is required")
        if not self.tone.rule:
            raise ValueError(f"[{self.name}] tone.rule is required")
        if not self.personality:
            raise ValueError(f"[{self.name}] personality must not be empty")
        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CharacterSheet":
        return cls.model_validate(data)

