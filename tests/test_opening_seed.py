from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.session.opening_seed import OpeningSeed, build_opening_seed


def test_all_omakase_still_builds_concrete_protagonist_seed() -> None:
    seed = build_opening_seed(
        answers={"6": "おまかせ", "8": "おまかせ"},
        character_yaml={"name": "三枝 玲奈"},
        profile_md=(
            "# Profile\n"
            "name: 三枝 玲奈\n\n"
            "## Initial Scene Anchors\n"
            "- 場所と状況: 閉店前の小さな店\n"
            "- 手元の具体物: 銀の鍵\n"
            "- 最初の距離: 初対面で、カウンター越しに向き合う\n"
            "- 会話の入口: 玲奈が鍵から目を上げる\n"
        ),
        story_spine_md=(
            "## Main Question\n"
            "玲奈は、主人公を同じ場に置ける相手として見られるか。\n\n"
            "## Reveal Ladder\n"
            "1. [pending] 銀の鍵の持ち主確認が必要になる。\n"
        ),
        relationship_spine_md="## 育てたいテーマ\n相手の境界を急かさず、同じ問題に向き合う。\n",
    )

    assert isinstance(seed, OpeningSeed)
    assert seed.hook_id == "main_initial_contact"
    assert seed.hook_type == "main"
    assert seed.status == "active"
    assert seed.scene_function == "起点"
    assert seed.protagonist_role
    assert seed.protagonist_reason
    assert seed.current_player_knowledge
    assert seed.protagonist_role != "その場の用件に関わる人物"
    assert "おまかせ" not in "\n".join(seed.as_dict().values())
    assert "Opening Seed" in seed.to_prompt_block()


def test_prop_inventory_stays_visible_props_not_player_facing_problem() -> None:
    prop_inventory = "メモ帳、ペン、預かり票の控え、濡れた宅配伝票、ミント缶、傷のついたスマホケース"
    seed = build_opening_seed(
        answers={"6": "おまかせ", "8": "おまかせ"},
        character_yaml={"name": "瀬戸 真琴", "occupation": "修理店の受付"},
        profile_md=(
            "# Profile\n"
            "name: 瀬戸 真琴\n\n"
            "## Initial Scene Anchors\n"
            "- 場所と状況: 雨の閉店前の修理店\n"
            f"- 手元の具体物: {prop_inventory}\n"
            "- 最初の距離: 初対面で、カウンター越しに向き合う\n"
            "- 会話の入口: 来店者の用件、見つからない控え、雨で読みにくくなった伝票、閉店時間までに確認できる範囲。\n"
        ),
        story_spine_md=(
            "## Main Question\n"
            "真琴は記録を守ったまま、目の前の相手を信用できるか。\n\n"
            "## Reveal Ladder\n"
            "1. [pending] 閉店前の雨の日、預かり票の控えが見つからず、濡れた宅配伝票と客の記憶が食い違っていることが表面化する。\n"
        ),
        relationship_spine_md="## 育てたいテーマ\n記録を守ることと人を信用することは同じではない。\n",
    )

    assert seed.visible_props == prop_inventory
    assert seed.player_facing_problem == "濡れた伝票と控えの照合"
    assert seed.player_facing_problem != prop_inventory
    assert "メモ帳、ペン" not in seed.player_facing_problem
    assert "濡れた伝票と控えを持ち込み" in seed.protagonist_role
    assert "その場の用件に関わる人物" not in seed.to_prompt_block()


def test_bookstore_shelf_consultation_uses_story_and_relationship_spines() -> None:
    seed = build_opening_seed(
        answers={
            "6": "書店で、棚に置く本について彼女へ相談しに来た。",
            "8": "仕事: 近所の小さな出版社で働く編集者",
        },
        character_yaml={"name": "朝倉 栞"},
        profile_md=(
            "# Profile\n"
            "name: 朝倉 栞\n\n"
            "## Initial Scene Anchors\n"
            "- 場所と状況: 古書と新刊が混じる書店の棚前\n"
            "- 手元の具体物: 候補本、棚札、古い栞\n"
            "- 最初の距離: 顔見知りだが、仕事の線引きは残っている\n"
            "- 会話の入口: 栞が棚札を持ったまま、候補本を一冊だけ戻す\n"
        ),
        story_spine_md=(
            "## Main Question\n"
            "栞は、自分の棚を誰かと一緒に変えることを選べるか。\n\n"
            "## Reveal Ladder\n"
            "1. [pending] 書店の棚に置く本の相談が、栞の譲れない選書基準に触れる。\n"
        ),
        relationship_spine_md="## 育てたいテーマ\n踏み込みすぎずに、相手の大事な場所へ手を添える。\n",
    )

    assert seed.protagonist_role == "近所の小さな出版社で働く編集者"
    assert seed.protagonist_reason == "書店で、棚に置く本について彼女へ相談しに来た。"
    assert seed.player_facing_problem == "棚に置く本の選び方の相談"
    assert seed.dramatic_question == "栞は、自分の棚を誰かと一緒に変えることを選べるか。"
    assert seed.relationship_stake == "踏み込みすぎずに、相手の大事な場所へ手を添える。"
    assert "棚" in seed.next_curiosity


def test_wallet_bookstore_scene_does_not_promote_repeated_prop_reveal() -> None:
    seed = build_opening_seed(
        answers={"6": "おまかせ", "8": "おまかせ"},
        character_yaml={"name": "水瀬 千佳", "occupation": "書店員"},
        profile_md=(
            "# Profile\n"
            "name: 水瀬 千佳\n\n"
            "## Initial Scene Anchors\n"
            "- 場所と状況: 閉店前の小さな書店\n"
            "- 手元の具体物: 落とした財布、鞄の文庫本、未開封ののど飴、左手首の時計\n"
            "- 最初の距離: 初対面で、レジ横の短い距離にいる\n"
            "- 会話の入口: 主人公が拾った財布を本人へ返そうとしている\n"
        ),
        story_spine_md=(
            "## Main Question\n"
            "千佳は、私物を拾った相手を急に近づけすぎず、短い礼を言えるか。\n\n"
            "## Reveal Ladder\n"
            "1. [pending] 鞄の文庫本と未開封ののど飴、左手首の時計を直す癖が、特定の場面で繰り返し現れる。\n"
        ),
        relationship_spine_md="## 育てたいテーマ\n礼を言うことと距離を詰めることは同じではない。\n",
    )

    assert seed.player_facing_problem == "落とした財布の受け渡しと本人確認"
    assert seed.protagonist_role == "落とした財布を拾い、本人へ返そうとしている人物"
    assert "財布" in seed.first_concrete_action
    assert "繰り返し現れる" not in seed.player_facing_problem
    assert "文庫本と未開封ののど飴" not in seed.player_facing_problem
