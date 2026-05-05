from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.session.voice_continuity_validator import validate_voice_continuity


REQUIRED_CONTENT = {
    "lilia/main/core.md": "# Core\n\n## Core Fixed\n\n- 自分の境界線を短期都合で消さない。\n",
    "lilia/main/voice.md": "# Voice\n\n## 呼び方\n\n- 主人公を「かねこさん」と呼ぶ。\n",
    "lilia/main/relationship.md": "# Relationship\n\n## 親密さ\n\n- 関心段階。明示的親密なし。\n",
    "lilia/main/memory.md": "# Memory\n\n## historical_fixed\n\n- 約束 / 拒否 / 保留: なし。\n",
    "lilia/main/beliefs.md": "# Beliefs\n\n## ユーザーについての仮説\n\n- まだ判断前。\n",
    "lilia/main/state.md": "# State\n\n## 第一反応\n\n- 短く確認する。\n",
    "current/hotset.md": "# Hotset\n\n## 呼び方 / 距離のアンカー\n\n- かねこさん。まだ距離を急がない。\n",
    "current/scene.md": "# Scene\n\n## 現在地\n\n- カフェ。\n",
    "current/event_card.md": "# Event Card\n\n## Visible Problem\n\n- 忘れ物を返す。\n",
}


def _write_session(root: Path, overrides: dict[str, str] | None = None) -> None:
    contents = dict(REQUIRED_CONTENT)
    contents.update(overrides or {})
    for rel_path, content in contents.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def test_validator_reports_missing_required_file(tmp_path: Path) -> None:
    _write_session(
        tmp_path,
        {
            "lilia/main/voice.md": "",
        },
    )
    (tmp_path / "lilia/main/voice.md").unlink()

    errors = validate_voice_continuity(tmp_path)

    assert "voice_continuity: missing required file: lilia/main/voice.md" in errors


def test_validator_reports_empty_voice_md(tmp_path: Path) -> None:
    _write_session(tmp_path, {"lilia/main/voice.md": ""})

    errors = validate_voice_continuity(tmp_path)

    assert "voice_continuity: core / voice が空である (core fixed の正本が無い)" in errors


def test_validator_pass_for_minimal_valid_session(tmp_path: Path) -> None:
    _write_session(tmp_path)

    errors = validate_voice_continuity(tmp_path)

    assert errors == []
