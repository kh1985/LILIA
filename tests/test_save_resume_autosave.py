from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_save_resume_requires_scene_tick_and_apply_turn_chain() -> None:
    content = (ROOT / "prompt" / "save_resume.md").read_text(encoding="utf-8")

    assert "通常プレイ1ターンが終わった後、**必ず** `./lilia scene-tick <session>` を実行する" in content
    assert "`autosave_required: true` が表示された場合、GM は **次のプレイ応答を返す前に**" in content
    assert "`autosave_required: true` を見て **保存しないまま次のプレイを返してはいけない**" in content

    assert "通常プレイ1ターンが終わった後、必要に応じて" not in content
    assert "勝手に `apply-turn` は実行しない" not in content

    for step in range(1, 8):
        assert f"{step}." in content
    assert "`./lilia apply-turn <session> <turn_update.md>` を実行する" in content
    assert "session.json の `turns_since_save` は 0 にリセットされる" in content


def test_save_resume_autosave_save_mode_updates_only_changed_sections() -> None:
    content = (ROOT / "prompt" / "save_resume.md").read_text(encoding="utf-8")

    assert "autosave 由来の Save Mode でも、以下のリストを機械的に全部更新しない" in content
    assert "`## 4. First Question` に従い" in content
    assert "実際に変わったセクションだけを turn_update.md に含める" in content
