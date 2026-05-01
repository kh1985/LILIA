#!/usr/bin/env python3
"""Generate minimal character YAML material for a LILIA session.

This standalone wrapper invokes Claude CLI through tools.character.core.master.
The ./lilia launcher does not call it automatically.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.character.core.master import generate_character  # noqa: E402


def parse_answers(path: Path) -> dict[int, str]:
    content = path.read_text(encoding="utf-8")
    answers: dict[int, list[str]] = {}
    current: int | None = None
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("## Q") and len(stripped) >= 5 and stripped[4].isdigit():
            current = int(stripped[4])
            answers.setdefault(current, [])
            continue
        if current is not None:
            answers[current].append(line)
    return {key: "\n".join(lines).strip() for key, lines in answers.items()}


def instruction_from_answers(path: Path) -> str:
    answers = parse_answers(path)
    if not answers:
        return path.read_text(encoding="utf-8").strip()

    def answer(number: int) -> str:
        return answers.get(number, "未回答").strip() or "未回答"

    return f"""LILIA用の初回人格profile素材として、現代日常に接地した女性1人を生成する。
完成済み攻略キャラではなく、初回sceneで演じられる人物にする。

Q&A:
- 最初に見える側面: {answer(1)}
- 現在の関係位置: {answer(2)}
- 生活の足場: {answer(3)}
- 今日の小さな保留: {answer(4)}
- 許されている距離: {answer(5)}
- 関係が動く小さな出来事: {answer(6)}
- 避けたいこと: {answer(7)}

条件:
- 名前を生成する
- 年齢は成人
- 生活上の役割や用事を持つ
- tone examplesを3つ出す
- personalityは行動で書く
- reactionsとforbiddenを出す
- 重い過去や恋愛成立は確定しない
- 現代の日常の具体物を入れる
"""


def build_instruction(args: argparse.Namespace) -> str:
    pieces: list[str] = []
    if args.answers:
        pieces.append(instruction_from_answers(Path(args.answers).expanduser()))
    if args.prompt_file:
        pieces.append(Path(args.prompt_file).expanduser().read_text(encoding="utf-8").strip())
    if args.instruction:
        pieces.append(args.instruction.strip())
    instruction = "\n\n".join(piece for piece in pieces if piece)
    if not instruction:
        raise SystemExit("error: provide an instruction, --answers, or --prompt-file")
    return instruction


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instruction", nargs="?", help="natural language character instruction")
    parser.add_argument("--answers", help="answers.md with ## Q1 ... ## Q7 sections")
    parser.add_argument("--prompt-file", help="extra prompt text file")
    parser.add_argument("-o", "--output", required=True, help="output YAML path")
    parser.add_argument(
        "--print-instruction",
        action="store_true",
        help="print the final instruction before calling Claude CLI",
    )
    args = parser.parse_args()

    instruction = build_instruction(args)
    if args.print_instruction:
        print(instruction)

    character = generate_character(instruction)
    output = Path(args.output).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        yaml.safe_dump(
            character.model_dump(exclude_none=True),
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
