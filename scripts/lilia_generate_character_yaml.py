#!/usr/bin/env python3
"""Generate minimal character YAML material for a LILIA session.

This standalone wrapper invokes an LLM CLI (codex / claude) through tools.character.core.master.
The ./lilia apply-newgame command uses the same LLM CLI route by default.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.character.core.master import generate_character  # noqa: E402


def load_launcher():
    loader = SourceFileLoader("lilia_launcher", str(ROOT / "lilia"))
    spec = spec_from_loader(loader.name, loader)
    if spec is None:
        raise RuntimeError("failed to load ./lilia launcher")
    module = module_from_spec(spec)
    loader.exec_module(module)
    return module


def choose_engine(requested: str) -> str | None:
    if requested == "auto":
        if shutil.which("codex"):
            return "codex"
        if shutil.which("claude"):
            return "claude"
        return None
    return requested if shutil.which(requested) else None


def instruction_from_answers(path: Path) -> str:
    launcher = load_launcher()
    try:
        answers = launcher.parse_newgame_answers(path)
    except SystemExit:
        return path.read_text(encoding="utf-8").strip()
    return launcher.build_character_instruction_from_answers(answers)


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
    parser.add_argument("--answers", help="answers.md with ## Q1 ... ## Q5 sections")
    parser.add_argument("--prompt-file", help="extra prompt text file")
    parser.add_argument("--engine", choices=["codex", "claude", "auto"], default="auto", help="LLM CLI engine")
    parser.add_argument("-o", "--output", required=True, help="output YAML path")
    parser.add_argument(
        "--print-instruction",
        action="store_true",
        help="print the final instruction before calling the LLM CLI",
    )
    args = parser.parse_args()

    instruction = build_instruction(args)
    if args.print_instruction:
        print(instruction)

    engine = choose_engine(args.engine)
    if engine is None:
        raise SystemExit(f"error: no LLM CLI found for --engine {args.engine}")
    character = generate_character(instruction, engine=engine)
    output = Path(args.output).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    character_data = character.model_dump(exclude_none=True)
    if yaml is not None:
        text = yaml.safe_dump(character_data, allow_unicode=True, sort_keys=False)
    else:
        text = load_launcher().dump_character_yaml(character_data)
    output.write_text(text, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
