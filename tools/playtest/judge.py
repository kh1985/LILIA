"""AI Playtest Judge: read transcript, score, and render report.md.

The judge is read-only. It loads the transcript from the run directory, asks
    an LLM to score it against a fixed rubric (PASS/WARN/FAIL plus per-item
scores and optional closure candidate evidence), and returns a parsed report.
The judge MUST NOT touch saves/, the run/session copy, or any other file
outside the run directory.
"""

from __future__ import annotations

import json
import re
from typing import Any


JUDGE_RESULTS: tuple[str, ...] = ("PASS", "WARN", "FAIL")
CLOSURE_HOOK_TYPES: tuple[str, ...] = ("main", "relationship", "life")
STORY_COMPLETION_STATUSES: tuple[str, ...] = (
    "continuing",
    "closure_candidate",
    "resolved",
    "deferred",
    "backgrounded",
    "worsened",
    "blocked",
)
_CLOSURE_HOOK_TYPE_ALIASES: dict[str, str] = {
    "main": "main",
    "relationship": "relationship",
    "life": "life",
    "life_exploration": "life",
    "life-exploration": "life",
}

JUDGE_SCORE_ITEMS: tuple[tuple[str, str], ...] = (
    ("voice_continuity", "Voice continuity"),
    ("character_subjectivity_first_reaction", "Character subjectivity / First reaction"),
    ("tempo_guard", "Tempo guard"),
    ("reply_affordance", "Reply affordance"),
    ("relationship_change_grounding", "Relationship change grounding"),
    ("relationship_change_audit", "Relationship change audit"),
    ("story_causality_scene_drive", "Story causality / Scene drive"),
    (
        "knowledge_boundary_player_orientation",
        "Knowledge boundary / Player orientation",
    ),
    ("inner_hidden_leakage", "Inner / hidden leakage"),
    ("over_leading", "Over-leading"),
    ("arc_closure_scene_progression", "Arc closure / Scene progression"),
)
JUDGE_SCORE_KEYS: tuple[str, ...] = tuple(key for key, _ in JUDGE_SCORE_ITEMS)
_JUDGE_SCORE_LABELS: dict[str, str] = {key: label for key, label in JUDGE_SCORE_ITEMS}

LEGACY_OPTIONAL_SCORE_DEFAULTS: dict[str, dict[str, Any]] = {
    "character_subjectivity_first_reaction": {
        "score": 3,
        "notes": "旧schema応答のため未評価。再judge推奨",
    },
    "relationship_change_audit": {
        "score": 3,
        "notes": "旧schema応答のため未評価。再judge推奨",
    },
    "knowledge_boundary_player_orientation": {
        "score": 3,
        "notes": "旧schema応答のため未評価。再judge推奨",
    },
    "story_causality_scene_drive": {
        "score": 3,
        "notes": "旧schema応答のため未評価。再judge推奨",
    },
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
    "2. character_subjectivity_first_reaction — 最初の一拍がユーザーの直近入力へのヒロイン反応になっているか。"
    "ヒロインがevent_cardやscene functionの進行役になっていないか。"
    "圧が観測可能な状況・所作・沈黙・台詞へ変換されているか。\n"
    "3. tempo_guard — 1ターンに前景化するhookが1本に絞られ、設定説明・問い・場面転換が詰め込まれていないか。\n"
    "4. reply_affordance — プレイヤーが次に何へ返せばよいか分かる入口がGMの応答にあるか。\n"
    "5. relationship_change_grounding — 関係や心境の変化に出来事の根拠があり、急進や停滞がないか。\n"
    "6. relationship_change_audit — 関係変化が実際の行動・会話・待機・境界線・約束・拒否・保留に基づき、"
    "信頼/安心感/親密さが早すぎず、拒否・保留・境界線・同行可否を尊重し、Relationship Hookが好感度化していないか。\n"
    "7. story_causality_scene_drive — sceneが確認手順や作業ログだけで止まらず、"
    "欲求/恐れ/誤解、選択の緊張、代償、不可逆変化、次の好奇心のどれかを生んでいるか。\n"
    "8. knowledge_boundary_player_orientation — プレイヤーが判断材料なしに選択や判断を迫られていないか。"
    "GM-only/meta情報が本文やヒロイン台詞に漏れていないか。"
    "ヒロインが知り得ない情報を断定していないか。"
    "不足しているのがプレイヤーへの可視手がかりなのか、出来事の因果不足なのかを混同していないか。\n"
    "9. inner_hidden_leakage — プレイヤー内心(括弧書き)、hidden vector、AFFINITY/bond、profile.md全文、internal prompt"
    "が漏れていないか。漏れがないほど高得点。\n"
    "10. over_leading — GMがプレイヤーの選択を奪うほど誘導していないか。誘導が弱いほど高得点。\n"
    "11. arc_closure_scene_progression — sceneの核成立後に余韻を引っ張りすぎず、"
    "入口と出口で状況・関係・問いのどれかが変わり、memory候補 / next hook / 次arc候補へ接続できているか。\n"
    "\n"
    "## Character Subjectivity / First Reaction 観点\n"
    "- 最初の一拍がユーザーの直近入力へのヒロイン反応になっているか。\n"
    "- ヒロインがevent_cardやscene functionの進行役になっていないか。\n"
    "- 圧が観測可能な状況・所作・沈黙・台詞へ変換されているか。\n"
    "- GM-only情報、hidden truth、relationship stake、next hookが本文やヒロイン台詞に漏れていないか。\n"
    "- ヒロイン自律行動が state / relationship / memory / beliefs に根拠を持つか。\n"
    "\n"
    "## Relationship Change Audit 観点\n"
    "- transcript内の行動、会話、待った時間、境界線、約束、拒否、保留だけを根拠にする。ユーザーの内心や未保存の推測でLILIAの認識を進めない。\n"
    "- WARN候補: 一度優しくしただけで深い信頼、安心、親密さ、呼び方、身体距離が大きく進む。\n"
    "- WARN/FAIL候補: 拒否、保留、境界確認、非同行や条件付き同行が次turnで無視され、了承済みや親密報酬として扱われる。\n"
    "- WARN/FAIL候補: 遠出、旅行、同居、危険地帯への同行が、LILIAの生活・仕事・関係段階・境界線確認なしに自動成立する。\n"
    "- WARN/FAIL候補: Relationship Hookが好感度、AFFINITY、bond、攻略ルート、正解選択肢列に見える。\n"
    "- WARN候補: memory / relationship / beliefs / decision_index / event_card / story_deck の保存責務が混ざる兆候がある。\n"
    "- PASS候補: 関係変化が実際に起きた出来事や言葉に接地し、拒否・保留・境界線が次の声や距離に残り、同行可否がagencyとして扱われる。\n"
    "- recommended_fixes には、根拠turn、どの境界線や保存先を見るべきか、親密化をどの距離まで戻すべきかを短く入れる。\n"
    "\n"
    "## Story Causality / Scene Drive 観点\n"
    "- transcript内で、出来事が関係・情報・状況・約束・境界線・信頼/警戒のどれかを実際に動かしたかを見る。\n"
    "- Player Orientationが十分でも、確認、照合、手順、復唱だけが続き、欲求/恐れ/誤解、選択の緊張、代償、不可逆変化、次の好奇心が弱い場合はWARN/FAIL候補。\n"
    "- WARN候補: ヒロインが有能に確認しているだけで、彼女本人のWant/Fear/Misbeliefや会話の衝突がsceneに効いていない。\n"
    "- WARN候補: プレイヤーが順番に従うだけで、どちらを選んでも何かが変わる迷い、関係に残るstake、次に見たい問いがない。\n"
    "- FAIL候補: 10ターン近く経っても、状況整理以外の変化がなく、memory / relationship / beliefs / next hook に保存すべき不可逆deltaが見えない。\n"
    "- PASS候補: 手順や調査があっても、その扱い方で信頼・警戒・情報・約束・境界線のどれかが変わり、次の好奇心へ接続している。\n"
    "- recommended_fixes には、どのturnで作業ログ化したか、Active Hook / Choice Tension / Irreversible Delta / Next Curiosity のどれを補うべきかを短く入れる。\n"
    "\n"
    "## Knowledge Boundary / Player Orientation 観点\n"
    "- transcript内でプレイヤーに見えている情報、共有済み情報、観察可能な手がかりだけを根拠にする。GM-only、meta、真相、未開示のstateをプレイヤーが知っている前提にしない。\n"
    "- Player Orientation不足は、プレイヤーが何を見て何を判断できるかの可視手がかり不足である。Story Causality不足は、出来事同士の因果や結果の接続不足であり、別の問題として書き分ける。\n"
    "- WARN候補: プレイヤーが知らない固有名、真相、目的、危険度、選択結果を前提に、選択・同行可否・推理・謝罪・告白などを迫っている。\n"
    "- WARN候補: 情報は存在するが、誰が知っている情報か、いま観察できる手がかりか、プレイヤーに共有済みかが曖昧で判断入口が弱い。\n"
    "- WARN/FAIL候補: GM-only、meta、knowledge_state、hidden vector、未開示truth、validator、checkpoint、保存責務などの管理情報が本文やヒロイン台詞に出ている。\n"
    "- WARN/FAIL候補: ヒロインが見ていない出来事、聞いていない内心、未共有のGM情報、別場所の事実、未来の結果を断定している。\n"
    "- PASS候補: 選択前に観察可能な手がかりや共有済み情報が短く提示され、知らないことは知らないまま扱われ、ヒロインの断定は本人が知り得る範囲に収まる。\n"
    "- recommended_fixes には、どのturnで誰に何が見えていなかったか、プレイヤーに渡すべき観察可能な手がかり、ヒロイン台詞から落とすべき未開示情報を短く入れる。\n"
    "\n"
    "## Arc Closure / Scene Progression 観点\n"
    "- closure候補: 別れの挨拶、戸が閉まる、店を出る、帰宅、就寝、翌朝、約束成立、境界線確認、そのsceneの問いに一度答えが出る。\n"
    "- WARN候補: closure候補後に同じsceneが長く続く、同じ余韻モチーフを3回以上反復する、10ターン以上同じsceneに留まり進行量が少ない。\n"
    "- WARN/FAIL候補: closure候補成立後に2ターン以上、足音・通知・気配・沈黙・視線・雨音などの同じ緊張を新しく足して延命し、next hook / 次に触れる入口へ渡していない。\n"
    "- WARN/FAIL候補: closure後の帰路、待機、独白、括弧内心、余韻だけの入力を理由に、同じsceneをさらに延命している。\n"
    "- WARN/FAIL候補: passive入力、短い同意、相づち、沈黙を理由に、閉店札・時計音・雨上がり・小物描写だけのターンを追加している。\n"
    "- WARN候補: 美文だがプレイヤーが次に何をするか分からない、next hook / 次に触れる入口がない。\n"
    "- PASS候補: sceneの核成立後1〜2ターン以内に自然に閉じ、closure後に小さな次入口やmemory候補 / next hook / 次arc候補が残る。\n"
    "- scene-tickが10/10に達した場合は、closure候補またはcheckpoint候補がないか確認する。ただしrunner metadataをPlay Mode本文の品質証拠として混ぜない。\n"
    "\n"
    "## Closure Candidate Reporting\n"
    "- closure_candidateは、sceneを閉じてもよい可能性があるturnをreport専用に記録する欄である。\n"
    "- next active hook candidateは、次に前景化できそうなhookを1本だけ推奨する。3本hookを選択肢UIとして並べない。\n"
    "- possible_next_hook_type は main / relationship / life のいずれかにする。\n"
    "- vagueな余韻だけをhook候補にしない。行動、場所、人、物、約束、未解決の問いなど、playable入口がある場合だけ候補にする。\n"
    "- closure候補後に2ターン以上続いている場合は、risk_if_continued と recommended_closure_action に、閉じるべきturnと次入口への渡し方を明記する。\n"
    "- recommended_fixes には、同じ緊張を足さず、次の1ターンで余韻整理またはnext hookへ渡す修正を入れる。passive入力で伸びている場合は、短い受け止めから閉店・帰宅・翌朝・次の連絡・見積もり・確認事項へ圧縮する修正を書く。\n"
    "- closure_candidate、hook_type、score、rubric、validator等の管理語はreport JSONでのみ使う。Play Mode本文に出てよい語として扱わない。\n"
    "\n"
    "## Story Completion / Next Story Arc Reporting\n"
    "- story_completion_statusはreport専用の軽量判定である。自動で本番stateへ適用しない。\n"
    "- statusは continuing / closure_candidate / resolved / deferred / backgrounded / worsened / blocked のいずれかにする。\n"
    "- closure_candidatesがあり、次arc候補へ渡せるがstory全体は未解決の場合は、continuingではなくclosure_candidateを使う。\n"
    "- recommended_next_arc_candidateは1本だけにする。複数候補や3択UIとして並べない。\n"
    "- suggested_active_hook_type は main / relationship / life のいずれかにする。\n"
    "- should_apply_now は必ず false、checkpoint_only は必ず true にする。\n"
    "- story_completion_status、next_arc_candidate、story_function等の管理語はreport JSONでのみ使い、Play Mode本文に出てよい語として扱わない。\n"
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
    '    "character_subjectivity_first_reaction": {"score": 1-5, "notes": "短く根拠"},\n'
    '    "tempo_guard":                   {"score": 1-5, "notes": "短く根拠"},\n'
    '    "reply_affordance":              {"score": 1-5, "notes": "短く根拠"},\n'
    '    "relationship_change_grounding": {"score": 1-5, "notes": "短く根拠"},\n'
    '    "relationship_change_audit":     {"score": 1-5, "notes": "短く根拠"},\n'
    '    "story_causality_scene_drive":   {"score": 1-5, "notes": "短く根拠"},\n'
    '    "knowledge_boundary_player_orientation": {"score": 1-5, "notes": "短く根拠"},\n'
    '    "inner_hidden_leakage":          {"score": 1-5, "notes": "短く根拠"},\n'
    '    "over_leading":                  {"score": 1-5, "notes": "短く根拠"},\n'
    '    "arc_closure_scene_progression": {"score": 1-5, "notes": "短く根拠"}\n'
    "  },\n"
    '  "warnings": ["軽微な懸念", "..."],\n'
    '  "failures": ["明確な違反", "..."],\n'
    '  "recommended_fixes": ["修正提案", "..."],\n'
    '  "notable_good_moments": ["良かった瞬間", "..."],\n'
    '  "closure_candidates": [\n'
    "    {\n"
    '      "closure_candidate_turns": [1, 2],\n'
    '      "reason": "closure候補と判断した短い根拠",\n'
    '      "possible_next_hook_type": "main|relationship|life",\n'
    '      "possible_next_question": "次に前景化できる問いを1本だけ",\n'
    '      "risk_if_continued": "続けた場合のdriftリスク",\n'
    '      "recommended_closure_action": "閉じ方または次hookへの渡し方"\n'
    "    }\n"
    "  ],\n"
    '  "story_completion": {\n'
    '    "story_completion_status": "continuing|closure_candidate|resolved|deferred|backgrounded|worsened|blocked",\n'
    '    "reason": "story/arc状態判定の短い根拠",\n'
    '    "recommended_next_arc_candidate": "次story arc候補を1本だけ",\n'
    '    "suggested_active_hook_type": "main|relationship|life",\n'
    '    "suggested_story_function": "次arc候補の軽いstory function",\n'
    '    "should_apply_now": false,\n'
    '    "checkpoint_only": true\n'
    "  }\n"
    "}\n"
    "```\n"
    "\n"
    "配列が空の場合は `[]` を返してください。null や省略は禁止です。\n"
    "closure_candidatesがない場合も `[]` を返してください。\n"
    "closure_candidatesは0件または1件だけにしてください。複数turnが候補なら `closure_candidate_turns` にまとめてください。\n"
    "story_completionが判定できない場合は continuing とし、recommended_next_arc_candidateは空文字にしてください。\n"
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

    def _required_string(item: dict[str, Any], field: str) -> str:
        value = item.get(field)
        if not isinstance(value, str):
            raise JudgeParseError(f"judge closure_candidates.{field} must be a string")
        return value.strip()

    def _closure_candidate_turns(value: Any) -> list[str]:
        if not isinstance(value, list):
            raise JudgeParseError(
                "judge closure_candidates.closure_candidate_turns must be an array"
            )
        turns: list[str] = []
        for turn in value:
            if isinstance(turn, bool) or not isinstance(turn, (int, float, str)):
                raise JudgeParseError(
                    "judge closure_candidates.closure_candidate_turns must contain strings or numbers"
                )
            if isinstance(turn, float) and turn.is_integer():
                turn_text = str(int(turn))
            else:
                turn_text = str(turn).strip()
            if turn_text:
                turns.append(turn_text)
        return turns

    def _closure_candidates() -> list[dict[str, Any]]:
        value = data.get("closure_candidates", [])
        if value is None:
            return []
        if not isinstance(value, list):
            raise JudgeParseError("judge 'closure_candidates' must be an array")
        if len(value) > 1:
            raise JudgeParseError(
                "judge 'closure_candidates' must contain at most one recommended next active hook candidate"
            )

        candidates: list[dict[str, Any]] = []
        for raw in value:
            if not isinstance(raw, dict):
                raise JudgeParseError(
                    "judge 'closure_candidates' must be an array of objects"
                )

            hook_type_raw = _required_string(raw, "possible_next_hook_type").lower()
            hook_type = _CLOSURE_HOOK_TYPE_ALIASES.get(hook_type_raw)
            if hook_type not in CLOSURE_HOOK_TYPES:
                raise JudgeParseError(
                    "judge closure_candidates.possible_next_hook_type "
                    f"must be one of {CLOSURE_HOOK_TYPES}, got {hook_type_raw!r}"
                )

            candidates.append(
                {
                    "closure_candidate_turns": _closure_candidate_turns(
                        raw.get("closure_candidate_turns", [])
                    ),
                    "reason": _required_string(raw, "reason"),
                    "possible_next_hook_type": hook_type,
                    "possible_next_question": _required_string(
                        raw, "possible_next_question"
                    ),
                    "risk_if_continued": _required_string(raw, "risk_if_continued"),
                    "recommended_closure_action": _required_string(
                        raw, "recommended_closure_action"
                    ),
                }
            )
        return candidates

    def _story_completion() -> dict[str, Any] | None:
        value = data.get("story_completion")
        if value is None:
            return None
        if not isinstance(value, dict):
            raise JudgeParseError("judge 'story_completion' must be an object")

        status = _required_string(value, "story_completion_status")
        if status not in STORY_COMPLETION_STATUSES:
            raise JudgeParseError(
                "judge story_completion.story_completion_status must be one of "
                f"{STORY_COMPLETION_STATUSES}, got {status!r}"
            )

        hook_type_raw = _required_string(value, "suggested_active_hook_type").lower()
        hook_type = _CLOSURE_HOOK_TYPE_ALIASES.get(hook_type_raw)
        if hook_type not in CLOSURE_HOOK_TYPES:
            raise JudgeParseError(
                "judge story_completion.suggested_active_hook_type "
                f"must be one of {CLOSURE_HOOK_TYPES}, got {hook_type_raw!r}"
            )

        should_apply_now = value.get("should_apply_now")
        if not isinstance(should_apply_now, bool):
            raise JudgeParseError("judge story_completion.should_apply_now must be a boolean")
        if should_apply_now:
            raise JudgeParseError("judge story_completion.should_apply_now must be false")

        checkpoint_only = value.get("checkpoint_only")
        if not isinstance(checkpoint_only, bool):
            raise JudgeParseError("judge story_completion.checkpoint_only must be a boolean")
        if not checkpoint_only:
            raise JudgeParseError("judge story_completion.checkpoint_only must be true")

        return {
            "story_completion_status": status,
            "reason": _required_string(value, "reason"),
            "recommended_next_arc_candidate": _required_string(
                value, "recommended_next_arc_candidate"
            ),
            "suggested_active_hook_type": hook_type,
            "suggested_story_function": _required_string(
                value, "suggested_story_function"
            ),
            "should_apply_now": False,
            "checkpoint_only": True,
        }

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
        "closure_candidates": _closure_candidates(),
        "story_completion": _story_completion(),
    }


def _format_bullets(items: list[str], empty_marker: str = "- (なし)") -> str:
    if not items:
        return empty_marker
    return "\n".join(f"- {item}" for item in items)


def _table_cell(value: object) -> str:
    text = str(value).replace("\n", " ").strip()
    return text.replace("|", "\\|") or "-"


def _format_closure_candidates(candidates: list[dict[str, Any]]) -> str:
    if not candidates:
        return "- (なし)"

    rows = [
        "| Closure turns | Reason | Next hook | Next question | Risk if continued | Recommended action |",
        "|---|---|---|---|---|---|",
    ]
    for candidate in candidates:
        turns = ", ".join(candidate.get("closure_candidate_turns", [])) or "-"
        rows.append(
            "| "
            + " | ".join(
                [
                    _table_cell(turns),
                    _table_cell(candidate.get("reason", "")),
                    _table_cell(candidate.get("possible_next_hook_type", "")),
                    _table_cell(candidate.get("possible_next_question", "")),
                    _table_cell(candidate.get("risk_if_continued", "")),
                    _table_cell(candidate.get("recommended_closure_action", "")),
                ]
            )
            + " |"
        )
    return "\n".join(rows)


def _format_story_completion(story_completion: dict[str, Any] | None) -> str:
    if not story_completion:
        return "- (なし)"

    rows = [
        "| Status | Reason | Next arc candidate | Active hook | Story function | should_apply_now | checkpoint_only |",
        "|---|---|---|---|---|---|---|",
        "| "
        + " | ".join(
            [
                _table_cell(story_completion.get("story_completion_status", "")),
                _table_cell(story_completion.get("reason", "")),
                _table_cell(story_completion.get("recommended_next_arc_candidate", "")),
                _table_cell(story_completion.get("suggested_active_hook_type", "")),
                _table_cell(story_completion.get("suggested_story_function", "")),
                _table_cell(str(story_completion.get("should_apply_now", False)).lower()),
                _table_cell(str(story_completion.get("checkpoint_only", True)).lower()),
            ]
        )
        + " |",
    ]
    return "\n".join(rows)


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
        "## Closure Candidates / Next Active Hook Candidate",
        "",
        _format_closure_candidates(parsed.get("closure_candidates", [])),
        "",
        "## Story Completion / Next Story Arc Candidate",
        "",
        _format_story_completion(parsed.get("story_completion")),
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
