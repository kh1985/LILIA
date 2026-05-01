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
            return value
    return fallback


def all_reactions(char: CharacterSheet) -> str:
    if not char.reactions:
        return "- 未設定"
    return "\n".join(f"- {key}: {value}" for key, value in char.reactions.items())


def render_profile(char: CharacterSheet, answers: dict[int | str, str]) -> str:
    q1 = answer(answers, 1, "初回sceneで観察する")
    q2 = answer(answers, 2, "初回scene前。関係位置は未確定")
    q3 = answer(answers, 3, char.context.current_situation or "初回sceneで具体化する")
    q4 = answer(answers, 4, "まだ言わないことは初回sceneで小さく観察する")
    q5 = answer(answers, 5, "踏み込みすぎず、境界線を確認する")
    q6 = answer(answers, 6, char.context.current_situation or "小さな生活上の出来事から始める")
    q7 = answer(answers, 7, "恋愛成立や重い事件を急がない")

    age = f"{char.age}" if char.age is not None else "未設定"
    role = char.occupation or "未設定"
    backstory = char.context.backstory or "未設定。深い過去は初回sceneで説明しきらない。"
    current = char.context.current_situation or q3
    first_personality = char.personality[0] if char.personality else "初回sceneで観察する"
    second_personality = char.personality[1] if len(char.personality) > 1 else first_personality

    sections = [
        "# LILIA Persona Profile",
        "",
        "このファイルは、初回からLILIAを安定して演じるための人格正本である。",
        "ただし、完成済み攻略キャラカードではない。",
        "関係で育った内容は core / voice / relationship / memory / beliefs へ分解して保存する。",
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
        f"- 困った時の出方: {reaction_value(char, '困', fallback=q4)}",
        f"- 褒められた時の反応: {reaction_value(char, '褒', fallback='少し受け取り、すぐには距離を詰めない')}",
        f"- 怒った時の反応: {reaction_value(char, '怒', fallback='声を荒げるより、言葉数や距離に出る')}",
        f"- 頼る / 断る / 待つ の傾向: {q5}",
        "",
        "## values",
        f"- 何を大事にしているか: {q3 if q3 != '初回sceneで具体化する' else role}",
        f"- 何は雑に扱わないか: {q7}",
        "",
        "## everyday anchors",
        f"- 生活の場所: {q3}",
        f"- 仕事 / 用事 / 習慣: {role}",
        f"- よく触る物: {current}",
        f"- 初回sceneで使える具体物: {q6}",
        "",
        "## memories",
        "- 初期時点で既にある生活上の記憶",
        f"- {backstory}",
        "- 実際に過去として固定してよいものだけ",
        "",
        "## contradictions",
        f"- 表の態度と内側の矛盾: {q1} / {q4}",
        f"- 頼りたい / 頼れない: {q5}",
        f"- 近づきたい / 距離を守りたい: {second_personality}",
        "",
        "## unspoken",
        f"- まだ言わないこと: {q4}",
        "- すぐには開示しない理由: 初回sceneで全部説明すると、関係で育つ余白が消えるため。",
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
        "### source reactions",
        all_reactions(char),
        "",
        "## forbidden",
        bullets(char.forbidden, "初期から恋愛成立や親密成立を確定しない"),
        "",
        "## context",
        f"- 初回scene開始時点の状況: {current}",
        f"- ユーザーとの関係位置: {q2}",
        f"- 今日なぜそこにいるか: {q3}",
        f"- 初回sceneの生活上の用事: {q6}",
        "",
        "## fixed memory",
        "core fixed:",
        f"  - {char.tone.rule}",
        f"  - {first_personality}",
        "historical fixed:",
        f"  - {backstory}",
        "",
        "## 5層構造 / Self-Understanding",
        f"Layer 1（自己物語）: {backstory}",
        f"Layer 2（心の核）: {q3}",
        "Layer 3（防壁マップ）:",
        f"  Say/Do Gap: {q1} / {q4}",
        f"  逃げ方: {reaction_value(char, '踏', '急', fallback=q5)}",
        f"  強がり方: {second_personality}",
        "Layer 4（心の扉マップ）:",
        "  CHINKトリガー:",
        "    - 境界線を尊重される",
        "    - 待ってもらえる",
        "  BARRIER強化:",
        "    - 急かされる",
        "    - 軽く扱われる",
        "Layer 5（段階的な開き方）:",
        "  Stage 1: 初回scene。観察と境界線。",
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
        f"  境遇: {backstory}",
        f"  価値観: {q3}",
        f"  欠点: {q4}",
        f"  口調: {char.tone.rule}",
        "",
        "壁:",
        f"  秘密: {q4}",
        "  開示条件: 数値ではなく、会話、記憶、境界線の尊重で変化する。",
        f"  拒否トリガー: {q5}",
        "",
        "育つ部分:",
        "  性格の発見: 初回sceneでユーザーの触れ方に反応して見える。",
        "  ユーザーとの関係変化: relationship / memory / beliefsへ保存する。",
        "  個人ストーリーの種: everyday anchorsとunspokenから小さく戻す。",
        "",
        "## Relationship Progression",
        "rapport:",
        "  stage: 初期 / 未確認",
        f"  note: {q2}",
        "",
        "intimacy:",
        "  stage: 未確認",
        "  note: 初回から成立させない。",
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
