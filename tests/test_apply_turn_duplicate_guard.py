from __future__ import annotations

import importlib.util
import json
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.session.state_consistency import validate_state_consistency


def load_lilia_module() -> ModuleType:
    loader = SourceFileLoader("lilia_cli_apply_turn_duplicate_test", str(ROOT / "lilia"))
    spec = importlib.util.spec_from_loader("lilia_cli_apply_turn_duplicate_test", loader)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_session(root: Path, name: str) -> Path:
    session = root / "saves" / name
    session.mkdir(parents=True)
    (session / "session.json").write_text(
        json.dumps(
            {
                "session_name": name,
                "current_phase": "active",
                "autosave": {
                    "enabled": True,
                    "interval_turns": 10,
                    "turns_since_save": 4,
                    "autosave_required": True,
                },
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return session


def write_turn_update(path: Path) -> Path:
    path.write_text(
        "\n".join(
            [
                "## memory",
                "",
                "- 澪は、かねこさんが写真を急かさず待ったことを覚えた。",
                "",
                "## relationship",
                "",
                "- 信頼が一段だけ増えたが、距離はまだ店先に留まっている。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def read_session_json(session: Path) -> dict:
    return json.loads((session / "session.json").read_text(encoding="utf-8"))


def write_hook_session(root: Path, name: str) -> Path:
    session = write_session(root, name)
    (session / "story").mkdir(parents=True, exist_ok=True)
    (session / "current").mkdir(parents=True, exist_ok=True)
    (session / "story/story_deck.md").write_text(
        """# Story Deck

## Three Hook Spine

### Main Hook
- hook_id: main_initial_request
- status: active
- current_function: 起点
- current_question: 写真の扱いをどう確認するか。
- visible_handle: 宛名のない写真を店で預かる。
- pressure: 依頼主に連絡がつかない。
- exit_condition: 写真を預かるか戻すか決まる。
- next_candidate: 翌日の確認。

### Relationship Hook
- hook_id: relationship_first_trust
- status: background
- current_function: 目標
- current_question: 境界線を守った確認が信頼へ残るか。
- relationship_stake: 急かさないことが信頼に触れる。
- boundary_or_trust_issue: 勝手に開けない線引き。
- exit_condition: 境界線が確認される。
- next_candidate: 次に会った時の短い沈黙。

### Life-Exploration Hook
- hook_id: life_revisit_route
- status: background
- current_function: 始動
- current_question: 翌日にもう一度店へ寄れるか。
- available_scope: 店、帰路、翌日の再訪。
- travel_or_life_option: 帰宅、再訪、単独行動。
- heroine_attendance: 同行は自動成立しない。
- exit_condition: 再訪する理由が残る。
- next_candidate: 翌日の夕方に店へ寄る。

## Background Hooks

- hook_id: relationship_first_trust
- hook_type: relationship
- status: background
- reason_backgrounded: 初回は写真の扱いを前景化する。
- return_condition: 境界線の確認に戻る時。
- last_known_state: 勝手に開けない線引き。

## Candidate Next Hooks

- 未設定
""",
        encoding="utf-8",
    )
    (session / "current/event_card.md").write_text(
        """# Event Card

## Active Hook

- hook_id: main_initial_request
- hook_type: main
- status: active
- foreground_reason: 宛名のない写真の扱いを今触れる入口にする。

## Scene Function

- function: 起点
- current_question: 写真の扱いをどう確認するか。
- entry_state: 写真の扱いが保留になっている。
- exit_condition: 写真を預かるか戻すか決まる。
- change_delta: 境界線の確認が関係に残る。
- next_hook_candidate: 翌日の確認。

## 表の出来事

宛名のない写真の扱いが止まっている。

## Visible Problem

写真を預かるか戻すかが決まっていない。

## First Concrete Action

写真の扱いを確認する。

## Handles 2-4

- ask: 状況を確認する
- wait: 判断を待つ

## Relationship Stake

勝手に開けない境界線を守れるか。

## If Ignored

写真は店に残る。

## Next Visible Change

翌日にもう一度確認する理由が残る。
""",
        encoding="utf-8",
    )
    (session / "current/scene.md").write_text("# Scene\n\n## 今の場面\n\n写真の扱いが保留になっている。\n", encoding="utf-8")
    (session / "current/hotset.md").write_text("# Hotset\n\n写真の扱いを急かさず確認する。\n", encoding="utf-8")
    return session


def write_hook_update(path: Path, body: str) -> Path:
    path.write_text("## hook_updates\n\n" + body.strip() + "\n", encoding="utf-8")
    return path


def test_apply_turn_rejects_same_turn_update_hash_after_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_session(tmp_path, "duplicate_case")
    update_path = write_turn_update(tmp_path / "turn_update.md")

    lilia.command_apply_turn(["duplicate_case", str(update_path)])
    capsys.readouterr()

    first_data = read_session_json(session)
    expected_hash = lilia.turn_update_fingerprint(lilia.parse_turn_update(update_path))
    assert first_data["applied_turn_updates"][0]["sha256"] == expected_hash

    memory_path = session / "lilia/main/memory.md"
    assert memory_path.read_text(encoding="utf-8").count("写真を急かさず待った") == 1

    with pytest.raises(SystemExit) as exc:
        lilia.command_apply_turn(["duplicate_case", str(update_path)])

    captured = capsys.readouterr()
    assert exc.value.code == 1
    assert "turn_update already applied" in captured.err
    assert "Use --force only when intentional" in captured.err
    assert memory_path.read_text(encoding="utf-8").count("写真を急かさず待った") == 1

    second_data = read_session_json(session)
    assert len(second_data["applied_turn_updates"]) == 1
    assert second_data["autosave"]["turns_since_save"] == 0


def test_apply_turn_dry_run_warns_for_duplicate_without_reapplying(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_session(tmp_path, "dry_run_duplicate_case")
    update_path = write_turn_update(tmp_path / "turn_update.md")

    lilia.command_apply_turn(["dry_run_duplicate_case", str(update_path)])
    capsys.readouterr()

    lilia.command_apply_turn(["--dry-run", "dry_run_duplicate_case", str(update_path)])
    captured = capsys.readouterr()

    assert "warning: turn_update already applied" in captured.err
    assert "dry-run: applied" in captured.out
    memory = (session / "lilia/main/memory.md").read_text(encoding="utf-8")
    assert memory.count("写真を急かさず待った") == 1
    assert len(read_session_json(session)["applied_turn_updates"]) == 1


def test_apply_turn_dry_run_then_actual_apply_succeeds(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_session(tmp_path, "dry_run_first_case")
    update_path = write_turn_update(tmp_path / "turn_update.md")

    lilia.command_apply_turn(["--dry-run", "dry_run_first_case", str(update_path)])
    capsys.readouterr()
    assert "applied_turn_updates" not in read_session_json(session)

    lilia.command_apply_turn(["dry_run_first_case", str(update_path)])
    capsys.readouterr()

    data = read_session_json(session)
    assert len(data["applied_turn_updates"]) == 1
    memory = (session / "lilia/main/memory.md").read_text(encoding="utf-8")
    assert memory.count("写真を急かさず待った") == 1


def test_apply_turn_force_allows_intentional_reapply(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_session(tmp_path, "force_case")
    update_path = write_turn_update(tmp_path / "turn_update.md")

    lilia.command_apply_turn(["force_case", str(update_path)])
    capsys.readouterr()
    lilia.command_apply_turn(["--force", "force_case", str(update_path)])
    captured = capsys.readouterr()

    assert "warning: turn_update already applied" in captured.err
    memory = (session / "lilia/main/memory.md").read_text(encoding="utf-8")
    assert memory.count("写真を急かさず待った") == 2
    assert len(read_session_json(session)["applied_turn_updates"]) == 1


def test_apply_turn_duplicate_guard_is_session_scoped(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    first_session = write_session(tmp_path, "first_case")
    second_session = write_session(tmp_path, "second_case")
    update_path = write_turn_update(tmp_path / "turn_update.md")

    lilia.command_apply_turn(["first_case", str(update_path)])
    capsys.readouterr()
    lilia.command_apply_turn(["second_case", str(update_path)])
    capsys.readouterr()

    assert len(read_session_json(first_session)["applied_turn_updates"]) == 1
    assert len(read_session_json(second_session)["applied_turn_updates"]) == 1
    first_memory = (first_session / "lilia/main/memory.md").read_text(encoding="utf-8")
    second_memory = (second_session / "lilia/main/memory.md").read_text(encoding="utf-8")
    assert first_memory.count("写真を急かさず待った") == 1
    assert second_memory.count("写真を急かさず待った") == 1


def test_turn_update_fingerprint_is_path_independent(tmp_path: Path) -> None:
    lilia = load_lilia_module()
    first = write_turn_update(tmp_path / "first.md")
    second_path = tmp_path / "nested" / "second.md"
    second_path.parent.mkdir(parents=True)
    second = write_turn_update(second_path)

    assert lilia.turn_update_fingerprint(
        lilia.parse_turn_update(first)
    ) == lilia.turn_update_fingerprint(lilia.parse_turn_update(second))


def test_apply_turn_updates_story_deck_hook_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_hook_session(tmp_path, "hook_status_case")
    update_path = write_hook_update(
        tmp_path / "turn_update.md",
        """
- hook_id: main_initial_request
- hook_type: main
- status: advanced
- current_function: 前進
- current_question: 写真の扱いを翌日の確認へどう接続するか。
- next_candidate: 翌日の夕方にもう一度確認する。
- update_target: story_deck
""",
    )

    lilia.command_apply_turn(["hook_status_case", str(update_path)])
    output = capsys.readouterr().out

    story_deck = (session / "story/story_deck.md").read_text(encoding="utf-8")
    assert "story/story_deck.md" in output
    assert "- hook_id: main_initial_request" in story_deck
    assert "- status: advanced" in story_deck
    assert "- current_function: 前進" in story_deck
    assert "翌日の夕方にもう一度確認する" in story_deck
    assert story_deck.count("- status: active") == 0


def test_apply_turn_updates_active_hook_metadata_only_for_current_hook(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_hook_session(tmp_path, "active_hook_metadata_case")
    update_path = write_hook_update(
        tmp_path / "turn_update.md",
        """
- hook_id: main_initial_request
- hook_type: main
- status: active
- foreground_reason: 翌日の確認へ進む前に、写真の扱いを今触れる入口として保つ。
- update_active_hook: true
""",
    )

    lilia.command_apply_turn(["active_hook_metadata_case", str(update_path)])
    capsys.readouterr()

    event_card = (session / "current/event_card.md").read_text(encoding="utf-8")
    story_deck = (session / "story/story_deck.md").read_text(encoding="utf-8")
    assert "foreground_reason: 翌日の確認へ進む前に" in event_card
    assert story_deck.count("- status: active") == 1


def test_apply_turn_rejects_active_hook_switch_without_promotion(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    write_hook_session(tmp_path, "unsafe_switch_case")
    update_path = write_hook_update(
        tmp_path / "turn_update.md",
        """
- hook_id: relationship_first_trust
- hook_type: relationship
- status: active
- foreground_reason: 関係の境界線を前景化する。
- update_active_hook: true
""",
    )

    with pytest.raises(SystemExit) as exc:
        lilia.command_apply_turn(["unsafe_switch_case", str(update_path)])

    assert exc.value.code == 1


def test_apply_turn_rejects_relationship_hook_affinity_route_words(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    write_hook_session(tmp_path, "relationship_route_case")
    update_path = write_hook_update(
        tmp_path / "turn_update.md",
        """
- hook_id: relationship_first_trust
- hook_type: relationship
- status: advanced
- current_question: 好感度ルートを進める。
- update_target: story_deck
""",
    )

    with pytest.raises(SystemExit) as exc:
        lilia.command_apply_turn(["relationship_route_case", str(update_path)])

    assert exc.value.code == 1


def test_apply_turn_appends_candidate_next_hooks_without_stale_detection(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_hook_session(tmp_path, "candidate_hook_case")
    update_path = write_hook_update(
        tmp_path / "turn_update.md",
        """
- hook_id: life_revisit_route
- hook_type: life
- candidate_id: life_revisit_evening
- function_candidate: 始動
- visible_entry: 翌日の夕方にもう一度店へ寄る。
- promotion_condition: resume入口に使う時だけactive stateへ昇格する。
- grounding_guard: Candidateのままではactive eventとして使わない。
- update_target: candidate
""",
    )

    lilia.command_apply_turn(["candidate_hook_case", str(update_path)])
    capsys.readouterr()

    story_deck = (session / "story/story_deck.md").read_text(encoding="utf-8")
    assert "## Candidate Next Hooks" in story_deck
    assert "life_revisit_evening" in story_deck
    result = validate_state_consistency(session)
    assert not any(issue.code == "candidate_next_hook_not_active" for issue in result.issues)
    assert not any(issue.code == "hotset_scene_event_mismatch" for issue in result.issues)


def test_apply_turn_accepts_candidate_only_hook_update(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_hook_session(tmp_path, "candidate_only_case")
    update_path = write_hook_update(
        tmp_path / "turn_update.md",
        """
- candidate_id: relationship_after_silence
- source_hook_id: relationship_first_trust
- hook_type: relationship
- function_candidate: 余韻
- visible_entry: 次に会った時の短い沈黙。
- promotion_condition: resume入口に使う時だけactive stateへ昇格する。
- grounding_guard: Candidateのままではactive eventとして使わない。
""",
    )

    lilia.command_apply_turn(["candidate_only_case", str(update_path)])
    capsys.readouterr()

    story_deck = (session / "story/story_deck.md").read_text(encoding="utf-8")
    assert "relationship_after_silence" in story_deck
    assert "次に会った時の短い沈黙" in story_deck


def test_apply_turn_duplicate_guard_blocks_repeated_hook_updates(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    lilia = load_lilia_module()
    monkeypatch.setattr(lilia, "ROOT", tmp_path)
    monkeypatch.setattr(lilia, "SAVES_DIR", tmp_path / "saves")
    session = write_hook_session(tmp_path, "hook_duplicate_case")
    update_path = write_hook_update(
        tmp_path / "turn_update.md",
        """
- hook_id: main_initial_request
- hook_type: main
- status: advanced
- next_candidate: 翌日の夕方にもう一度確認する。
- update_target: story_deck
""",
    )

    lilia.command_apply_turn(["hook_duplicate_case", str(update_path)])
    capsys.readouterr()

    with pytest.raises(SystemExit):
        lilia.command_apply_turn(["hook_duplicate_case", str(update_path)])
    captured = capsys.readouterr()

    assert "turn_update already applied" in captured.err
    story_deck = (session / "story/story_deck.md").read_text(encoding="utf-8")
    assert story_deck.count("翌日の夕方にもう一度確認する") == 1
