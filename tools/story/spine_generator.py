"""AI bridge for generating LILIA story and relationship spine markdown."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MAX_ATTEMPTS = 3


class SpineGenerationError(RuntimeError):
    """Raised when the AI spine generator cannot produce valid markdown."""


def generate_story_and_relationship_spine(answers: dict, character_yaml: dict, engine: str) -> dict:
    """Generate validated story_spine.md and relationship_spine.md content."""

    if not isinstance(answers, dict):
        raise SpineGenerationError("answers must be a dict")
    if not isinstance(character_yaml, dict):
        raise SpineGenerationError("character_yaml must be a dict")

    candidates = _engine_candidates(engine)
    references = _load_sanitized_references()
    previous_error = ""
    q1_text = _answer_text(answers, 1)
    cli_failures: list[str] = []

    for attempt_index in range(MAX_ATTEMPTS):
        prompt = _build_generation_prompt(
            answers=answers,
            character_yaml=character_yaml,
            references=references,
            attempt_index=attempt_index,
            previous_error=previous_error,
        )

        raw_output = ""
        engine_used = ""
        for candidate_engine in candidates:
            try:
                raw_output = _run_engine(candidate_engine, prompt)
                engine_used = candidate_engine
                break
            except SpineGenerationError as exc:
                cli_failures.append(f"{candidate_engine}: {exc}")
                if engine != "auto":
                    raise
        if not raw_output or not engine_used:
            detail = "; ".join(cli_failures[-4:]) or "no engine produced output"
            raise SpineGenerationError(f"story spine generation could not start: {detail}")

        try:
            parsed = _parse_generation_output(raw_output)
            _validate_spine_output(parsed, q1_text=q1_text)
            parsed["engine_used"] = engine_used
            parsed["validation_retry_count"] = attempt_index
            return parsed
        except SpineGenerationError as exc:
            previous_error = str(exc)

    raise SpineGenerationError(
        "story spine generation failed after 3 attempts: "
        + (previous_error or "unknown validation error")
    )


def _engine_candidates(engine: str) -> list[str]:
    if engine not in {"codex", "claude", "auto"}:
        raise SpineGenerationError("engine must be one of: codex, claude, auto")
    if engine == "auto":
        return ["codex", "claude"]
    return [engine]


def _answer_text(answers: dict, number: int) -> str:
    keys = (
        number,
        str(number),
        f"q{number}",
        f"Q{number}",
        f"Q{number}.",
    )
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


def _build_engine_command(engine: str, prompt: str) -> tuple[list[str], str | None]:
    if engine == "claude":
        return ["claude", "-p", prompt], None
    if engine == "codex":
        return [
            "codex",
            "exec",
            "--cd",
            str(ROOT),
            "--sandbox",
            "read-only",
            "--color",
            "never",
            "-",
        ], prompt
    raise SpineGenerationError(f"unsupported engine: {engine}")


def _run_engine(engine: str, prompt: str) -> str:
    command, stdin_text = _build_engine_command(engine, prompt)
    env = os.environ.copy()

    try:
        result = subprocess.run(
            command,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
    except FileNotFoundError as exc:
        raise SpineGenerationError(f"{engine} command was not found") from exc
    except subprocess.TimeoutExpired as exc:
        raise SpineGenerationError(f"{engine} generation timed out after 120 seconds") from exc

    if result.returncode != 0:
        stderr = result.stderr.strip() or "(no stderr)"
        raise SpineGenerationError(f"{engine} CLI failed: {stderr}")
    if not result.stdout.strip():
        raise SpineGenerationError(f"{engine} CLI returned empty output")
    return result.stdout


def _load_sanitized_references() -> dict[str, str]:
    return {
        "story_pattern_stock": _sanitize_reference(
            (ROOT / "references" / "story_pattern_stock.md").read_text(encoding="utf-8")
        ),
        "story_structure_stock": _sanitize_reference(
            (ROOT / "references" / "story_structure_stock.md").read_text(encoding="utf-8")
        ),
    }


def _sanitize_reference(text: str) -> str:
    """Remove concrete works and example blocks while preserving abstract structure."""

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

        if stripped.startswith("**観察される作品**"):
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


def _is_concrete_reference_heading(heading_text: str) -> bool:
    return any(
        marker in heading_text
        for marker in [
            "当てはめ例",
            "例",
            "出典",
        ]
    )


def _looks_like_concrete_example_line(line: str) -> bool:
    return bool(
        re.match(r"^-+\s*\[?(ヒロイン|ユーザー|主人公)", line)
        or re.match(r"^####\s*\[?ヒロイン", line)
        or re.match(r"^-+\s*厚い防壁", line)
        or re.match(r"^-+\s*静かな日常", line)
        or re.match(r"^-+\s*大きな転機", line)
    )


def _contains_reference_work_observation(line: str) -> bool:
    if "（" in line and "）" in line and any(token in line for token in ["Before", "Normal", "Monster"]):
        return True
    return False


def _build_generation_prompt(
    *,
    answers: dict,
    character_yaml: dict,
    references: dict[str, str],
    attempt_index: int,
    previous_error: str,
) -> str:
    answers_json = json.dumps(answers, ensure_ascii=False, indent=2, default=str)
    character_json = json.dumps(character_yaml, ensure_ascii=False, indent=2, sort_keys=True, default=str)

    retry_block = ""
    if previous_error:
        retry_block = f"""
## 前回の失敗

以下の理由で検証に失敗しました。今回の出力では必ず直してください。

{previous_error}
"""

    return f"""あなたはLILIA用のStory Spine / Relationship Spine生成補助です。
Q&A回答とcharacter YAMLから、`current/story_spine.md` と `story/relationship_spine.md` の初期Markdownを生成してください。

LILIAは、ユーザーとの会話・選択・物語を記憶し、関係性と人格の出方が少しずつ変化していくAI恋愛シミュレーションです。
ストーリーは主役ではなく、LILIAの人格、記憶、信頼、距離感、声、境界線、beliefsを変化させる装置として扱います。
LILIAを所有物、攻略対象、ユーザーに都合よく最適化される存在として扱わないでください。

## Example Anchoring Control

- 例文や参照棚の語彙を、そのまま人格・設定・出来事に固定しない。
- ユーザー回答とcharacter YAMLを最優先する。
- 曖昧な要素は例で補完せず、未確定または仮置きとして扱う。
- 作品名、参照作品の固有名詞、台詞、人物配置、展開順を出力に入れない。
- pattern / structure はGM内部の選択情報としてだけ使う。作中本文ではない。

## 参照棚の扱い

下のreferenceは、作品名の観察行と具体例を取り除いたサニタイズ済み抽象メモです。
感情の骨、選択の力学、関係の形だけを使ってください。

### story_pattern_stock（sanitized）

{references["story_pattern_stock"]}

### story_structure_stock（sanitized）

{references["story_structure_stock"]}

## 入力: Q&A answers

```json
{answers_json}
```

## 入力: character YAML material

```json
{character_json}
```

## 生成ルール

1. `story_pattern_stock` から1〜2パターンだけ選ぶ。3個以上は選ばない。
2. `story_structure_stock` から1構造だけ選ぶ。
3. 選んだ理由は、ユーザー回答・character YAML・関係の温度に紐づけて短く書く。
4. `story_spine.md` は、Main Question / Reveal Ladder / Background Truth / Pressure Direction / Prize / Heroine Tie / if ignored / Drift Guard を持つ。
5. `relationship_spine.md` は、育てたいテーマ / 最初の摩擦 / LILIAが守るもの / LILIAが避けるもの / ユーザー側に問うこと / 関係が変化する方向 を持つ。
6. Q5を必ず「傷」に押し込めない。癖、特徴、職業的なもの、葛藤、好きなもの、保留として扱ってよい。
7. 初回から恋愛成立、親密成立、好意確定、ベッドシーン確定にしない。
8. AFFINITY、bond、好感度、攻略、ハーレム、ルートという語彙を出さない。
9. `story_spine.md` と `relationship_spine.md` の責務を混ぜない。
10. 出力全体をコードフェンスで囲まない。

## 出力フォーマット

必ず次の3セクションだけを、この順番で出力してください。

## 選択
selected_pattern: P番号とパターン名。2個の場合はカンマ区切り。
selected_structure: 構造名
selection_reason: 1-3文。作品名や参照作品の固有名詞は出さない。

## story_spine.md
# Story Spine

## Main Question
（1行。「○○は△△できるか」の形）

## Reveal Ladder
1. [pending] （第1段階で表面に出る具体内容）
2. [pending] （第2段階で見え始める具体内容）
3. [pending] （第3段階で核に近づく具体内容）

## Background Truth (GM only)
（GM内部資料。仮説でよいので具体内容を書く）

## Pressure Direction
- [standing] （状況から来る圧1）
- [standing] （状況から来る圧2）
- [standing] （状況から来る圧3）

## Prize
（達成された場合に得られる関係または状態）

## Heroine Tie
- 生活: （生活に刺さる点）
- 秘密: （秘密に刺さる点）
- 境界: （境界に刺さる点）
- 感情: （感情に刺さる点）

## if ignored
- （放置された場合の具体的変化1）
- （放置された場合の具体的変化2）
- （放置された場合の具体的変化3）

## Drift Guard
- （物名1） - （ブレた時に戻る焦点1）
- （物名2） - （ブレた時に戻る焦点2）
- （物名3） - （ブレた時に戻る焦点3）

## relationship_spine.md
# Relationship Spine

## 育てたいテーマ
（1-3文）

## 最初の摩擦
（1-3文）

## LILIAが守るもの
（1-3文）

## LILIAが避けるもの
（1-3文）

## ユーザー側に問うこと
（1-3文）

## 関係が変化する方向
（1-3文）

重要:
- Reveal Ladder の3行は必ず `[pending]` で始める。
- Pressure Direction の3行は必ず `[standing]` で始める。
- if ignored と Drift Guard は必ず `- ` で始める箇条書きにする。
- Drift Guard は必ず `物名 - 焦点` の形にする。

{retry_block}
attempt: {attempt_index + 1}/{MAX_ATTEMPTS}
"""


def _parse_generation_output(text: str) -> dict[str, Any]:
    sections = _extract_known_sections(text)
    missing = [name for name in ["選択", "story_spine.md", "relationship_spine.md"] if not sections.get(name)]
    if missing:
        raise SpineGenerationError("missing required sections: " + ", ".join(missing))

    selected_pattern, selected_structure, selection_reason = _parse_selection_section(sections["選択"])
    story_spine = _strip_outer_fence(sections["story_spine.md"]).strip()
    relationship_spine = _strip_outer_fence(sections["relationship_spine.md"]).strip()

    if not story_spine:
        raise SpineGenerationError("story_spine.md section is empty")
    if not relationship_spine:
        raise SpineGenerationError("relationship_spine.md section is empty")

    return {
        "story_spine": story_spine,
        "relationship_spine": relationship_spine,
        "story_spine_md": story_spine,
        "relationship_spine_md": relationship_spine,
        "selected_pattern": selected_pattern,
        "selected_structure": selected_structure,
        "selection_reason": selection_reason,
    }


def _extract_known_sections(text: str) -> dict[str, str]:
    marker_re = re.compile(r"^##\s*(選択|story_spine\.md|relationship_spine\.md)\s*$", re.MULTILINE)
    matches = list(marker_re.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        name = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[name] = text[start:end].strip()
    return sections


def _parse_selection_section(section: str) -> tuple[list[str], str, str]:
    values = {
        "selected_pattern": "",
        "selected_structure": "",
        "selection_reason": "",
    }
    aliases = {
        "selected_pattern": {"selected_pattern", "pattern", "パターン", "選択パターン"},
        "selected_structure": {"selected_structure", "structure", "構造", "選択構造"},
        "selection_reason": {"selection_reason", "reason", "理由", "選択理由"},
    }

    for raw_line in section.splitlines():
        line = raw_line.strip().lstrip("-").strip()
        if not line or ":" not in line and "：" not in line:
            continue
        key, value = re.split(r"[:：]", line, maxsplit=1)
        normalized_key = key.strip()
        clean_value = value.strip()
        for target_key, names in aliases.items():
            if normalized_key in names and clean_value:
                values[target_key] = clean_value

    if not values["selection_reason"]:
        free_text = " ".join(line.strip() for line in section.splitlines() if line.strip())
        values["selection_reason"] = free_text[:300]

    missing = [key for key, value in values.items() if not value]
    if missing:
        raise SpineGenerationError("selection section is missing fields: " + ", ".join(missing))
    selected_patterns = _selected_pattern_ids(values["selected_pattern"])
    if not selected_patterns:
        raise SpineGenerationError("selection section is missing P-number pattern ids")
    if len(selected_patterns) > 2:
        raise SpineGenerationError("selection section selected more than 2 patterns")
    return selected_patterns, values["selected_structure"], values["selection_reason"]


def _selected_pattern_ids(text: str) -> list[str]:
    ids: list[str] = []
    for match in re.findall(r"P\s*(\d{1,2})", text, flags=re.IGNORECASE):
        item = f"P{int(match)}"
        if item not in ids:
            ids.append(item)
    return ids


def _strip_outer_fence(text: str) -> str:
    stripped = text.strip()
    match = re.match(r"^```(?:markdown|md)?\s*(.*?)\s*```$", stripped, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    return text


def _validate_spine_output(parsed: dict[str, Any], q1_text: str) -> None:
    try:
        from tools.story.spine_validator import validate_spine_output
    except ModuleNotFoundError as exc:
        if exc.name == "tools.story.spine_validator":
            raise SpineGenerationError(
                "tools.story.spine_validator.validate_spine_output is unavailable"
            ) from exc
        raise

    valid, errors = validate_spine_output(
        story_spine_md=parsed["story_spine"],
        relationship_spine_md=parsed["relationship_spine"],
        pattern_stock_path=ROOT / "references" / "story_pattern_stock.md",
        media_stock_path=ROOT / "references" / "story_media_stock.md",
        q1_text=q1_text,
    )
    if not valid:
        raise SpineGenerationError("validator issues: " + _stringify_issues(errors))


def _stringify_issues(issues: Any) -> str:
    if issues is None:
        return ""
    if isinstance(issues, str):
        return issues
    if isinstance(issues, dict):
        return json.dumps(issues, ensure_ascii=False, sort_keys=True, default=str)
    if isinstance(issues, (list, tuple, set)):
        return "; ".join(_stringify_issues(issue) for issue in issues if issue)
    return str(issues)
