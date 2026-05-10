"""State consistency checks and next-hook promotion for LILIA sessions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


REQUIRED_EVENT_CARD_FIELDS = [
    "Visible Problem",
    "First Concrete Action",
    "Handles 2-4",
    "Relationship Stake",
    "If Ignored",
    "Next Visible Change",
]

ACTIVE_STATE_FILES = [
    "current/scene.md",
    "current/event_card.md",
    "current/hotset.md",
]

GROUNDING_GUARD_TEXT = (
    "resume 1ターン目では、current/scene.md、current/event_card.md、current/hotset.md、"
    "story/story_deck.md、lilia/main/memory.md、lilia/main/beliefs.md に明示されたものだけを"
    "場面の具体手がかりとして使う。\n"
    "story/story_deck.md は素材棚として参照し、active scene/event_card/hotsetに接続していない"
    "背景化materialを、resume 1ターン目の新しい証拠として前景化しない。\n"
    "active event_cardにない小道具、書類、連絡手段、識別情報、過去の控え類を、"
    "最初からそこにあったものとして足さない。\n"
    "電話や訪問などの入口でも、保存にない着信表示、連絡先の識別、場所の固有情報、控え類、"
    "手元の補助記録をresume 1ターン目の既存情報として描写しない。\n"
    "新しい具体物を出す場合は、active event_card の First Concrete Action と矛盾せず、"
    "scene内で今発見されたものとして明示し、Save Modeでevent_card/story_deck/memory候補として残す。"
)


@dataclass(frozen=True)
class StateConsistencyIssue:
    severity: str
    code: str
    message: str
    files: tuple[str, ...] = ()


@dataclass(frozen=True)
class StateConsistencyResult:
    status: str
    issues: tuple[StateConsistencyIssue, ...]

    @property
    def ok(self) -> bool:
        return self.status == "PASS"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def append_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = read_text(path)
    separator = "\n\n" if existing.strip() else ""
    path.write_text(existing.rstrip() + separator + content.rstrip() + "\n", encoding="utf-8")


def normalize_heading(heading: str) -> str:
    heading = re.sub(r"\s+-\s+.*$", "", heading.strip())
    return re.sub(r"\s+", " ", heading).lower()


def markdown_sections(content: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in content.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            current = normalize_heading(match.group(1))
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return {key: "\n".join(lines).strip() for key, lines in sections.items()}


def heading_blocks(content: str, target_heading: str) -> list[str]:
    target = normalize_heading(target_heading)
    blocks: list[str] = []
    current: str | None = None
    lines: list[str] = []
    for line in content.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            if current == target:
                blocks.append("\n".join(lines).strip())
            current = normalize_heading(match.group(1))
            lines = []
            continue
        if current == target:
            lines.append(line)
    if current == target:
        blocks.append("\n".join(lines).strip())
    return [block for block in blocks if meaningful_text(block)]


def latest_heading_block(content: str, target_heading: str) -> str:
    blocks = heading_blocks(content, target_heading)
    return blocks[-1] if blocks else ""


def latest_next_hook(session_root: Path) -> tuple[str, str]:
    event_hook = latest_heading_block(read_text(session_root / "current/event_card.md"), "Next Hook")
    story_deck = read_text(session_root / "story/story_deck.md")
    story_hook = latest_heading_block(story_deck, "Candidate Next Hook")
    if event_hook:
        return event_hook, "current/event_card.md"
    if story_hook:
        return story_hook, "story/story_deck.md"
    return "", ""


def meaningful_text(text: str) -> str:
    cleaned_lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        if re.match(r"^[-*]\s*未設定\s*$", line):
            continue
        if re.match(r"^[-*]\s*[^:：]+[:：]\s*$", line):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()


def section_text(content: str, heading: str) -> str:
    return markdown_sections(content).get(normalize_heading(heading), "")


def active_event_text(event_card: str) -> str:
    sections = markdown_sections(event_card)
    active_parts = [sections.get(normalize_heading(field), "") for field in REQUIRED_EVENT_CARD_FIELDS]
    active_parts.append(sections.get("表の出来事", ""))
    return meaningful_text("\n".join(active_parts))


def hook_terms(hook: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", meaningful_text(hook))
    chunks = [
        chunk.strip(" -:：。、「」『』（）()")
        for chunk in re.split(r"[。\n、,，/／]+", normalized)
        if chunk.strip(" -:：。、「」『』（）()")
    ]
    terms: list[str] = []
    for chunk in chunks:
        if len(chunk) >= 6:
            terms.append(chunk[:18])
        elif len(chunk) >= 3:
            terms.append(chunk)
    return terms[:6]


def has_hook_overlap(target: str, hook: str) -> bool:
    target_clean = meaningful_text(target)
    if not target_clean:
        return False
    terms = hook_terms(hook)
    return any(term and term in target_clean for term in terms)


def event_card_missing_fields(event_card: str) -> list[str]:
    sections = markdown_sections(event_card)
    missing: list[str] = []
    for field in REQUIRED_EVENT_CARD_FIELDS:
        if not meaningful_text(sections.get(normalize_heading(field), "")):
            missing.append(field)
    return missing


def validate_state_consistency(session_root: Path) -> StateConsistencyResult:
    root = Path(session_root)
    issues: list[StateConsistencyIssue] = []

    for rel_path in ACTIVE_STATE_FILES:
        if not (root / rel_path).exists():
            issues.append(
                StateConsistencyIssue(
                    "FAIL",
                    "missing_active_file",
                    f"{rel_path} is missing",
                    (rel_path,),
                )
            )

    scene = read_text(root / "current/scene.md")
    event_card = read_text(root / "current/event_card.md")
    hotset = read_text(root / "current/hotset.md")
    story_deck = read_text(root / "story/story_deck.md")

    missing_fields = event_card_missing_fields(event_card)
    if missing_fields:
        issues.append(
            StateConsistencyIssue(
                "FAIL",
                "event_card_required_fields",
                "current/event_card.md missing active fields: " + ", ".join(missing_fields),
                ("current/event_card.md",),
            )
        )

    hook, hook_source = latest_next_hook(root)
    if hook:
        event_matches = has_hook_overlap(active_event_text(event_card), hook)
        scene_matches = has_hook_overlap(scene, hook)
        hotset_matches = has_hook_overlap(hotset, hook)
        story_matches = has_hook_overlap(story_deck, hook)

        if not event_matches:
            issues.append(
                StateConsistencyIssue(
                    "WARN",
                    "candidate_next_hook_not_active",
                    f"{hook_source} has a Next Hook, but current/event_card.md active fields do not reflect it",
                    ("current/event_card.md", hook_source),
                )
            )
        if (hotset_matches or story_matches) and (not event_matches or not scene_matches):
            issues.append(
                StateConsistencyIssue(
                    "FAIL",
                    "hotset_scene_event_mismatch",
                    "hotset/story_deck point at a next scene, but current/scene.md or current/event_card.md still looks stale",
                    ("current/hotset.md", "current/scene.md", "current/event_card.md", hook_source),
                )
            )

    if meaningful_text(story_deck) and meaningful_text(event_card) == meaningful_text(story_deck):
        issues.append(
            StateConsistencyIssue(
                "WARN",
                "event_card_matches_story_deck",
                "current/event_card.md appears to mirror story/story_deck.md instead of holding one active event",
                ("current/event_card.md", "story/story_deck.md"),
            )
        )

    if any(issue.severity == "FAIL" for issue in issues):
        status = "FAIL"
    elif issues:
        status = "WARN"
    else:
        status = "PASS"
    return StateConsistencyResult(status=status, issues=tuple(issues))


def format_state_consistency_report(result: StateConsistencyResult) -> str:
    lines = [f"state consistency: {result.status}"]
    for issue in result.issues:
        files = f" [{', '.join(issue.files)}]" if issue.files else ""
        lines.append(f"{issue.severity}: {issue.code}: {issue.message}{files}")
    return "\n".join(lines)


def summarize_next_hook(next_hook: str) -> str:
    text = meaningful_text(next_hook)
    text = re.sub(r"\s+", " ", text).strip()
    return text or "次に確認する小さな入口"


def infer_time_from_next_hook(next_hook: str) -> str:
    text = summarize_next_hook(next_hook)
    for keyword in ["翌朝", "翌日", "次の日", "次回", "後日", "夕方", "夜", "朝", "帰宅後"]:
        if keyword in text:
            return f"{keyword}を含む次scene"
    return "保存された次の入口で示された次scene"


def render_promoted_scene(next_hook: str, timestamp: str) -> str:
    summary = summarize_next_hook(next_hook)
    return "\n".join(
        [
            "# Scene",
            "",
            "## 今いる場所",
            "",
            "- 保存された次の入口に明示された場所。明示がない場合は、前sceneから自然に戻れる場所。",
            "",
            "## 現在時刻または場面時間",
            "",
            f"- {infer_time_from_next_hook(next_hook)}。",
            "",
            "## LILIAとユーザーの距離",
            "",
            "- 前回保存されたrelationship / memory / beliefsの距離を維持する。",
            "",
            "## 今この場で見えているもの",
            "",
            f"- {summary}",
            "",
            "## 今の場面",
            "",
            f"- {summary}",
            "",
            "## 直前のやりとり",
            "",
            "- 前sceneは一度閉じ、保存された次の入口から再開する。",
            "",
            "## 初回sceneの入口",
            "",
            "- 該当なし。これはresume後の次scene入口。",
            "",
            "## 次に起きそうなこと",
            "",
            f"- {summary}",
            "",
            "## 次にユーザーへ渡す行動余地",
            "",
            "- 状況を確認する / LILIAの手順を待つ / 必要な範囲だけ一緒に確認する / どこまで触れるか線引きを確認する。",
            "",
            "## State Consistency",
            "",
            f"- promoted_from_next_hook_at: {timestamp}",
        ]
    )


def render_promoted_event_card(next_hook: str, timestamp: str) -> str:
    summary = summarize_next_hook(next_hook)
    return "\n".join(
        [
            "# Event Card",
            "",
            "## Active Hook",
            "",
            "- hook_id: promoted_next_hook",
            "- hook_type: main / relationship / life",
            "- status: active",
            "- foreground_reason: 保存された次の入口を次sceneの入口として前景化する。",
            "- 注: Active Hookは今触れる1本だけ。3hookを3択UIとして並べない。",
            "",
            "## Scene Function",
            "",
            "- function: 始動",
            f"- current_question: {summary}",
            "- entry_state: 前sceneは一度閉じ、保存された次の入口から次sceneへ入る。",
            "- exit_condition: 状況確認の入口が成立し、次に触れる可視問題が明確になる。",
            "- change_delta: 保存された次の入口候補がactive event_cardへ昇格する。",
            "- next_hook_candidate: Save Modeで必要になった場合だけ更新する。",
            "- 注: Story Function名は内部タグ。Play Mode本文へそのまま出さない。",
            "",
            "## 表の出来事",
            "",
            f"{summary}",
            "",
            "## Visible Problem",
            "",
            f"{summary}",
            "",
            "## First Concrete Action",
            "",
            "LILIAは保存された次の入口に沿って、状況確認の入口だけを出す。active event_cardにない具体手がかりは追加しない。",
            "",
            "## Handles 2-4",
            "",
            "- ask: 状況を確認する",
            "- wait: LILIAの手順を待つ",
            "- support: 必要な範囲だけ一緒に確認する",
            "- boundary: どこまで触れるか線引きを確認する",
            "",
            "## Relationship Stake",
            "",
            "保存済みの約束、信頼、警戒、距離、境界線、記憶が次sceneの第一声で巻き戻らないかが賭けになる。",
            "",
            "## If Ignored",
            "",
            "この入口に触れなかった場合、次の入口は保留札として残り、LILIAの確認や距離の取り方に小さく戻る。",
            "",
            "## Next Visible Change",
            "",
            "LILIAの確認、沈黙、呼び方、距離、または次の約束の扱いに変化が出る。",
            "",
            "## Grounding Guard",
            "",
            GROUNDING_GUARD_TEXT,
            "",
            "## State Consistency",
            "",
            f"- promoted_from_next_hook_at: {timestamp}",
        ]
    )


def render_promoted_hotset(next_hook: str, timestamp: str) -> str:
    summary = summarize_next_hook(next_hook)
    return "\n".join(
        [
            "# Hotset",
            "",
            "このファイルは再開時の短い温度キャッシュです。正本ではありません。",
            "apply-turnでは肥大化を避けるため、最新のhotsetだけを短く保持します。",
            "",
            "## 会話の温度",
            "",
            "- 前sceneは一度閉じ、保存された次の入口から次sceneへ入る。",
            "",
            "## 呼び方 / 距離のアンカー",
            "",
            "- 呼び方と距離はrelationship / memory / beliefsの保存済み状態を優先する。",
            "",
            "## 次に会った時の第一反応",
            "",
            f"- {summary}",
            "",
            "## 未消化の感情",
            "",
            "- 保存された次の入口に残った確認、保留、境界線を急がず扱う。",
            "",
            "## 言い残し / まだ言っていないこと",
            "",
            f"- {summary}",
            "",
            "## 最新scene後のecho",
            "",
            f"- 次の1ターンに響くこと: {summary}",
            "- 第一反応の方向: 保存済みの距離を保って確認する",
            "- まだ触れない方がいいこと: active event_cardにない具体手がかりを勝手に足さない",
            "",
            "## 現在のイベント要約",
            "",
            f"- {summary}",
            "",
            "## 次の小さな出来事",
            "",
            f"- {summary}",
            "",
            "## 未確定の余白",
            "",
            "- 新しい手がかりはscene内で発見された時だけ扱い、Save Modeで保存候補に残す。",
            "",
            "## 次にユーザーへ向き合う時の空気",
            "",
            f"- {summary}",
            "",
            "## State Consistency",
            "",
            f"- promoted_from_next_hook_at: {timestamp}",
        ]
    )


def render_backgrounded_event_card(previous_event_card: str, timestamp: str) -> str:
    sections = markdown_sections(previous_event_card)
    if not meaningful_text(previous_event_card):
        return ""
    lines = [
        f"## Backgrounded Event Card - {timestamp}",
        "",
        "current/event_card.md was promoted from Next Hook; previous active event is no longer the resume entry.",
        "",
    ]
    for heading in ["表の出来事", "Visible Problem", "First Concrete Action", "Relationship Stake", "If Ignored", "Next Visible Change"]:
        body = meaningful_text(sections.get(normalize_heading(heading), ""))
        if body:
            lines.extend([f"### {heading}", "", body, ""])
    return "\n".join(lines).rstrip()


def promote_next_hook_to_active_state(
    session_root: Path,
    next_hook: str,
    timestamp: str,
    *,
    update_scene: bool = True,
    update_event_card: bool = True,
    update_hotset: bool = True,
    background_previous_event: bool = True,
) -> list[str]:
    updated: list[str] = []
    root = Path(session_root)
    if update_scene:
        write_text(root / "current/scene.md", render_promoted_scene(next_hook, timestamp))
        updated.append("current/scene.md")
    if update_event_card:
        previous_event = read_text(root / "current/event_card.md")
        if background_previous_event:
            background = render_backgrounded_event_card(previous_event, timestamp)
            if background:
                append_text(root / "story/story_deck.md", background)
                updated.append("story/story_deck.md")
        write_text(root / "current/event_card.md", render_promoted_event_card(next_hook, timestamp))
        updated.append("current/event_card.md")
    if update_hotset:
        write_text(root / "current/hotset.md", render_promoted_hotset(next_hook, timestamp))
        updated.append("current/hotset.md")
    return list(dict.fromkeys(updated))
