"""Deterministic opening-scene control seed.

This module turns loose newgame materials into the small set of control values
that must not depend on an LLM filling Markdown blanks correctly.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any


@dataclass(frozen=True)
class OpeningSeed:
    hook_id: str
    hook_type: str
    status: str
    scene_function: str
    protagonist_role: str
    protagonist_reason: str
    current_player_knowledge: str
    player_facing_problem: str
    visible_props: str
    first_concrete_action: str
    relationship_stake: str
    next_curiosity: str
    candidate_next_hook: str
    dramatic_question: str
    entry_state: str
    exit_condition: str
    change_delta: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)

    def to_prompt_block(self) -> str:
        rows = ["## Opening Seed", ""]
        for key, value in self.as_dict().items():
            rows.append(f"- {key}: {value}")
        return "\n".join(rows)


def build_opening_seed(
    *,
    answers: dict,
    character_yaml: dict,
    profile_md: str,
    story_spine_md: str,
    relationship_spine_md: str,
    lilia_name: str = "",
) -> OpeningSeed:
    profile_sections = _markdown_sections(profile_md)
    story_sections = _markdown_sections(story_spine_md)
    relationship_sections = _markdown_sections(relationship_spine_md)
    anchors = profile_sections.get("initial scene anchors", "")

    name = _clean(
        str(character_yaml.get("name") or lilia_name or _profile_field(profile_md, "name") or "ヒロイン")
    )
    place = _compact(
        _profile_bullet_value(anchors, "場所と状況")
        or _profile_field(profile_md, "current_situation")
        or "日常の中で短い確認ができる場所",
        limit=54,
    )
    visible_props = _compact(
        _profile_bullet_value(anchors, "手元の具体物")
        or _first_drift_guard(story_sections.get("drift guard", ""))
        or "目の前の用件",
        limit=80,
    )
    opening_entry = _compact(
        _profile_bullet_value(anchors, "会話の入口")
        or f"{name}と目の前の用件を確認する",
        limit=80,
    )
    entry_state = _compact(
        _profile_bullet_value(anchors, "最初の距離")
        or "初対面。互いに相手の出方をまだ測っている。",
        limit=72,
    )
    dramatic_question = _compact(
        story_sections.get("main question", "")
        or f"{name}は、主人公を同じ場に置ける相手として見られるか。",
        limit=90,
    )
    relationship_stake = _compact(
        relationship_sections.get("育てたいテーマ", "")
        or "急かさず、相手がまだ言わない部分を境界として残せるか。",
        limit=90,
    )
    player_facing_problem = _player_facing_problem(
        story_sections=story_sections,
        opening_entry=opening_entry,
        visible_props=visible_props,
        name=name,
    )
    protagonist_role = _protagonist_role(
        answers=answers,
        player_facing_problem=player_facing_problem,
        opening_entry=opening_entry,
        visible_props=visible_props,
    )
    q6 = _answer_text(answers, 6)
    explicit_reason = _compact(q6, limit=90) if q6 and not _is_omakase(q6) else ""
    protagonist_reason = explicit_reason or (
        f"主人公は{protagonist_role}。"
        if "来た" in protagonist_role or "持ち込" in protagonist_role
        else f"主人公は{protagonist_role}として、{player_facing_problem}に関わるためその場にいる。"
    )
    current_player_knowledge = (
        f"{place}で、{player_facing_problem}を今ここで確認する必要がある。"
        f"{name}とはまだ信用も警戒も固まっていない。"
    )
    first_concrete_action = _first_concrete_action(player_facing_problem)
    next_curiosity = _next_curiosity(player_facing_problem)
    candidate_next_hook = "next_small_confirmation"
    exit_condition = f"{player_facing_problem}の扱い方か、次に確かめる対象が一つ決まる。"
    change_delta = f"{name}が主人公を、待てる相手か急かす相手かで仮判断する。"

    return OpeningSeed(
        hook_id="main_initial_contact",
        hook_type="main",
        status="active",
        scene_function="起点",
        protagonist_role=protagonist_role,
        protagonist_reason=protagonist_reason,
        current_player_knowledge=current_player_knowledge,
        player_facing_problem=player_facing_problem,
        visible_props=visible_props,
        first_concrete_action=first_concrete_action,
        relationship_stake=relationship_stake,
        next_curiosity=next_curiosity,
        candidate_next_hook=candidate_next_hook,
        dramatic_question=dramatic_question,
        entry_state=entry_state,
        exit_condition=exit_condition,
        change_delta=change_delta,
    )


def _player_facing_problem(
    *,
    story_sections: dict[str, str],
    opening_entry: str,
    visible_props: str,
    name: str,
) -> str:
    reveal_entry = _first_reveal_ladder_item(story_sections.get("reveal ladder", ""))
    candidates = [
        _paraphrase_problem(reveal_entry),
        _paraphrase_problem(opening_entry),
    ]
    if not _looks_like_prop_inventory(visible_props):
        candidates.append(_compact(visible_props, limit=42))
    candidates.append(f"{name}の前に出された用件の確認")
    for candidate in candidates:
        value = _compact(candidate, limit=42)
        if value and not _looks_like_prop_inventory(value):
            return value
    return "目の前の用件をどう確認するか"


def _protagonist_role(
    *,
    answers: dict,
    player_facing_problem: str,
    opening_entry: str,
    visible_props: str,
) -> str:
    q8 = _answer_text(answers, 8)
    if q8 and not _is_omakase(q8):
        explicit = _explicit_role_from_q8(q8)
        if explicit:
            return explicit
        return _compact(q8, limit=36)

    text = " ".join([player_facing_problem, opening_entry, visible_props])
    if "修理" in text or "受付" in text or "預かり票" in text or "伝票" in text:
        return "濡れた伝票と控えを持ち込み、受付で確認を求める来店者"
    if "USB" in text or "ＵＳＢ" in text:
        return "黒いUSBを返しに来た便利屋"
    if "棚" in text or "書店" in text or "本" in text:
        return "棚づくりの相談内容を本人に確認しに来た人物"
    if "忘れ物" in text or "落とし物" in text:
        return "忘れ物を本人に返しに来た人物"
    return "目の前の用件を本人に確認しに来た人物"


def _explicit_role_from_q8(text: str) -> str:
    match = re.search(r"(?:仕事|職業|立場)\s*[:：]\s*([^。\n]+)", text)
    if match:
        return _compact(match.group(1), limit=36)
    parts = [part.strip() for part in re.split(r"[、,\n/]+", text) if part.strip()]
    for part in reversed(parts):
        if re.search(r"仕事|職|会社員|自営業|店|書店|技師|便利屋|配達|学生|教師|講師|職人|相談", part):
            return _compact(part, limit=36)
    return ""


def _first_concrete_action(problem: str) -> str:
    if "伝票" in problem or "控え" in problem:
        return "濡れた伝票と控えを見える場所に出し、読める範囲を一つ確認する。"
    if "USB" in problem or "ＵＳＢ" in problem:
        return "黒いUSBを見える場所に置き、受け渡しの経緯を短く伝える。"
    if "棚" in problem or "書店" in problem or "本" in problem:
        return "相談メモを見える場所に置き、棚づくりで今決めたい点を一つ確認する。"
    if "忘れ物" in problem or "落とし物" in problem:
        return "忘れ物を相手が受け取れる距離に出し、本人のものか確認する。"
    return "目の前の用件を見える場所に出し、今確認したい点を一つ伝える。"


def _next_curiosity(problem: str) -> str:
    if "伝票" in problem or "控え" in problem:
        return "読めない部分が、記録や相手の記憶とどこまで一致するか。"
    if "USB" in problem or "ＵＳＢ" in problem:
        return "誰がなぜ主人公を挟んで受け渡しさせたのか。"
    if "棚" in problem or "書店" in problem or "本" in problem:
        return "どの本を置けば、相手が守りたい棚の静けさと人の足が両立するか。"
    return "次に何を確かめれば、相手との距離が少し動くか。"


def _paraphrase_problem(text: str) -> str:
    value = _clean(text)
    if not value:
        return ""
    if "USB" in value or "ＵＳＢ" in value:
        return "黒いUSBの受け渡しと出所確認"
    if "預かり票" in value and "伝票" in value:
        return "濡れた伝票と控えの照合"
    if "伝票" in value and "番号" in value:
        return "読めない伝票番号の照合"
    if "棚" in value and "置く本" in value:
        return "棚に置く本の選び方の相談"
    if "棚" in value and ("本" in value or "書店" in value):
        return "書店の棚づくり相談"
    if "忘れ物" in value or "落とし物" in value:
        return "忘れ物の返し方と本人確認"
    if "食い違" in value:
        subject = value.split("食い違", 1)[0]
        subject = subject.rsplit("、", 1)[-1]
        subject = re.sub(r"[がはをにでと、。\s]+$", "", subject).strip()
        if subject:
            return f"{subject}の食い違いの確認"
    if re.search(r"確認|照合|返|渡|相談|決め", value):
        return value
    return ""


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


def _looks_like_prop_inventory(value: str) -> bool:
    text = _clean(value)
    separator_count = text.count("、") + text.count(",") + text.count("・")
    prop_mentions = len(
        re.findall(
            r"メモ帳|ペン|伝票|控え|ミント缶|スマホケース|鍵|封筒|USB|グラス|名刺入れ|紙片|付箋|文庫本|時計|カップ",
            text,
        )
    )
    if separator_count >= 4 and prop_mentions >= 4:
        return True
    return bool(
        separator_count >= 3
        and prop_mentions >= 3
        and not re.search(r"確認|照合|返|渡|選|決|困|食い違|読め|見つから|扱|受け渡し|出所|相談", text)
    )


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


def _profile_bullet_value(section: str, label: str) -> str:
    match = re.search(rf"^\s*[-*]\s*{re.escape(label)}\s*[:：]\s*(.+)$", section, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _first_drift_guard(section: str) -> str:
    for raw_line in section.splitlines():
        line = re.sub(r"^\s*[-*]\s*", "", raw_line).strip()
        if line:
            return line.split(" - ", 1)[0].strip()
    return ""


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


def _is_omakase(value: str) -> bool:
    normalized = re.sub(r"\s+", "", value)
    return normalized in {"おまかせ", "お任せ"}


def _compact(text: str, *, limit: int) -> str:
    value = _clean(text)
    value = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", value)
    value = re.sub(r"\[pending\]\s*", "", value)
    if len(value) > limit:
        value = value[:limit].rstrip("、。,. ") + "。"
    return value


def _clean(text: Any) -> str:
    value = str(text or "").strip()
    value = re.sub(r"\s+", " ", value)
    return value.strip()
