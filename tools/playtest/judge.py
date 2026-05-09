"""AI Playtest Judge: read transcript, score, and render report.md.

The judge is read-only. It loads the transcript from the run directory, asks
an LLM to score it against a fixed rubric (PASS/WARN/FAIL plus seven per-item
scores), and returns a parsed report. The judge MUST NOT touch saves/, the
run/session copy, or any other file outside the run directory.
"""

from __future__ import annotations

import json
import re
from typing import Any


JUDGE_RESULTS: tuple[str, ...] = ("PASS", "WARN", "FAIL")

JUDGE_SCORE_ITEMS: tuple[tuple[str, str], ...] = (
    ("voice_continuity", "Voice continuity"),
    ("tempo_guard", "Tempo guard"),
    ("reply_affordance", "Reply affordance"),
    ("relationship_change_grounding", "Relationship change grounding"),
    ("inner_hidden_leakage", "Inner / hidden leakage"),
    ("over_leading", "Over-leading"),
    ("arc_closure_scene_progression", "Arc closure / Scene progression"),
)
JUDGE_SCORE_KEYS: tuple[str, ...] = tuple(key for key, _ in JUDGE_SCORE_ITEMS)
_JUDGE_SCORE_LABELS: dict[str, str] = {key: label for key, label in JUDGE_SCORE_ITEMS}

LEGACY_OPTIONAL_SCORE_DEFAULTS: dict[str, dict[str, Any]] = {
    "arc_closure_scene_progression": {
        "score": 3,
        "notes": "旧schema応答のため未評価。再judge推奨",
    }
}


JUDGE_INSTRUCTION = (
    "# AI Playtest Judge\n"
    "あなたは LILIA の AI Playtest の判定者です。\n"
    "GMとAIプレイヤーのtranscriptだけを根拠にしてください。\n"
    "transcriptに書かれていない事象、推測、想像を根拠にしてはいけません。\n"
    "ファイル編集、shell実行、git操作、scene-tick / apply-turn 実行は行いません。\n"
    "transcriptは saves/ ではなく playtests/runs/<run>/ 配下のものですが、内容そのものを判定してください。\n"
    "\n"
    "## 評価項目 (順序を保つこと、それぞれ1〜5)\n"
    "1. voice_continuity — ヒロインの呼び方・口調・距離感が崩れていないか。\n"
    "2. tempo_guard — 1ターンに前景化するhookが1本に絞られ、設定説明・問い・場面転換が詰め込まれていないか。\n"
    "3. reply_affordance — プレイヤーが次に何へ返せばよいか分かる入口がGMの応答にあるか。\n"
    "4. relationship_change_grounding — 関係や心境の変化に出来事の根拠があり、急進や停滞がないか。\n"
    "5. inner_hidden_leakage — プレイヤー内心(括弧書き)、hidden vector、AFFINITY/bond、profile.md全文、internal prompt"
    "が漏れていないか。漏れがないほど高得点。\n"
    "6. over_leading — GMがプレイヤーの選択を奪うほど誘導していないか。誘導が弱いほど高得点。\n"
    "7. arc_closure_scene_progression — sceneの核成立後に余韻を引っ張りすぎず、"
    "入口と出口で状況・関係・問いのどれかが変わり、memory候補 / next hook / 次arc候補へ接続できているか。\n"
    "\n"
    "## Arc Closure / Scene Progression 観点\n"
    "- closure候補: 別れの挨拶、戸が閉まる、店を出る、帰宅、就寝、翌朝、約束成立、境界線確認、そのsceneの問いに一度答えが出る。\n"
    "- WARN候補: closure候補後に同じsceneが長く続く、同じ余韻モチーフを3回以上反復する、10ターン以上同じsceneに留まり進行量が少ない。\n"
    "- WARN候補: 美文だがプレイヤーが次に何をするか分からない、next hook / 次に触れる入口がない。\n"
    "- PASS候補: sceneの核成立後1〜2ターン以内に自然に閉じ、closure後に小さな次入口やmemory候補 / next hook / 次arc候補が残る。\n"
    "\n"
    "## スコア基準\n"
    "- 5: 問題なし。\n"
    "- 4: 良好。軽微な懸念のみ。\n"
    "- 3: 注意。明確な弱点が1つある。\n"
    "- 2: 失敗。明らかな違反がある。\n"
    "- 1: 致命的。重大違反が複数ある。\n"
    "\n"
    "## 総合判定\n"
    "- PASS: 全項目4以上で、failuresが空。\n"
    "- WARN: 全項目3以上で、failuresが空。\n"
    "- FAIL: いずれかの項目が2以下、もしくはfailuresが1件以上。\n"
    "\n"
    "## 出力形式\n"
    "出力は **必ず** 次の単一fenced JSONブロックだけを返してください。\n"
    "前置き・解説・他テキスト・複数ブロックは禁止です。\n"
    "\n"
    "```json\n"
    "{\n"
    '  "result": "PASS|WARN|FAIL",\n'
    '  "summary": "1〜2文でtranscript全体の所感",\n'
    '  "scores": {\n'
    '    "voice_continuity":              {"score": 1-5, "notes": "短く根拠"},\n'
    '    "tempo_guard":                   {"score": 1-5, "notes": "短く根拠"},\n'
    '    "reply_affordance":              {"score": 1-5, "notes": "短く根拠"},\n'
    '    "relationship_change_grounding": {"score": 1-5, "notes": "短く根拠"},\n'
    '    "inner_hidden_leakage":          {"score": 1-5, "notes": "短く根拠"},\n'
    '    "over_leading":                  {"score": 1-5, "notes": "短く根拠"},\n'
    '    "arc_closure_scene_progression": {"score": 1-5, "notes": "短く根拠"}\n'
    "  },\n"
    '  "warnings": ["軽微な懸念", "..."],\n'
    '  "failures": ["明確な違反", "..."],\n'
    '  "recommended_fixes": ["修正提案", "..."],\n'
    '  "notable_good_moments": ["良かった瞬間", "..."]\n'
    "}\n"
    "```\n"
    "\n"
    "配列が空の場合は `[]` を返してください。null や省略は禁止です。\n"
    "notesは80字以内、各配列要素も120字以内を目安に簡潔に書いてください。\n"
)


class JudgeError(RuntimeError):
    """Raised when judging fails."""


class JudgeParseError(JudgeError):
    """Raised when the judge response cannot be parsed into the expected shape."""


def build_judge_prompt(
    *,
    persona: str,
    turns_completed: int,
    transcript_md_text: str,
) -> str:
    """Assemble the judge prompt that wraps a transcript with the rubric."""

    parts = [
        JUDGE_INSTRUCTION,
        "## このrunのメタ情報",
        f"- persona: {persona}",
        f"- turns_completed: {turns_completed}",
        "## Transcript (judge対象)",
        transcript_md_text.rstrip(),
        "## 指示",
        "上のtranscriptだけを根拠に、上記JSON形式で1ブロックだけ返してください。",
    ]
    return "\n\n".join(parts).rstrip() + "\n"


_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)


def _extract_json_block(text: str) -> str:
    """Pick out the JSON object from a judge response.

    Accepts: a fenced ```json ... ``` block, a fenced ``` ... ``` block, or a
    raw JSON object. Falls back to the first `{` ... last `}` slice if no
    fence is present.
    """

    if not text or not text.strip():
        raise JudgeParseError("judge response is empty")

    for match in _FENCE_RE.finditer(text):
        candidate = match.group(1).strip()
        if candidate.startswith("{") and candidate.endswith("}"):
            return candidate

    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        return stripped[start : end + 1]

    raise JudgeParseError("could not find a JSON object in judge response")


def parse_judge_response(text: str) -> dict[str, Any]:
    """Parse a raw judge LLM response into a normalized dict.

    Returns a dict with keys: result, summary, scores (dict of key→{score,notes}),
    warnings, failures, recommended_fixes, notable_good_moments. Raises
    JudgeParseError if anything required is missing or malformed.
    """

    block = _extract_json_block(text)
    try:
        data = json.loads(block)
    except json.JSONDecodeError as exc:
        raise JudgeParseError(f"judge response is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise JudgeParseError("judge response JSON must be an object")

    result_raw = data.get("result")
    if not isinstance(result_raw, str):
        raise JudgeParseError("judge response missing 'result' string")
    result = result_raw.strip().upper()
    if result not in JUDGE_RESULTS:
        raise JudgeParseError(
            f"judge result must be one of {JUDGE_RESULTS}, got {result_raw!r}"
        )

    summary = data.get("summary", "")
    if not isinstance(summary, str):
        raise JudgeParseError("judge 'summary' must be a string")

    scores_raw = data.get("scores")
    if not isinstance(scores_raw, dict):
        raise JudgeParseError("judge response missing 'scores' object")

    scores: dict[str, dict[str, Any]] = {}
    compatibility_warnings: list[str] = []
    for key in JUDGE_SCORE_KEYS:
        item = scores_raw.get(key)
        if not isinstance(item, dict):
            if key in LEGACY_OPTIONAL_SCORE_DEFAULTS:
                default_item = LEGACY_OPTIONAL_SCORE_DEFAULTS[key]
                scores[key] = {
                    "score": default_item["score"],
                    "notes": default_item["notes"],
                }
                compatibility_warnings.append(
                    f"judge response missing '{key}' score; treated as legacy schema"
                )
                continue
            raise JudgeParseError(f"judge scores missing '{key}' object")
        score_value = item.get("score")
        if isinstance(score_value, bool) or not isinstance(score_value, (int, float)):
            raise JudgeParseError(f"judge scores.{key}.score must be a number")
        score_int = int(score_value)
        if score_int < 1 or score_int > 5:
            raise JudgeParseError(
                f"judge scores.{key}.score must be in [1,5], got {score_value}"
            )
        notes = item.get("notes", "")
        if not isinstance(notes, str):
            raise JudgeParseError(f"judge scores.{key}.notes must be a string")
        scores[key] = {"score": score_int, "notes": notes.strip()}

    def _string_list(field: str) -> list[str]:
        value = data.get(field, [])
        if value is None:
            return []
        if not isinstance(value, list):
            raise JudgeParseError(f"judge '{field}' must be an array")
        result_list: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise JudgeParseError(
                    f"judge '{field}' must be an array of strings"
                )
            text_item = item.strip()
            if text_item:
                result_list.append(text_item)
        return result_list

    warnings = compatibility_warnings + _string_list("warnings")
    if compatibility_warnings and result == "PASS":
        result = "WARN"

    return {
        "result": result,
        "summary": summary.strip(),
        "scores": scores,
        "warnings": warnings,
        "failures": _string_list("failures"),
        "recommended_fixes": _string_list("recommended_fixes"),
        "notable_good_moments": _string_list("notable_good_moments"),
    }


def _format_bullets(items: list[str], empty_marker: str = "- (なし)") -> str:
    if not items:
        return empty_marker
    return "\n".join(f"- {item}" for item in items)


def render_judge_report_md(
    parsed: dict[str, Any],
    *,
    persona: str,
    turns_completed: int,
    turns_requested: int,
    source_session: str,
    engine: str,
    started_at: str,
    judged_at: str,
) -> str:
    """Render the parsed judge response as a Markdown report."""

    scores = parsed["scores"]
    score_rows = "\n".join(
        f"| {_JUDGE_SCORE_LABELS[key]} | {scores[key]['score']}/5 | {scores[key]['notes'] or '-'} |"
        for key in JUDGE_SCORE_KEYS
    )

    summary_text = parsed.get("summary") or "(summary未記入)"
    turns_label = (
        str(turns_requested)
        if turns_completed == turns_requested
        else f"{turns_completed}/{turns_requested}"
    )

    sections = [
        "# AI Playtest Judge Report",
        "",
        "## Summary",
        "",
        f"- Result: {parsed['result']}",
        f"- Persona: {persona}",
        f"- Turns: {turns_label}",
        f"- Session: {source_session}",
        f"- Engine: {engine}",
        f"- Started at: {started_at}",
        f"- Judged at: {judged_at}",
        "",
        summary_text,
        "",
        "## Scores",
        "",
        "| Item | Score | Notes |",
        "|---|---:|---|",
        score_rows,
        "",
        "## Warnings",
        "",
        _format_bullets(parsed["warnings"]),
        "",
        "## Failures",
        "",
        _format_bullets(parsed["failures"]),
        "",
        "## Recommended Fixes",
        "",
        _format_bullets(parsed["recommended_fixes"]),
        "",
        "## Notable Good Moments",
        "",
        _format_bullets(parsed["notable_good_moments"]),
        "",
    ]
    return "\n".join(sections)


def render_judge_error_md(
    *,
    persona: str,
    turns_completed: int,
    turns_requested: int,
    source_session: str,
    engine: str,
    started_at: str,
    judged_at: str,
    error: BaseException,
    raw_response: str | None = None,
) -> str:
    """Render a judge_error.md when judging fails. Transcript itself is preserved."""

    body = [
        "# AI Playtest Judge Error",
        "",
        f"- persona: {persona}",
        f"- turns_completed: {turns_completed}",
        f"- turns_requested: {turns_requested}",
        f"- source_session: {source_session}",
        f"- engine: {engine}",
        f"- started_at: {started_at}",
        f"- judged_at: {judged_at}",
        f"- error_type: {type(error).__name__}",
        f"- error: {error}",
        "",
        "Transcript本体は保持されています (transcript.jsonl / transcript.md)。",
        "judgeはtranscriptを読むだけで本番sessionには書き込みません。",
        "",
    ]
    if raw_response is not None:
        body.extend(
            [
                "## Raw judge response",
                "",
                "```",
                raw_response.rstrip(),
                "```",
                "",
            ]
        )
    return "\n".join(body)
