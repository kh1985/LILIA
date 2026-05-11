from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_lilia_module() -> ModuleType:
    loader = SourceFileLoader("lilia_cli_help_test", str(ROOT / "lilia"))
    spec = importlib.util.spec_from_loader("lilia_cli_help_test", loader)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_default_usage_stays_focused(capsys: pytest.CaptureFixture[str]) -> None:
    lilia = load_lilia_module()

    lilia.main([])

    output = capsys.readouterr().out
    assert "./lilia new" in output
    assert "./lilia resume" in output
    assert "./lilia apply-turn" in output
    assert "./lilia menu" in output
    assert "./lilia help dev" in output
    assert "./lilia ai-playtest" not in output
    assert "./lilia dev-test" not in output
    assert "./lilia archive-codex-logs" not in output


def test_help_dev_shows_playtest_commands(capsys: pytest.CaptureFixture[str]) -> None:
    lilia = load_lilia_module()

    lilia.main(["help", "dev"])

    output = capsys.readouterr().out
    assert "LILIA development commands" in output
    assert "./lilia ai-playtest" in output
    assert "./lilia growth-smoke" in output
    assert "./lilia dev-smoke" in output
    assert "./lilia archive-codex-logs" not in output


def test_help_all_shows_compatibility_and_utilities(capsys: pytest.CaptureFixture[str]) -> None:
    lilia = load_lilia_module()

    lilia.main(["help", "all"])

    output = capsys.readouterr().out
    assert "LILIA all commands" in output
    assert "./lilia prompt-only new" in output
    assert "./lilia long-growth" in output
    assert "./lilia archive-codex-logs" in output
    assert "./lilia format-input" in output


def test_help_rejects_unknown_topic() -> None:
    lilia = load_lilia_module()

    with pytest.raises(SystemExit):
        lilia.main(["help", "unknown"])
