"""
LLM CLI bridge for minimal character YAML generation.

This intentionally ports only the small external YAML-material flow from the
old character system. LILIA does not revive cast/heroine files or affinity
routes; generated YAML must be converted to lilia/main/profile.md before use.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    yaml = None

try:
    from pydantic import ValidationError
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    class ValidationError(ValueError):
        pass

try:
    from tools.character.core.schema import CharacterSheet
    SIMPLE_YAML_LOADER = None
except ModuleNotFoundError as exc:  # pragma: no cover - depends on local environment
    if exc.name != "pydantic":
        raise
    from scripts.lilia_character_to_profile import CharacterSheet, load_simple_character_yaml

    SIMPLE_YAML_LOADER = load_simple_character_yaml


ROOT = Path(__file__).resolve().parents[3]


MASTER_SYSTEM_PROMPT = """あなたはLILIA用のPersona Profile素材を作るキャラクター設計補助です。
ユーザーの指示を受け取り、現代日常に接地した成人女性1人のcharacter YAMLを生成してください。

このYAMLは完成済み攻略キャラカードではありません。
LILIAのfirst scene前に lilia/main/profile.md へ変換する素材です。

## 出力フォーマット

必ず1つだけ ```yaml ブロックで出力してください。

```yaml
name: "名前"
age: 24
occupation: "職業・生活上の役割"
appearance:
  hair_style: "髪型"
  hair_color: "髪色"
  notes: "現代日常に接地した外見の補足"
tone:
  rule: "語尾・距離感・沈黙のルールを1文で"
  examples:
    - user: "最近どう？"
      char: "その人らしい短い返答"
    - user: "ありがとう"
      char: "その人らしい短い返答"
    - user: "それ、本当？"
      char: "その人らしい短い返答"
personality:
  - "形容詞ではなく行動で見える性格を書く"
  - "困った時、頼る/断る/待つの傾向を書く"
  - "褒められた時や踏み込まれた時の出方を書く"
reactions:
  褒められたとき: "反応"
  怒ったとき: "反応"
  急かされたとき: "反応"
  踏み込まれたとき: "反応"
forbidden:
  - "初期段階で絶対にしないこと"
  - "その場では言わないこと"
context:
  backstory: "固定してよい生活上の背景を2文以内で。重い過去を全部説明しない"
  current_situation: "first scene開始時点の生活上の用事や状況"
```

## 条件

- 名前を生成する。
- 年齢は成人にする。
- 生活上の役割や用事を持たせる。
- 現代日常の具体物を入れる。
- personalityは形容詞ではなく行動で書く。
- reactionsとforbiddenを出す。
- tone examplesを3つ出す。
- 重い過去、恋愛成立、好意、親密成立を確定しない。
- AFFINITY、bond、好感度、攻略、ハーレム、ルートという語彙を出さない。
- 能力や異常性がある場合も、初期sceneで即発火させない。
"""


def build_engine_command(engine: str, prompt: str) -> tuple[list[str], str | None]:
    if engine == "claude":
        return ["claude", "-p", prompt], None
    if engine == "codex":
        return [
            "codex",
            "exec",
            "--cd",
            str(ROOT),
            "--sandbox",
            "read-only",
            "--color",
            "never",
            "-",
        ], prompt
    raise ValueError(f"unsupported engine: {engine}")


def generate_characters(instruction: str, engine: str = "claude") -> list[CharacterSheet]:
    full_prompt = f"{MASTER_SYSTEM_PROMPT}\n\n---\n\n{instruction.strip()}"
    env = {key: value for key, value in os.environ.items() if key != "CLAUDECODE"}
    command, stdin_text = build_engine_command(engine, full_prompt)

    try:
        result = subprocess.run(
            command,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"{engine} command was not found. Install/login to the requested LLM CLI, "
            "or use the fallback instruction in prompt/newgame.md to generate the same schema manually."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("character YAML generation timed out after 120 seconds") from exc

    if result.returncode != 0:
        raise RuntimeError(f"{engine} CLI failed:\n{result.stderr.strip()}")

    raw_dicts = parse_yaml_blocks(result.stdout)
    if not raw_dicts:
        raise ValueError(f"no YAML block with a character name was found in {engine} output")

    characters: list[CharacterSheet] = []
    errors: list[str] = []
    for index, raw in enumerate(raw_dicts, 1):
        try:
            characters.append(CharacterSheet.from_dict(raw))
        except (ValidationError, ValueError) as exc:
            name = raw.get("name", f"#{index}") if isinstance(raw, dict) else f"#{index}"
            if hasattr(exc, "errors"):
                errors.append(f"{name}: {exc.errors()[0]['msg']}")
            else:
                errors.append(f"{name}: {exc}")

    if not characters:
        raise ValueError("no valid character YAML was generated: " + "; ".join(errors))
    return characters


def generate_character(instruction: str, engine: str = "claude") -> CharacterSheet:
    return generate_characters(instruction, engine=engine)[0]


def parse_yaml_blocks(text: str) -> list[dict[str, Any]]:
    blocks = re.findall(r"```yaml\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if not blocks:
        blocks = [segment.strip() for segment in text.split("---") if segment.strip()]

    results: list[dict[str, Any]] = []
    for block in blocks:
        if yaml is None:
            if SIMPLE_YAML_LOADER is None:
                continue
            temp_path: Path | None = None
            try:
                with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".yaml", delete=False) as temp_file:
                    temp_file.write(block)
                    temp_path = Path(temp_file.name)
                parsed = SIMPLE_YAML_LOADER(temp_path)
            except Exception:
                continue
            finally:
                if temp_path and temp_path.exists():
                    temp_path.unlink()
        else:
            try:
                parsed = yaml.safe_load(block)
            except yaml.YAMLError:
                continue
        if isinstance(parsed, list):
            results.extend(item for item in parsed if isinstance(item, dict) and "name" in item)
        elif isinstance(parsed, dict) and "characters" in parsed and isinstance(parsed["characters"], list):
            results.extend(
                item for item in parsed["characters"] if isinstance(item, dict) and "name" in item
            )
        elif isinstance(parsed, dict) and "name" in parsed:
            results.append(parsed)
    return results
