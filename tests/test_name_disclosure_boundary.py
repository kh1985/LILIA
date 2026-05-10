from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.session import document_generator


def load_lilia():
    loader = SourceFileLoader("lilia_launcher_name_boundary", str(ROOT / "lilia"))
    spec = importlib.util.spec_from_loader("lilia_launcher_name_boundary", loader)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_knowledge_state_keeps_q7_as_meta_desired_call_name() -> None:
    lilia = load_lilia()

    md = lilia.render_ai_knowledge_state_document(
        ai_knowledge_state_md="",
        protagonist_md="# Protagonist\n\n## 呼ばれ方\n\n呼称（開示後）: かねこさん\n",
        profile="# Profile\n\n## 基礎情報\n\n- name: 詩月\n",
        answers={7: "かねこさん", 9: "特になし"},
        lilia_name="詩月",
    )

    assert "- key: protagonist_call_name" in md
    assert 'value: "かねこさん"' in md
    assert "fictional_status: meta" in md
    assert "known_to: [protagonist]" in md
    assert "希望呼称 / 開示後呼称" in md
    assert "予約名" in md
    assert "- key: heroine_name" in md
    assert 'value: "詩月"' in md
    assert "known_to: [heroine]" in md
    assert "player-facing scene では未開示" in md


def test_meta_name_values_are_hidden_from_runtime_prompt_context() -> None:
    lilia = load_lilia()

    knowledge = """
## knowledge_state

```yaml
items:
  - key: protagonist_call_name
    value: "かねこさん"
    fictional_status: meta
    source: protagonist
    known_to: [protagonist]
    acquired_at: pre_play
    weight: medium
  - key: heroine_name
    value: "詩月"
    fictional_status: meta
    source: heroine_self_disclosure
    known_to: [heroine]
    acquired_at: pre_play
    weight: high
```
"""
    protagonist = """
# Protagonist

## 呼ばれ方

呼称（開示後）: かねこさん

## 身体
"""

    sanitized_knowledge = lilia.sanitize_knowledge_state_for_context(knowledge)
    sanitized_protagonist = lilia.sanitize_protagonist_for_context(protagonist)

    assert "かねこさん" not in sanitized_knowledge
    assert "かねこさん" not in sanitized_protagonist
    assert lilia.KNOWLEDGE_HIDDEN_VALUE in sanitized_knowledge
    assert lilia.KNOWLEDGE_HIDDEN_VALUE in sanitized_protagonist
    assert 'value: "詩月"' in sanitized_knowledge


def test_prompts_include_name_disclosure_rule() -> None:
    core = (ROOT / "prompt" / "core.md").read_text(encoding="utf-8")
    save_resume = (ROOT / "prompt" / "save_resume.md").read_text(encoding="utf-8")

    for text in (core, save_resume):
        assert "Name Disclosure Rule" in text
        assert "characters cannot use names or call names they have not learned in fiction" in text
        assert "desired_call_name / 開示後呼称" in text
        assert "自己紹介、名刺、伝票、予約名、名札" in text
        assert "player-facing scene で未開示" in text


def test_document_generator_prompt_preserves_name_boundary() -> None:
    context = {
        "answers": {"1": "詩月", "7": "かねこさん", "9": "特になし"},
        "character_yaml": {"name": "詩月"},
        "profile_md": "# profile",
        "story_spine_md": "# story",
        "relationship_spine_md": "# relationship",
        "engine": "auto",
        "lilia_name": "詩月",
        "session_name": "name_boundary",
    }

    prompt = document_generator._build_group_c_prompt(context)

    assert "Name Disclosure Boundary" in prompt
    assert "Q7の呼ばれ方は desired_call_name / 開示後呼称" in prompt
    assert "初回からヒロインが知っている呼称ではない" in prompt
    assert "known_to: [protagonist]" in prompt
    assert "player-facing本文" in prompt
