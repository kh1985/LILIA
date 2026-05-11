from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.session.knowledge_boundary import assess_knowledge_boundary


def _knowledge_doc(yaml_block: str) -> str:
    return f"""# Knowledge State

## knowledge_state

```yaml
{yaml_block.strip()}
```
"""


def test_knowledge_boundary_classifies_core_buckets() -> None:
    report = assess_knowledge_boundary(
        _knowledge_doc(
            """
items:
  - key: usb_delivery
    value: "便利屋が黒いUSBを預かっている"
    fictional_status: shared
    source: protagonist_self_disclosure
    known_to: [protagonist, heroine]
    acquired_at: scene_1
    weight: high
    notes: "二人が今見ている問題"
  - key: usb_true_route
    value: "USBは偶然ではなく二人を接触させる導線"
    fictional_status: gm_only
    source: story_spine
    known_to: [GM]
    acquired_at: pre_play
    weight: high
    notes: "Reveal Ladderで段階開示する"
  - key: heroine_suspicion
    value: "かねこが仕掛け側かもしれない"
    fictional_status: meta
    source: inferred
    known_to: [heroine]
    acquired_at: scene_1
    weight: medium
    notes: "透子の疑い。事実ではない"
  - key: visible_envelope
    value: "白い封筒がテーブルにある"
    fictional_status: observable
    source: observation
    known_to: [protagonist, heroine]
    acquired_at: scene_1
    weight: medium
    notes: "その場で観察できる"
"""
        )
    )

    assert report.ok
    assert [item.key for item in report.boundary.gm_truth] == ["usb_true_route"]
    assert [item.key for item in report.boundary.shared_facts] == ["usb_delivery", "visible_envelope"]
    assert [item.key for item in report.boundary.observable_now] == ["visible_envelope"]
    assert [item.key for item in report.boundary.heroine_beliefs_or_suspicions] == ["heroine_suspicion"]
    assert [item.key for item in report.boundary.do_not_reveal_yet] == ["usb_true_route"]


def test_knowledge_boundary_rejects_gm_only_leak_to_player() -> None:
    report = assess_knowledge_boundary(
        _knowledge_doc(
            """
items:
  - key: hidden_culprit
    value: "依頼主の正体"
    fictional_status: gm_only
    source: story_spine
    known_to: [GM, protagonist]
    acquired_at: pre_play
    weight: high
    notes: "まだ出さない"
"""
        )
    )

    assert not report.ok
    assert "hidden_culprit: gm_only must be known_to [GM]" in report.errors


def test_knowledge_boundary_reports_missing_required_fields() -> None:
    report = assess_knowledge_boundary(
        _knowledge_doc(
            """
items:
  - key: incomplete
    value: "途中の項目"
    fictional_status: shared
"""
        )
    )

    assert not report.ok
    assert "incomplete: missing field(s): acquired_at, known_to, source, weight" in report.errors
