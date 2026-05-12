from __future__ import annotations

import re
import time
from pathlib import Path
import sys
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.session import document_generator


def _minimal_args() -> dict[str, Any]:
    return {
        "answers": {"1": "テスト"},
        "character_yaml": {"name": "テスト", "age": 24},
        "profile_md": "# profile",
        "story_spine_md": "# story",
        "relationship_spine_md": "# relationship",
        "engine": "auto",
    }


def test_generate_session_documents_runs_groups_in_parallel(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_generate_group(**kwargs: Any) -> dict[str, Any]:
        group_name = kwargs["group_name"]
        calls.append(group_name)
        time.sleep(0.2)
        return {
            "documents": {path: f"# {path}\n" for path in kwargs["rel_paths"]},
            "meta": {"engine_used": "stub", "validation_retry_count": 0},
        }

    monkeypatch.setattr(document_generator, "_generate_group", fake_generate_group)
    monkeypatch.setattr(document_generator, "validate_session_documents", lambda *args, **kwargs: (True, []))

    start = time.perf_counter()
    result = document_generator.generate_session_documents(**_minimal_args())
    elapsed = time.perf_counter() - start

    assert set(calls) == {"group_a", "group_b", "group_c"}
    assert elapsed < 0.45
    assert set(result["documents"]) == set(document_generator.ALL_PATHS)


def test_generate_session_documents_propagates_first_group_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_generate_group(**kwargs: Any) -> dict[str, Any]:
        if kwargs["group_name"] == "group_b":
            raise document_generator.DocumentGenerationError("group_b exploded")
        time.sleep(0.2)
        return {
            "documents": {path: f"# {path}\n" for path in kwargs["rel_paths"]},
            "meta": {"engine_used": "stub", "validation_retry_count": 0},
        }

    monkeypatch.setattr(document_generator, "_generate_group", fake_generate_group)

    with pytest.raises(document_generator.DocumentGenerationError, match="group_b exploded"):
        document_generator.generate_session_documents(**_minimal_args())


def test_group_a_uses_deterministic_fallback_after_invalid_generation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    template_root = ROOT / "templates" / "session"

    def template_for(path: str) -> str:
        template_path = template_root / path
        return template_path.read_text(encoding="utf-8")

    def invalid_group_a_output(*args: Any, **kwargs: Any) -> str:
        return "\n".join(
            f"===FILE: {path}===\n{template_for(path)}"
            for path in document_generator.GROUP_A_PATHS
        )

    monkeypatch.setattr(document_generator, "engine_candidates", lambda engine: ["stub"])
    monkeypatch.setattr(document_generator, "run_engine", invalid_group_a_output)

    result = document_generator._generate_group(
        group_name="group_a",
        rel_paths=document_generator.GROUP_A_PATHS,
        prompt="group a prompt",
        answers={"1": "おまかせ", "8": "おまかせ"},
        story_spine_md=(
            "## Main Question\n"
            "主人公は相手の境界を待てるか\n\n"
            "## Background Truth\n"
            "これは本文に出さない真相。\n"
        ),
        engine="codex",
        context={
            "answers": {"1": "おまかせ", "8": "おまかせ"},
            "character_yaml": {"name": "三枝 玲奈", "occupation": "小さな店の店主"},
            "profile_md": (
                "# Profile\n"
                "name: 三枝 玲奈\n"
                "occupation: 小さな店の店主\n\n"
                "## Initial Scene Anchors\n"
                "- 場所と状況: 閉店前の小さな店\n"
                "- 手元の具体物: 伝票と銀の鍵\n"
                "- 最初の距離: 初対面で、カウンター越しに向き合う\n"
                "- 会話の入口: 玲奈が伝票から目を上げる\n"
            ),
            "story_spine_md": "## Main Question\n主人公は相手の境界を待てるか\n",
            "relationship_spine_md": "## 育てたいテーマ\n近づくことと明かすことは同じではない。\n",
            "session_name": "test",
        },
    )

    assert result["meta"]["validation"] == "deterministic_fallback"
    assert result["documents"]["current/event_card.md"].count("hook_id: main_initial_contact") == 1
    assert "未設定" not in "\n".join(result["documents"].values())


def test_group_a_fallback_turns_prop_inventory_into_playable_problem(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    template_root = ROOT / "templates" / "session"

    def template_for(path: str) -> str:
        template_path = template_root / path
        return template_path.read_text(encoding="utf-8")

    def invalid_group_a_output(*args: Any, **kwargs: Any) -> str:
        return "\n".join(
            f"===FILE: {path}===\n{template_for(path)}"
            for path in document_generator.GROUP_A_PATHS
        )

    story_spine = (
        "## Main Question\n"
        "瀬戸真琴は、失くした控えをめぐる混乱の中で、自分の線を守ったまま誰かを信用できるか\n\n"
        "## Reveal Ladder\n"
        "1. [pending] 閉店前の雨の日、預かり票の控えが見つからず、濡れた宅配伝票と客の記憶が食い違っていることが表面化する。\n"
    )
    prop_inventory = "メモ帳、ペン、預かり票の控え、濡れた宅配伝票、ミント缶、傷のついたスマホケース"
    monkeypatch.setattr(document_generator, "engine_candidates", lambda engine: ["stub"])
    monkeypatch.setattr(document_generator, "run_engine", invalid_group_a_output)

    result = document_generator._generate_group(
        group_name="group_a",
        rel_paths=document_generator.GROUP_A_PATHS,
        prompt="group a prompt",
        answers={"1": "おまかせ", "8": "おまかせ"},
        story_spine_md=story_spine,
        engine="codex",
        context={
            "answers": {"1": "おまかせ", "8": "おまかせ"},
            "character_yaml": {"name": "瀬戸 真琴", "occupation": "修理店の受付"},
            "profile_md": (
                "# Profile\n"
                "name: 瀬戸 真琴\n"
                "occupation: 修理店の受付\n\n"
                "## Initial Scene Anchors\n"
                "- 場所と状況: 雨の閉店前の修理店\n"
                f"- 手元の具体物: {prop_inventory}\n"
                "- 最初の距離: 初対面で、カウンター越しに向き合う\n"
                "- 会話の入口: 来店者の用件、見つからない控え、雨で読みにくくなった伝票、閉店時間までに確認できる範囲。\n"
            ),
            "story_spine_md": story_spine,
            "relationship_spine_md": "## 育てたいテーマ\n記録を守ることと人を信用することは同じではない。\n",
            "session_name": "test",
        },
    )

    event_card = result["documents"]["current/event_card.md"]
    scene = result["documents"]["current/scene.md"]
    assert result["meta"]["validation"] == "deterministic_fallback"
    assert "foreground_reason: 初回sceneでプレイヤーが今触れられる入口を、濡れた伝票と控えの照合に絞るため。" in event_card
    assert "主人公は濡れた伝票と控えを持ち込み、受付で確認を求める来店者。" in scene
    assert "その場の用件に関わる人物" not in scene + event_card
    assert f"foreground_reason: 初回sceneでプレイヤーが今触れられる入口を、{prop_inventory}" not in event_card


def test_group_a_fallback_uses_wallet_entry_instead_of_repeated_prop_reveal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    template_root = ROOT / "templates" / "session"

    def template_for(path: str) -> str:
        template_path = template_root / path
        return template_path.read_text(encoding="utf-8")

    def invalid_group_a_output(*args: Any, **kwargs: Any) -> str:
        return "\n".join(
            f"===FILE: {path}===\n{template_for(path)}"
            for path in document_generator.GROUP_A_PATHS
        )

    story_spine = (
        "## Main Question\n"
        "千佳は、私物を拾った相手を急に近づけすぎず、短い礼を言えるか。\n\n"
        "## Reveal Ladder\n"
        "1. [pending] 鞄の文庫本と未開封ののど飴、左手首の時計を直す癖が、特定の場面で繰り返し現れる。\n"
    )
    monkeypatch.setattr(document_generator, "engine_candidates", lambda engine: ["stub"])
    monkeypatch.setattr(document_generator, "run_engine", invalid_group_a_output)

    result = document_generator._generate_group(
        group_name="group_a",
        rel_paths=document_generator.GROUP_A_PATHS,
        prompt="group a prompt",
        answers={"1": "おまかせ", "8": "おまかせ"},
        story_spine_md=story_spine,
        engine="claude",
        context={
            "answers": {"1": "おまかせ", "8": "おまかせ"},
            "character_yaml": {"name": "水瀬 千佳", "occupation": "書店員"},
            "profile_md": (
                "# Profile\n"
                "name: 水瀬 千佳\n"
                "occupation: 書店員\n\n"
                "## Initial Scene Anchors\n"
                "- 場所と状況: 閉店前の小さな書店\n"
                "- 手元の具体物: 落とした財布、鞄の文庫本、未開封ののど飴、左手首の時計\n"
                "- 最初の距離: 初対面で、レジ横の短い距離にいる\n"
                "- 会話の入口: 主人公が拾った財布を本人へ返そうとしている\n"
            ),
            "story_spine_md": story_spine,
            "relationship_spine_md": "## 育てたいテーマ\n礼を言うことと距離を詰めることは同じではない。\n",
            "session_name": "test",
        },
    )

    docs_text = "\n".join(result["documents"].values())
    event_card = result["documents"]["current/event_card.md"]
    scene = result["documents"]["current/scene.md"]
    assert result["meta"]["validation"] == "deterministic_fallback"
    assert "落とした財布の受け渡しと本人確認" in event_card
    assert "主人公は落とした財布を拾い、本人へ返そうとしている人物。" in scene
    assert "pending Reveal Ladder leaked" not in str(result["meta"])
    assert "繰り返し現れる" not in docs_text


def test_group_a_repairs_blank_control_fields_from_opening_seed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = {
        "answers": {"1": "おまかせ", "8": "おまかせ"},
        "character_yaml": {"name": "三枝 玲奈", "occupation": "小さな店の店主"},
        "profile_md": (
            "# Profile\n"
            "name: 三枝 玲奈\n"
            "occupation: 小さな店の店主\n\n"
            "## Initial Scene Anchors\n"
            "- 場所と状況: 閉店前の小さな店\n"
            "- 手元の具体物: 伝票と銀の鍵\n"
            "- 最初の距離: 初対面で、カウンター越しに向き合う\n"
            "- 会話の入口: 玲奈が伝票から目を上げる\n"
        ),
        "story_spine_md": "## Main Question\n主人公は相手の境界を待てるか\n",
        "relationship_spine_md": "## 育てたいテーマ\n近づくことと明かすことは同じではない。\n",
        "session_name": "test",
    }

    class FakeOpeningSeed:
        def as_dict(self) -> dict[str, Any]:
            return {
                "active_hook": {
                    "hook_id": "main_initial_contact",
                    "hook_type": "main",
                    "status": "active",
                    "foreground_reason": "seed固定の入口に絞るため。",
                },
                "scene_function": {
                    "function": "起点",
                    "current_question": "seedの問いを追う。",
                    "entry_state": "seedの初期距離。",
                    "exit_condition": "seedの出口条件。",
                    "change_delta": "seedの変化差分。",
                    "next_hook_candidate": "next_small_confirmation",
                },
                "player_orientation": {
                    "protagonist_reason": "主人公はseed由来の来店者。",
                    "current_player_knowledge": "seed由来の手がかりを知っている。",
                    "opening_must_show": "seed由来の場所、用件、距離。",
                    "still_hidden": "seed由来の真相。",
                },
                "player_facing_problem": "seed由来の表入口",
                "protagonist_reason": "主人公はseed由来の来店者。",
                "first_concrete_action": "seed由来の一手。",
                "next_curiosity": "seed由来の次の問い。",
                "visible_props": "seed由来の物証。",
            }

    def blank_control_fields(*args: Any, **kwargs: Any) -> str:
        docs = document_generator._fallback_group_a_documents(context)
        event_card = docs["current/event_card.md"]
        event_card = event_card.replace("- hook_id: main_initial_contact", "- hook_id:")
        event_card = event_card.replace("- hook_type: main", "- hook_type: relationship")
        event_card = event_card.replace("- status: active", "- status: background", 1)
        event_card = re.sub(r"^- foreground_reason: .+$", "- foreground_reason:", event_card, flags=re.MULTILINE)
        event_card = event_card.replace("- function: 起点", "- function: 試練")
        for field in ["current_question", "entry_state", "exit_condition", "change_delta", "next_hook_candidate"]:
            event_card = re.sub(rf"^- {field}: .+$", f"- {field}:", event_card, flags=re.MULTILINE)
        for label in [
            "プレイヤーが最初に見える入口",
            "主人公が関われる理由",
            "最初の一手で触れる対象",
            "入口として見せる違和感 / 困りごと",
            "まだGMだけが保持してよい真相",
            "ヒロイン本人も知らない / 言語化できないこと",
            "主人公が今判断するために本文で見せること",
            "ヒロインの台詞や態度から観察できること",
            "物理的に見える手がかり",
            "開示してよい条件",
            "開示してよい主体",
            "開示されたら更新する knowledge_state key",
            "まだ本文に書かないこと",
            "まだヒロインに言わせないこと",
            "まだ主人公が知った扱いにしないこと",
        ]:
            event_card = re.sub(rf"^([ \t]*[-*][ \t]*{re.escape(label)}:).+$", rf"\1", event_card, flags=re.MULTILINE)
        docs["current/event_card.md"] = event_card

        scene = docs["current/scene.md"]
        for label in [
            "主人公がここにいる理由",
            "主人公がscene開始時点で知っていること",
            "冒頭本文で必ず見せる前提",
            "まだ隠すこと",
        ]:
            scene = re.sub(rf"^- {label}: .+$", f"- {label}:", scene, flags=re.MULTILINE)
        docs["current/scene.md"] = scene
        return "\n".join(f"===FILE: {path}===\n{docs[path]}" for path in document_generator.GROUP_A_PATHS)

    monkeypatch.setattr(document_generator, "build_opening_seed", lambda **kwargs: FakeOpeningSeed())
    monkeypatch.setattr(document_generator, "engine_candidates", lambda engine: ["stub"])
    monkeypatch.setattr(document_generator, "run_engine", blank_control_fields)

    result = document_generator._generate_group(
        group_name="group_a",
        rel_paths=document_generator.GROUP_A_PATHS,
        prompt="group a prompt",
        answers=context["answers"],
        story_spine_md=context["story_spine_md"],
        engine="codex",
        context=context,
    )

    event_card = result["documents"]["current/event_card.md"]
    scene = result["documents"]["current/scene.md"]
    assert result["meta"]["validation"] == "pass"
    assert result["meta"]["validation_retry_count"] == 0
    assert "- hook_id: main_initial_contact" in event_card
    assert "- hook_type: main" in event_card
    assert "- status: active" in event_card
    assert "- foreground_reason: seed固定の入口に絞るため。" in event_card
    assert "- function: 起点" in event_card
    assert "- current_question: seedの問いを追う。" in event_card
    assert "- プレイヤーが最初に見える入口: seed由来の表入口" in event_card
    assert "- 最初の一手で触れる対象: seed由来の一手。" in event_card
    assert "- 物理的に見える手がかり: seed由来の物証。" in event_card
    assert "- まだ本文に書かないこと: 背景や意図の断定。" in event_card
    assert "- 主人公がここにいる理由: 主人公はseed由来の来店者。" in scene
    assert "- 主人公がscene開始時点で知っていること: seed由来の手がかりを知っている。" in scene


def test_group_b_normalizes_omakase_fragments_in_protagonist_and_knowledge_state() -> None:
    context = {
        "answers": {3: "おまかせ", 5: "おまかせ", 7: "おまかせ", 8: "おまかせ", 9: "かせ"},
        "character_yaml": {"name": "東雲 紗和", "occupation": "区立図書館の司書"},
        "profile_md": "# Profile\nname: 東雲 紗和\noccupation: 区立図書館の司書\n",
        "story_spine_md": "",
        "relationship_spine_md": "",
    }
    protagonist = document_generator._normalize_protagonist_document(
        "# Protagonist\n\n## スタイル\n\n- 服装: おまかせ\n",
        context,
    )
    knowledge_state = document_generator._render_knowledge_state_document(
        "",
        protagonist,
        context,
    )

    assert "- 服装: 未確定" in protagonist
    assert 'key: protagonist_call_name\n    value: "未確定"' in knowledge_state
    assert 'key: session_constraints\n    value: "特になし"' in knowledge_state
    assert "おまかせ" not in protagonist
    assert "かせ" not in knowledge_state
