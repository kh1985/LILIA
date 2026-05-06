from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.character.core import master


VALID_CHARACTER_YAML = """```yaml
name: "澪"
age: 25
occupation: "夜間図書館の司書"
appearance:
  hair_style: "肩で切った髪"
  hair_color: "黒"
  notes: "指先に紙の跡が残る"
tone:
  rule: "短く返して、困ると本題を少し逸らす"
  examples:
    - user: "最近どう？"
      char: "変わらないよ。少しだけ忙しいけど"
    - user: "ありがとう"
      char: "いいよ、それくらい"
    - user: "それ、本当？"
      char: "疑うなら、確かめればいい"
personality:
  - "頼まれる前に棚を直すが、礼を言われると目を逸らす"
reactions:
  褒められたとき: "指先で栞を揃える"
forbidden:
  - "初対面で好意を確定しない"
context:
  backstory: "古い図書館で働いている。"
  current_situation: "閉館後の忘れ物を探している。"
```"""


def test_auto_character_priority_defaults_to_claude(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LILIA_CHARACTER_ENGINE", raising=False)
    monkeypatch.setattr(master.shutil, "which", lambda command: f"/usr/bin/{command}")

    assert master._character_engine_candidates("auto") == ["claude", "codex"]


def test_auto_character_priority_respects_codex_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LILIA_CHARACTER_ENGINE", "codex")
    monkeypatch.setattr(master.shutil, "which", lambda command: f"/usr/bin/{command}")

    assert master._character_engine_candidates("auto") == ["codex", "claude"]


def test_claude_only_auto_executes_claude(monkeypatch: pytest.MonkeyPatch) -> None:
    used: list[str] = []
    monkeypatch.delenv("LILIA_CHARACTER_ENGINE", raising=False)
    monkeypatch.setattr(
        master.shutil,
        "which",
        lambda command: f"/usr/bin/{command}" if command == "claude" else None,
    )

    def fake_run_engine(engine: str, prompt: str, *, timeout: float, root: Path) -> str:
        used.append(engine)
        return VALID_CHARACTER_YAML

    monkeypatch.setattr(master, "run_engine", fake_run_engine)
    characters = master.generate_characters("司書を作って", engine="auto")

    assert used == ["claude"]
    assert characters[0].name == "澪"


def test_codex_only_auto_executes_codex(monkeypatch: pytest.MonkeyPatch) -> None:
    used: list[str] = []
    monkeypatch.delenv("LILIA_CHARACTER_ENGINE", raising=False)
    monkeypatch.setattr(
        master.shutil,
        "which",
        lambda command: f"/usr/bin/{command}" if command == "codex" else None,
    )

    def fake_run_engine(engine: str, prompt: str, *, timeout: float, root: Path) -> str:
        used.append(engine)
        return VALID_CHARACTER_YAML

    monkeypatch.setattr(master, "run_engine", fake_run_engine)
    characters = master.generate_characters("司書を作って", engine="auto")

    assert used == ["codex"]
    assert characters[0].name == "澪"
