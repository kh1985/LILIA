from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.session.document_validator import validate_opening_plan_consistency


def _scene_with_plan(plan: str) -> str:
    return f"""# Scene

## 今いる場所

- 路地裏。

## Opening Plan

{plan.strip()}
"""


VALID_PLAN = """
selected_patterns: [O3, O14]
selection_reason: 音で異常を先に置き、発見の瞬間から関係を始める。
must_include:
  - O3: 視覚情報は最後、金属音と雨の温度だけを先に置く。
  - O14: 発見の瞬間から始め、助けるか様子を見る余地を残す。
4_jobs:
  hook: 路地裏に転がる金属音。
  orientation: 便利屋の主人公が依頼帰りに裏道を通っている。
  agency: 倒れている人物へ近づくか、距離を置くかを選べる。
  unresolved: 誰が倒れているのか、なぜここにいるのか。
clarity_anchors:
  protagonist_role: 便利屋として依頼帰りであることを荷物と服装で示す。
  protagonist_purpose: 近道として人通りの少ない裏道を通っている。
  location_function: 搬入口と消えかけた看板で商店街裏の路地だと分かる。
  heroine_relation: 見覚えがない人物として初対面の戸惑いを置く。
opening_caveats:
  - O14: 助けた後から始めない。
"""


def test_opening_plan_validator_passes_valid_plan() -> None:
    assert validate_opening_plan_consistency(_scene_with_plan(VALID_PLAN)) == []


def test_opening_plan_validator_warns_without_a_group() -> None:
    plan = VALID_PLAN.replace("[O3, O14]", "[O5, O14]")
    warnings = validate_opening_plan_consistency(_scene_with_plan(plan))
    assert any("A-group" in warning for warning in warnings)


def test_opening_plan_validator_warns_without_d_group() -> None:
    plan = VALID_PLAN.replace("[O3, O14]", "[O3, O9]")
    warnings = validate_opening_plan_consistency(_scene_with_plan(plan))
    assert any("D-group" in warning for warning in warnings)


def test_opening_plan_validator_warns_for_two_from_same_group() -> None:
    plan = VALID_PLAN.replace("[O3, O14]", "[O1, O3, O14]")
    warnings = validate_opening_plan_consistency(_scene_with_plan(plan))
    assert any("multiple patterns from group A" in warning for warning in warnings)


def test_opening_plan_validator_warns_for_unknown_pattern() -> None:
    plan = VALID_PLAN.replace("[O3, O14]", "[O3, O16]")
    warnings = validate_opening_plan_consistency(_scene_with_plan(plan))
    assert any("unknown pattern: O16" in warning for warning in warnings)


def test_opening_plan_validator_warns_for_missing_4_jobs_field() -> None:
    plan = VALID_PLAN.replace("  agency: 倒れている人物へ近づくか、距離を置くかを選べる。", "  agency:")
    warnings = validate_opening_plan_consistency(_scene_with_plan(plan))
    assert any("4_jobs.agency" in warning for warning in warnings)


def test_opening_plan_validator_warns_for_missing_clarity_anchor() -> None:
    plan = VALID_PLAN.replace(
        "  location_function: 搬入口と消えかけた看板で商店街裏の路地だと分かる。",
        "  location_function:",
    )
    warnings = validate_opening_plan_consistency(_scene_with_plan(plan))
    assert any("clarity_anchors.location_function" in warning for warning in warnings)

