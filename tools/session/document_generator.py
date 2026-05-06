"""AI bridge for generating LILIA downstream session markdown documents."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import re
from typing import Any

from tools.common.engine_runner import (
    EngineRunnerError,
    EngineTimeoutError,
    engine_candidates,
    engine_timeout_seconds,
    run_engine,
)
from tools.common.references import load_sanitized_reference
from tools.session.document_validator import validate_session_documents


ROOT = Path(__file__).resolve().parents[2]
MAX_ATTEMPTS = 3

GROUP_A_PATHS = [
    "current/scene.md",
    "current/event_card.md",
    "current/hotset.md",
    "current/relationship_overview.md",
    "story/story_deck.md",
]

GROUP_B_PATHS = [
    "lilia/main/core.md",
    "lilia/main/voice.md",
    "lilia/main/state.md",
    "lilia/main/relationship.md",
    "lilia/main/memory.md",
    "lilia/main/beliefs.md",
]

GROUP_C_PATHS = [
    "current/protagonist.md",
    "current/knowledge_state.md",
]

ALL_PATHS = GROUP_A_PATHS + GROUP_B_PATHS + GROUP_C_PATHS


class DocumentGenerationError(RuntimeError):
    """Raised when downstream session documents cannot be generated."""


def generate_session_documents(
    answers: dict,
    character_yaml: dict,
    profile_md: str,
    story_spine_md: str,
    relationship_spine_md: str,
    engine: str,
    **kwargs: Any,
) -> dict:
    """Generate validated downstream session markdown files."""
    logger = kwargs.get("logger")
    _write_log(
        logger,
        "[downstream_docs] generate_session_documents enter",
        engine=engine,
        session_name=kwargs.get("session_name") or "",
        answer_count=len(answers) if isinstance(answers, dict) else "invalid",
    )

    if not isinstance(answers, dict):
        raise DocumentGenerationError("answers must be a dict")
    if not isinstance(character_yaml, dict):
        raise DocumentGenerationError("character_yaml must be a dict")
    for name, value in [
        ("profile_md", profile_md),
        ("story_spine_md", story_spine_md),
        ("relationship_spine_md", relationship_spine_md),
    ]:
        if not isinstance(value, str) or not value.strip():
            raise DocumentGenerationError(f"{name} must be non-empty markdown")

    context = {
        "answers": answers,
        "character_yaml": character_yaml,
        "profile_md": profile_md,
        "story_spine_md": story_spine_md,
        "relationship_spine_md": relationship_spine_md,
        "engine": engine,
        "lilia_name": kwargs.get("lilia_name") or kwargs.get("lilia_display_name") or "",
        "session_name": kwargs.get("session_name") or "",
    }
    documents: dict[str, str] = {}
    group_meta: dict[str, dict[str, Any]] = {}

    group_specs = [
        ("group_a", GROUP_A_PATHS, _build_group_a_prompt(context)),
        ("group_b", GROUP_B_PATHS, _build_group_b_prompt(context)),
        ("group_c", GROUP_C_PATHS, _build_group_c_prompt(context)),
    ]
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}
        for group_name, rel_paths, prompt in group_specs:
            _write_log(logger, f"[downstream_docs] {group_name} start", paths=rel_paths)
            futures[
                executor.submit(
                    _generate_group,
                    group_name=group_name,
                    rel_paths=rel_paths,
                    prompt=prompt,
                    answers=answers,
                    story_spine_md=story_spine_md,
                    engine=engine,
                    context=context,
                    logger=logger,
                )
            ] = group_name

        for future in as_completed(futures):
            group_name = futures[future]
            try:
                group_result = future.result()
            except Exception:
                for pending in futures:
                    if pending is not future:
                        pending.cancel()
                raise
            documents.update(group_result["documents"])
            group_meta[group_name] = group_result["meta"]
            _write_log(
                logger,
                f"[downstream_docs] {group_name} complete",
                files=list(group_result["documents"]),
            )

    _write_log(logger, "[downstream_docs] combined validation start", files=list(documents))
    valid, errors = validate_session_documents(
        documents,
        answers,
        story_spine_md=story_spine_md,
        expected_paths=ALL_PATHS,
    )
    if not valid:
        _write_log(logger, "[downstream_docs] combined validation failed", error="; ".join(errors[:8]))
        raise DocumentGenerationError("combined downstream validation failed: " + "; ".join(errors[:8]))
    _write_log(logger, "[downstream_docs] combined validation pass")

    engine_used = next((meta.get("engine_used") for meta in group_meta.values() if meta.get("engine_used")), engine)
    retry_count = sum(int(meta.get("validation_retry_count", 0)) for meta in group_meta.values())
    return {
        "documents": {path: documents[path] for path in ALL_PATHS},
        "engine_used": engine_used,
        "validation_retry_count": retry_count,
        "groups": group_meta,
    }


def generate_scene_event_documents(
    answers: dict,
    character_yaml: dict,
    profile_md: str,
    story_spine_md: str,
    relationship_spine_md: str,
    engine: str,
) -> dict[str, str]:
    result = generate_session_documents(
        answers=answers,
        character_yaml=character_yaml,
        profile_md=profile_md,
        story_spine_md=story_spine_md,
        relationship_spine_md=relationship_spine_md,
        engine=engine,
    )
    return {path: result["documents"][path] for path in GROUP_A_PATHS}


def generate_lilia_internal_documents(
    answers: dict,
    character_yaml: dict,
    profile_md: str,
    story_spine_md: str,
    relationship_spine_md: str,
    engine: str,
) -> dict[str, str]:
    result = generate_session_documents(
        answers=answers,
        character_yaml=character_yaml,
        profile_md=profile_md,
        story_spine_md=story_spine_md,
        relationship_spine_md=relationship_spine_md,
        engine=engine,
    )
    return {path: result["documents"][path] for path in GROUP_B_PATHS}


def generate_protagonist_documents(
    answers: dict,
    character_yaml: dict,
    profile_md: str,
    engine: str,
) -> dict[str, str]:
    context = {
        "answers": answers,
        "character_yaml": character_yaml,
        "profile_md": profile_md,
        "story_spine_md": "",
        "relationship_spine_md": "",
        "engine": engine,
        "lilia_name": "",
        "session_name": "",
    }
    result = _generate_group(
        group_name="group_c",
        rel_paths=GROUP_C_PATHS,
        prompt=_build_group_c_prompt(context),
        answers=answers,
        story_spine_md="",
        engine=engine,
        context=context,
    )
    return result["documents"]


def load_sanitized_opening_pattern_stock() -> str:
    return load_sanitized_reference("references/opening_pattern_stock.md")


def _generate_group(
    *,
    group_name: str,
    rel_paths: list[str],
    prompt: str,
    answers: dict,
    story_spine_md: str,
    engine: str,
    context: dict[str, Any] | None = None,
    logger: Any = None,
) -> dict[str, Any]:
    candidates = engine_candidates(engine)
    if not candidates:
        raise DocumentGenerationError("no available engine CLI was found")
    previous_error = ""
    cli_failures: list[str] = []
    _write_log(
        logger,
        "[downstream_docs] group enter",
        group=group_name,
        paths=rel_paths,
        candidates=candidates,
        prompt_chars=len(prompt),
    )

    for attempt_index in range(MAX_ATTEMPTS):
        attempt_prompt = prompt
        if previous_error:
            attempt_prompt += f"""

## 前回の検証エラー

以下をすべて直して、同じ FILE ブロック形式だけで再出力してください。

{previous_error}
"""
        raw_output = ""
        engine_used = ""
        _write_log(logger, "[downstream_docs] group attempt start", group=group_name, attempt=attempt_index + 1)
        for candidate in _attempt_engine_order(candidates, attempt_index):
            try:
                _write_log(
                    logger,
                    "[downstream_docs] llm call start",
                    group=group_name,
                    attempt=attempt_index + 1,
                    engine=candidate,
                    prompt_chars=len(attempt_prompt),
                )
                raw_output = run_engine(
                    candidate,
                    attempt_prompt,
                    timeout=engine_timeout_seconds(),
                    root=ROOT,
                )
                engine_used = candidate
                _write_log(
                    logger,
                    "[downstream_docs] llm call complete",
                    group=group_name,
                    attempt=attempt_index + 1,
                    engine=candidate,
                    output_chars=len(raw_output),
                )
                break
            except EngineRunnerError as exc:
                cli_failures.append(f"{candidate}: {exc}")
                _write_log(
                    logger,
                    "[downstream_docs] llm call failed",
                    group=group_name,
                    attempt=attempt_index + 1,
                    engine=candidate,
                    error=str(exc),
                )
                if engine != "auto":
                    raise DocumentGenerationError(str(exc)) from exc
        if not raw_output or not engine_used:
            detail = "; ".join(cli_failures[-4:]) or "no engine produced output"
            raise DocumentGenerationError(f"{group_name}: generation could not start: {detail}")

        try:
            parsed = _parse_file_blocks(raw_output, rel_paths)
            _write_log(
                logger,
                "[downstream_docs] parse complete",
                group=group_name,
                attempt=attempt_index + 1,
                files=list(parsed),
            )
            if group_name == "group_c" and context is not None:
                parsed["current/protagonist.md"] = _normalize_protagonist_document(
                    parsed["current/protagonist.md"],
                    context,
                )
                parsed["current/knowledge_state.md"] = _render_knowledge_state_document(
                    parsed["current/knowledge_state.md"],
                    parsed["current/protagonist.md"],
                    context,
                )
            valid, errors = validate_session_documents(
                parsed,
                answers,
                story_spine_md=story_spine_md,
                expected_paths=rel_paths,
            )
            if not valid:
                raise DocumentGenerationError("; ".join(errors[:8]))
            _write_log(
                logger,
                "[downstream_docs] group validation pass",
                group=group_name,
                attempt=attempt_index + 1,
            )
            return {
                "documents": parsed,
                "meta": {
                    "engine_used": engine_used,
                    "validation_retry_count": attempt_index,
                    "validation": "pass",
                },
            }
        except DocumentGenerationError as exc:
            previous_error = str(exc)
            _write_log(
                logger,
                "[downstream_docs] group validation failed",
                group=group_name,
                attempt=attempt_index + 1,
                error=previous_error,
            )

    raise DocumentGenerationError(
        f"{group_name}: generation failed after 3 attempts: {previous_error or 'unknown validation error'}"
    )


def _write_log(logger: Any, event: str, **fields: object) -> None:
    if logger is None or not hasattr(logger, "write"):
        return
    try:
        logger.write(event, **fields)
    except Exception:
        return


def _attempt_engine_order(candidates: list[str], attempt_index: int) -> list[str]:
    if attempt_index < 2 or len(candidates) == 1:
        return candidates[:1]
    return candidates[1:]


def _parse_file_blocks(raw_output: str, expected_paths: list[str]) -> dict[str, str]:
    pattern = re.compile(
        r"^===FILE:\s*(.+?)\s*===\s*\n(.*?)(?=^===FILE:\s*.+?\s*===\s*$|\Z)",
        flags=re.MULTILINE | re.DOTALL,
    )
    documents: dict[str, str] = {}
    for match in pattern.finditer(raw_output.strip()):
        path = match.group(1).strip()
        content = match.group(2).strip()
        if path in expected_paths:
            documents[path] = content.rstrip() + "\n"

    missing = [path for path in expected_paths if not documents.get(path, "").strip()]
    if missing:
        raise DocumentGenerationError("missing FILE block(s): " + ", ".join(missing))
    return {path: documents[path] for path in expected_paths}


def _normalize_protagonist_document(content: str, context: dict[str, Any]) -> str:
    fields = _protagonist_fields(content, context)
    lines = content.rstrip().splitlines()
    lines = _ensure_section_field(lines, "身体", "性別", fields["gender"])
    lines = _ensure_section_field(lines, "身体", "身長感", fields["height"])
    lines = _ensure_section_field(lines, "身体", "体格", fields["build"])
    lines = _ensure_section_field(lines, "身体", "仕事 / 立場", fields["occupation"])
    lines = _ensure_section_field(lines, "スタイル", "服装", fields["style"])
    return "\n".join(lines).rstrip() + "\n"


def _ensure_section_field(lines: list[str], section: str, label: str, value: str) -> list[str]:
    field_re = re.compile(rf"^(\s*[-*]?\s*){re.escape(label)}\s*[:：]")
    for index, line in enumerate(lines):
        match = field_re.match(line)
        if match:
            prefix = match.group(1) or "- "
            if not prefix.strip():
                prefix = "- "
            lines[index] = f"{prefix}{label}: {value}"
            return lines

    start = None
    end = len(lines)
    for index, line in enumerate(lines):
        if line.strip() == f"## {section}":
            start = index
            continue
        if start is not None and index > start and line.startswith("## "):
            end = index
            break
    insert_at = end
    if start is not None:
        for index in range(start + 1, end):
            if lines[index].strip().startswith("- "):
                insert_at = index + 1
    lines.insert(insert_at, f"- {label}: {value}")
    if insert_at + 1 < len(lines) and lines[insert_at + 1].startswith("## "):
        lines.insert(insert_at + 1, "")
    return lines


def _protagonist_fields(content: str, context: dict[str, Any]) -> dict[str, str]:
    q8 = _answer_text(context["answers"], 8)
    parts = [part.strip() for part in re.split(r"[、,/／。\n]+", q8) if part.strip()]
    compact = re.sub(r"\s+", "", q8)

    gender = _field_value(content, ["性別"])
    if not gender:
        if "女" in compact:
            gender = "女"
        elif "男" in compact:
            gender = "男"
        else:
            gender = "未確定"

    height = _field_value(content, ["身長感"])
    if not height:
        cm_match = re.search(r"(\d{2,3}\s*cm)", q8, re.IGNORECASE)
        if cm_match:
            height = cm_match.group(1).replace(" ", "")
        elif any(word in compact for word in ["長身", "高め", "背が高"]):
            height = "高め"
        elif any(word in compact for word in ["小柄", "低め", "背が低"]):
            height = "低め"
        else:
            height = "未確定"

    build = _field_value(content, ["体格"])
    if not build:
        if any(word in compact for word in ["痩せ", "細身"]):
            build = "痩せ型"
        elif any(word in compact for word in ["がっしり", "筋肉質"]):
            build = "がっしり"
        elif any(word in compact for word in ["標準", "普通", "中肉"]):
            build = "標準"
        else:
            build = "未確定"

    occupation = _field_value(content, ["仕事 / 立場", "仕事", "立場"])
    if not occupation:
        occupation = _infer_job(parts)

    style = _field_value(content, ["服装"])
    if not style:
        style = _infer_style(parts, occupation)

    return {
        "gender": gender,
        "height": height,
        "build": build,
        "occupation": occupation,
        "style": style,
    }


def _field_value(content: str, labels: list[str]) -> str:
    for label in labels:
        match = re.search(rf"{re.escape(label)}\s*[:：]\s*(.+)", content)
        if match:
            value = match.group(1).strip()
            value = re.sub(r"\s*←.*$", "", value).strip()
            if value and value not in {"(未設定)", "未設定"}:
                return value
    return ""


def _infer_job(parts: list[str]) -> str:
    job_words = ["仕事", "職", "勤務", "配達", "会社員", "学生", "教師", "医師", "看護", "店員", "エンジニア", "コンサル", "便利屋"]
    for part in parts:
        if any(word in part for word in job_words):
            return part
    return "未確定"


def _infer_style(parts: list[str], occupation: str) -> str:
    skip_words = ["男", "女", "cm", "痩せ", "細身", "普通", "標準", "仕事", "職", "勤務", occupation]
    clothing_words = ["服", "パーカー", "シャツ", "スーツ", "制服", "コート", "装備", "靴", "帽", "ジャケット", "ワンピース"]
    for part in parts:
        if any(word in part for word in clothing_words):
            return part
    candidates = [part for part in parts if not any(word and word in part for word in skip_words)]
    return candidates[0] if candidates else "未確定"


def _render_knowledge_state_document(
    ai_content: str,
    protagonist_md: str,
    context: dict[str, Any],
) -> str:
    del ai_content
    fields = _protagonist_fields(protagonist_md, context)
    story_fields = _story_fields(context.get("story_spine_md", ""))
    character = context.get("character_yaml") if isinstance(context.get("character_yaml"), dict) else {}
    profile = str(context.get("profile_md") or "")
    answers = context["answers"]

    name = str(character.get("name") or context.get("lilia_name") or _profile_field(profile, "name") or "未確定")
    occupation = str(character.get("occupation") or _profile_field(profile, "occupation") or "未確定")
    visual_anchor = _profile_quality(profile) or _answer_text(answers, 3) or "未確定"
    background_truth = story_fields.get("background_truth") or _answer_text(answers, 5) or "未確定"
    constraints = _answer_text(answers, 9) or "特になし"

    item_specs = [
        dict(key="protagonist_call_name", value=_answer_text(answers, 7) or "未確定", fictional_status="meta", source="protagonist", known_to=["protagonist"], acquired_at="pre_play", weight="medium", notes="ヒロインが知る経路がない時点では使わない。自己紹介、伝票、名札、紹介などの装置を経由する"),
        dict(key="protagonist_gender", value=fields["gender"], fictional_status="observable", source="protagonist", known_to=["protagonist"], acquired_at="pre_play", weight="low", notes="視覚的に観察可能"),
        dict(key="protagonist_height", value=fields["height"], fictional_status="observable", source="protagonist", known_to=["protagonist"], acquired_at="pre_play", weight="low", notes="視覚的に観察可能"),
        dict(key="protagonist_build", value=fields["build"], fictional_status="observable", source="protagonist", known_to=["protagonist"], acquired_at="pre_play", weight="low", notes="視覚的に観察可能"),
        dict(key="protagonist_style", value=fields["style"], fictional_status="observable", source="protagonist", known_to=["protagonist"], acquired_at="pre_play", weight="low", notes="視覚的に観察可能"),
        dict(key="protagonist_occupation", value=fields["occupation"], fictional_status="meta", source="protagonist", known_to=["protagonist"], acquired_at="pre_play", weight="medium", notes="主人公がscene内で開示するまでヒロインは知らない"),
        dict(key="heroine_name", value=name, fictional_status="meta", source="heroine_self_disclosure", known_to=["heroine"], acquired_at="pre_play", weight="high", notes="初対面で自己紹介すると shared に昇格"),
        dict(key="heroine_occupation", value=occupation, fictional_status="meta", source="heroine_self_disclosure", known_to=["heroine"], acquired_at="pre_play", weight="medium", notes="自己紹介または場面内の自然な開示で shared に昇格"),
        dict(key="heroine_visual_anchor", value=visual_anchor, fictional_status="observable", source="observation", known_to=["heroine", "protagonist"], acquired_at="scene_1", weight="medium", notes="描写の縛りとして初回から観測可能"),
        dict(key="heroine_background_truth", value=background_truth, fictional_status="gm_only", source="story_spine", known_to=["GM"], acquired_at="pre_play", weight="high", notes="Reveal Ladder で段階的に開示される。本文に直接出さない"),
        dict(key="reveal_ladder_stage_1", value=story_fields.get("visible") or "未確定", fictional_status="gm_only", source="story_spine", known_to=["GM"], acquired_at="pre_play", weight="medium", notes="開示時に shared へ昇格"),
        dict(key="reveal_ladder_stage_2", value=story_fields.get("near_reveal") or "未確定", fictional_status="gm_only", source="story_spine", known_to=["GM"], acquired_at="pre_play", weight="medium", notes="開示時に shared へ昇格"),
        dict(key="reveal_ladder_stage_3", value=story_fields.get("deep_reveal") or "未確定", fictional_status="gm_only", source="story_spine", known_to=["GM"], acquired_at="pre_play", weight="high", notes="開示時に shared へ昇格"),
        dict(key="session_constraints", value=constraints, fictional_status="meta-system", source="protagonist", known_to=["GM"], acquired_at="pre_play", weight="low", notes="GM 内部参照のみ。フィクション内に出さない"),
    ]
    item_lines: list[str] = []
    for spec in item_specs:
        item_lines.extend(_knowledge_item_yaml(**spec))
        item_lines.append("")

    return "\n".join(
        [
            "# Knowledge State",
            "",
            "このファイルは「事実とその経路」を保持する。",
            "",
            "## このファイルの目的",
            "",
            "GM が scene 生成時に、この情報を誰が知っていて、どの経路で使えるかを判断する。",
            "",
            "## ステータス（fictional_status）の4種類",
            "",
            "- meta: プレイヤー由来で、フィクション内ではまだ開示されていない。",
            "- observable: 視覚的・物理的に観察可能。",
            "- shared: scene の中で開示された共有事実。",
            "- gm_only: GM だけが知る真相。",
            "",
            "## 各項目の構造",
            "",
            "各項目は key / value / fictional_status / source / known_to / acquired_at / weight / notes を持つ。",
            "",
            "## 初期化（newgame 時）",
            "",
            "主人公由来、ヒロイン自己情報、story_spine由来、session制約を分けて初期化する。",
            "",
            "## 知識項目テンプレート",
            "",
            "実データは下の `## knowledge_state` に置く。このセクションにはサンプル用の `items:` ブロックを置かない。",
            "",
            "## 更新タイミング",
            "",
            "Save Mode で fictional_status の昇格、新規項目、known_to の追加、重みの変化を turn_update.md に書く。",
            "",
            "## knowledge_state",
            "",
            "```yaml",
            "items:",
            *item_lines,
            "```",
            "",
            "## 連動仕様",
            "",
            "knowledge_state.md は事実と経路を持つ。memory.md は感情の跡、story_spine.md は真相、decision_index.md は約束・拒否・保留を持つ。",
            "",
        ]
    )


def _knowledge_item_yaml(
    *,
    key: str,
    value: str,
    fictional_status: str,
    source: str,
    known_to: list[str],
    acquired_at: str,
    weight: str,
    notes: str = "",
) -> list[str]:
    def scalar(raw: str) -> str:
        clean = (raw or "未確定").replace("\n", " / ").strip() or "未確定"
        return '"' + clean.replace("\\", "\\\\").replace('"', '\\"') + '"'

    known = "[" + ", ".join(known_to or ["GM"]) + "]"
    lines = [
        f"  - key: {key}",
        f"    value: {scalar(value)}",
        f"    fictional_status: {fictional_status}",
        f"    source: {source}",
        f"    known_to: {known}",
        f"    acquired_at: {acquired_at}",
        f"    weight: {weight}",
    ]
    if notes:
        lines.append(f"    notes: {scalar(notes)}")
    return lines


def _story_fields(markdown: str) -> dict[str, str]:
    sections = _markdown_sections(markdown)
    reveal_lines = [
        re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", line).strip()
        for line in sections.get("reveal ladder", "").splitlines()
        if re.match(r"^\s*(?:[-*]|\d+[.)])\s+", line)
    ]
    reveal_lines = [line for line in reveal_lines if line]
    return {
        "background_truth": sections.get("background truth", "") or sections.get("background truth gm only", ""),
        "visible": reveal_lines[0] if len(reveal_lines) > 0 else "",
        "near_reveal": reveal_lines[1] if len(reveal_lines) > 1 else "",
        "deep_reveal": reveal_lines[2] if len(reveal_lines) > 2 else "",
    }


def _markdown_sections(markdown: str) -> dict[str, str]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", markdown, re.MULTILINE))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        key = re.sub(r"[\(\（].*?[\)\）]", "", match.group(1)).strip().lower()
        sections[key] = markdown[start:end].strip()
    return sections


def _profile_field(profile: str, field: str) -> str:
    match = re.search(rf"^{re.escape(field)}\s*:\s*(.+)$", profile, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _profile_quality(profile: str) -> str:
    match = re.search(r"必ず入れる質感1\s*[:：]\s*(.+)", profile)
    return match.group(1).strip() if match else ""


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


def _build_group_a_prompt(context: dict[str, Any]) -> str:
    opening_pattern_stock = load_sanitized_opening_pattern_stock()
    constraints = """
1. 各ファイルは異なる目的を持つ。同じ文や同じ素材を複数ファイルへコピペしない。
2. 文を途中で切らない。「...」「…」で終わらせない。
3. 全セッション共通のテンプレ表現を使わない。
   禁止: 「{ヒロイン名}が自分で決めるまで待つ」
   禁止: 「{ヒロイン名}に名乗る / 名前を聞く」
   禁止: 「{物}に触れず、扱い方だけを提案する」
4. Initial Scene Anchors は切り貼りせず、それぞれのファイルの目的に合わせて再構成する。
5. story_spine の Background Truth と [pending] の Reveal Ladder は GM only として隠す。
   scene/event_card/hotset/relationship_overview/story_deck へ直接書かない。
6. event_card の handles は選択肢UIではなく、このヒロイン固有の現在状況へ触れる入口にする。
7. current/event_card.md は原則1, 3, 4, 5を意識し、Visible Problem / Relationship Stake / Next Visible Change に感情の圧と未完了を残す。
8. current/scene.md は原則2, 3, 5を意識し、感情名ではなく身体反応、環境、予想との差、未解決の要素で初回sceneを始める。
9. current/hotset.md は原則5を意識し、再開時に戻す未完了の余白を短く残す。
10. current/scene.md の末尾に必ず `## Opening Plan` セクションを出す。
    Q&A の Q3（描写の縛り）、Q5（内面に持っているもの）、Q6（出会い + 関係性の起点）、Q9（避けたい展開）、
    character YAML、profile.md、story_spine の Background Truth / Drift Guard を解釈し、
    下の Opening Pattern Stock から A群 1 + D群 1（必須） + B群またはC群から最大1（任意）を選ぶ。
11. Opening Pattern の選択ルール:
    - 必ず A群（O1-O4）から1つ、D群（O13-O15）から1つ。
    - B群（O5-O8）またはC群（O9-O12）から任意で1つ追加可。
    - 3つ以上の混在は禁止。
    - 同じ群から2つ採用するのは禁止。
    - Q9に「停滞を避けたい」がある場合、O9 / O10 / O14 を優先候補にする。
    - Q5に過去の傷・秘密が強い場合、O5 / O11 を候補にする。
    - Q6が偶然の出会いの場合、O13 / O14 を候補にする。
12. `## Opening Plan` は以下の固定フォーマットで出す。空欄、未設定、TODO、placeholder を残さない。

```text
## Opening Plan

selected_patterns: [O<n>, O<n>] または [O<n>, O<n>, O<n>]
selection_reason: 1-2文の短い説明
must_include:
  - O<n>: そのパターンが要求する具体要素
  - O<n>: そのパターンが要求する具体要素
4_jobs:
  hook: 冒頭の掴みになる要素
  orientation: 主人公の位置・職業・状況。3文以内で読み取れる形
  agency: プレイヤーの初手の選択余地
  unresolved: 持ち越す問い
clarity_anchors:
  protagonist_role: 主人公の職業・立場を示す具体描写、1行
  protagonist_purpose: なぜ今この場にいるかの具体描写、1行
  location_function: 場所が何の場所か伝わる描写、1行。固有名詞のみで終わらせない
  heroine_relation: 主人公とヒロインの関係性が判別できる手がかり、1行
opening_caveats:
  - パターン固有の典型的失敗をどう回避するかの1行
```

13. `clarity_anchors` は冒頭本文を書く LLM が自然な描写へ織り込むための足場である。
    説明調にせず、役割・目的・場所機能・関係性を1行の描写に含められる具体度で書く。
    悪い例: 「鴉ノ宿のガラス戸を細く叩いていた」
    良い例: 「オカルトショップ『鴉ノ宿』のガラス戸を、雨が細く叩いていた」
14. `must_include` は選んだパターンの「形」から必須要素を1-2個抜く。
    O3: 視覚情報は最後、音/匂い/温度を先に置く。2感覚までで止める。
    O14: 発見の瞬間から始める。助けた後から始めない。助ける/通過/様子を見る余地を残す。
    O15: 日常のルーチンが先、違和感は1-2点で止める。
15. `## 次に起きそうなこと` は Opening Plan の `agency` と矛盾させない。プレイヤーの選択を奪わない。
16. `## 直前のやりとり` は Opening Plan の `4_jobs.hook` と整合させる。

## ファイル間の抽象レベル分離（重要）

scene.md / event_card.md / hotset.md には、ヒロインの「最初の反応」を書くセクションがある。
それぞれ異なる抽象レベルから書け。同じ内容を別表現で複数ファイルへ書くな。

- current/scene.md `## 直前のやりとり`:
  場面開始の **物理的な事実** だけを書く。ヒロインの意図や行動段取りは書かない。
  良い例: 「客人さんが置物を差し出した。朔は伝票から目を上げた」
  悪い例: 「朔は確認のため、布を敷いて置物を置くよう促した」（行動段取りは event_card の責務）

- current/event_card.md `## First Concrete Action`:
  この場面の **最初のトリガー行動を 1 つだけ** 書く。チェックリスト形式にしない。
  良い例: 「朔は帳場に乾いた布を敷き、置物をそこへ置くよう促す」
  悪い例: 「朔は布を敷き、置いた場所、触った人、変化の時間を確認する」
  複数の質問を一度に列挙するのは禁止。次の質問は次のターンで出る。

- current/hotset.md `## 次に会った時の第一反応`:
  再開時のキャッシュとして **短い要約** だけ。動作と質問のリストにしない。
  良い例: 「朔は次回会った時、まず品物を見る」
  悪い例: 「朔は布を敷き、場所を聞き、時間を聞き、触った人を聞く」

scene.md の `## 直前のやりとり` に event_card の First Concrete Action を貼り付けるな。
event_card の First Concrete Action に hotset の要約を貼り付けるな。
3 つのセクションの抽象レベルを必ず区別しろ。

## Opening Pattern Stock（作品名サニタイズ済み）

```md
""".rstrip() + "\n" + opening_pattern_stock + "\n```\n"
    return _build_base_prompt(
        context=context,
        rel_paths=GROUP_A_PATHS,
        role="あなたは LILIA セッションの初回シーン素材を作る設計者です。",
        constraints=constraints,
    )


def _build_group_b_prompt(context: dict[str, Any]) -> str:
    return _build_base_prompt(
        context=context,
        rel_paths=GROUP_B_PATHS,
        role="あなたは LILIA 本体の内面ファイルを初期化する設計者です。",
        constraints="""
1. core.md / voice.md / state.md / relationship.md / memory.md / beliefs.md は異なる側面を書く。同じ文を複数ファイルに使わない。
2. core.md: 変わってはいけない核。profile の丸写しではなく、人格の骨格だけを書く。
3. voice.md: 口調、沈黙、第一反応、言わない言葉、距離の置き方を書く。固定台詞集にしない。
4. state.md: 初回 scene 直前の一時状態を書く。長文の連結や「/」区切りの寄せ集めにしない。
5. relationship.md: 初期距離、信頼、境界線、合意、止まれる余地を書く。好意や恋愛成立は確定しない。
6. memory.md の short_term は初回 scene 前なので、未発生または初回 scene 前の状況だけにする。
7. beliefs.md は正解ではなく LILIA 側の仮説を書く。ユーザーの内面を断定しない。
8. 文を途中で切らない。「...」「…」で終わらせない。
9. relationship.md は原則6, 7, 8を意識し、圧力下で見える核、Q1-Q9由来の要素、成功にも残るコストを関係の余白として扱う。
10. memory.md は原則5, 7を意識し、未完了の言葉、約束、プレイヤーが持ち込んだ要素を後で返せる形にする。

## ファイル間の抽象レベル分離（重要）

voice.md / state.md には「第一反応」セクションがある。それぞれ異なる抽象レベルから書け。

- lilia/main/voice.md `## 第一反応`:
  ヒロインの **永続的な反応の癖** を書く。「ヒロインという人は、異変を見るとこういう反応をするタイプだ」という性格として書く。
  具体物（場所名、人名、商品名、状況の固有要素）を出さない。
  良い例: 「異変を聞いた時、まず表情を変えずに品物を確認する。原因の断定を避ける」
  悪い例: 「布を敷いて、置いた場所、触った人、変化の時間を聞く」
  具体物のリストは event_card の責務。voice.md には性格だけ書く。

- lilia/main/state.md `## 第一反応`:
  **今だけの気分** による反応を書く。今日の特殊事情（疲労、雨、閉店前の急ぎ等）が反応にどう影響しているかを書く。
  voice.md の永続的な癖と被らせるな。
  良い例: 「閉店前の疲労があり、いつもより数珠に触れる時間が長くなっている」
  悪い例: 「触った人、置いた場所、変化の時間を短く確認する」
  これは voice.md の永続的な癖と区別がつかない。

voice.md には「ヒロインがいつもどう反応する人か」、state.md には「今日の状況がそれをどう変えているか」、と明確に役割を分けろ。
""",
    )


def _build_group_c_prompt(context: dict[str, Any]) -> str:
    return _build_base_prompt(
        context=context,
        rel_paths=GROUP_C_PATHS,
        role="あなたは主人公側情報と knowledge_state の protagonist 系項目を初期化する設計者です。",
        constraints="""
1. Q8（主人公の身体・格好・仕事）を分解して書く。Q8全文を服装や体格へ丸ごと入れない。
2. current/protagonist.md の身体には、性別 / 身長感 / 体格 / 仕事 / 立場 を独立して書く。
3. current/protagonist.md のスタイルには、服装の特徴だけを書く。職業や身長を含めない。
4. knowledge_state.md はテンプレートと同じ ## 見出しを持たせる。
5. knowledge_state.md の実データは `## knowledge_state` セクション内の1つの fenced YAML block に書く。
6. YAML は `items:` の下に protagonist 系6項目を必ず含める:
   protagonist_call_name, protagonist_gender, protagonist_height, protagonist_build, protagonist_style, protagonist_occupation
7. heroine_* と reveal_ladder_* と session_constraints も、入力 story_spine/profile から生成して含める。
   ただし Background Truth は gm_only とし、本文説明として漏らさない。
8. Q8全文を YAML の value に入れない。
""",
    )


def _build_base_prompt(
    *,
    context: dict[str, Any],
    rel_paths: list[str],
    role: str,
    constraints: str,
) -> str:
    answers_json = json.dumps(context["answers"], ensure_ascii=False, indent=2, default=str)
    character_json = json.dumps(
        context["character_yaml"],
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        default=str,
    )
    structures = "\n\n".join(_template_structure(path) for path in rel_paths)
    output_blocks = "\n".join(f"===FILE: {path}===\n[{path} の本文]" for path in rel_paths)

    return f"""{role}

LILIAは、ユーザーとの会話・選択・物語を記憶し、関係性と人格の出方が少しずつ変化していくAI恋愛シミュレーションです。
ストーリーは主役ではなく、LILIAの人格、記憶、信頼、距離感、声、境界線、beliefsを変化させる装置です。

## 入力素材

### Q&A
```json
{answers_json}
```

### character.yaml
```json
{character_json}
```

### profile.md
```md
{context["profile_md"].strip()}
```

### current/story_spine.md
```md
{context["story_spine_md"].strip()}
```

### story/relationship_spine.md
```md
{context["relationship_spine_md"].strip()}
```

## 共通制約

1. Q&A の値をそのまま埋め込まず、意味を解釈して自然な日本語へ再構成する。
2. 1文ずつ完結させる。途中で切れた文を作らない。
3. 「未確定: profile/answers から再推論」「[未確定: Q3で指定されなかったため、scene 内で profile から導出]」などの残骸を出さない。
4. 「おまかせ」「特になし」をそのまま素材として増幅しない。profile と character.yaml から仮説を立てて埋める。
5. 参照作品名、人物名、固有地名、組織名、設定名を出さない。
6. 同じ30文字以上の文を3ファイル以上に出さない。
7. 各ファイルの `##` 見出しは、下のセクション構造と同じ文言・順序・数で出す。
8. 前置き、説明、後書き、コードフェンス外の余計な注釈を出さない。
9. 「第一反応」「最初の反応」「First Concrete Action」「次に会った時の反応」「直前のやりとり」のような、ヒロインの反応を書くセクションが複数ファイルにある場合、各セクションは異なる抽象レベル（永続的な癖 / 今だけの気分 / 場面のトリガー / 再開キャッシュ / 物理事実）から書け。同じ具体物の列挙を別表現で複数ファイルに書くな。

## 感情設計の原則

以下の生成は `docs/EMOTIONAL_DESIGN_PRINCIPLES.md` の8原則を参照する。
Docsの文をそのまま貼らず、各ファイルの責務に合わせて story / scene / event_card / relationship / memory / hotset に反映する。

## このグループ固有の制約

{constraints.strip()}

## 各ファイルのセクション構造

{structures}

## 出力フォーマット

以下の FILE ブロックだけを出力してください。

{output_blocks}
"""


def _template_structure(rel_path: str) -> str:
    template_path = _template_path(rel_path)
    if not template_path.exists():
        raise DocumentGenerationError(f"template not found: {template_path}")
    text = template_path.read_text(encoding="utf-8")
    h1 = next((line.strip() for line in text.splitlines() if line.startswith("# ")), "# " + rel_path)
    headings = [line.strip() for line in text.splitlines() if line.startswith("## ")]
    if rel_path == "current/knowledge_state.md":
        extra = "\n".join(
            [
                "",
                "knowledge_state.md では、`## 知識項目テンプレート` に fenced YAML を置かないこと。",
                "`## knowledge_state` の下にだけ、実データの fenced YAML block を1つ置くこと。",
            ]
        )
    else:
        extra = ""
    return f"### {rel_path}\n{h1}\n" + "\n".join(headings) + extra


def _template_path(rel_path: str) -> Path:
    if rel_path == "current/protagonist.md":
        return ROOT / "templates" / "session" / "protagonist.md"
    if rel_path == "current/knowledge_state.md":
        return ROOT / "templates" / "session" / "knowledge_state.md"
    return ROOT / "templates" / "session" / rel_path
