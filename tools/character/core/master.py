"""
LLM CLI bridge for minimal character YAML generation.

This intentionally ports only the small external YAML-material flow from the
old character system. LILIA does not revive cast/heroine files or affinity
routes; generated YAML must be converted to lilia/main/profile.md before use.
"""

from __future__ import annotations

from pathlib import Path
import re
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
    from tools.character.core.simple_schema import CharacterSheet, load_simple_character_yaml

    SIMPLE_YAML_LOADER = load_simple_character_yaml

from tools.common.engine_runner import (
    EngineRunnerError,
    EngineTimeoutError,
    engine_candidates,
    engine_timeout_seconds,
    run_engine,
)


ROOT = Path(__file__).resolve().parents[3]
MAX_ATTEMPTS = 3


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


class CharacterGenerationError(RuntimeError):
    """Raised when character YAML generation fails."""


def generate_characters(instruction: str, engine: str = "claude") -> list[CharacterSheet]:
    candidates = engine_candidates(engine)
    if not candidates:
        raise CharacterGenerationError(
            "no available LLM CLI was found. Install/login to claude or codex, "
            "or use the fallback instruction in prompt/newgame.md to generate the same schema manually."
        )

    previous_error = ""
    failures: list[str] = []
    for attempt_index in range(MAX_ATTEMPTS):
        full_prompt = f"{MASTER_SYSTEM_PROMPT}\n\n---\n\n{instruction.strip()}"
        if previous_error:
            full_prompt += f"""

## 前回の失敗

以下を直して、必ず1つだけ yaml ブロックを再出力してください。

{previous_error}
"""

        for candidate in _attempt_engine_order(candidates, attempt_index):
            try:
                raw_output = run_engine(
                    candidate,
                    full_prompt,
                    timeout=engine_timeout_seconds(),
                    root=ROOT,
                )
                return _parse_characters(raw_output, candidate)
            except EngineRunnerError as exc:
                previous_error = str(exc)
                failures.append(f"{candidate}: {exc}")
                if engine != "auto":
                    raise CharacterGenerationError(str(exc)) from exc
            except (ValueError, ValidationError) as exc:
                previous_error = str(exc)
                failures.append(f"{candidate}: {exc}")

    detail = "; ".join(failures[-4:]) or previous_error or "unknown generation error"
    raise CharacterGenerationError("character YAML generation failed after 3 attempts: " + detail)


def _attempt_engine_order(candidates: list[str], attempt_index: int) -> list[str]:
    if attempt_index < 2 or len(candidates) == 1:
        return candidates[:1]
    return candidates[1:]


def _parse_characters(raw_output: str, engine: str) -> list[CharacterSheet]:
    raw_dicts = parse_yaml_blocks(raw_output)
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
