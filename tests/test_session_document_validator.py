from __future__ import annotations

from pathlib import Path
import sys

import pytest


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


def _playable_event_card(overrides: dict[str, str] | None = None) -> str:
    body = {
        "表の出来事": "- カフェでユイが忘れたイヤホンを、かねこが見つけて返す。",
        "Visible Problem": "\n".join(
            [
                "- 誰が困っているか: 忘れ物に気づいていないユイ。",
                "- 何が止まりそうか: 会釈だけの関係が用件のある会話へ進む機会。",
                "- 何に触れると入口になるか: イヤホンを丁寧に差し出して確認すること。",
            ]
        ),
        "First Concrete Action": "\n".join(
            [
                "- 誰に / 何に: ユイと、彼女の黒いワイヤレスイヤホン。",
                "- どう触るか: 席の近くで短く声をかけ、相手が受け取れる距離に差し出す。",
                "- 初回sceneで重すぎない一手: 忘れ物を返す用件だけに留める。",
            ]
        ),
        "Handles 2-4": "\n".join(
            [
                "- handle 1: 忘れ物だと短く伝える。",
                "- handle 2: 店員に預けるか本人に返すかを迷う。",
                "- handle 3 optional:",
                "- handle 4 optional:",
                "- 注: handlesは選択肢ではなく行動余地。",
            ]
        ),
        "Relationship Stake": "- 丁寧に扱われるかで、ユイの警戒と短い信頼の残り方が変わる。",
        "Crisis / Ability Check": "- 能力や危機は発生しない。",
        "If Ignored": "- イヤホンは店員に預けられ、会釈だけの関係が続く。",
        "Next Visible Change": "\n".join(
            [
                "- ユイは受け取ったあと、右手首のブレスレットを親指で触る。",
                "- 声 / 沈黙 / 呼び方 / 距離に出る変化: 礼の声が短くなり、目を長く合わせない。",
            ]
        ),
        "進行状態": "- status: 継続",
        "Story Residue": "\n".join(
            [
                "- memoryに残るもの: 忘れ物を雑に扱われなかったこと。",
                "- relationshipに残るもの:",
                "- beliefsに残るもの:",
                "- voiceに残るもの:",
            ]
        ),
        "Truth Hiding Boundary": "- 隠してよい真相: ユイが距離を測る理由。\n- 見せる入口: 忘れ物を返すこと。",
        "Intimacy / Boundary Check": "- 親密sceneの場合だけ確認: 該当しない。",
        "揺れるLILIA": "- ユイは助かったと思う一方で、見られていたことに小さく警戒する。",
        "その出来事がLILIAに刺さる理由": "- 持ち物の扱いが、ユイにとって生活の手順と隙の見られ方に触れる。",
        "ユーザーへの問い": "- 選択肢ではなく、用件以上に踏み込まない行動余地として置く。",
        "関係に残る変化": "- 会釈だけだった関係に、忘れ物を返した朝の記憶が加わる。",
    }
    body.update(overrides or {})
    return _doc("current/event_card.md", body)


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


def test_validator_rejects_event_card_with_unfilled_visible_problem() -> None:
    docs = _valid_documents()
    docs["current/event_card.md"] = _playable_event_card(
        {
            "Visible Problem": "\n".join(
                [
                    "- 誰が困っているか:",
                    "- 何が止まりそうか: 会釈だけの関係が用件のある会話へ進む機会。",
                    "- 何に触れると入口になるか: イヤホンを丁寧に差し出して確認すること。",
                ]
            )
        }
    )
    valid, errors = validate_session_documents(docs, ANSWERS)
    assert not valid
    assert any("Visible Problem の '誰が困っているか' が空である" in error for error in errors)


def test_validator_rejects_event_card_with_only_one_handle() -> None:
    docs = _valid_documents()
    docs["current/event_card.md"] = _playable_event_card(
        {
            "Handles 2-4": "\n".join(
                [
                    "- handle 1: 忘れ物だと短く伝える。",
                    "- handle 2:",
                    "- handle 3 optional:",
                    "- handle 4 optional:",
                    "- 注: handlesは選択肢ではなく行動余地。",
                ]
            )
        }
    )
    valid, errors = validate_session_documents(docs, ANSWERS)
    assert not valid
    assert any("Handles 2-4 が 2 個未満" in error for error in errors)


def test_validator_rejects_event_card_with_remnant_unfilled_marker() -> None:
    docs = _valid_documents()
    docs["current/event_card.md"] = _playable_event_card({"Relationship Stake": "- 未設定"})
    valid, errors = validate_session_documents(docs, ANSWERS)
    assert not valid
    assert any("未設定 が ## Relationship Stake に残存している" in error for error in errors)


def test_validator_pass_for_session_002b_event_card() -> None:
    event_card_path = ROOT / "saves" / "session_002b" / "current" / "event_card.md"
    if not event_card_path.exists():
        pytest.skip("session_002b event_card.md is not stored in this checkout")

    docs = _valid_documents()
    docs["current/event_card.md"] = event_card_path.read_text(encoding="utf-8")
    valid, errors = validate_session_documents(docs, ANSWERS)
    assert valid, errors
