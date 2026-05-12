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

try:
    from tools.session.opening_seed import build_opening_seed
except ImportError:  # Worker A owns tools/session/opening_seed.py.
    build_opening_seed = None  # type: ignore[assignment]


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

    def __init__(
        self,
        message: str,
        *,
        target_group: str = "",
        engine: str = "",
        timeout_seconds: float | str | None = None,
        session_name: str = "",
    ) -> None:
        super().__init__(message)
        self.target_group = target_group
        self.engine = engine
        self.timeout_seconds = timeout_seconds
        self.session_name = session_name


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
    _ensure_opening_seed(context)
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
    context = context or {}
    candidates = engine_candidates(engine)
    if not candidates:
        raise DocumentGenerationError(
            "no available engine CLI was found",
            target_group=group_name,
            engine=engine,
            timeout_seconds=_timeout_label(),
            session_name=str(context.get("session_name") or ""),
        )
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
                contextual_error = _format_engine_failure(
                    exc,
                    phase="spines_generated",
                    engine=candidate,
                    target_group=group_name,
                    timeout_seconds=_timeout_label(),
                    session_name=str(context.get("session_name") or ""),
                )
                cli_failures.append(contextual_error)
                _write_log(
                    logger,
                    "[downstream_docs] llm call failed",
                    group=group_name,
                    attempt=attempt_index + 1,
                    engine=candidate,
                    error=contextual_error,
                )
                if engine != "auto":
                    raise DocumentGenerationError(
                        contextual_error,
                        target_group=group_name,
                        engine=candidate,
                        timeout_seconds=_timeout_label(),
                        session_name=str(context.get("session_name") or ""),
                    ) from exc
        if not raw_output or not engine_used:
            detail = "; ".join(cli_failures[-4:]) or "no engine produced output"
            raise DocumentGenerationError(
                f"{group_name}: generation could not start: {detail}",
                target_group=group_name,
                engine=engine,
                timeout_seconds=_timeout_label(),
                session_name=str(context.get("session_name") or ""),
            )

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
            if group_name == "group_a" and context is not None:
                parsed = _repair_group_a_documents_with_opening_seed(parsed, context)
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
            if group_name == "group_a" and attempt_index >= 1 and _should_use_group_a_fallback(previous_error):
                fallback_result = _try_group_a_deterministic_fallback(
                    context=context,
                    answers=answers,
                    story_spine_md=story_spine_md,
                    rel_paths=rel_paths,
                    logger=logger,
                    group_name=group_name,
                    engine_used=engine_used,
                    reason=previous_error,
                )
                if fallback_result is not None:
                    return fallback_result

    if group_name == "group_a":
        fallback_result = _try_group_a_deterministic_fallback(
            context=context,
            answers=answers,
            story_spine_md=story_spine_md,
            rel_paths=rel_paths,
            logger=logger,
            group_name=group_name,
            engine_used=engine_used,
            reason=previous_error or "unknown validation error",
        )
        if fallback_result is not None:
            return fallback_result

    raise DocumentGenerationError(
        f"{group_name}: generation failed after 3 attempts: {previous_error or 'unknown validation error'}",
        target_group=group_name,
        engine=engine,
        timeout_seconds=_timeout_label(),
        session_name=str(context.get("session_name") or ""),
    )


def _should_use_group_a_fallback(error: str) -> bool:
    return any(
        marker in error
        for marker in [
            "still identical to session template",
            "Active Hook",
            "Scene Function",
            "pending Reveal Ladder leaked",
        ]
    )


def _try_group_a_deterministic_fallback(
    *,
    context: dict[str, Any],
    answers: dict,
    story_spine_md: str,
    rel_paths: list[str],
    logger: Any,
    group_name: str,
    engine_used: str,
    reason: str,
) -> dict[str, Any] | None:
    fallback_documents = _fallback_group_a_documents(context)
    valid, errors = validate_session_documents(
        fallback_documents,
        answers,
        story_spine_md=story_spine_md,
        expected_paths=rel_paths,
    )
    if not valid:
        _write_log(
            logger,
            "[downstream_docs] group deterministic fallback failed",
            group=group_name,
            error="; ".join(errors[:8]),
        )
        return None
    _write_log(
        logger,
        "[downstream_docs] group deterministic fallback pass",
        group=group_name,
        reason=reason,
    )
    return {
        "documents": fallback_documents,
        "meta": {
            "engine_used": engine_used or "deterministic_fallback",
            "validation_retry_count": MAX_ATTEMPTS,
            "validation": "deterministic_fallback",
        },
    }


def _fallback_group_a_documents(context: dict[str, Any]) -> dict[str, str]:
    seed = _group_a_seed(context)
    return {
        "current/scene.md": _fallback_scene_md(seed),
        "current/event_card.md": _fallback_event_card_md(seed),
        "current/hotset.md": _fallback_hotset_md(seed),
        "current/relationship_overview.md": _fallback_relationship_overview_md(seed),
        "story/story_deck.md": _fallback_story_deck_md(seed),
    }


def _ensure_opening_seed(context: dict[str, Any]) -> Any:
    seed = context.get("opening_seed")
    if seed is not None:
        return seed
    if build_opening_seed is None:
        return None
    seed = build_opening_seed(
        answers=context.get("answers", {}),
        character_yaml=context.get("character_yaml", {}),
        profile_md=str(context.get("profile_md") or ""),
        story_spine_md=str(context.get("story_spine_md") or ""),
        relationship_spine_md=str(context.get("relationship_spine_md") or ""),
        lilia_name=str(context.get("lilia_name") or ""),
    )
    context["opening_seed"] = seed
    return seed


def _opening_seed_prompt_block(context: dict[str, Any]) -> str:
    seed = _ensure_opening_seed(context)
    if seed is None:
        return (
            "OpeningSeed is unavailable in this checkout. "
            "When tools.session.opening_seed.build_opening_seed is present, "
            "its to_prompt_block() / as_dict() output is inserted here."
        )
    if hasattr(seed, "to_prompt_block") and callable(seed.to_prompt_block):
        block = str(seed.to_prompt_block()).strip()
        if block:
            return block
    seed_dict = _opening_seed_as_dict(seed)
    if seed_dict:
        return json.dumps(seed_dict, ensure_ascii=False, indent=2, sort_keys=True, default=str)
    return str(seed).strip()


def _opening_seed_as_dict(seed: Any) -> dict[str, Any]:
    if seed is None:
        return {}
    if isinstance(seed, dict):
        return seed
    if hasattr(seed, "as_dict") and callable(seed.as_dict):
        value = seed.as_dict()
        return value if isinstance(value, dict) else {}
    return {}


def _repair_group_a_documents_with_opening_seed(
    documents: dict[str, str],
    context: dict[str, Any],
) -> dict[str, str]:
    seed = _ensure_opening_seed(context)
    seed_dict = _opening_seed_as_dict(seed)
    if not seed_dict:
        return documents

    fallback = _group_a_seed(context)
    values = _opening_seed_repair_values(seed_dict, fallback)
    repaired = dict(documents)
    if "current/event_card.md" in repaired:
        repaired["current/event_card.md"] = _repair_event_card_with_opening_seed(
            repaired["current/event_card.md"],
            values,
        )
    if "current/scene.md" in repaired:
        repaired["current/scene.md"] = _repair_scene_orientation_with_opening_seed(
            repaired["current/scene.md"],
            values,
        )
    return repaired


def _opening_seed_repair_values(seed: dict[str, Any], fallback: dict[str, str]) -> dict[str, str]:
    return {
        "hook_id": _seed_lookup(seed, "active_hook.hook_id", "hook_id", "main_hook_id") or fallback["main_hook_id"],
        "hook_type": _seed_lookup(seed, "active_hook.hook_type", "hook_type") or "main",
        "hook_status": _seed_lookup(seed, "active_hook.status", "status") or "active",
        "foreground_reason": (
            _seed_lookup(seed, "active_hook.foreground_reason", "foreground_reason")
            or _foreground_reason_from_seed(seed)
            or f"初回sceneでプレイヤーが今触れられる入口を、{fallback['visible_handle']}に絞るため。"
        ),
        "function": _seed_lookup(seed, "scene_function.function", "function", "scene_function") or "起点",
        "current_question": (
            _seed_lookup(seed, "scene_function.current_question", "current_question", "dramatic_question")
            or fallback["main_question"]
        ),
        "entry_state": _seed_lookup(seed, "scene_function.entry_state", "entry_state") or fallback["first_distance"],
        "exit_condition": (
            _seed_lookup(seed, "scene_function.exit_condition", "exit_condition")
            or "用件の扱い方か、次に確かめる対象が一つ決まる。"
        ),
        "change_delta": (
            _seed_lookup(seed, "scene_function.change_delta", "change_delta")
            or f"{fallback['name']}が主人公を、待てる相手か急かす相手かで仮判断する。"
        ),
        "next_hook_candidate": (
            _seed_lookup(
                seed,
                "scene_function.next_hook_candidate",
                "next_hook_candidate",
                "candidate_next_hook",
                "candidate_id",
            )
            or fallback["candidate_id"]
        ),
        "protagonist_reason": (
            _seed_lookup(
                seed,
                "player_orientation.protagonist_reason",
                "player_orientation.protagonist_purpose",
                "protagonist_reason",
                "protagonist_purpose",
            )
            or f"主人公は{fallback['protagonist_role']}。"
        ),
        "current_player_knowledge": (
            _seed_lookup(
                seed,
                "player_orientation.current_player_knowledge",
                "player_orientation.player_knowledge",
                "current_player_knowledge",
                "player_knowledge",
            )
            or f"{_seed_lookup(seed, 'player_facing_problem') or fallback['visible_handle']}を今ここで確認する必要がある。"
        ),
        "opening_must_show": (
            _seed_lookup(seed, "player_orientation.opening_must_show", "opening_must_show")
            or _opening_must_show_from_seed(seed, fallback)
        ),
        "still_hidden": (
            _seed_lookup(seed, "player_orientation.still_hidden", "still_hidden")
            or f"用件の本当の出所、背後の意図、{fallback['name']}がまだ言語化しない警戒。"
        ),
    }


def _foreground_reason_from_seed(seed: dict[str, Any]) -> str:
    problem = _seed_lookup(seed, "player_facing_problem")
    if not problem:
        return ""
    return f"初回sceneでプレイヤーが今触れられる入口を、{problem}に絞るため。"


def _opening_must_show_from_seed(seed: dict[str, Any], fallback: dict[str, str]) -> str:
    pieces = [
        _seed_lookup(seed, "visible_props"),
        _seed_lookup(seed, "player_facing_problem"),
        _seed_lookup(seed, "protagonist_reason"),
        f"{fallback['name']}との初期距離",
    ]
    compact = "、".join(piece.strip("。") for piece in pieces if piece)
    return compact + "。" if compact else f"場所、用件、主人公が関わる理由、{fallback['name']}との初期距離。"


def _seed_lookup(seed: dict[str, Any], *paths: str) -> str:
    for path in paths:
        current: Any = seed
        for part in path.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                current = None
                break
        if current is not None:
            value = _clean_seed_value(str(current))
            if value:
                return value
    return ""


def _repair_event_card_with_opening_seed(content: str, values: dict[str, str]) -> str:
    content = _set_section_field(content, "Active Hook", "hook_id", values["hook_id"], force=True)
    content = _set_section_field(content, "Active Hook", "hook_type", values["hook_type"], force=True)
    content = _set_section_field(content, "Active Hook", "status", values["hook_status"], force=True)
    content = _set_section_field(content, "Active Hook", "foreground_reason", values["foreground_reason"])
    content = _set_section_field(content, "Scene Function", "function", values["function"], force=True)
    for field in ["current_question", "entry_state", "exit_condition", "change_delta", "next_hook_candidate"]:
        content = _set_section_field(content, "Scene Function", field, values[field])
    return content


def _repair_scene_orientation_with_opening_seed(content: str, values: dict[str, str]) -> str:
    content = _set_section_field(content, "Player Orientation", "主人公がここにいる理由", values["protagonist_reason"])
    content = _set_section_field(
        content,
        "Player Orientation",
        "主人公がscene開始時点で知っていること",
        values["current_player_knowledge"],
    )
    content = _set_section_field(content, "Player Orientation", "冒頭本文で必ず見せる前提", values["opening_must_show"])
    content = _set_section_field(content, "Player Orientation", "まだ隠すこと", values["still_hidden"])
    return content


def _set_section_field(
    content: str,
    section_name: str,
    field: str,
    value: str,
    *,
    force: bool = False,
) -> str:
    if not value:
        return content
    section_re = re.compile(rf"^##\s+{re.escape(section_name)}\s*$", re.MULTILINE)
    section_match = section_re.search(content)
    if not section_match:
        return content

    next_match = re.search(r"^##\s+.+?\s*$", content[section_match.end() :], flags=re.MULTILINE)
    section_end = section_match.end() + next_match.start() if next_match else len(content)
    section = content[section_match.end() : section_end]
    field_re = re.compile(rf"^([ \t]*[-*]?[ \t]*{re.escape(field)}[ \t]*[:：][ \t]*)(.*)$", re.MULTILINE)
    field_match = field_re.search(section)
    if not field_match:
        insert = f"\n- {field}: {value}"
        return content[:section_end].rstrip() + insert + "\n" + content[section_end:]

    current_value = field_match.group(2).strip()
    if not force and not _opening_seed_repair_needed(current_value):
        return content

    prefix = field_match.group(1).rstrip() + " "
    repaired_section = section[: field_match.start()] + prefix + value + section[field_match.end() :]
    return content[: section_match.end()] + repaired_section + content[section_end:]


def _opening_seed_repair_needed(value: str) -> bool:
    return not value.strip() or value.strip().lower() in {"未設定", "todo", "placeholder", "n/a", "none", "-"}


def _group_a_seed(context: dict[str, Any]) -> dict[str, str]:
    character = context.get("character_yaml") if isinstance(context.get("character_yaml"), dict) else {}
    profile = str(context.get("profile_md") or "")
    story = str(context.get("story_spine_md") or "")
    relationship = str(context.get("relationship_spine_md") or "")
    profile_sections = _markdown_sections(profile)
    story_sections = _markdown_sections(story)
    relationship_sections = _markdown_sections(relationship)

    name = _clean_seed_value(
        str(character.get("name") or context.get("lilia_name") or _profile_field(profile, "name") or "ヒロイン")
    )
    occupation = _clean_seed_value(
        str(character.get("occupation") or _profile_field(profile, "occupation") or "生活上の用事を持つ女性")
    )
    current_situation = _compact_seed_text(
        _profile_field(profile, "current_situation")
        or _profile_bullet_value(profile_sections.get("initial scene anchors", ""), "場所と状況")
        or profile_sections.get("context", "")
        or "日常の中に、予定外の小さな用件が入り込んでいる。",
        "日常の中に、予定外の小さな用件が入り込んでいる。",
    )
    main_question = _compact_seed_text(
        story_sections.get("main question", ""),
        f"{name}は、主人公を同じ場に置ける相手として見られるか。",
    )
    relationship_theme = _compact_seed_text(
        relationship_sections.get("育てたいテーマ", ""),
        "近づきすぎず、離れすぎず、相手の境界を見ながら同じ問題へ向く。",
    )
    visible_props = _compact_seed_text(
        _profile_bullet_value(profile_sections.get("initial scene anchors", ""), "手元の具体物")
        or _first_drift_guard(story_sections.get("drift guard", ""))
        or "目の前にある小さな用件",
        "目の前にある小さな用件",
    )
    place = _compact_seed_text(
        _profile_bullet_value(profile_sections.get("initial scene anchors", ""), "場所と状況")
        or current_situation,
        "人目のある日常の場所",
    )
    first_distance = _compact_seed_text(
        _profile_bullet_value(profile_sections.get("initial scene anchors", ""), "最初の距離")
        or "初対面。互いに相手の出方をまだ測っている。",
        "初対面。互いに相手の出方をまだ測っている。",
    )
    opening_entry = _compact_seed_text(
        _profile_bullet_value(profile_sections.get("initial scene anchors", ""), "会話の入口")
        or f"{name}が、主人公の持ち込んだ用件を確かめる。",
        f"{name}が、主人公の持ち込んだ用件を確かめる。",
    )

    visible_handle = _fallback_visible_handle(
        story_sections=story_sections,
        opening_entry=opening_entry,
        visible_props=visible_props,
        name=name,
    )
    protagonist_role = _protagonist_role_from_answers(context.get("answers", {}))
    if _generic_protagonist_role(protagonist_role):
        protagonist_role = _fallback_protagonist_role(
            visible_handle=visible_handle,
            opening_entry=opening_entry,
            visible_props=visible_props,
        )
    seed_dict = _opening_seed_as_dict(_ensure_opening_seed(context))
    seed_player_problem = _seed_lookup(seed_dict, "player_facing_problem")
    seed_role = _seed_lookup(seed_dict, "protagonist_role")
    seed_question = _seed_lookup(seed_dict, "dramatic_question", "scene_function.current_question")
    seed_relationship_stake = _seed_lookup(seed_dict, "relationship_stake")
    seed_entry_state = _seed_lookup(seed_dict, "entry_state", "scene_function.entry_state")
    seed_visible_props = _seed_lookup(seed_dict, "visible_props")
    seed_candidate = _seed_lookup(seed_dict, "candidate_next_hook", "scene_function.next_hook_candidate")
    if seed_player_problem:
        visible_handle = seed_player_problem
    if seed_role:
        protagonist_role = seed_role
    if seed_question:
        main_question = seed_question
    if seed_relationship_stake:
        relationship_theme = seed_relationship_stake
    if seed_entry_state:
        first_distance = seed_entry_state
    if seed_visible_props:
        visible_props = seed_visible_props
    return {
        "name": name,
        "occupation": occupation,
        "current_situation": current_situation,
        "main_question": main_question,
        "relationship_theme": relationship_theme,
        "visible_handle": visible_handle,
        "visible_props": visible_props,
        "place": place,
        "first_distance": first_distance,
        "opening_entry": opening_entry,
        "protagonist_role": protagonist_role,
        "main_hook_id": "main_initial_contact",
        "relationship_hook_id": "relationship_first_boundary",
        "life_hook_id": "life_daily_return",
        "candidate_id": seed_candidate or "next_small_confirmation",
    }


def _fallback_scene_md(seed: dict[str, str]) -> str:
    return f"""# Scene

## 今いる場所

- {seed['place']}

## 現在時刻または場面時間

- 初回sceneの開始直後。日常の流れが少しだけ乱れた時間。

## LILIAとユーザーの距離

- {seed['first_distance']}

## 今この場で見えているもの

- {seed['visible_props']}。{seed['name']}の表情、手元、視線の止まり方。

## 今の場面

- {seed['current_situation']}

## 直前のやりとり

- 作中会話はまだ始まっていない。主人公は{seed['protagonist_role']}。

## 初回sceneの入口

- {seed['opening_entry']}

## Player Orientation

- 主人公がここにいる理由: 主人公は{seed['protagonist_role']}。
- 主人公がscene開始時点で知っていること: {seed['visible_handle']}を今ここで確認する必要があり、{seed['name']}とはまだ信用も警戒も固まっていない。
- 冒頭本文で必ず見せる前提: 場所、用件、主人公が関わる理由、{seed['name']}との初期距離。
- まだ隠すこと: 用件の本当の出所、背後の意図、{seed['name']}がまだ言語化しない警戒。
- 注: 真相は隠してよいが、主人公が今動くための判断材料は隠さない。

## 次に起きそうなこと

- {seed['name']}は、用件そのものより先に、主人公がどう扱うかを短く見る。

## 次にユーザーへ渡す行動余地

- 用件を差し出す、経緯を話す、相手の様子を見る、先に確認を求める。

## Opening Plan

selected_patterns: [O1, O13]
selection_reason: 初回は待ち合わせの形で足場を作り、用件への触れ方で関係の入口を開く。
must_include:
  - O1: {seed['name']}が先に場にいて、主人公の到着を受ける。
  - O13: 主人公が関わる理由を、持ち込んだ用件で見せる。
4_jobs:
  hook: {seed['visible_handle']}が最初の掴みになる。
  orientation: 主人公は{seed['protagonist_role']}。
  agency: プレイヤーは用件を出すか、経緯を話すか、観察するかを選べる。
  unresolved: {seed['main_question']}
clarity_anchors:
  protagonist_role: 主人公は{seed['protagonist_role']}として扱われる。
  protagonist_purpose: 目の前の用件を、相手にどう渡すかを決めるために来ている。
  location_function: この場所は、人目がありつつ短い確認ができる日常の場である。
  heroine_relation: {seed['name']}とは初対面で、信用も警戒もまだ固まっていない。
opening_caveats:
  - 真相説明ではなく、見えている用件と相手の反応から始める。
"""


def _fallback_event_card_md(seed: dict[str, str]) -> str:
    return f"""# Event Card

今動いているストーリーイベントを、LILIAの内面と関係の変化に結びつけて記録します。
初回sceneでは、重い事件ではなく関係を少し動かす小さな出来事として扱います。
抽象的な違和感ではなく、今ユーザーが触れられる可視イベントを1つだけ置きます。
詳細な物語素材や未回収札は `story/story_deck.md` に分けます。

## Active Hook

- hook_id: {seed['main_hook_id']}
- hook_type: main
- status: active
- foreground_reason: 初回sceneでプレイヤーが今触れられる入口を、{seed['visible_handle']}に絞るため。
- 注: Active Hookは今触れる1本だけ。3hookを3択UIとして並べない。

## Scene Function

- function: 起点
- current_question: {seed['main_question']}
- entry_state: {seed['first_distance']}
- exit_condition: 用件の扱い方か、次に確かめる対象が一つ決まる。
- change_delta: {seed['name']}が主人公を、待てる相手か急かす相手かで仮判断する。
- next_hook_candidate: {seed['candidate_id']}
- 注: Story Function名は内部タグ。Play Mode本文へそのまま出さない。

## 表の出来事

- 主人公が{seed['protagonist_role']}として、{seed['name']}の前に小さな用件を持ち込む。

## Visible Problem

- 誰が困っているか: {seed['name']}。困っているとは言い切らず、用件の扱われ方を見ている。
- 何が止まりそうか: 用件だけを処理すると、二人の間に残る違和感と距離が動かない。
- 何に触れると入口になるか: {seed['visible_handle']}、持ち込まれた経緯、相手の反応。

## Player-Facing Entrance

- プレイヤーが最初に見える入口: {seed['visible_handle']}をどう扱うか。
- 主人公が関われる理由: 主人公は{seed['protagonist_role']}として、この用件を持ち込んでいる。
- 最初の一手で触れる対象: {seed['visible_handle']}
- 入口として見せる違和感 / 困りごと: 普通の用件だけでは終わらなさそうだが、真相はまだ見えない。

## Knowledge Boundary / Reveal Control

- allowed hidden truth:
  - まだGMだけが保持してよい真相: 用件の本当の出所、背後の意図、深い背景。
  - ヒロイン本人も知らない / 言語化できないこと: {seed['name']}がなぜ強く警戒しているかの深い理由。
- judgment material that must not be hidden:
  - 主人公が今判断するために本文で見せること: 主人公がここにいる理由、目の前の用件、相手の警戒。
  - ヒロインの台詞や態度から観察できること: 軽い言葉の奥に、相手の扱い方を見ている気配がある。
  - 物理的に見える手がかり: {seed['visible_handle']}と、{seed['name']}の手元や視線。
- reveal conditions:
  - 開示してよい条件: 主人公が経緯を話す、用件を見せる、本人確認や次の確認を求める。
  - 開示してよい主体: 地の文、{seed['name']}の短い確認、または共有された物証。
  - 開示されたら更新する knowledge_state key: shared_scene_entry、protagonist_current_purpose、heroine_suspicion
- do-not-reveal-yet:
  - まだ本文に書かないこと: 背後の意図の断定。
  - まだヒロインに言わせないこと: GMだけが知る真相や、本人がまだ言語化していない理由。
  - まだ主人公が知った扱いにしないこと: 用件の本当の出所と最終的な意味。
- 注: 真相を伏せても、判断材料と行動入口は伏せない。

## First Concrete Action

- 誰に / 何に: {seed['visible_handle']}
- どう触るか: 見せる、差し出す、経緯を話す、まだ渡さず確認する。
- 初回sceneで重すぎない一手: {seed['name']}が手元を見て、軽い言葉で扱い方を探る。

## Handles 2-4

- handle 1: 用件を見える場所に出す。
- handle 2: ここに来た経緯を短く話す。
- handle 3 optional: 相手の名前や目的を先に確認する。
- handle 4 optional: 周囲や相手の反応を観察する。
- 注: handlesは選択肢ではなく行動余地。

## Relationship Stake

- 早く答えを奪うか、相手がまだ言わない部分を境界として残せるか。

## Pressure / Agency

- pressure_source: protagonist_initiated
- initiator: protagonist
- passive_or_active: mixed
- pressure_summary: 主人公が持ち込んだ用件が、{seed['name']}の警戒と距離感に小さな圧をかける。
- 注: これはGM用。本文に pressure_source などの管理語を出さない。

## Observable Pressure

- 本文に出してよい観測可能な圧:
  - {seed['visible_handle']}がその場にある。
  - {seed['name']}の視線や沈黙が、用件の扱い方を測っている。
- ヒロインがその場で見えるもの:
  - 主人公が{seed['visible_handle']}を持ち込んでいること。
- 主人公がその場で見えるもの:
  - {seed['name']}がすぐには答えを出さないこと。
- まだ観測できないもの:
  - 用件の本当の出所や最終的な意味。

## Heroine Initiative Candidate

- ヒロインが自分から動くなら:
  - {seed['name']}が、用件の扱い方を短く確認する。
- 発火条件:
  - 主人公が用件を見せる、または経緯を話す。
- その動きの根拠になる state, relationship, memory, beliefs:
  - state: 警戒しながらも、用件の扱い方は確認したい。
- 禁止: scene function や relationship stake を直接理由にしない。

## Pressure Conversion Rule

- GM内部圧:
  - 背景真相やrelationship stakeを急いで説明したくなる圧。
- 観測可能な形へ変換:
  - 視線、沈黙、手元、距離、短い確認に変換する。
- 台詞・所作への変換:
  - {seed['name']}らしい短い確認や、言い切らない反応にする。

## Crisis / Ability Check

- crisis pressure: 日常の場所に、予定外の用件が入り込んでいる。
- possible responses:
  - 逃げる: 用件だけ残して距離を取る。
  - 守る: 相手の境界線を急かさず、扱い方を慎重にする。
  - 交渉する: どこまで情報を交換するか短く決める。
  - 隠す: 周囲に見せない形で用件を扱う。
  - 耐える: 分からない部分を残したまま会話を続ける。
  - 助けを呼ぶ: 初回では原則使わず、危険が見えた時だけ検討する。
  - 能力を使う: 初期sceneでは扱わない。
  - あえて戦わない: 受け渡しと観察だけで終える。
- ability constraint:
  - can: 初回では通常の観察と会話だけを使う。
  - cannot: 能力や特殊解決で関係や真相を即時処理しない。
  - condition: 能力導入が正式に起きた時だけ再評価する。
  - cost: 初回では設定しない。
  - trace: 初回では残さない。
  - risk: 会話の焦点が管理説明へ寄ること。
- relationship risk: 境界線を詰めると、{seed['name']}の返事が短くなる。
- post-crisis residue: 主人公が用件をどう扱ったかが、次の距離感に残る。

## If Ignored

- {seed['name']}は用件だけを受け取り、次の接触では冗談を少し硬くする。

## Next Visible Change

- {seed['name']}が情報を一つだけ増やすか、逆に距離を保つ理由を作る。
- 声 / 沈黙 / 呼び方 / 距離に出る変化: 声が低くなる。

## 進行状態

- status: 継続
- 触れられたhandle: 初回開始前
- relationship stakeの変化: これから判定する
- if ignoredの発火: まだ発火していない
- 次に更新するvisible change: 用件の扱い方への反応
- story_deckへ落とす未回収札: 用件の出所と次の確認先

## Story Residue

- memoryに残るもの: 主人公が用件をどう扱ったか。
- relationshipに残るもの: 境界線を待てる相手かどうか。
- beliefsに残るもの: 主人公が巻き込まれた側か、仕掛け側かの仮説。
- voiceに残るもの: 近づくが触れない距離、短い確認の言い方。
- story_deckへ戻す未回収札: 次の確認。
- NPC / Contact note optional: 必要が出るまで背景に置く。

## Truth Hiding Boundary

- 隠してよい真相: 用件の本当の出所、背後の意図、{seed['name']}がまだ言語化しない警戒。
- 見せる入口: {seed['visible_handle']}が普通の用件だけでは終わらなさそうな違和感。

## Intimacy / Boundary Check

- 親密sceneの場合だけ確認: 初回は親密sceneとして扱わない。
- intimacy stage: 初対面
- consent stage: 確認前
- boundary state: 待つ
- 成人/合意/相互性/境界線/止まれる余地: 成人同士。都度確認する。
- aftercareまたは翌朝の第一声: 初回では対象外。
- 雑な乱入になっていないか: 外圧は関係の選択を揺らす範囲に留める。

## 揺れるLILIA

- {seed['name']}は明るさを保ちながら、用件の扱われ方と主人公の間を見ている。

## その出来事がLILIAに刺さる理由

- {seed['relationship_theme']}

## ユーザーへの問い

- 選択肢ではなく、行動余地として書く: 用件をどう扱い、どこまで経緯を話すか。
- 必要なら自然な候補: 差し出す / 経緯を話す / 先に確認する / 周囲を見る。
- 自由入力の余白: 便利屋らしい態度、警戒、軽口、沈黙を自由に出せる。

## 関係に残る変化

- {seed['name']}が主人公を、用件を任せられる相手かどうかで見始める。
- 親密scene後に保存するもの: 初回では発生させない。
"""


def _fallback_hotset_md(seed: dict[str, str]) -> str:
    return f"""# Hotset

再開時に最初に読む、短い現在状態のまとめです。
チェックリストや正解手順ではなく、次の1ターンに効く温度だけを短く上書きします。

## 会話の温度

- {seed['place']}で、{seed['name']}が主人公の持ち込んだ用件を見ている。

## 呼び方 / 距離のアンカー

- 初回は「あなた」など、まだ距離を残した呼び方を使う。
- 注: ここはechoであり、正本は `lilia/main/voice.md` と `lilia/main/relationship.md`。

## 次に会った時の第一反応

- {seed['name']}はまず手元と用件を見て、短い言葉で扱い方を確かめる。

## 未消化の感情

- 任せたい気配と、任せることで弱点になる警戒が同居している。

## 言い残し / まだ言っていないこと

- 用件の本当の出所、背後の意図、自分がどこまで察しているか。

## 親密scene後の余韻

- 次回1ターンに効くaftercare: 初回では扱わない。
- 第一反応: 近づきすぎず、用件の扱いを先に見る。
- 呼び方 / 距離の変化: まだ変化前。
- まだ触れないこと: 真相と深い身元。

## 最新scene後のecho

memory.md の echo から、次の1ターンに効くものだけを短く抜く。
hotset は正本ではない。memory.md の echo を更新したら hotset の echo も再生成する。

- 次の1ターンに響くこと: 主人公が用件をどう扱うか。
- 第一反応の方向: 明るさを残しつつ、返事は短く確かめる。
- まだ触れない方がいいこと: 真相の断定。

## 現在のイベント要約

- 主人公が{seed['protagonist_role']}として、{seed['visible_handle']}を{seed['name']}の前に持ち込む。

## 次の小さな出来事

- 用件を出す、経緯を話す、先に本人確認する、周囲を見る。

## 未確定の余白

- 誰がこの用件を二人の間に置いたのかは、まだ保留にする。

## 次にユーザーへ向き合う時の空気

- 明るさと観察、近さと境界線が同時にある。
"""


def _fallback_relationship_overview_md(seed: dict[str, str]) -> str:
    return f"""# Relationship Overview

現在の関係全体を短く把握するための補助要約です。
詳細ログではなく、再開時に関係の現在形を掴むために使います。
正本ではなく、`relationship`、`memory`、`beliefs` の軽量入口として扱います。

## 現在の関係全体の要約

- 初対面。主人公は{seed['protagonist_role']}として、{seed['name']}の前に用件を持ち込む。

## 距離感

- 会話は始まるが、信用も警戒もまだ決まっていない。

## 呼び方 / 声のアンカー

- 初回は「あなた」など距離を残した呼び方。声は軽くても、核心は簡単に渡さない。

## 親密さの初期扱い

- 未確認 / 関心段階 / 明示的親密なし

## intimacy / consent / boundary

- intimacy stage: 初対面
- consent stage: 確認前
- boundary state: 待つ
- 現在形の一言: 近い反応は観察であり、私的な許可ではない。

## 信頼

- まだ成立していない。用件の扱い方で仮判断する。

## 警戒

- 高め。相手が何を知っていて、どこまで踏み込むかを見る。

## 興味

- 主人公が急かす相手か、待てる相手かに興味がある。

## 甘え

- まだ発生していない。頼るとしても短い依頼の形に留める。

## 衝突

- {seed['name']}は近づくが、自分の情報は簡単に渡さない。

## 誤解や思い込み

- 主人公が巻き込まれた側か、仕掛け側かは保留している。

## 保留

- 用件の本当の出所、背後の意図、深い身元。

## 境界線

- 接触なし。秘密や危険な依頼は都度確認する。

## resume時に無かったことにしないもの

- 用件はただの日常処理ではなく、関係の入口として扱う。

## 次に変化しそうな点

- 主人公が用件をどう扱うかで、信頼か警戒のどちらかへ少し動く。

## 最新チェックポイント

直近の重要scene後に、今のLILIAの空気を散文で1-3行保存する。
データ層（intimacy stage、距離感）では拾えない質感を残すための層。
Save Mode でのみ更新する。Play Mode では更新しない。

- イベント名: 初回scene前
- LILIAの空気: 明るさと警戒が同じ場所にある。
- 核（このsceneで何がLILIAに残ったか）: 主人公の扱い方をこれから見る。

注: データではなく散文で書く。「intimacy stage 4」ではなく「声を隠さないと決めた」と書く。
全部の重要sceneで更新する必要はない。質感が変わった時だけ更新する。
古いチェックポイントは上書きしてよい。長期保存は archive/beats/ に任せる。
"""


def _fallback_story_deck_md(seed: dict[str, str]) -> str:
    return f"""# Story Deck

関係を揺らし、LILIAの内面や距離感を変化させるstory素材と未回収札の整理です。
例文集ではなく、次イベント判断に必要なものだけを置きます。
story_deckは素材棚です。Active Hookそのものは `current/event_card.md` 上部に置きます。
Main / Relationship / Life-Explorationの3hookを、Play Mode本文の3択UIとして出しません。

## Three Hook Spine

### Main Hook
- hook_id: {seed['main_hook_id']}
- status: active
- current_function: 起点
- current_question: {seed['main_question']}
- visible_handle: {seed['visible_handle']}
- pressure: 日常の用件に、相手の反応を測る圧が混ざる。
- exit_condition: 用件の扱い方か次に確かめる対象が一つ決まる。
- next_candidate: {seed['candidate_id']}

### Relationship Hook
- hook_id: {seed['relationship_hook_id']}
- status: background
- current_function: 目標
- current_question: {seed['name']}は、主人公を境界を待てる相手として見られるか。
- relationship_stake: 秘密を奪うのではなく、言わない部分を残したまま同じ問題へ向けるか。
- boundary_or_trust_issue: 近さ、待つこと、情報を交換条件にしないこと。
- exit_condition: {seed['name']}の声や距離に、小さな信頼か警戒が出る。
- next_candidate: 境界線を尊重した後の短い依頼。

### Life-Exploration Hook
- hook_id: {seed['life_hook_id']}
- status: background
- current_function: 始動
- current_question: {seed['name']}の日常の場所は、どこまで主人公を受け入れるか。
- available_scope: {seed['place']}
- travel_or_life_option: 再訪、帰り道、短い移動、日常の用事。
- heroine_attendance: {seed['name']}本人が選んだ時だけ同行する。
- exit_condition: 表の生活側に戻れる入口が一つ見える。
- next_candidate: 日常の場所での再確認。

注:
- status候補: background, active, pending, advanced, resolved, worsened, blocked, archived
- story_deck上のhookは原則 background, pending, advanced, resolved, worsened, blocked, archived として扱う。
- `active` は現在のActive Hookとの対応を示す参照に限る。今触れる可視イベント本体は `current/event_card.md` に置く。
- current_function は内部診断タグであり、Play Mode本文へそのまま出さない。

## 現在使えるstory素材

- {seed['visible_handle']}。中身や真相ではなく、扱い方が関係を動かす。
- {seed['place']}。日常の場に、小さな違和感が混ざる。
- {seed['name']}の明るさと警戒の差。

## 初回sceneで使う小さな出来事

- 素材名 / 未回収札: {seed['visible_handle']}
- 現在sceneで触る内容は `current/event_card.md` に置く

## 関係を揺らす圧

- 用件だけを処理すると、相手を待てるかどうかの判断が残る。

## 未回収札

- 用件の本当の出所。
- {seed['name']}がまだ言わない警戒。
- 次にどこで確認するか。

## 背景化したevent_card

- 現在sceneから外れた出来事: 初回前なので背景化した出来事はない。
- 後で戻す条件: 用件の出所や境界線が残った時。
- 関係に残った圧: 主人公が待てる相手かどうか。

## Background Hooks

- hook_id: {seed['relationship_hook_id']}
- hook_type: relationship
- status: background
- reason_backgrounded: Active Hookは目の前の用件に絞るため。
- return_condition: {seed['name']}が言わないことを待たれる、または急かされる。
- last_known_state: 初回前。

注:
- Background Hooks は、今は前景化していないhookの素材棚です。
- Active Hook以外の2本を消さず、関係・生活・事件の戻り口として短く保持します。
- ここにあるhookはPlay Mode本文でそのまま提示せず、current/event_card.md のActive Hookに昇格した時だけ今触れる入口になります。

## Candidate Next Hooks

- candidate_id: {seed['candidate_id']}
- source_hook_id: {seed['main_hook_id']}
- hook_type: main
- function_candidate: 次の確認
- visible_entry: 用件の経緯、次に確かめる対象、場を変えるかどうか。
- promotion_condition: 初回sceneで用件の扱い方が決まる。
- grounding_guard: 大きな真相説明に寄せず、{seed['name']}の反応と境界線で動かす。

注:
- Candidate Next Hook は次scene候補であり、まだactive eventではありません。
- resume入口に使う場合は、current/scene.md、current/event_card.md、current/hotset.md へpromotionします。
- story/story_deck.mdに候補として残しただけでは、resume 1ターン目の入口として扱いません。
- current/event_card.md の上部は、今ユーザーが触れるActive Hookだけを持ちます。

## World Pressure / 1-3 Scene Return

- 戻る可能性のある圧: 用件の出所。
- 何scene後に小さく戻るか: 1-3 scene後。
- 戻る形: 連絡、再訪、別の小さな依頼、日常側の違和感。
- LILIAとの関係に何を問い直すか: 情報を渡す範囲と、相手を巻き込む覚悟。
- 親密sceneを雑に壊さないための注意: 外圧は関係の選択を揺らすために使う。

## Crisis / Ability Echo

- unresolved trace: 用件の出所が残る。
- delayed cost: 次の確認で、相手をどこまで巻き込むかが問われる。
- returning pressure: 日常の場に別経路の連絡が戻る可能性。
- relationship risk still active: 境界線を急かすと警戒が増える。
- LILIAがまだ言えていないこと: 自分がどこまで察しているか。
- 1-3 scene後に戻る形: 短い連絡、再訪、目に見える違和感。

## NPC / Contact Notes

- name or label: 背景の連絡元
- tier: 1
- current role: 用件を二人の間に置いた可能性のある存在
- promotion trigger: 連絡や物証が次に出た時
- storage destination: story_deck
- known: 用件が現在sceneにある
- suspected: 背後に意図がある
- unknown: 誰が何のために置いたか
- LILIAの記憶/関係/beliefsへの影響: 主人公を巻き込むかどうかの判断に響く

## まだ使わない未回収札

- 深い真相や過去は、初回では説明しない。

## 次に使うなら

- 用件の経緯確認、場所を変える提案、{seed['name']}からの短い依頼。
"""


def _fallback_visible_handle(
    *,
    story_sections: dict[str, str],
    opening_entry: str,
    visible_props: str,
    name: str,
) -> str:
    """Return one playable problem, not a raw prop inventory."""

    reveal_entry = _first_reveal_ladder_item(story_sections.get("reveal ladder", ""))
    candidates = [
        _paraphrase_story_problem(reveal_entry),
        _paraphrase_story_problem(opening_entry),
    ]
    if not _looks_like_prop_inventory(visible_props):
        candidates.append(_compact_seed_text(visible_props, "", limit=40))
    candidates.append(f"{name}の前に出された用件の確認")
    for candidate in candidates:
        value = _compact_seed_text(candidate, "", limit=40)
        if value and not _looks_like_prop_inventory(value):
            return value
    return "目の前の用件をどう確認するか"


def _first_reveal_ladder_item(section: str) -> str:
    for raw_line in section.splitlines():
        line = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", raw_line).strip()
        if not line:
            continue
        if "[pending]" not in line and "[revealed]" in line:
            continue
        line = re.sub(r"\[[^\]]+\]\s*", "", line).strip()
        if line:
            return line
    return ""


def _paraphrase_story_problem(text: str) -> str:
    value = _clean_seed_value(text)
    if not value:
        return ""
    if "USB" in value or "ＵＳＢ" in value:
        return "黒いUSBの受け渡しと出所確認"
    if "預かり票" in value and "伝票" in value:
        return "濡れた伝票と控えの照合"
    if "伝票" in value and "番号" in value:
        return "読めない伝票番号の照合"
    if "忘れ物" in value or "落とし物" in value:
        return "忘れ物の返し方と本人確認"
    if "食い違" in value:
        subject = value.split("食い違", 1)[0]
        subject = subject.rsplit("、", 1)[-1]
        subject = re.sub(r"[がはをにでと、。\s]+$", "", subject).strip()
        if subject:
            return f"{subject}の食い違いの確認"
    if "確認" in value or "照合" in value or "返" in value or "渡" in value:
        return value
    return ""


def _generic_protagonist_role(value: str) -> bool:
    normalized = _clean_seed_value(value)
    return normalized in {
        "",
        "その場の用件に関わる人物",
        "この場の用件に関わる人物",
    }


def _fallback_protagonist_role(
    *,
    visible_handle: str,
    opening_entry: str,
    visible_props: str,
) -> str:
    text = " ".join([visible_handle, opening_entry, visible_props])
    if "修理" in text or "受付" in text or "預かり票" in text or "伝票" in text:
        return "濡れた伝票と控えを持ち込み、受付で確認を求める来店者"
    if "USB" in text or "ＵＳＢ" in text:
        return "黒いUSBを返しに来た便利屋"
    if "忘れ物" in text or "落とし物" in text:
        return "忘れ物を本人に返しに来た人物"
    return "目の前の用件を本人に確認しに来た人物"


def _looks_like_prop_inventory(value: str) -> bool:
    text = _clean_seed_value(value)
    if not text:
        return False
    separator_count = text.count("、") + text.count(",") + text.count("・")
    prop_mentions = len(
        re.findall(
            r"メモ帳|ペン|伝票|控え|ミント缶|スマホケース|鍵|封筒|USB|グラス|名刺入れ|紙片",
            text,
        )
    )
    if separator_count >= 4 and prop_mentions >= 4:
        return True
    if separator_count >= 3 and prop_mentions >= 3 and not re.search(
        r"確認|照合|返|渡|選|決|困|食い違|読め|見つから|扱|受け渡し|出所",
        text,
    ):
        return True
    return False


def _protagonist_role_from_answers(answers: object) -> str:
    if not isinstance(answers, dict):
        return "その場の用件に関わる人物"
    q8 = _answer_text(answers, 8)
    if not q8 or q8 in {"おまかせ", "お任せ"}:
        return "その場の用件に関わる人物"
    job_match = re.search(r"(?:仕事|職業|立場)\s*[:：]\s*([^。\n]+)", q8)
    if job_match:
        return _clean_seed_value(job_match.group(1))
    return _compact_seed_text(q8, "その場の用件に関わる人物", limit=24)


def _profile_bullet_value(section: str, label: str) -> str:
    match = re.search(rf"^\s*[-*]\s*{re.escape(label)}\s*[:：]\s*(.+)$", section, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _first_drift_guard(section: str) -> str:
    for raw_line in section.splitlines():
        line = re.sub(r"^\s*[-*]\s*", "", raw_line).strip()
        if not line:
            continue
        return line.split(" - ", 1)[0].strip()
    return ""


def _compact_seed_text(text: str, default: str, *, limit: int = 96) -> str:
    value = _clean_seed_value(text)
    if not value:
        value = default
    value = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\[pending\]\s*", "", value)
    if len(value) > limit:
        value = value[:limit].rstrip("、。,. ") + "。"
    return value or default


def _clean_seed_value(text: str) -> str:
    value = str(text or "").replace("\n", " / ").strip()
    value = re.sub(r"おまかせ|お任せ|TODO|PLACEHOLDER|placeholder", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\s+", " ", value).strip(" /")
    return value


def _is_unspecified_input_fragment(value: str) -> bool:
    compact = re.sub(r"\s+", "", str(value or "")).strip("「」『』'\"")
    return compact in {
        "",
        "おまかせ",
        "お任せ",
        "まかせ",
        "まかせる",
        "任せる",
        "任せます",
        "未指定",
        "特になし",
        "なし",
        "かせ",
    }


def _answer_or_default(value: str, default: str) -> str:
    return default if _is_unspecified_input_fragment(value) else value


def _write_log(logger: Any, event: str, **fields: object) -> None:
    if logger is None or not hasattr(logger, "write"):
        return
    try:
        logger.write(event, **fields)
    except Exception:
        return


def _timeout_label() -> str:
    try:
        return f"{engine_timeout_seconds():g}"
    except Exception as exc:
        return f"invalid:{exc}"


def _format_engine_failure(
    exc: BaseException,
    *,
    phase: str,
    engine: str,
    target_group: str,
    timeout_seconds: str,
    session_name: str,
) -> str:
    return (
        f"{exc} "
        f"(apply_newgame_phase={phase}; "
        f"engine={engine}; "
        f"target_group={target_group}; "
        f"timeout_seconds={timeout_seconds}; "
        f"session_name={session_name})"
    )


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
    parts = [
        part.strip()
        for part in re.split(r"[、,/／。\n]+", q8)
        if part.strip() and not _is_unspecified_input_fragment(part)
    ]
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
            if value and value not in {"(未設定)", "未設定"} and not _is_unspecified_input_fragment(value):
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
    visual_anchor = _answer_or_default(_profile_quality(profile) or _answer_text(answers, 3), "未確定")
    background_truth = _answer_or_default(story_fields.get("background_truth") or _answer_text(answers, 5), "未確定")
    constraints = _answer_or_default(_answer_text(answers, 9), "特になし")

    item_specs = [
        dict(key="protagonist_call_name", value=_answer_or_default(_answer_text(answers, 7), "未確定"), fictional_status="meta", source="protagonist", known_to=["protagonist"], acquired_at="pre_play", weight="medium", notes="希望呼称 / 開示後呼称。ヒロインが知る経路がない時点では使わない。自己紹介、伝票、名札、予約名、他者紹介などの装置を経由する"),
        dict(key="protagonist_gender", value=fields["gender"], fictional_status="observable", source="protagonist", known_to=["protagonist"], acquired_at="pre_play", weight="low", notes="視覚的に観察可能"),
        dict(key="protagonist_height", value=fields["height"], fictional_status="observable", source="protagonist", known_to=["protagonist"], acquired_at="pre_play", weight="low", notes="視覚的に観察可能"),
        dict(key="protagonist_build", value=fields["build"], fictional_status="observable", source="protagonist", known_to=["protagonist"], acquired_at="pre_play", weight="low", notes="視覚的に観察可能"),
        dict(key="protagonist_style", value=fields["style"], fictional_status="observable", source="protagonist", known_to=["protagonist"], acquired_at="pre_play", weight="low", notes="視覚的に観察可能"),
        dict(key="protagonist_occupation", value=fields["occupation"], fictional_status="meta", source="protagonist", known_to=["protagonist"], acquired_at="pre_play", weight="medium", notes="主人公がscene内で開示するまでヒロインは知らない"),
        dict(key="heroine_name", value=name, fictional_status="meta", source="heroine_self_disclosure", known_to=["heroine"], acquired_at="pre_play", weight="high", notes="ヒロイン本人とGMは知っているが、主人公 / player-facing scene では未開示。名乗り、名札、看板、予約表などで開示されると shared に昇格"),
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
    opening_seed_block = _opening_seed_prompt_block(context)
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
7. current/event_card.md は原則1, 3, 4, 5を意識し、Visible Problem / Relationship Stake / Pressure / Observable Pressure / Next Visible Change に感情の圧と未完了を残す。
   `## Active Hook` と `## Scene Function` は内部補助であり、既存の Visible Problem / First Concrete Action / Handles / Relationship Stake / If Ignored / Next Visible Change を置き換えない。
   Story Function名やhook statusをPlay Mode本文のように説明せず、event_card内の診断メモとして短く置く。
8. current/event_card.md の `## Player-Facing Entrance`、`## Pressure / Agency`、`## Observable Pressure`、`## Knowledge Boundary / Reveal Control` は必ず埋める。
   真相は隠してよいが、プレイヤーが今判断するための材料は隠さない。
   Pressure SourceやRelationship Stakeはヒロインの知識ではない。本文へ出す前に観測可能な状況、沈黙、所作、台詞、返せる入口へ変換する。
   allowed hidden truth / do-not-reveal-yet にはGMだけの真相を置き、judgment material には本文で見せる足場を置く。
   reveal conditions には「何が起きたら、誰が、どの knowledge_state key を更新するか」を短く書く。
9. current/scene.md は原則2, 3, 5を意識し、感情名ではなく身体反応、環境、予想との差、未解決の要素で初回sceneを始める。
   `## Player Orientation` は必ず埋める。主人公がここにいる理由、開始時点で知っていること、冒頭本文で必ず見せる前提、まだ隠すことを分ける。
   プレイヤーが知らない前提で判断を迫らない。
10. current/hotset.md は原則5を意識し、再開時に戻す未完了の余白を短く残す。
11. current/scene.md の末尾に必ず `## Opening Plan` セクションを出す。
    Q&A の Q3（描写の縛り）、Q5（内面に持っているもの）、Q6（出会い + 関係性の起点）、Q9（避けたい展開）、
    character YAML、profile.md、story_spine の Background Truth / Drift Guard を解釈し、
    下の Opening Pattern Stock から A群 1 + D群 1（必須） + B群またはC群から最大1（任意）を選ぶ。
12. Opening Pattern の選択ルール:
    - 必ず A群（O1-O4）から1つ、D群（O13-O15）から1つ。
    - B群（O5-O8）またはC群（O9-O12）から任意で1つ追加可。
    - 3つ以上の混在は禁止。
    - 同じ群から2つ採用するのは禁止。
    - Q9に「停滞を避けたい」がある場合、O9 / O10 / O14 を優先候補にする。
    - Q5に過去の傷・秘密が強い場合、O5 / O11 を候補にする。
    - Q6が偶然の出会いの場合、O13 / O14 を候補にする。
13. `## Opening Plan` は以下の固定フォーマットで出す。空欄、未設定、TODO、placeholder を残さない。

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

14. `clarity_anchors` は冒頭本文を書く LLM が自然な描写へ織り込むための足場である。
    説明調にせず、役割・目的・場所機能・関係性を1行の描写に含められる具体度で書く。
    悪い例: 「鴉ノ宿のガラス戸を細く叩いていた」
    良い例: 「オカルトショップ『鴉ノ宿』のガラス戸を、雨が細く叩いていた」
15. `must_include` は選んだパターンの「形」から必須要素を1-2個抜く。
    O3: 視覚情報は最後、音/匂い/温度を先に置く。2感覚までで止める。
    O14: 発見の瞬間から始める。助けた後から始めない。助ける/通過/様子を見る余地を残す。
    O15: 日常のルーチンが先、違和感は1-2点で止める。
16. `## 次に起きそうなこと` は Opening Plan の `agency` と矛盾させない。プレイヤーの選択を奪わない。
17. `## 直前のやりとり` は Opening Plan の `4_jobs.hook` と整合させる。
18. story/story_deck.md の `## Three Hook Spine` は素材棚である。
    Main / Relationship / Life-Explorationを3択UIとして並べず、現在のActive Hook本体は current/event_card.md へ置く。
    Background Hooks / Candidate Next Hooks はmaterial shelfであり、今すぐPlay Modeで前景化しない候補として短く保持する。
    Active Hook以外の2本hookを消さず、activeでないhookはBackground Hooksへ残す。
    next_hook候補はCandidate Next Hooksへ残す。ただしCandidate Hookをresume入口に使う場合はcandidate promotionが必要で、
    current/scene.md / current/event_card.md / current/hotset.md のactive stateが同じ入口を指すようにそろえる。
    Background / Candidate Hookのhook_id、status、candidate_idなどの管理語はPlay Mode本文に出さない。
19. story/story_deck.md の `## Three Hook Spine` では、初期3hookを必ず埋める。
    空欄、未設定、TODO、placeholderを残さない。profile / character.yaml / story_spine / relationship_spine / Q&Aから短く生成する。
    必ず `## Three Hook Spine` の直下に、以下の `###` 小見出しとfield名をこの順番で出す。
    ```md
    ### Main Hook
    - hook_id: main_initial_request のような短いID
    - status: active または background
    - current_function: 起点 / 目標 / 始動 / 試練 のいずれか
    - current_question: このMain Hookで追う問い
    - visible_handle: プレイヤーが触れる外側の出来事
    - pressure: 小さな圧
    - exit_condition: 閉じてよい条件
    - next_candidate: 次に接続する候補

    ### Relationship Hook
    - hook_id: relationship_first_trust のような短いID
    - status: active または background
    - current_function: 起点 / 目標 / 始動 / 試練 のいずれか
    - current_question: 距離や境界線の問い
    - relationship_stake: 関係に残る賭け
    - boundary_or_trust_issue: 境界線、信頼、誤解、約束、保留
    - exit_condition: 関係変化が見えたと判断する条件
    - next_candidate: 次に接続する候補

    ### Life-Exploration Hook
    - hook_id: life_revisit_route のような短いID
    - status: active または background
    - current_function: 起点 / 目標 / 始動 / 試練 のいずれか
    - current_question: 生活や移動から戻る問い
    - available_scope: 今自然に動ける生活圏
    - travel_or_life_option: 帰宅、再訪、食事、単独行動、移動など
    - heroine_attendance: 同行/非同行/保留/条件付きの扱い
    - exit_condition: 生活行動が次の入口へ接続する条件
    - next_candidate: 次に接続する候補
    ```
    - Main Hook: hook_id / status / current_function / current_question / visible_handle / pressure / exit_condition / next_candidate
      外側の出来事、依頼、小事件、仕事、街の圧、小さな謎を扱う。hook_idは `main_initial_request` のような安定した短いIDにする。
    - Relationship Hook: hook_id / status / current_function / current_question / relationship_stake / boundary_or_trust_issue / exit_condition / next_candidate
      好感度や攻略ルートではなく、距離、信頼、境界線、約束、誤解、LILIAが主人公をどう同じ場に置けるかを扱う。
    - Life-Exploration Hook: hook_id / status / current_function / current_question / available_scope / travel_or_life_option / heroine_attendance / exit_condition / next_candidate
      生活、場所、移動、帰宅、食事、単独行動、遠出、同行/非同行の受け皿を扱う。初期値は現在の場所・生活圏に自然な入口にする。
    statusは初期Active Hookに対応する1本だけ `active` 参照にしてよい。それ以外は background / pending など軽い状態にする。
    `## Background Hooks` には、少なくとも hook_id / hook_type / status / reason_backgrounded / return_condition / last_known_state を使える形で、
    今は前景化していないhookを素材棚として残す。
    `## Candidate Next Hooks` には、少なくとも candidate_id / source_hook_id / hook_type / function_candidate / visible_entry / promotion_condition / grounding_guard を使える形で、
    scene closure後の次候補を素材棚として残す。ここに残しただけではactive eventにしない。
20. current/event_card.md の `## Active Hook` には、初期sceneで今触れるhookを1本だけ入れる。
    通常はMain Hookをactiveにする。Q&Aやprofile上、関係起点が強い場合だけRelationship Hookにしてよい。
    Life Hookをactiveにするのは、初回sceneが移動、再訪、生活導線から始まる場合だけ。
    `hook_id` は story/story_deck.md 側の対応hookと一致させ、`hook_type` は main / relationship / life のどれかにする。
21. current/event_card.md の `## Scene Function` には、初回sceneの内部診断を入れる。
    functionは 起点 / 目標 / 始動 / 試練 を基本にする。初回から奈落 / 選択 / 着地 / 余韻へ飛ばしすぎない。
    current_question / entry_state / exit_condition / change_delta / next_hook_candidate を必ず埋める。
    Exit ConditionとChange Deltaは、sceneの入口と出口で何が変われば閉じてよいかを示す。
22. Three Hook / Story Function / hook_id / status / Scene Function名は内部stateである。
    Play Mode本文として説明しない。番号付き3択、ボタン、同時質問、管理語の露出として書かない。
23. 下の `Opening Seed` は初回sceneの制御値である。
    Active Hook の hook_id / hook_type / status、Scene Function の function、Player Orientation の足場は seed を正とする。
    AI判断で変更しない。空欄化しない。別名へ置き換えない。
    foreground_reason / current_question / entry_state / exit_condition / change_delta / next_hook_candidate も、
    seedに値がある場合はそれを優先し、足りない自然文だけを周辺文脈に合わせて補う。

## Opening Seed

以下はAIが決め直してはいけない制御値である。特に hook_id / hook_type / status / function は seed 固定。

```text
""" + opening_seed_block + """
```

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
9. Name Disclosure Boundary:
   - Q7の呼ばれ方は desired_call_name / 開示後呼称であり、初回からヒロインが知っている呼称ではない。
   - protagonist_call_name は fictional_status: meta、known_to: [protagonist] とし、自己紹介、名刺、伝票、予約名、名札、看板、他者紹介などで共有されるまでヒロインの台詞に使わせない。
   - ヒロイン名は heroine_name として保持してよいが、自己紹介前は fictional_status: meta、known_to: [heroine] とし、player-facing本文では「彼女」「占い師の女性」など見えている呼び方を優先する。
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
    headings = [line.strip() for line in text.splitlines() if line.startswith("## ") or line.startswith("### ")]
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
