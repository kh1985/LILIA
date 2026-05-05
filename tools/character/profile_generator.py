"""AI bridge for generating validated LILIA Persona Profile markdown."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MAX_ATTEMPTS = 3
ENGINE_TIMEOUT_SECONDS = 300


class ProfileGenerationError(RuntimeError):
    """Raised when the AI profile generator cannot produce valid markdown."""


def generate_profile_document(answers: dict, character_yaml: dict, engine: str) -> dict:
    """Generate validated Wave 12.1 ``profile.md`` content.

    Returns a dict with ``profile_md``, ``engine_used``, and
    ``validation_retry_count``. ``engine`` must be ``codex``, ``claude``, or
    ``auto``.
    """

    if not isinstance(answers, dict):
        raise ProfileGenerationError("answers must be a dict")
    if not isinstance(character_yaml, dict):
        raise ProfileGenerationError("character_yaml must be a dict")

    candidates = _engine_candidates(engine)
    previous_error = ""
    cli_failures: list[str] = []

    for attempt_index in range(MAX_ATTEMPTS):
        prompt = _build_generation_prompt(
            answers=answers,
            character_yaml=character_yaml,
            attempt_index=attempt_index,
            previous_error=previous_error,
        )

        raw_output = ""
        engine_used = ""
        for candidate_engine in candidates:
            try:
                raw_output = _run_engine(candidate_engine, prompt)
                engine_used = candidate_engine
                break
            except ProfileGenerationError as exc:
                cli_failures.append(f"{candidate_engine}: {exc}")
                if engine != "auto":
                    raise
        if not raw_output or not engine_used:
            detail = "; ".join(cli_failures[-4:]) or "no engine produced output"
            raise ProfileGenerationError(f"profile generation could not start: {detail}")

        try:
            profile_md = _parse_generation_output(raw_output)
            _validate_profile_output(profile_md, answers=answers, character_yaml=character_yaml)
            return {
                "profile_md": profile_md,
                "engine_used": engine_used,
                "validation_retry_count": attempt_index,
            }
        except ProfileGenerationError as exc:
            previous_error = str(exc)

    raise ProfileGenerationError(
        "profile generation failed after 3 attempts: "
        + (previous_error or "unknown validation error")
    )


def _engine_candidates(engine: str) -> list[str]:
    if engine not in {"codex", "claude", "auto"}:
        raise ProfileGenerationError("engine must be one of: codex, claude, auto")
    if engine == "auto":
        return ["codex", "claude"]
    return [engine]


def _build_engine_command(engine: str, prompt: str) -> tuple[list[str], str | None]:
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
    raise ProfileGenerationError(f"unsupported engine: {engine}")


def _run_engine(engine: str, prompt: str) -> str:
    command, stdin_text = _build_engine_command(engine, prompt)
    env = os.environ.copy()

    try:
        result = subprocess.run(
            command,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=ENGINE_TIMEOUT_SECONDS,
            env=env,
        )
    except FileNotFoundError as exc:
        raise ProfileGenerationError(f"{engine} command was not found") from exc
    except subprocess.TimeoutExpired as exc:
        raise ProfileGenerationError(
            f"{engine} generation timed out after {ENGINE_TIMEOUT_SECONDS} seconds"
        ) from exc

    if result.returncode != 0:
        stderr = result.stderr.strip() or "(no stderr)"
        raise ProfileGenerationError(f"{engine} CLI failed: {stderr}")
    if not result.stdout.strip():
        raise ProfileGenerationError(f"{engine} CLI returned empty output")
    return result.stdout


def _build_generation_prompt(
    *,
    answers: dict,
    character_yaml: dict,
    attempt_index: int,
    previous_error: str,
) -> str:
    answers_json = json.dumps(answers, ensure_ascii=False, indent=2, default=str)
    character_json = json.dumps(character_yaml, ensure_ascii=False, indent=2, sort_keys=True, default=str)
    retry_block = ""
    if previous_error:
        retry_block = f"""
## 前回の失敗

以下の理由で検証に失敗しました。今回の出力では必ず直してください。

{previous_error}
"""

    return f"""あなたはLILIA用のPersona Profile生成補助です。
Q&A回答と生成済みcharacter YAMLから、first scene前に読む `lilia/main/profile.md` を1つ生成してください。

LILIAは、ユーザーとの会話・選択・物語を記憶し、関係性と人格の出方が少しずつ変化していくAI恋愛シミュレーションです。
`profile.md` は完成済み攻略キャラカードではありません。初回から生活、行動、矛盾、反応、禁忌を持たせるための人格正本です。
関係で育った内容は後で core / voice / relationship / memory / beliefs へ分解されます。

## Example Anchoring Control

- prompt内の例文、見出し、候補語を人格や設定へ固定しない。
- ユーザー回答とcharacter YAMLを最優先する。
- 曖昧な要素は例で補完せず、初回sceneで育つ余白として具体的な保留にする。
- Q1本文を30文字以上そのままコピーしない。要約・分解・変換する。
- AFFINITY、bond、好感度、ルートという語彙を出さない。`攻略トリガー` と `ハーレム展開の強制` は固定リスト内だけで使う。
- 初回から恋愛成立、親密成立、好意確定、能力反応の即時発火を確定しない。

## 感情設計の原則

profile の contradictions, unspoken, Layer 構造, relationship progression は、
`docs/EMOTIONAL_DESIGN_PRINCIPLES.md` の以下の原則に従う:

- 原則6: LILIA の核（Layer の深層）は、平時には半分しか見えない設計にする。
- 原則7: Q1-Q9 でプレイヤーが指定した要素を、profile に統合する。
- 原則8: relationship progression に「成功にもコストがある」余白を残す。

## 入力: Q&A answers

```json
{answers_json}
```

## 入力: character YAML material

```json
{character_json}
```

## 生成ルール

1. 出力は `# LILIA Persona Profile` から始める。
2. 出力全体をコードフェンスで囲まない。
3. `##` セクションは、下のWave 12.1 skeletonだけを、この順番で出す。
4. すべての必須subfieldを埋める。`未設定`、`未確定`、`TODO`、`placeholder`、`[ヒロイン名]` などの残骸を出さない。
5. field行を `...` や `…` で終えない。
6. Deepening Tagsは13個すべて `- [ ]` の未チェックで、順番も文言も完全一致にする。
7. Do Not Predefineは8個だけ、順番も文言も完全一致にする。
8. 具体化は生活、行動、反応、境界線、手元の物、初回scene入口に寄せる。固定台詞集にはしない。

## Wave 12.1 strict skeleton

# LILIA Persona Profile

このファイルは、初回からLILIAを安定して演じるための人格正本である。
ただし、完成済み攻略キャラカードではない。
関係で育った内容は core / voice / relationship / memory / beliefs へ分解して保存する。

## 基礎情報
name: ...
age: ...
occupation: ...
role: ...
appearance: ...
body: ...
outfit: ...

## appearance
hair_style: ...
hair_color: ...
eye_color: ...
body: ...
outfit: ...
notes: ...

## tone
rule: ...
examples:
  - ...
  - ...

## personality
- 行動で見える性格: ...
- 困った時の出方: ...
- 褒められた時の反応: ...
- 怒った時の反応: ...
- 頼る / 断る / 待つ の傾向: ...

## values
- 何を大事にしているか: ...
- 何は雑に扱わないか: ...

## everyday anchors
- 生活の場所: ...
- 仕事 / 用事 / 習慣: ...
- よく触る物: ...
- 初回sceneで使える具体物: ...

## memories
- 初期時点で既にある生活上の記憶: ...
- 実際に過去として固定してよいものだけ: ...

## contradictions
- 表の態度: ...
- 内側の反応: ...
- 表の態度と内側の矛盾: ...
- 頼りたい / 頼れない: ...
- 近づきたい / 距離を守りたい: ...

## unspoken
- まだ言わないこと: ...
- すぐには開示しない理由: ...

## reactions
能力や異常性に触れた相手には: ...
弱っている相手には: ...
急かされたとき: ...
感謝されたとき: ...
踏み込まれたとき: ...
待ってもらえたとき: ...
助けられすぎたとき: ...
軽く扱われたとき: ...

## sensuality / body distance
- 初期距離: ...
- 近づいてよい条件: ...
- 止まる合図: ...
- 触れられた時の出方: ...
- 親密さを急がないための制約: ...

## forbidden
- ...
- 初回から恋愛成立、親密成立、攻略トリガーを確定しない
- 例文由来の語彙を固定人格にしない

## context [GM-internal pre-play assumption]
- 初回scene開始時点の状況: ...
- ユーザーとの関係位置: ...
- 表と内の差: ...
- 内面に持っているもの: ...
- 今日なぜそこにいるか: ...
- 初回sceneの生活上の用事: ...

## 描写の縛り
- 必ず入れる質感1: ...
- 必ず入れる質感2: ...

## Initial Scene Anchors
- 場所と状況: ...
- 手元の具体物: ...
- 最初の距離: ...
- 会話の入口: ...

## fixed memory
core fixed:
  - ...
historical fixed:
  - ...

## 5層構造 / Self-Understanding
Layer 1（自己物語）: ...
Layer 2（心の核）: ...
Layer 3（防壁マップ）:
  Say/Do Gap: ...
  逃げ方: ...
  強がり方: ...
Layer 4（心の扉マップ）:
  CHINKトリガー:
    - ...
  BARRIER強化:
    - ...
Layer 5（段階的な開き方）:
  Stage 1: ...
  Stage 2: ...
  Stage 3: ...
  Stage 4: ...
  Stage 5: ...

## voice by relationship stage
Stage 1: ...
Stage 2: ...
Stage 3: ...
Stage 4: ...
Stage 5: ...

## 人格設計
骨:
  境遇: ...
  価値観: ...
  欠点: ...
  口調: ...

壁:
  秘密: ...
  開示条件: ...
  拒否トリガー: ...

育つ部分:
  性格の発見: ...
  ユーザーとの関係変化: ...
  個人ストーリーの種: ...

## Relationship Progression
rapport:
  stage: 初期 / 未確認
  note: ...
intimacy:
  stage: 未確認
  note: ...
consent:
  stage: 未確認
  note: ...
boundary:
  state: 確認する / 待つ
  note: ...
self-understanding:
  stage: 初期
  note: ...

## Multi-Relationship / Jealousy Profile
status: latent
揺れやすい条件:
- ...
揺れにくい条件:
- ...
表に出る反応:
- ...
禁止:
- 初期から嫉妬イベントを強制しない
- 嫉妬を好感度ペナルティとして扱わない
- 他者との関係をLILIAへの否定として自動処理しない

## Ability / Intimacy Resonance
status: dormant
能力が導入された場合に見ること:
- LILIAの体質や感覚がどう反応するか
- その反応が本人の境界線とどう衝突するか
- 合意なしに能力で親密さを進めないための制約
- 能力使用後に memory / relationship / beliefs へ何を残すか
初期sceneでは使わない。
能力が導入された時だけ有効化する。

## Deepening Tags
- [ ] 境界線を尊重された
- [ ] 自分から頼った
- [ ] 自分から断った
- [ ] 呼び方が変わった
- [ ] 沈黙を共有した
- [ ] 小さな約束が残った
- [ ] 誤解を修正した
- [ ] 摩擦を処理した
- [ ] 秘密の一部を共有した
- [ ] 親密後のaftercareが残った
- [ ] 他者との関係について確認した
- [ ] 離れる自由を確認した
- [ ] 能力との相互作用を確認した

## Do Not Predefine
- 完成された恋愛感情
- ユーザーへの好意
- 攻略トリガー
- 親密成立
- 重い過去を説明で全部出すこと
- 固定台詞集
- ハーレム展開の強制
- 能力反応の即時発火

{retry_block}
attempt: {attempt_index + 1}/{MAX_ATTEMPTS}
"""


def _parse_generation_output(text: str) -> str:
    stripped = _strip_outer_fence(text).strip()
    marker = re.search(r"^#\s+LILIA Persona Profile\s*$", stripped, flags=re.MULTILINE)
    if marker:
        stripped = stripped[marker.start() :].strip()
    if not stripped.startswith("# LILIA Persona Profile"):
        raise ProfileGenerationError("output must start with `# LILIA Persona Profile`")
    return stripped


def _strip_outer_fence(text: str) -> str:
    stripped = text.strip()
    match = re.match(r"^```(?:markdown|md)?\s*(.*?)\s*```$", stripped, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    return text


def _validate_profile_output(profile_md: str, *, answers: dict, character_yaml: dict) -> None:
    try:
        from tools.character.profile_validator import validate_profile_output
    except ModuleNotFoundError as exc:
        if exc.name == "tools.character.profile_validator":
            raise ProfileGenerationError(
                "tools.character.profile_validator.validate_profile_output is unavailable"
            ) from exc
        raise

    valid, errors = validate_profile_output(profile_md, answers=answers, character_yaml=character_yaml)
    if not valid:
        raise ProfileGenerationError("validator issues: " + _stringify_issues(errors))


def _stringify_issues(issues: Any) -> str:
    if issues is None:
        return ""
    if isinstance(issues, str):
        return issues
    if isinstance(issues, dict):
        return json.dumps(issues, ensure_ascii=False, sort_keys=True, default=str)
    if isinstance(issues, (list, tuple, set)):
        return "; ".join(_stringify_issues(issue) for issue in issues if issue)
    return str(issues)
