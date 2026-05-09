"""Unit tests for tools/playtest/judge.py.

The judge is read-only with respect to saves/ and run/session/. These tests
only exercise prompt building, response parsing, and Markdown rendering — no
LLM CLI is invoked.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.playtest import judge


VALID_PAYLOAD: dict = {
    "result": "PASS",
    "summary": "Voiceは終始安定。10ターンを通じて関係変化に根拠あり。",
    "scores": {
        "voice_continuity": {"score": 5, "notes": "呼び方も口調も維持"},
        "tempo_guard": {"score": 4, "notes": "1ターン1hookに近い"},
        "reply_affordance": {"score": 5, "notes": "毎ターン明確な入口"},
        "relationship_change_grounding": {"score": 4, "notes": "出来事の根拠あり"},
        "inner_hidden_leakage": {"score": 5, "notes": "漏れなし"},
        "over_leading": {"score": 4, "notes": "誘導は最小"},
        "arc_closure_scene_progression": {
            "score": 4,
            "notes": "closure後の次入口あり",
        },
    },
    "warnings": ["軽微なテンポの揺れ"],
    "failures": [],
    "recommended_fixes": ["tempo guardの再確認"],
    "notable_good_moments": ["3ターン目の沈黙の使い方"],
}


def _payload_with_overrides(**overrides) -> dict:
    payload = json.loads(json.dumps(VALID_PAYLOAD))
    for key, value in overrides.items():
        payload[key] = value
    return payload


def test_build_judge_prompt_includes_rubric_and_transcript() -> None:
    prompt = judge.build_judge_prompt(
        persona="normal",
        turns_completed=10,
        transcript_md_text="# AI Playtest Transcript\n\n## Turn 1 - GM\n本文",
    )

    # Rubric and section markers
    assert "AI Playtest Judge" in prompt
    assert "voice_continuity" in prompt
    assert "tempo_guard" in prompt
    assert "reply_affordance" in prompt
    assert "relationship_change_grounding" in prompt
    assert "inner_hidden_leakage" in prompt
    assert "over_leading" in prompt
    assert "arc_closure_scene_progression" in prompt
    assert "別れの挨拶" in prompt
    assert "同じ余韻モチーフを3回以上反復" in prompt
    assert "10ターン以上同じscene" in prompt
    assert "memory候補 / next hook / 次arc候補" in prompt
    # Meta + transcript embedded
    assert "persona: normal" in prompt
    assert "turns_completed: 10" in prompt
    assert "## Turn 1 - GM" in prompt


def test_parse_judge_response_accepts_fenced_json() -> None:
    body = "前置きはダメだが念のためテスト。\n\n```json\n" + json.dumps(VALID_PAYLOAD) + "\n```\n"
    parsed = judge.parse_judge_response(body)

    assert parsed["result"] == "PASS"
    assert parsed["summary"].startswith("Voice")
    assert set(parsed["scores"].keys()) == set(judge.JUDGE_SCORE_KEYS)
    assert parsed["scores"]["voice_continuity"]["score"] == 5
    assert parsed["warnings"] == ["軽微なテンポの揺れ"]
    assert parsed["failures"] == []


def test_parse_judge_response_accepts_raw_json() -> None:
    parsed = judge.parse_judge_response(json.dumps(VALID_PAYLOAD))
    assert parsed["result"] == "PASS"


def test_parse_judge_response_normalizes_result_case() -> None:
    payload = _payload_with_overrides(result="warn")
    parsed = judge.parse_judge_response(json.dumps(payload))
    assert parsed["result"] == "WARN"


def test_parse_judge_response_rejects_invalid_result() -> None:
    payload = _payload_with_overrides(result="OK")
    with pytest.raises(judge.JudgeParseError):
        judge.parse_judge_response(json.dumps(payload))


def test_parse_judge_response_rejects_missing_score_key() -> None:
    payload = json.loads(json.dumps(VALID_PAYLOAD))
    del payload["scores"]["over_leading"]
    with pytest.raises(judge.JudgeParseError):
        judge.parse_judge_response(json.dumps(payload))


def test_parse_judge_response_accepts_legacy_missing_new_score_key() -> None:
    payload = json.loads(json.dumps(VALID_PAYLOAD))
    del payload["scores"]["arc_closure_scene_progression"]

    parsed = judge.parse_judge_response(json.dumps(payload))

    assert parsed["result"] == "WARN"
    assert parsed["scores"]["arc_closure_scene_progression"]["score"] == 3
    assert "旧schema応答" in parsed["scores"]["arc_closure_scene_progression"]["notes"]
    assert any("legacy schema" in item for item in parsed["warnings"])


def test_parse_judge_response_rejects_out_of_range_score() -> None:
    payload = json.loads(json.dumps(VALID_PAYLOAD))
    payload["scores"]["tempo_guard"]["score"] = 7
    with pytest.raises(judge.JudgeParseError):
        judge.parse_judge_response(json.dumps(payload))


def test_parse_judge_response_rejects_non_numeric_score() -> None:
    payload = json.loads(json.dumps(VALID_PAYLOAD))
    payload["scores"]["voice_continuity"]["score"] = "five"
    with pytest.raises(judge.JudgeParseError):
        judge.parse_judge_response(json.dumps(payload))


def test_parse_judge_response_rejects_bool_score() -> None:
    payload = json.loads(json.dumps(VALID_PAYLOAD))
    payload["scores"]["voice_continuity"]["score"] = True
    with pytest.raises(judge.JudgeParseError):
        judge.parse_judge_response(json.dumps(payload))


def test_parse_judge_response_rejects_non_array_warnings() -> None:
    payload = _payload_with_overrides(warnings="軽微なテンポの揺れ")
    with pytest.raises(judge.JudgeParseError):
        judge.parse_judge_response(json.dumps(payload))


def test_parse_judge_response_rejects_empty() -> None:
    with pytest.raises(judge.JudgeParseError):
        judge.parse_judge_response("")


def test_parse_judge_response_rejects_no_json_object() -> None:
    with pytest.raises(judge.JudgeParseError):
        judge.parse_judge_response("プレーンテキストでJSONなし")


def test_parse_judge_response_filters_blank_array_items() -> None:
    payload = _payload_with_overrides(
        warnings=["", "  ", "本物の警告"],
        failures=[],
    )
    parsed = judge.parse_judge_response(json.dumps(payload))
    assert parsed["warnings"] == ["本物の警告"]
    assert parsed["failures"] == []


def test_render_judge_report_md_contains_required_sections() -> None:
    parsed = judge.parse_judge_response(json.dumps(VALID_PAYLOAD))
    report = judge.render_judge_report_md(
        parsed,
        persona="normal",
        turns_completed=10,
        turns_requested=10,
        source_session="saves/session_001",
        engine="codex",
        started_at="2026-05-08T06:00:00+09:00",
        judged_at="2026-05-08T06:30:00+09:00",
    )

    assert report.startswith("# AI Playtest Judge Report")
    assert "## Summary" in report
    assert "- Result: PASS" in report
    assert "- Persona: normal" in report
    assert "- Turns: 10" in report
    assert "- Session: saves/session_001" in report
    assert "- Engine: codex" in report
    assert "- Started at: 2026-05-08T06:00:00+09:00" in report
    assert "- Judged at: 2026-05-08T06:30:00+09:00" in report
    assert "## Scores" in report
    assert "| Voice continuity | 5/5 |" in report
    assert "| Tempo guard | 4/5 |" in report
    assert "| Reply affordance | 5/5 |" in report
    assert "| Relationship change grounding | 4/5 |" in report
    assert "| Inner / hidden leakage | 5/5 |" in report
    assert "| Over-leading | 4/5 |" in report
    assert "| Arc closure / Scene progression | 4/5 | closure後の次入口あり |" in report
    assert "## Warnings" in report
    assert "- 軽微なテンポの揺れ" in report
    assert "## Failures" in report
    assert "- (なし)" in report  # failures empty
    assert "## Recommended Fixes" in report
    assert "- tempo guardの再確認" in report
    assert "## Notable Good Moments" in report
    assert "- 3ターン目の沈黙の使い方" in report


def test_render_judge_report_md_partial_turns_label() -> None:
    parsed = judge.parse_judge_response(json.dumps(VALID_PAYLOAD))
    report = judge.render_judge_report_md(
        parsed,
        persona="boundary",
        turns_completed=4,
        turns_requested=10,
        source_session="saves/session_005",
        engine="claude",
        started_at="2026-05-08T06:00:00+09:00",
        judged_at="2026-05-08T06:30:00+09:00",
    )
    assert "- Turns: 4/10" in report


def test_render_judge_error_md_includes_error_and_optional_raw() -> None:
    error = judge.JudgeParseError("no JSON object")
    body = judge.render_judge_error_md(
        persona="passive",
        turns_completed=10,
        turns_requested=10,
        source_session="saves/session_001",
        engine="codex",
        started_at="2026-05-08T06:00:00+09:00",
        judged_at="2026-05-08T06:30:00+09:00",
        error=error,
        raw_response="LLMが返してきた生レスポンス本文",
    )

    assert body.startswith("# AI Playtest Judge Error")
    assert "- error_type: JudgeParseError" in body
    assert "- error: no JSON object" in body
    assert "Transcript本体は保持されています" in body
    assert "## Raw judge response" in body
    assert "LLMが返してきた生レスポンス本文" in body


def test_render_judge_error_md_without_raw_response() -> None:
    error = TimeoutError("engine timed out")
    body = judge.render_judge_error_md(
        persona="normal",
        turns_completed=10,
        turns_requested=10,
        source_session="saves/session_001",
        engine="codex",
        started_at="2026-05-08T06:00:00+09:00",
        judged_at="2026-05-08T06:30:00+09:00",
        error=error,
    )
    assert "## Raw judge response" not in body
    assert "- error_type: TimeoutError" in body
