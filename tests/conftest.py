"""Shared pytest fixtures and helpers.

``PYTHONPATH=src`` is the documented way to run this suite. This conftest also
inserts ``src`` on ``sys.path`` so a bare ``pytest`` works on a fresh clone
without any packaging framework (no setup.py / pyproject.toml).
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "daily_sample.json"


def load_fixture() -> dict:
    """Return a fresh copy of the mock briefing document."""
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.fixture()
def doc() -> dict:
    return load_fixture()


def make_document(text: str = "演示文本", **overrides) -> dict:
    """Build a minimal but fully valid document, overriding one tab's text.

    Used by the word-budget tests, which need precise control over length.
    """
    document = {
        "meta": {
            "report_type": "Daily Briefing",
            "run_date": "2026-10-20",
            "data_date": "2026-10-20",
            "data_mode": "mock",
        },
        "tabs": {
            "highlights": {
                "tab_number": 1,
                "items": [
                    {
                        "availability": "available",
                        "text": text,
                        "source": {
                            "name": "mock-provider",
                            "provider_tier": "P0",
                            "locator": "mock://unit-test",
                        },
                        "confidence": "HIGH",
                        "estimated": False,
                        "unavailable_reason": None,
                    }
                ],
            },
            "market_snapshot": {"tab_number": 2, "items": []},
            "impact_analysis": {"tab_number": 3, "items": []},
            "knowledge_bite": {"tab_number": 4, "items": []},
            "follow_up": {"tab_number": 5, "items": []},
        },
        "methodology": {
            "methods": ["单元测试用方法"],
            "limitations": ["单元测试用局限说明"],
        },
    }
    document = copy.deepcopy(document)
    for key, value in overrides.items():
        if key == "meta":
            document["meta"].update(value)
        elif key == "methodology":
            document["methodology"].update(value)
        else:
            document[key] = value
    return document


def repeat_cjk(n: int) -> str:
    """Return a string of exactly ``n`` counted words (1 CJK char each)."""
    return "测" * n
