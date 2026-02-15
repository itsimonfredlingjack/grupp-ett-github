"""Unit tests for scripts/jules_review_api.py.

These tests validate deterministic extraction of review text from session
activities without calling external APIs.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = Path("scripts/jules_review_api.py")

spec = importlib.util.spec_from_file_location("jules_review_api", SCRIPT_PATH)
assert spec is not None
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def test_extract_agent_messages_collects_string_and_dict_messages() -> None:
    activities = [
        {"agentMessaged": {"agentMessage": "hello"}},
        {"agentMessaged": {"agentMessage": {"text": "world"}}},
        {"agentMessaged": {"agentMessage": {"content": "  trimmed  "}}},
        {"agentMessaged": {"agentMessage": {"nested": {"text": "deep"}}}},
    ]

    assert module.extract_agent_messages(activities) == [
        "hello",
        "world",
        "trimmed",
        "deep",
    ]


def test_select_best_agent_message_prefers_messages_with_severity() -> None:
    messages = [
        "All good.",
        "[LOW] foo.py:10 — Minor formatting issue",
    ]
    assert module.select_best_agent_message(messages) == messages[1]


def test_select_best_agent_message_prefers_more_findings() -> None:
    one = "[HIGH] a.py:1 — Issue A"
    two = "[HIGH] b.py:2 — Issue B\n[LOW] c.py:3 — Issue C"
    assert module.select_best_agent_message([one, two]) == two
