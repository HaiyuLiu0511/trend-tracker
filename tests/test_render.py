"""Rendering tests — five-tab structure, evidence marks, HTML safety."""

from __future__ import annotations

import re

from conftest import load_fixture

from daily_briefing.render import render
from daily_briefing.schema import TAB_DEFS, TAB_ORDER


def _panels(html: str):
    return re.findall(r'data-tab="([a-z_]+)"', html)


def test_r01_exactly_five_tab_panels_in_frozen_order():
    html = render(load_fixture())
    assert _panels(html) == TAB_ORDER
    assert html.count('role="tabpanel"') == 5


def test_r01b_first_panel_is_visible_without_javascript():
    html = render(load_fixture())
    first = re.search(r'<section class="tab-panel"[^>]*data-tab="highlights"[^>]*>', html)
    assert first, "highlights panel not found"
    assert "hidden" not in first.group(0)
    others = re.findall(r'<section class="tab-panel"[^>]*hidden>', html)
    assert len(others) == 4


def test_r02_tab_headings_use_frozen_question_form():
    html = render(load_fixture())
    for key in TAB_ORDER:
        definition = TAB_DEFS[key]
        expected = f"Tab {definition['number']}: {definition['question']}"
        assert expected in html, f"missing heading: {expected}"
    assert html.count("Tab 5: 哪些事需要持续跟踪？") == 1


def test_r03_title_uses_report_type_and_data_date():
    html = render(load_fixture())
    assert "<title>Daily Briefing — 2026-10-20</title>" in html
    assert "Daily Briefing — 2026-10-20" in html


def test_r04_header_distinguishes_run_date_from_data_date():
    doc = load_fixture()
    doc["meta"]["run_date"] = "2026-10-21"
    html = render(doc)
    assert "Run Date: 2026-10-21" in html
    assert "Data Date: 2026-10-20" in html


def test_r05_evidenced_fallback_is_rendered():
    html = render(load_fixture())
    # highlights[1]: P1 succeeded after P0 returned no_data
    assert "fallback from P0 mock-primary-feed no_data" in html


def test_r06_no_fallback_claim_without_routing_evidence():
    """A P2 tier alone must NOT imply that P0 failed (Slice 1 rule 6)."""
    html = render(load_fixture())
    # impact_analysis[1] is P2 with no routing block.
    assert "mock-web-scrape (P2)" in html
    # and there is exactly one fallback note per evidenced item, never for P2.
    assert html.count("fallback from") == 2
    for match in re.findall(r"Source: mock-web-scrape[^<]*", html):
        assert "fallback" not in match


def test_r07_every_available_item_shows_confidence_badge():
    html = render(load_fixture())
    badges = re.findall(r'data-confidence="([A-Z\-]+)"', html)
    # 8 available items in the fixture (1 item is intentionally unavailable)
    assert len(badges) == 8
    assert set(badges) == {"HIGH", "MEDIUM", "LOW-MEDIUM", "LOW"}


def test_r08_estimated_item_is_labelled():
    html = render(load_fixture())
    assert 'data-estimated="true"' in html
    assert "（估算）" in html


def test_r09_missing_data_renders_label_and_reason():
    html = render(load_fixture())
    assert "数据不可用" in html
    assert "P0 mock-market-feed 无北向资金当日数据" in html


def test_r10_mock_mode_renders_persistent_banner():
    html = render(load_fixture())
    assert 'data-banner="mock"' in html
    assert "MOCK DATA" in html
    assert 'name="data-mode" content="mock"' in html


def test_r11_real_mode_must_disclose_unverified_evidence():
    """data_mode=real states provenance, never verification (Slice 1 rule)."""
    doc = load_fixture()
    doc["meta"]["data_mode"] = "real"
    html = render(doc)

    # a disclosure banner is mandatory
    assert 'data-banner="unverified-evidence"' in html
    assert "NOT VERIFIED" in html
    assert "不等于已验证" in html
    assert "未实现自动验证机制" in html

    # the mock banner must NOT appear in real mode
    assert 'data-banner="mock"' not in html
    assert "MOCK DATA" not in html

    # footer restates the same limit for real mode
    assert "data_mode=real" in html
    assert "数据真实性由输入方负责，系统未做核验" in html


def test_r11b_both_modes_state_that_badges_are_not_verified():
    for mode in ("mock", "real"):
        doc = load_fixture()
        doc["meta"]["data_mode"] = mode
        html = render(doc)
        assert "不代表本系统已验证该结论" in html, mode


def test_r11c_confidence_scale_is_unchanged_by_real_mode():
    """Real mode must not promote, rename or add a confidence level."""
    doc = load_fixture()
    doc["meta"]["data_mode"] = "real"
    html = render(doc)
    badges = set(re.findall(r'data-confidence="([A-Z\-]+)"', html))
    assert badges == {"HIGH", "MEDIUM", "LOW-MEDIUM", "LOW"}
    # every "VERIFIED" occurrence must belong to a negation phrase,
    # never stand alone as a positive verification claim
    residual = html.replace("UNVERIFIED", "").replace("NOT VERIFIED", "")
    assert "VERIFIED" not in residual
    assert "已验证结论" not in html


def test_r12_footer_documents_methodology_limits_and_routing():
    html = render(load_fixture())
    assert "Methodology — 使用的方法" in html
    assert "Methodology — 适用条件与局限" in html
    assert "P0 → P1 → P2 → P3" in html
    assert "P0-003" in html  # scope disclaimer stays visible
    assert "尚未完成" in html


def test_r13_tabs_are_interactive_without_framework():
    html = render(load_fixture())
    assert 'role="tablist"' in html
    assert html.count('role="tab"') == 5
    assert "<script>" in html
    # no external front-end framework
    for banned in ("react", "vue.js", "jquery", "tailwind", "bootstrap"):
        assert banned not in html.lower()


def test_r14_dark_theme_and_card_grid_present():
    html = render(load_fixture())
    assert "--bg:#0f1117" in html  # dark background token
    assert "display:grid" in html  # card grid layout


def test_r15_html_is_escaped_against_injection():
    doc = load_fixture()
    doc["tabs"]["highlights"]["items"][0]["text"] = "<script>alert(1)</script>"
    html = render(doc)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_r16_single_file_no_external_resources():
    html = render(load_fixture())
    assert "http://" not in html
    assert "https://" not in html.replace('xmlns="http://www.w3.org/', "")
