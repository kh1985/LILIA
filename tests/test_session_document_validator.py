from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.session.document_validator import (
    DOWNSTREAM_SESSION_DOCUMENT_FILES,
    validate_session_documents,
)


ANSWERS = {
    1: "結城さくら、26歳、夜勤が多い総合病院の病棟看護師、穏やかだが線引きははっきりしている",
    6: "初対面、終電後の駅で、眠っていたところを缶コーヒーで起こされる",
    8: "男、175cm、痩せ型、よれたパーカー、深夜配達の仕事、終電後の配達帰り",
}


def _template_path(rel_path: str) -> Path:
    if rel_path == "current/protagonist.md":
        return ROOT / "templates" / "session" / "protagonist.md"
    if rel_path == "current/knowledge_state.md":
        return ROOT / "templates" / "session" / "knowledge_state.md"
    return ROOT / "templates" / "session" / rel_path


def _headings(rel_path: str) -> list[str]:
    text = _template_path(rel_path).read_text(encoding="utf-8")
    return [line[3:].strip() for line in text.splitlines() if line.startswith("## ")]


def _doc(rel_path: str, body_by_heading: dict[str, str] | None = None) -> str:
    body_by_heading = body_by_heading or {}
    lines = ["# Test", ""]
    for heading in _headings(rel_path):
        lines.extend(["", f"## {heading}", "", body_by_heading.get(heading, "- さくら固有の短い初期値。")])
    return "\n".join(lines).strip() + "\n"


def _knowledge_doc(yaml_block: str) -> str:
    body = {heading: "- 運用メモ。" for heading in _headings("current/knowledge_state.md")}
    body["知識項目テンプレート"] = "実データは下の `## knowledge_state` に置く。"
    body["knowledge_state"] = f"```yaml\n{yaml_block.strip()}\n```"
    return _doc("current/knowledge_state.md", body)


def _valid_documents() -> dict[str, str]:
    docs = {path: _doc(path) for path in DOWNSTREAM_SESSION_DOCUMENT_FILES}
    docs["current/protagonist.md"] = _doc(
        "current/protagonist.md",
        {
            "呼ばれ方": "呼称: かねこくん",
            "身体": "- 性別: 男\n- 身長感: 175cm\n- 体格: 痩せ型\n- 仕事 / 立場: 深夜配達の仕事",
            "スタイル": "- 服装: よれたパーカー\n- 雰囲気の特徴: 深夜帰りの生活感",
        },
    )
    docs["current/knowledge_state.md"] = _knowledge_doc(
        """
items:
  - key: protagonist_call_name
    value: "かねこくん"
    fictional_status: meta
    source: protagonist
    known_to: [protagonist]
    acquired_at: pre_play
    weight: medium
  - key: protagonist_gender
    value: "男"
    fictional_status: observable
    source: protagonist
    known_to: [protagonist]
    acquired_at: pre_play
    weight: low
  - key: protagonist_height
    value: "175cm"
    fictional_status: observable
    source: protagonist
    known_to: [protagonist]
    acquired_at: pre_play
    weight: low
  - key: protagonist_build
    value: "痩せ型"
    fictional_status: observable
    source: protagonist
    known_to: [protagonist]
    acquired_at: pre_play
    weight: low
  - key: protagonist_style
    value: "よれたパーカー"
    fictional_status: observable
    source: protagonist
    known_to: [protagonist]
    acquired_at: pre_play
    weight: low
  - key: protagonist_occupation
    value: "深夜配達の仕事"
    fictional_status: meta
    source: protagonist
    known_to: [protagonist]
    acquired_at: pre_play
    weight: medium
  - key: heroine_name
    value: "結城さくら"
    fictional_status: meta
    source: heroine_self_disclosure
    known_to: [heroine]
    acquired_at: pre_play
    weight: high
  - key: heroine_occupation
    value: "病棟看護師"
    fictional_status: meta
    source: heroine_self_disclosure
    known_to: [heroine]
    acquired_at: pre_play
    weight: medium
  - key: heroine_visual_anchor
    value: "銀のネックレス"
    fictional_status: observable
    source: observation
    known_to: [heroine, protagonist]
    acquired_at: scene_1
    weight: medium
  - key: heroine_background_truth
    value: "勤務外の優しさに線を引こうとしている"
    fictional_status: gm_only
    source: story_spine
    known_to: [GM]
    acquired_at: pre_play
    weight: high
  - key: reveal_ladder_stage_1
    value: "缶コーヒー一本ぶんだけ関わる"
    fictional_status: gm_only
    source: story_spine
    known_to: [GM]
    acquired_at: pre_play
    weight: medium
  - key: reveal_ladder_stage_2
    value: "声と沈黙の差が出る"
    fictional_status: gm_only
    source: story_spine
    known_to: [GM]
    acquired_at: pre_play
    weight: medium
  - key: reveal_ladder_stage_3
    value: "ネックレスの由来に近づく"
    fictional_status: gm_only
    source: story_spine
    known_to: [GM]
    acquired_at: pre_play
    weight: high
  - key: session_constraints
    value: "特になし"
    fictional_status: meta-system
    source: protagonist
    known_to: [GM]
    acquired_at: pre_play
    weight: low
"""
    )
    return docs


def test_validator_rejects_template_expression() -> None:
    docs = _valid_documents()
    docs["current/event_card.md"] += "\n- 次の行動の判断について、急かさず短く聞く\n"
    valid, errors = validate_session_documents(docs, ANSWERS)
    assert not valid
    assert any("forbidden template expression" in error for error in errors)


def test_validator_rejects_q8_verbatim_in_protagonist() -> None:
    docs = _valid_documents()
    docs["current/protagonist.md"] = docs["current/protagonist.md"].replace(
        "- 服装: よれたパーカー",
        "- 服装: 男、175cm、痩せ型、よれたパーカー、深夜配達の仕事、終電後の配達帰り",
    )
    valid, errors = validate_session_documents(docs, ANSWERS)
    assert not valid
    assert any("Q8" in error for error in errors)


def test_validator_rejects_invalid_knowledge_yaml() -> None:
    docs = _valid_documents()
    docs["current/knowledge_state.md"] = _knowledge_doc("items:\n  - key: [")
    valid, errors = validate_session_documents(docs, ANSWERS)
    assert not valid
    assert any("YAML" in error for error in errors)
