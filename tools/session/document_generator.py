"""AI bridge for generating LILIA downstream session markdown documents."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any

from tools.session.document_validator import validate_session_documents


ROOT = Path(__file__).resolve().parents[2]
MAX_ATTEMPTS = 3
ENGINE_TIMEOUT_SECONDS = 300

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

    group_a = _generate_group(
        group_name="group_a",
        rel_paths=GROUP_A_PATHS,
        prompt=_build_group_a_prompt(context),
        answers=answers,
        story_spine_md=story_spine_md,
        engine=engine,
        context=context,
    )
    documents.update(group_a["documents"])
    group_meta["group_a"] = group_a["meta"]

    group_b = _generate_group(
        group_name="group_b",
        rel_paths=GROUP_B_PATHS,
        prompt=_build_group_b_prompt(context),
        answers=answers,
        story_spine_md=story_spine_md,
        engine=engine,
        context=context,
    )
    documents.update(group_b["documents"])
    group_meta["group_b"] = group_b["meta"]

    group_c = _generate_group(
        group_name="group_c",
        rel_paths=GROUP_C_PATHS,
        prompt=_build_group_c_prompt(context),
        answers=answers,
        story_spine_md=story_spine_md,
        engine=engine,
        context=context,
    )
    documents.update(group_c["documents"])
    group_meta["group_c"] = group_c["meta"]

    valid, errors = validate_session_documents(
        documents,
        answers,
        story_spine_md=story_spine_md,
        expected_paths=ALL_PATHS,
    )
    if not valid:
        raise DocumentGenerationError("combined downstream validation failed: " + "; ".join(errors[:8]))

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


def _generate_group(
    *,
    group_name: str,
    rel_paths: list[str],
    prompt: str,
    answers: dict,
    story_spine_md: str,
    engine: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidates = _engine_candidates(engine)
    previous_error = ""
    cli_failures: list[str] = []

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
        for candidate in candidates:
            try:
                raw_output = _run_engine(candidate, attempt_prompt)
                engine_used = candidate
                break
            except DocumentGenerationError as exc:
                cli_failures.append(f"{candidate}: {exc}")
                if engine != "auto":
                    raise
        if not raw_output or not engine_used:
            detail = "; ".join(cli_failures[-4:]) or "no engine produced output"
            raise DocumentGenerationError(f"{group_name}: generation could not start: {detail}")

        try:
            parsed = _parse_file_blocks(raw_output, rel_paths)
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

    raise DocumentGenerationError(
        f"{group_name}: generation failed after 3 attempts: {previous_error or 'unknown validation error'}"
    )


def _engine_candidates(engine: str) -> list[str]:
    if engine not in {"codex", "claude", "auto"}:
        raise DocumentGenerationError("engine must be one of: codex, claude, auto")
    if engine == "auto":
        return ["codex", "claude"]
    return [engine]


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
    raise DocumentGenerationError(f"unsupported engine: {engine}")


def _run_engine(engine: str, prompt: str) -> str:
    command, stdin_text = _build_engine_command(engine, prompt)
    env = os.environ.copy()
    try:
        result = subprocess.run(
            command,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=ENGINE_TIMEOUT_SECONDS,
            env=env,
        )
    except FileNotFoundError as exc:
        raise DocumentGenerationError(f"{engine} command was not found") from exc
    except subprocess.TimeoutExpired as exc:
        raise DocumentGenerationError(
            f"{engine} generation timed out after {ENGINE_TIMEOUT_SECONDS} seconds"
        ) from exc

    if result.returncode != 0:
        stderr = result.stderr.strip() or "(no stderr)"
        raise DocumentGenerationError(f"{engine} CLI failed: {stderr}")
    if not result.stdout.strip():
        raise DocumentGenerationError(f"{engine} CLI returned empty output")
    return result.stdout


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
    return _build_base_prompt(
        context=context,
        rel_paths=GROUP_A_PATHS,
        role="あなたは LILIA セッションの初回シーン素材を作る設計者です。",
        constraints="""
1. 各ファイルは異なる目的を持つ。同じ文や同じ素材を複数ファイルへコピペしない。
2. 文を途中で切らない。「...」「…」で終わらせない。
3. 全セッション共通のテンプレ表現を使わない。
   禁止: 「次の行動の判断について、急かさず短く聞く」
   禁止: 「{ヒロイン名}が自分で決めるまで待つ」
   禁止: 「{ヒロイン名}に名乗る / 名前を聞く」
   禁止: 「{物}に触れず、扱い方だけを提案する」
4. Initial Scene Anchors は切り貼りせず、それぞれのファイルの目的に合わせて再構成する。
5. story_spine の Background Truth と [pending] の Reveal Ladder は GM only として隠す。
   scene/event_card/hotset/relationship_overview/story_deck へ直接書かない。
6. event_card の handles は選択肢UIではなく、このヒロイン固有の現在状況へ触れる入口にする。
""",
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
