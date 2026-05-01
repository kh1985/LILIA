#!/usr/bin/env python3
"""Convert character YAML material into lilia/main/profile.md."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.character.core.schema import CharacterSheet  # noqa: E402


DEEPENING_TAGS = [
    "境界線を尊重された",
    "自分から頼った",
    "自分から断った",
    "呼び方が変わった",
    "沈黙を共有した",
    "小さな約束が残った",
    "誤解を修正した",
    "摩擦を処理した",
    "秘密の一部を共有した",
    "親密後のaftercareが残った",
    "他者との関係について確認した",
    "離れる自由を確認した",
    "能力との相互作用を確認した",
]

META_PATTERNS = [
    r"初回\s*sceneで観察する",
    r"まだ言わないことは初回\s*sceneで小さく観察する",
    r"関係で育つ余白",
    r"未確定",
    r"数値ではなく",
    r"保存する",
    r"\bprofile\b",
    r"\bprompt\b",
]

SOURCE_FALLBACK = "まだ固定しない"


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        if not data:
            raise ValueError("YAML list is empty")
        data = data[0]
    if isinstance(data, dict) and "characters" in data and isinstance(data["characters"], list):
        if not data["characters"]:
            raise ValueError("characters list is empty")
        data = data["characters"][0]
    if not isinstance(data, dict):
        raise ValueError("character YAML must be a mapping")
    return data


def parse_answers(path: Path | None) -> dict[int | str, str]:
    if path is None:
        return {}
    content = path.read_text(encoding="utf-8")
    sections: dict[int | str, list[str]] = {}
    current: int | str | None = None
    for line in content.splitlines():
        match = re.match(r"^##\s*Q([1-7])(?:\b|[.\s:：-])", line.strip(), re.IGNORECASE)
        if match:
            current = int(match.group(1))
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    if not sections and content.strip():
        return {"summary": content.strip()}
    return {key: "\n".join(lines).strip() for key, lines in sections.items()}


def answer(answers: dict[int | str, str], key: int | str, fallback: str = "未設定") -> str:
    value = answers.get(key, "")
    return value.strip() if isinstance(value, str) and value.strip() else fallback


def bullets(items: Iterable[str], fallback: str = "未設定") -> str:
    clean = [item.strip() for item in items if item and item.strip()]
    if not clean:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in clean)


def kv_block(items: Iterable[tuple[str, str]]) -> str:
    return "\n".join(f"{key}: {value}" for key, value in items)


def compact_text(text: str | None) -> str:
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def is_meta_text(text: str | None) -> bool:
    clean = compact_text(text)
    if not clean or clean in {"未設定", "未確定"}:
        return True
    return any(re.search(pattern, clean, re.IGNORECASE) for pattern in META_PATTERNS)


def source_text(text: str | None, fallback: str = "") -> str:
    clean = compact_text(text)
    if is_meta_text(clean):
        return fallback
    return clean


def source_answer(answers: dict[int | str, str], key: int | str, fallback: str = "") -> str:
    return source_text(answers.get(key, ""), fallback)


def first_sentence(text: str | None) -> str:
    clean = source_text(text)
    if not clean:
        return ""
    return re.split(r"[。.!?！？]", clean, maxsplit=1)[0].strip()


def dedupe(items: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        clean = source_text(item)
        if not clean:
            continue
        key = re.sub(r"\s+", "", clean)
        if key in seen:
            continue
        seen.add(key)
        result.append(clean)
    return result


def join_items(items: Iterable[str], fallback: str = SOURCE_FALLBACK) -> str:
    clean = dedupe(items)
    return "、".join(clean) if clean else fallback


def contains_any(text: str, words: Iterable[str]) -> bool:
    return any(word in text for word in words)


def appearance_text(char: CharacterSheet) -> str:
    parts = []
    if char.appearance.hair_style:
        parts.append(f"髪型: {char.appearance.hair_style}")
    if char.appearance.hair_color:
        parts.append(f"髪色: {char.appearance.hair_color}")
    if char.appearance.notes:
        parts.append(char.appearance.notes)
    return " / ".join(parts) if parts else "未設定"


def tone_examples(char: CharacterSheet) -> str:
    if not char.tone.examples:
        return "  - 未設定"
    lines: list[str] = []
    for example in char.tone.examples:
        if example.user:
            lines.append(f"  - User: {example.user} / LILIA: {example.char}")
        else:
            lines.append(f"  - LILIA: {example.char}")
    return "\n".join(lines)


def reaction_value(char: CharacterSheet, *keywords: str, fallback: str = "未設定") -> str:
    for key, value in char.reactions.items():
        if any(word in key for word in keywords):
            return source_text(value, fallback)
    return fallback


def all_reactions(char: CharacterSheet) -> str:
    if not char.reactions:
        return "- 未設定"
    lines = []
    for key, value in char.reactions.items():
        clean = source_text(value)
        if clean:
            lines.append(f"- {key}: {clean}")
    return "\n".join(lines) if lines else "- 未設定"


def source_personality(char: CharacterSheet) -> list[str]:
    return dedupe(char.personality)


def infer_values(char: CharacterSheet) -> list[str]:
    text = " ".join(
        source_text(value)
        for value in [
            char.occupation,
            char.tone.rule,
            " ".join(char.personality),
            " ".join(char.reactions.values()),
            char.context.backstory,
            char.context.current_situation,
        ]
    )
    values = [
        "自分で決める余地を残すこと",
        "相手に負担を渡しすぎないこと",
    ]
    if contains_any(text, ["予定", "ドタキャン", "帰るタイミング", "崩れ"]):
        values.append("予定が崩れても平気な顔を保つこと")
    if contains_any(text, ["踏み込", "軽口", "軽く", "距離", "扱われ"]):
        values.append("軽く扱われないこと")
    if contains_any(text, ["クライアント", "フリーランス", "在宅", "一人でやれる"]):
        values.append("仕事と生活の範囲を自分で決めること")
    return dedupe(values)


def infer_everyday_anchors(char: CharacterSheet) -> dict[str, str]:
    role = source_text(char.occupation)
    backstory = source_text(char.context.backstory)
    current = source_text(char.context.current_situation)
    appearance = source_text(char.appearance.notes)
    text = " ".join([role, backstory, current, appearance])

    places: list[str] = []
    if "コンビニ" in text:
        places.append("夜のコンビニ前")
    if "帰" in current:
        places.append("帰り道")
    if contains_any(text, ["在宅", "上京", "一人でやれる"]):
        places.append("一人で戻る部屋")
    if not places:
        places.append("日常の用事が残る場所")

    tasks: list[str] = []
    role_summary = first_sentence(role)
    if role_summary:
        tasks.append(role_summary)
    if contains_any(text, ["Web", "デザイナー"]):
        tasks.append("Web制作")
    if "クライアント" in text:
        tasks.append("クライアント連絡")
    if "在宅" in text:
        tasks.append("在宅作業")
    if "コンビニ" in current:
        tasks.append("夜の買い物")
    if contains_any(current, ["予定", "ドタキャン"]):
        tasks.append("予定変更後の帰り支度")

    objects: list[str] = []
    if contains_any(text, ["スマホ", "連絡", "予定", "ドタキャン", "クライアント"]):
        objects.append("スマホ")
    if "コンビニ" in text:
        objects.extend(["レシート", "コンビニ袋"])
    if "トート" in text:
        objects.append("トートバッグ")
    if contains_any(text, ["傘", "雨", "濡"]):
        objects.append("ビニール傘")

    scene_objects: list[str] = []
    if "コンビニ" in text:
        scene_objects.extend(["温かい飲み物", "レシート", "コンビニ袋"])
    if contains_any(text, ["予定", "ドタキャン", "連絡"]):
        scene_objects.append("未読通知のあるスマホ")
    if "トート" in text:
        scene_objects.append("ロゴ入りのトートバッグ")
    if contains_any(text, ["傘", "雨", "濡"]):
        scene_objects.append("開きにくいビニール傘")
    if not scene_objects:
        scene_objects.append("手元に残っている小さな持ち物")

    return {
        "places": join_items(places),
        "tasks": join_items(tasks),
        "objects": join_items(objects),
        "scene_objects": join_items(scene_objects),
    }


def infer_context_event(char: CharacterSheet, q6: str) -> str:
    current = source_text(char.context.current_situation)
    if q6 and q6 != current:
        return q6
    if contains_any(current, ["予定", "ドタキャン", "コンビニ"]):
        return "帰るタイミングを探す間に、スマホの通知か手元の買い物が会話のきっかけになる"
    return "生活上の小さな用事が会話のきっかけになる"


def infer_presence_reason(char: CharacterSheet) -> str:
    current = source_text(char.context.current_situation)
    if contains_any(current, ["友人", "ドタキャン", "予定"]):
        return "友人との予定が消えて、帰る踏ん切りがつかないため"
    if "コンビニ" in current:
        return "買い物のあと、帰る前に少し足が止まっているため"
    if "仕事" in current:
        return "仕事か用事の切れ目で、次の行動を決めきれていないため"
    return "日常の用事の途中で、少しだけ足が止まっているため"


def infer_contradictions(char: CharacterSheet) -> list[str]:
    tone = source_text(char.tone.rule)
    personality = " ".join(source_personality(char))
    current = source_text(char.context.current_situation)
    text = " ".join([tone, personality, current])

    outward = "平気な顔で軽口を返す" if contains_any(text, ["軽口", "平気", "フラット"]) else "落ち着いて見える態度を保つ"
    inward = "予定が崩れて少し所在なくなっている" if contains_any(current, ["予定", "ドタキャン", "帰るタイミング"]) else "言葉にする前に気持ちを内側で整理している"
    contradiction = "誰かと話したいが、自分から寂しいとは言わない"
    if contains_any(personality, ["頼る", "一人で抱え", "最後の手段"]):
        contradiction = "助けがあると楽になる場面ほど、頼る相手を選びすぎる"
    return [
        f"表: {outward}",
        f"裏: {inward}",
        f"矛盾: {contradiction}",
        "矛盾: 近づきたい気配があっても、踏み込まれると返事が遅れる",
    ]


def infer_unspoken(char: CharacterSheet) -> list[str]:
    current = source_text(char.context.current_situation)
    backstory = source_text(char.context.backstory)
    appearance = source_text(char.appearance.notes)
    text = " ".join([current, backstory, appearance, char.occupation or ""])
    items: list[str] = []
    if contains_any(current, ["友人", "ドタキャン"]):
        items.append("友人にドタキャンされたことを、気にしていないふりをしている")
    if contains_any(text, ["スマホ", "連絡", "予定", "ドタキャン", "レシート"]):
        items.append("スマホの通知やレシートの内容を見られたくない")
    if contains_any(current, ["帰る", "帰り", "タイミング"]):
        items.append("一緒に帰れると少し助かるが、送ってほしいとは言いたくない")
    if contains_any(backstory, ["仕事", "広げる気", "一人でやれる"]):
        items.append("仕事の範囲を広げない理由は、まだ説明しない")
    if not items:
        items.append("事情を聞かれても、すぐ整理して話せる状態ではない")
    return dedupe(items)


def infer_layer_one(char: CharacterSheet) -> str:
    backstory = source_text(char.context.backstory)
    role = source_text(char.occupation)
    if contains_any(backstory, ["上京", "地方"]) and role:
        return "上京して数年、自分で扱える範囲の仕事と生活を守っている"
    if backstory:
        return first_sentence(backstory) or backstory
    return first_sentence(role) or "自分の生活を自分の速度で保っている"


def infer_layer_two(values: list[str]) -> str:
    if values:
        return " / ".join(values[:2])
    return "自分で選べる余地と、相手への負担を増やしすぎない距離感"


def infer_person_design_flaw(char: CharacterSheet) -> str:
    personality = " ".join(source_personality(char))
    if contains_any(personality, ["頼る", "一人で抱え", "最後の手段"]):
        return "頼れば楽になる場面でも、相手を選びすぎて言い出すのが遅れる"
    if contains_any(personality, ["流す", "寡黙", "沈黙"]):
        return "踏み込まれると軽く流すか黙り、必要な説明まで遅れる"
    return "平気な顔を保ちすぎて、困っていることが伝わりにくい"


def render_profile(char: CharacterSheet, answers: dict[int | str, str]) -> str:
    age = f"{char.age}" if char.age is not None else "未設定"
    role = source_text(char.occupation, SOURCE_FALLBACK)
    backstory = source_text(char.context.backstory, "深い過去はまだ固定しない")
    current = source_text(char.context.current_situation, "日常の小さな用事の途中にいる")
    q1 = source_answer(answers, 1, "落ち着いて見えるが、返答の間や持ち物に乱れが出る")
    q2 = source_answer(answers, 2, "互いをまだ深く知らない距離")
    q5 = source_answer(answers, 5, "踏み込みすぎず、境界線を確認する")
    q6 = source_answer(answers, 6, "")
    q7 = source_answer(answers, 7, "恋愛成立や重い事件を急がない")

    personality = source_personality(char)
    first_personality = personality[0] if personality else "話しかけられれば返すが、自分から急に距離を詰めない"
    second_personality = (
        personality[1]
        if len(personality) > 1
        else "困った時ほど一人で抱え、頼る相手を選ぶまで時間がかかる"
    )
    third_personality = (
        personality[2]
        if len(personality) > 2
        else "褒められると一度受け流し、話題を変えようとする"
    )
    values = infer_values(char)
    anchors = infer_everyday_anchors(char)
    small_event = infer_context_event(char, q6)
    contradictions = infer_contradictions(char)
    unspoken = infer_unspoken(char)
    layer_one = infer_layer_one(char)
    layer_two = infer_layer_two(values)
    flaw = infer_person_design_flaw(char)
    forbidden = dedupe(
        [
            *char.forbidden,
            q7,
            "初期から恋愛成立や親密成立を確定しない",
        ]
    )

    sections = [
        "# LILIA Persona Profile",
        "",
        "このファイルは、初回からLILIAを安定して演じるための人格正本である。",
        "ただし、完成済み攻略キャラカードではない。",
        "関係で育った内容は core / voice / relationship / memory / beliefs へ分解して記録する。",
        "",
        "## 基礎情報",
        kv_block(
            [
                ("name", char.name),
                ("age", age),
                ("role", role),
                ("appearance", appearance_text(char)),
            ]
        ),
        "",
        "## tone",
        f"rule: {char.tone.rule}",
        "examples:",
        tone_examples(char),
        "",
        "## personality",
        f"- 行動で見える性格: {first_personality}",
        f"- 困った時の出方: {reaction_value(char, '困', fallback=second_personality)}",
        f"- 褒められた時の反応: {reaction_value(char, '褒', fallback=third_personality)}",
        f"- 怒った時の反応: {reaction_value(char, '怒', fallback='声を荒げるより、言葉数や距離に出る')}",
        f"- 頼る / 断る / 待つ の傾向: {q5}",
        "",
        "## values",
        bullets(values),
        "",
        "## everyday anchors",
        f"- 生活の場所: {anchors['places']}",
        f"- 仕事 / 用事 / 習慣: {anchors['tasks']}",
        f"- よく触る物: {anchors['objects']}",
        f"- 初回sceneで使える具体物: {anchors['scene_objects']}",
        "",
        "## memories",
        "- 初期時点で既にある生活上の記憶",
        f"- {backstory}",
        "- 実際に過去として固定してよいものだけ",
        "",
        "## contradictions",
        bullets(contradictions),
        "",
        "## unspoken",
        bullets(unspoken),
        "- すぐには開示しない理由: 事情を整理する前に同情や判断を向けられたくないため。",
        "",
        "## reactions",
        f"能力や異常性に触れた相手には: {reaction_value(char, '能力', '異常', fallback='すぐには信じず、境界線と安全を確認する')}",
        f"弱っている相手には: {reaction_value(char, '弱', fallback='助けようとするが、相手の主体性を奪わない')}",
        f"急かされたとき: {reaction_value(char, '急', fallback='一歩引き、答えを迫られるほど閉じる')}",
        f"感謝されたとき: {reaction_value(char, '感謝', 'ありがとう', fallback='受け取るが、照れや距離をごまかす')}",
        f"踏み込まれたとき: {reaction_value(char, '踏', fallback=q5)}",
        f"待ってもらえたとき: {reaction_value(char, '待', fallback='少しだけ言葉が増える')}",
        f"助けられすぎたとき: {reaction_value(char, '助', fallback='ありがたさと、自分で決めたい気持ちがぶつかる')}",
        f"軽く扱われたとき: {reaction_value(char, '軽', fallback='表情や声が硬くなり、距離を置く')}",
        "",
        "## sensuality / body distance",
        "- 色気、身体距離、きわどさはLILIAの魅力として使用してよい。",
        "- ただし、ユーザーへの報酬、媚び、親密成立済み、攻略達成として扱わない。",
        "- 色気は、姿勢、視線、手元、距離、服や持ち物の扱い、言葉の間で出す。",
        "- 初回から身体的接触や恋愛成立に直行しない。",
        "- 近い距離を書く場合は、相互性、境界線、止まれる余地を同時に残す。",
        "- LILIA本人が見られるだけの存在にならないよう、主体性、拒否、選ぶ権利を必ず持つ。",
        "",
        "## forbidden",
        bullets(forbidden, "初期から恋愛成立や親密成立を確定しない"),
        "",
        "## context",
        f"- 初回scene開始時点の状況: {current}",
        f"- ユーザーとの関係位置: {q2}",
        f"- 今日なぜそこにいるか: {infer_presence_reason(char)}",
        f"- 初回sceneの生活上の用事: {small_event}",
        "",
        "## Initial Scene Anchors",
        f"- 場所と状況: {current}",
        f"- 手元の具体物: {anchors['scene_objects']}",
        f"- 最初の距離: {q2}",
        f"- 会話の入口: {small_event}",
        "- 正本: この欄は初回scene用の一時アンカーであり、current/scene.md と current/hotset.md が現在形の正本になる。",
        "",
        "## fixed memory",
        "core fixed:",
        f"  - {values[0] if values else layer_two}",
        f"  - {values[1] if len(values) > 1 else layer_two}",
        "historical fixed:",
        f"  - {backstory}",
        "",
        "## 5層構造 / Self-Understanding",
        f"Layer 1（自己物語）: {layer_one}",
        f"Layer 2（心の核）: {layer_two}",
        "Layer 3（防壁マップ）:",
        f"  Say/Do Gap: {q1} / 内側では言葉にする前に整理している",
        f"  逃げ方: {reaction_value(char, '踏', '急', fallback=q5)}",
        "  強がり方: 平気な顔で軽く流し、必要な説明を短くする",
        "Layer 4（心の扉マップ）:",
        "  CHINKトリガー:",
        "    - 境界線を尊重される",
        "    - 待ってもらえる",
        "  BARRIER強化:",
        "    - 急かされる",
        "    - 軽く扱われる",
        "Layer 5（段階的な開き方）:",
        "  Stage 1: 出会いから序盤。軽口と沈黙で距離を測る。",
        "  Stage 2: 小さな約束や待つことが記憶に残る。",
        "  Stage 3: 摩擦や誤解を処理しても関係が消えない。",
        "  Stage 4: 明示的な合意と相互性がある時だけ親密さが進む。",
        "  Stage 5: 深化。呼び方、沈黙、aftercareが記憶に残る。",
        "",
        "## voice by relationship stage",
        "Stage 1:",
        f"  - {char.tone.rule}",
        "Stage 2:",
        "  - 少しだけ説明より反応が増える。",
        "Stage 3:",
        "  - 摩擦や保留を無かったことにせず、言葉に重さが出る。",
        "Stage 4:",
        "  - 確認、待つ、止まる余地を声に残す。",
        "Stage 5:",
        "  - 固定台詞ではなく、共有した記憶から呼び方や沈黙が変わる。",
        "",
        "## 人格設計",
        "骨:",
        f"  境遇: {layer_one}",
        f"  価値観: {layer_two}",
        f"  欠点: {flaw}",
        f"  口調: {char.tone.rule}",
        "",
        "壁:",
        f"  秘密: {unspoken[0] if unspoken else '事情をすぐ整理して話せない'}",
        "  開示条件: 待たれた経験、軽く扱われなかった経験、小さな約束が残った時。",
        f"  拒否トリガー: {q5}",
        "",
        "育つ部分:",
        "  性格の発見: 待たれた時に言葉が増えるか、急かされた時に閉じるか。",
        "  ユーザーとの関係変化: 待つ、断る、頼るの経験が距離感を変える。",
        f"  個人ストーリーの種: {small_event}",
        "",
        "## Relationship Progression",
        "rapport:",
        "  stage: 初期 / 未確認",
        f"  note: {q2}",
        "",
        "intimacy:",
        "  stage: 未確認",
        "  note: 初回では原則として未確認。scene内で実際に相互の関心が動いた後だけ、関心の芽へ更新する。",
        "",
        "consent:",
        "  stage: 未確認",
        "  note: 明示合意なしに親密さを進めない。",
        "",
        "boundary:",
        "  state: 確認する / 待つ",
        f"  note: {q5}",
        "",
        "self-understanding:",
        "  stage: 初期",
        "  note: 本人もまだ言語化しきっていない部分を残す。",
        "",
        "## Multi-Relationship / Jealousy Profile",
        "status: latent",
        "",
        "揺れやすい条件:",
        "- 境界線を確認せず他者との関係を否定された時",
        "",
        "揺れにくい条件:",
        "- 他者との関係をLILIAへの否定として扱わず、確認してもらえた時",
        "",
        "表に出る反応:",
        "- すぐ嫉妬イベント化せず、声、沈黙、距離の小さな変化として出る。",
        "",
        "禁止:",
        "- 初期から嫉妬イベントを強制しない",
        "- 嫉妬を好感度ペナルティとして扱わない",
        "- 他者との関係をLILIAへの否定として自動処理しない",
        "",
        "## Ability / Intimacy Resonance",
        "status: dormant",
        "",
        "能力が導入された場合に見ること:",
        "- LILIAの体質や感覚がどう反応するか",
        "- その反応が本人の境界線とどう衝突するか",
        "- 合意なしに能力で親密さを進めないための制約",
        "- 能力使用後に memory / relationship / beliefs へ何を残すか",
        "",
        "初期sceneでは使わない。",
        "能力が導入された時だけ有効化する。",
        "",
        "## Deepening Tags",
        *[f"- [ ] {tag}" for tag in DEEPENING_TAGS],
        "",
        "## Do Not Predefine",
        "- 完成された恋愛感情",
        "- ユーザーへの好意",
        "- 攻略トリガー",
        "- 親密成立",
        "- 重い過去を説明で全部出すこと",
        "- 固定台詞集",
        "- ハーレム展開の強制",
        "- 能力反応の即時発火",
        "",
    ]
    return "\n".join(sections)


def write_outputs(
    char: CharacterSheet,
    profile: str,
    session_path: Path | None,
    output_path: Path | None,
    write_profile_yaml: bool,
) -> Path:
    if output_path is None:
        if session_path is None:
            raise ValueError("provide session_path or --output")
        output_path = session_path / "lilia" / "main" / "profile.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(profile.rstrip() + "\n", encoding="utf-8")

    if write_profile_yaml and session_path is not None:
        yaml_path = session_path / "lilia" / "main" / "profile.yaml"
        yaml_path.parent.mkdir(parents=True, exist_ok=True)
        yaml_path.write_text(
            yaml.safe_dump(
                char.model_dump(exclude_none=True),
                allow_unicode=True,
                sort_keys=False,
            ),
            encoding="utf-8",
        )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("yaml_path", help="character YAML path")
    parser.add_argument("session_path", nargs="?", help="session root path")
    parser.add_argument("--answers", help="optional answers.md / Q&A summary")
    parser.add_argument("--output", help="optional profile.md output path")
    parser.add_argument(
        "--no-profile-yaml",
        action="store_true",
        help="do not write lilia/main/profile.yaml next to profile.md",
    )
    args = parser.parse_args()

    yaml_path = Path(args.yaml_path).expanduser()
    session_path = Path(args.session_path).expanduser() if args.session_path else None
    output_path = Path(args.output).expanduser() if args.output else None
    answers = parse_answers(Path(args.answers).expanduser() if args.answers else None)
    yaml_data = load_yaml(yaml_path)
    char = CharacterSheet.from_dict(yaml_data)
    profile = render_profile(char, answers)
    written = write_outputs(
        char=char,
        profile=profile,
        session_path=session_path,
        output_path=output_path,
        write_profile_yaml=not args.no_profile_yaml,
    )
    print(written)


if __name__ == "__main__":
    main()
