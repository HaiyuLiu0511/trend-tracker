"""Quality-gate tests — 500-word budget, missing data, evidence completeness.

Frozen sources: docs/core/REPORT_DESIGN.md L87, docs/daily/workflow.md L33,
docs/evidence/EVIDENCE_LAYER.md.
"""

from __future__ import annotations

import re

import pytest
from conftest import load_fixture, make_document, repeat_cjk

from daily_briefing.render import render
from daily_briefing.schema import (
    TAB_ORDER,
    UNAVAILABLE_LABEL,
    WORD_LIMIT,
    WordLimitExceeded,
    count_tab_words,
    count_words,
)


# ---------------------------------------------------------------- word count

def test_q07_count_words_mixes_cjk_and_latin_tokens():
    assert count_words("测试") == 2
    assert count_words("hello world") == 2
    assert count_words("AI 芯片") == 1 + 2  # 1 latin token + 2 CJK chars
    assert count_words("") == 0


def test_q07b_count_words_ignores_html_tags():
    assert count_words("<b>测试</b>") == 2
    assert count_words("<span class=\"x\">hello</span>") == 1


def test_q07c_count_words_keeps_digits_and_compounds():
    assert count_words("涨 0.82%") == 2  # CJK 涨 + token 0.82
    assert count_words("v2.0-baseline") == 1


def test_q01_fixture_is_within_budget():
    doc = load_fixture()
    for key in TAB_ORDER:
        count = count_tab_words(doc["tabs"][key]["items"], key)
        assert count <= WORD_LIMIT, f"{key} = {count}"


def test_q02_over_budget_fails_and_does_not_truncate():
    doc = make_document(text=repeat_cjk(WORD_LIMIT + 1))
    with pytest.raises(WordLimitExceeded) as excinfo:
        render(doc)
    assert excinfo.value.tab_key == "highlights"
    assert excinfo.value.count == WORD_LIMIT + 1
    assert "NOT truncated" in str(excinfo.value)


def test_q03_exact_budget_passes():
    doc = make_document(text=repeat_cjk(WORD_LIMIT))
    html = render(doc)
    assert html  # rendered without raising


def test_q03b_word_limit_gate_has_no_bypass():
    """The 500-word gate is mandatory: no public switch may disable it."""
    import inspect

    from daily_briefing import render as render_mod

    params = inspect.signature(render_mod.render).parameters
    assert "enforce_word_limit" not in params, "render() must not expose a bypass"

    from daily_briefing.__main__ import main

    # The CLI must reject the removed flag rather than silently ignoring it.
    with pytest.raises(SystemExit) as excinfo:
        main(["--input", "x.json", "--no-word-limit"])
    assert excinfo.value.code == 2  # argparse usage error


def test_q03c_over_budget_never_writes_output_via_cli(tmp_path):
    """CLI must exit non-zero AND leave no artefact behind."""
    import json

    from daily_briefing.__main__ import main

    doc = make_document(text=repeat_cjk(WORD_LIMIT + 1))
    src = tmp_path / "over.json"
    src.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "out.html"

    code = main(["--input", str(src), "--out", str(out)])
    assert code == 3
    assert not out.exists(), "over-budget run must not write any artefact"


# ------------------------------------------------------------- missing data

def test_q04_unavailable_item_shows_label_and_reason():
    html = render(load_fixture())
    assert UNAVAILABLE_LABEL in html
    # the reason text is rendered verbatim
    assert "P1 mock-alt-feed 未接入" in html


def test_q05_unavailable_item_has_no_confidence_badge():
    doc = load_fixture()
    html = render(doc)
    missing_card = re.search(
        r'<article class="card card-missing"[^>]*data-availability="unavailable">'
        r"(.*?)</article>",
        html,
        re.S,
    )
    assert missing_card, "missing-data card not found"
    block = missing_card.group(1)
    assert "data-confidence" not in block
    assert UNAVAILABLE_LABEL in block


def test_q05b_missing_data_card_fabricates_no_numbers():
    """No numeric value may appear inside a 数据不可用 card."""
    doc = load_fixture()
    html = render(doc)
    for block in re.findall(
        r'<article class="card card-missing"[^>]*>(.*?)</article>', html, re.S
    ):
        body = re.sub(r"<[^>]+>", " ", block)
        # keep only the declared reason sentence, ignore the fixed label
        body = body.replace(UNAVAILABLE_LABEL, "")
        digits = re.findall(r"\d+(?:\.\d+)?", body)
        # the fixture reason legitimately cites P0/P1 tier labels; any *other*
        # digit sequence would indicate fabricated data.
        assert all(d in ("0", "1") for d in digits), f"suspicious numbers: {digits}"


def test_q06_estimated_badge_only_when_flagged():
    doc = load_fixture()
    assert 'data-estimated="true"' in render(doc)

    doc2 = make_document()
    assert 'data-estimated="true"' not in render(doc2)


def test_q06b_empty_tab_renders_missing_data_not_blank():
    doc = make_document()
    html = render(doc)
    assert "本 Tab 未提供任何条目" in html


def test_q10_display_metadata_is_excluded_from_word_budget():
    """next_check is required by contract but must not consume the word budget."""
    doc = make_document()
    follow_up = {
        "tab_number": 5,
        "items": [
            {
                "availability": "available",
                "action": "动作",  # 2 CJK chars
                "next_check": "2026-11-03 跟进供应链出货进度公告并核对产能爬坡时间表",
                "source": {
                    "name": "mock-provider",
                    "provider_tier": "P0",
                    "locator": "mock://unit-test",
                },
                "confidence": "MEDIUM",
                "estimated": False,
                "unavailable_reason": None,
            }
        ],
    }
    doc["tabs"]["follow_up"] = follow_up
    assert count_tab_words(follow_up["items"], "follow_up") == 2
    render(doc)  # long next_check must not trip the 500-word gate


# -------------------------------------------------------- evidence complete

def test_q08_every_available_item_has_source_and_confidence():
    doc = load_fixture()
    for key in TAB_ORDER:
        for item in doc["tabs"][key]["items"]:
            if item["availability"] != "available":
                continue
            assert item["source"]["name"], key
            assert item["source"]["locator"], key
            assert item["confidence"], key


def test_q09_no_successful_p0_claim_without_evidence():
    """P0 items need no routing block; non-P0 needs no fallback claim either."""
    doc = load_fixture()
    html = render(doc)
    # impact_analysis[1] is P2 without routing: rendered plainly, no fallback.
    assert "Source: mock-web-scrape (P2)" in html
    assert "mock-web-scrape (P2, fallback" not in html
