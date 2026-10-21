"""Minimum Daily Pipeline tests — Slice 3.

Covers the approved rules R1-R6 from ``SLICE3_REVISED_RULES.md``:

  R1  follow-up ``action`` must be supplied explicitly
  R2  ``sources[0]`` is the input-chosen primary source; transport only
  R3  exact text mapping (``TAB1_TEXT_FORMAT`` for Tab 1, ``summary`` for Tab 3)
  R4  explicit event selection by the input; no scoring / ranking / filtering
  R5  ``build_document()`` is pure; the CLI never bypasses the quality gates
  R6  missing market data uses a neutral reason, never an invented failure

Helpers are local to this module: ``tests/conftest.py`` must not be modified.
"""

from __future__ import annotations

import copy
import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest

from contracts.event import ContractError
from daily_briefing.pipeline import (
    NEUTRAL_MARKET_MISSING_REASON,
    TAB1_TEXT_FORMAT,
    build_document,
    main,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path(__file__).parent / "fixtures" / "pipeline_sample.json"

FACT = "evt-20261020-chip-v2"
FACT_UNSELECTED = "evt-20261020-chip-launch"
INF_A = "evt-20261020-margin-chain"
INF_B = "evt-20261020-chip-impact"
OPEN_HYP = "evt-20261020-dedup-hypothesis"
ACTIVE_HYP = "evt-20261020-delivery-hypothesis"


def load_source() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def with_source(mutate) -> dict:
    source = load_source()
    mutate(source)
    return source


def build(mutate=None) -> dict:
    return build_document(mutate(load_source()) if mutate else load_source())


# --------------------------------------------------------------------------
# R4 — explicit event selection
# --------------------------------------------------------------------------


def test_p01_tab1_uses_selected_facts_in_input_order():
    document = with_source(
        lambda s: s["selection"].update(
            {"tab1_event_ids": [FACT_UNSELECTED, FACT]}
        )
    )
    items = build_document(document)["tabs"]["highlights"]["items"]
    assert [i["event_id"] for i in items] == [FACT_UNSELECTED, FACT]


def test_p02_tab3_uses_selected_inferences_in_input_order():
    document = with_source(
        lambda s: s["selection"].update({"tab3_event_ids": [INF_A, INF_B]})
    )
    items = build_document(document)["tabs"]["impact_analysis"]["items"]
    # the fixture deliberately lists these in the reverse of the events order
    assert [i["event_id"] for i in items] == [INF_A, INF_B]
    assert [i["event_id"] for i in items] != [INF_B, INF_A]


def test_p03_unselected_events_are_not_shown_but_are_preserved():
    document = build_document(load_source())
    shown = {i.get("event_id") for i in document["tabs"]["highlights"]["items"]}
    assert FACT_UNSELECTED not in shown
    kept = {e["event_id"] for e in document["events"]}
    assert FACT_UNSELECTED in kept
    assert len(document["events"]) == 6


def test_p04_tab1_rejects_a_non_fact_id():
    document = with_source(lambda s: s["selection"].update({"tab1_event_ids": [INF_B]}))
    with pytest.raises(ContractError, match="requires 'fact'"):
        build_document(document)


def test_p05_tab3_rejects_a_non_inference_id():
    document = with_source(lambda s: s["selection"].update({"tab3_event_ids": [FACT]}))
    with pytest.raises(ContractError, match="requires 'inference'"):
        build_document(document)


def test_p06_selection_rejects_unknown_id():
    document = with_source(
        lambda s: s["selection"].update({"tab1_event_ids": ["evt-20261020-nope"]})
    )
    with pytest.raises(ContractError, match="unknown event"):
        build_document(document)


@pytest.mark.parametrize("field", ["tab1_event_ids", "tab3_event_ids"])
def test_p07_empty_selection_is_allowed(field):
    document = with_source(lambda s: s["selection"].update({field: []}))
    built = build_document(document)
    tab = "highlights" if field.startswith("tab1") else "impact_analysis"
    assert built["tabs"][tab]["items"] == []


def test_p08_duplicate_selection_id_is_rejected():
    document = with_source(
        lambda s: s["selection"].update({"tab1_event_ids": [FACT, FACT]})
    )
    with pytest.raises(ContractError, match="repeats event id"):
        build_document(document)


def test_p09_pipeline_exposes_no_scoring_or_ranking():
    import daily_briefing.pipeline as pipeline

    for name in ("score", "rank", "select_best", "importance", "prioritise"):
        assert not hasattr(pipeline, name), f"unexpected helper: {name}"


def test_p10_open_event_without_a_plan_entry_is_rejected():
    """R4: an open event may not be dropped silently."""
    document = with_source(lambda s: s["follow_up_plan"].clear())
    with pytest.raises(ContractError, match="no entry for it"):
        build_document(document)


def test_p11_active_event_may_stay_out_of_tab5():
    """The explicit opt-out: status=active instead of open."""
    document = build_document(load_source())
    tracked = {i["event_id"] for i in document["tabs"]["follow_up"]["items"]}
    assert OPEN_HYP in tracked
    assert ACTIVE_HYP not in tracked


# --------------------------------------------------------------------------
# R3 — exact text mapping
# --------------------------------------------------------------------------


def test_p12_tab1_text_is_the_exact_fixed_format():
    source = load_source()
    event = next(e for e in source["events"] if e["event_id"] == FACT)
    item = build_document(source)["tabs"]["highlights"]["items"][0]
    assert item["text"] == TAB1_TEXT_FORMAT.format(
        title=event["title"], summary=event["summary"]
    )
    assert item["text"] == f"{event['title']}：{event['summary']}"


def test_p13_tab3_text_is_the_verbatim_summary():
    source = load_source()
    event = next(e for e in source["events"] if e["event_id"] == INF_A)
    item = next(
        i
        for i in build_document(source)["tabs"]["impact_analysis"]["items"]
        if i["event_id"] == INF_A
    )
    assert item["text"] == event["summary"]


def test_p14_source_text_is_not_rewritten():
    """Punctuation and wording in the source must survive untouched."""
    source = with_source(
        lambda s: s["events"][1].update(
            {
                "title": "标题，含标点；以及空格",
                "summary": "摘要（含括号）与 English words 混排，不应被改写。",
            }
        )
    )
    event = next(e for e in source["events"] if e["event_id"] == FACT)
    item = build_document(source)["tabs"]["highlights"]["items"][0]
    assert item["text"].endswith(event["summary"])
    assert event["title"] in item["text"]


def test_p15_pipeline_introduces_no_extra_wording():
    source = load_source()
    document = build_document(source)
    facts = {e["event_id"]: e for e in source["events"]}
    for item in document["tabs"]["highlights"]["items"]:
        event = facts[item["event_id"]]
        assert item["text"] == f"{event['title']}：{event['summary']}"
    inferences = {e["event_id"]: e for e in source["events"]}
    for item in document["tabs"]["impact_analysis"]["items"]:
        assert item["text"] == inferences[item["event_id"]]["summary"]


# --------------------------------------------------------------------------
# R2 — source and confidence transport
# --------------------------------------------------------------------------


def test_p16_primary_source_is_sources_zero_and_full_list_is_kept():
    source = load_source()
    event = next(e for e in source["events"] if e["event_id"] == FACT)
    assert len(event["sources"]) == 2
    document = build_document(source)
    item = document["tabs"]["highlights"]["items"][0]
    assert item["source"] == event["sources"][0]
    kept = next(e for e in document["events"] if e["event_id"] == FACT)
    assert len(kept["sources"]) == 2


def test_p17_confidence_is_copied_verbatim():
    source = load_source()
    events = {e["event_id"]: e for e in source["events"]}
    document = build_document(source)
    for tab in ("highlights", "impact_analysis", "follow_up"):
        for item in document["tabs"][tab]["items"]:
            assert item["confidence"] == events[item["event_id"]]["confidence"]


def test_p18_pipeline_makes_no_verification_claim():
    import daily_briefing.pipeline as pipeline

    source_text = inspect.getsource(pipeline)
    # the module must not assert that it verified anything
    assert "已验证" not in source_text
    assert "验证通过" not in source_text


def test_p19_fallback_annotation_is_still_rendered_by_existing_rules():
    from daily_briefing.render import render

    html = render(build_document(load_source()))
    assert "fallback from P0 mock-primary-feed timeout" in html


# --------------------------------------------------------------------------
# R1 — follow-up discipline
# --------------------------------------------------------------------------


def test_p20_action_is_required_and_never_derived():
    document = with_source(lambda s: s["follow_up_plan"][0].pop("action"))
    with pytest.raises(ContractError, match="action is required"):
        build_document(document)


def test_p20b_action_does_not_fall_back_to_verification_criteria():
    """Dropping action must fail even though the event has criteria."""
    source = load_source()
    event = next(e for e in source["events"] if e["event_id"] == OPEN_HYP)
    assert event.get("verification_criteria")
    source["follow_up_plan"][0].pop("action")
    with pytest.raises(ContractError, match="action is required"):
        build_document(source)


def test_p21_next_check_is_required_and_never_generated():
    document = with_source(lambda s: s["follow_up_plan"][0].pop("next_check"))
    with pytest.raises(ContractError, match="next_check is required"):
        build_document(document)


def test_p22_tab5_text_comes_from_action_only():
    source = load_source()
    item = build_document(source)["tabs"]["follow_up"]["items"][0]
    assert item["action"] == source["follow_up_plan"][0]["action"]
    event = next(e for e in source["events"] if e["event_id"] == OPEN_HYP)
    assert event["verification_criteria"] not in item["action"]


def test_p23_verification_criteria_stays_on_the_event():
    source = load_source()
    document = build_document(source)
    kept = next(e for e in document["events"] if e["event_id"] == OPEN_HYP)
    assert kept["verification_criteria"]
    html_text = json.dumps(document["tabs"]["follow_up"]["items"], ensure_ascii=False)
    assert "verification_criteria" not in html_text
    assert kept["verification_criteria"] not in html_text


# --------------------------------------------------------------------------
# R6 — missing market data
# --------------------------------------------------------------------------


def test_p24_absent_market_data_with_a_real_reason():
    source = with_source(
        lambda s: s.update(
            {"market_data": {"items": [], "unavailable_reason": "交易所当日休市，无行情数据。"}}
        )
    )
    item = build_document(source)["tabs"]["market_snapshot"]["items"][0]
    assert item["availability"] == "unavailable"
    assert item["unavailable_reason"] == "交易所当日休市，无行情数据。"


def test_p25_absent_market_data_without_a_reason_is_neutral():
    source = with_source(lambda s: s.update({"market_data": {"items": []}}))
    item = build_document(source)["tabs"]["market_snapshot"]["items"][0]
    assert item["unavailable_reason"] == NEUTRAL_MARKET_MISSING_REASON
    # must not invent a provider failure
    for forbidden in ("P0", "P1", "P2", "P3", "westock", "finmind", "无数据"):
        assert forbidden not in item["unavailable_reason"]


def test_p26_items_present_with_a_reason_is_rejected():
    document = with_source(
        lambda s: s["market_data"].update({"unavailable_reason": "不应存在"})
    )
    with pytest.raises(ContractError, match="must be null"):
        build_document(document)


def test_p27_empty_reason_string_is_rejected():
    document = with_source(
        lambda s: s.update({"market_data": {"items": [], "unavailable_reason": ""}})
    )
    with pytest.raises(ContractError, match="unavailable_reason"):
        build_document(document)


def test_p27b_missing_market_data_key_uses_the_neutral_wording():
    source = load_source()
    source.pop("market_data")
    item = build_document(source)["tabs"]["market_snapshot"]["items"][0]
    assert item["unavailable_reason"] == NEUTRAL_MARKET_MISSING_REASON


def test_p27c_market_items_are_mapped_verbatim():
    source = load_source()
    entry = source["market_data"]["items"][0]
    item = build_document(source)["tabs"]["market_snapshot"]["items"][0]
    assert item["text"] == entry["text"]
    assert item["source"] == entry["source"]
    assert item["confidence"] == entry["confidence"]
    assert "event_id" not in item


# --------------------------------------------------------------------------
# Knowledge Bite discipline
# --------------------------------------------------------------------------


def test_p28_missing_knowledge_bites_is_rejected():
    document = with_source(lambda s: s.pop("knowledge_bites"))
    with pytest.raises(ContractError, match="knowledge_bites must be a non-empty list"):
        build_document(document)


def test_p29_empty_knowledge_bites_is_rejected():
    document = with_source(lambda s: s.update({"knowledge_bites": []}))
    with pytest.raises(ContractError, match="knowledge_bites must be a non-empty list"):
        build_document(document)


@pytest.mark.parametrize("field", ["cognitive_unit", "why_it_matters"])
def test_p29b_knowledge_bite_fields_are_required(field):
    document = with_source(lambda s: s["knowledge_bites"][0].pop(field))
    with pytest.raises(ContractError, match=field):
        build_document(document)


def test_p30_knowledge_bites_are_not_generated_from_events():
    """R4/X1: no event summary may leak into Tab 4 when bites are missing."""
    source = with_source(lambda s: s.pop("knowledge_bites"))
    with pytest.raises(ContractError):
        build_document(source)


def test_p30b_knowledge_bite_event_ids_must_exist():
    document = with_source(
        lambda s: s["knowledge_bites"][0].update({"event_ids": ["evt-20261020-nope"]})
    )
    with pytest.raises(ContractError, match="unknown event"):
        build_document(document)


# --------------------------------------------------------------------------
# R5 — purity and CLI
# --------------------------------------------------------------------------


def test_p31_build_document_does_not_mutate_its_input():
    source = load_source()
    snapshot = copy.deepcopy(source)
    build_document(source)
    assert source == snapshot


def test_p32_build_document_output_passes_the_existing_contract():
    from daily_briefing.schema import validate

    document = build_document(load_source())
    assert validate(document) is document


def test_p33_daily_briefing_main_module_is_untouched():
    original = (
        REPO_ROOT / "src" / "daily_briefing" / "__main__.py"
    ).read_text(encoding="utf-8")
    assert "daily_briefing.pipeline" not in original
    assert "--no-word-limit" not in original


def test_p34_build_document_performs_no_io(tmp_path):
    before = set(p.name for p in tmp_path.iterdir())
    build_document(load_source())
    assert set(p.name for p in tmp_path.iterdir()) == before


def test_p35_cli_end_to_end(tmp_path):
    src = tmp_path / "source.json"
    src.write_text(
        json.dumps(load_source(), ensure_ascii=False), encoding="utf-8"
    )
    out = tmp_path / "report.html"
    code = main(["--input", str(src), "--out", str(out)])
    assert code == 0
    html = out.read_text(encoding="utf-8")
    assert html.count('role="tabpanel"') == 5
    assert "Tab 5: 哪些事需要持续跟踪？" in html


def test_p36_cli_rejects_a_contract_violation(tmp_path):
    src = tmp_path / "bad.json"
    src.write_text(json.dumps({"meta": {}}), encoding="utf-8")
    out = tmp_path / "report.html"
    assert main(["--input", str(src), "--out", str(out)]) == 4
    assert not out.exists()


def test_p37_cli_missing_input_returns_2(tmp_path):
    assert main(["--input", str(tmp_path / "nope.json")]) == 2


def test_p37b_cli_does_not_write_when_the_word_gate_fails(tmp_path):
    """R5: the 500-word gate is never bypassed and no artefact is left."""
    source = load_source()
    source["knowledge_bites"][0]["cognitive_unit"] = "测" * 501
    src = tmp_path / "over.json"
    src.write_text(json.dumps(source, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "over.html"
    code = main(["--input", str(src), "--out", str(out)])
    assert code == 3
    assert not out.exists()


def test_p37c_module_runs_as_a_script(tmp_path):
    """python -m daily_briefing.pipeline must really invoke main()."""
    src = tmp_path / "source.json"
    src.write_text(json.dumps(load_source(), ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "script.html"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "daily_briefing.pipeline",
            "--input",
            str(src),
            "--out",
            str(out),
        ],
        cwd=REPO_ROOT,
        env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert out.exists()


# --------------------------------------------------------------------------
# regression and end-to-end
# --------------------------------------------------------------------------


def test_p38_rendering_the_pipeline_output_yields_five_tabs():
    from daily_briefing.render import render

    html = render(build_document(load_source()))
    for heading in (
        "Tab 1: 今天发生了什么？",
        "Tab 2: 市场整体状态如何？",
        "Tab 3: 事件的影响链是什么？",
        "Tab 4: 今天学到了什么？",
        "Tab 5: 哪些事需要持续跟踪？",
    ):
        assert heading in html


def test_p39_mock_banner_is_still_rendered():
    from daily_briefing.render import render

    assert "MOCK DATA" in render(build_document(load_source()))


def test_p40_methodology_is_owned_by_the_input():
    source = load_source()
    document = build_document(source)
    assert document["methodology"] == source["methodology"]


def test_p41_real_mode_still_declares_that_evidence_is_unverified():
    from daily_briefing.render import render

    source = with_source(lambda s: s["meta"].update({"data_mode": "real"}))
    html = render(build_document(source))
    assert "NOT VERIFIED" in html


# --------------------------------------------------------------------------
# Round 2 corrections — orphan follow-up plans, missing meta fields
# --------------------------------------------------------------------------


def test_p42_plan_for_an_unknown_event_is_rejected():
    """Backward direction: an orphan plan must never be dropped silently."""
    source = with_source(
        lambda s: s["follow_up_plan"].append(
            {
                "event_id": "evt-20261020-does-not-exist",
                "action": "孤立计划",
                "next_check": "2026-10-30",
            }
        )
    )
    with pytest.raises(ContractError, match="unknown event"):
        build_document(source)


def test_p43_plan_for_a_non_open_event_is_rejected():
    """Only status=open events may appear in the Follow-up Tracker."""
    source = with_source(
        lambda s: s["follow_up_plan"].append(
            {
                "event_id": ACTIVE_HYP,
                "action": "针对 active 事件的计划",
                "next_check": "2026-10-30",
            }
        )
    )
    with pytest.raises(ContractError, match="only events with status 'open'"):
        build_document(source)


def test_p43b_plan_for_a_fact_event_is_rejected():
    source = with_source(
        lambda s: s["follow_up_plan"].append(
            {"event_id": FACT, "action": "针对事实事件的计划", "next_check": "2026-10-30"}
        )
    )
    with pytest.raises(ContractError, match="only events with status 'open'"):
        build_document(source)


def test_p44_valid_plan_is_still_accepted_and_order_is_unchanged():
    source = load_source()
    document = build_document(source)
    items = document["tabs"]["follow_up"]["items"]
    assert [i["event_id"] for i in items] == [OPEN_HYP]
    assert items[0]["action"] == source["follow_up_plan"][0]["action"]
    assert items[0]["next_check"] == source["follow_up_plan"][0]["next_check"]


def test_p44b_multiple_open_events_keep_event_order():
    source = with_source(
        lambda s: (
            s["events"].append(
                {
                    "event_id": "evt-20261020-second-open",
                    "title": "第二个待验证假设",
                    "summary": "【演示数据】第二条已纳入跟踪的假设。",
                    "assertion_type": "hypothesis",
                    "status": "open",
                    "occurred_at": "2026-10-20",
                    "collected_at": "2026-10-20",
                    "data_date": "2026-10-20",
                    "verification_criteria": "验证标准。",
                    "sources": [
                        {
                            "name": "mock-research-note",
                            "provider_tier": "P2",
                            "locator": "mock://test/second-open",
                        }
                    ],
                    "confidence": "LOW",
                    "estimated": False,
                }
            ),
            s["follow_up_plan"].append(
                {
                    "event_id": "evt-20261020-second-open",
                    "action": "第二条跟踪动作",
                    "next_check": "2026-10-25",
                }
            ),
        )
    )
    items = build_document(source)["tabs"]["follow_up"]["items"]
    assert [i["event_id"] for i in items] == [OPEN_HYP, "evt-20261020-second-open"]


@pytest.mark.parametrize("field", ["run_date", "data_date", "data_mode"])
def test_p45_missing_meta_field_raises_contract_error(field):
    """No unhandled KeyError may escape build_document()."""
    source = with_source(lambda s: s["meta"].pop(field))
    with pytest.raises(ContractError, match=field):
        build_document(source)


@pytest.mark.parametrize("field", ["run_date", "data_date", "data_mode"])
def test_p45b_missing_meta_field_is_not_a_key_error(field):
    source = with_source(lambda s: s["meta"].pop(field))
    try:
        build_document(source)
    except ContractError:
        pass
    except KeyError as exc:  # pragma: no cover - the bug this test guards
        pytest.fail(f"unhandled KeyError for meta.{field}: {exc}")


def test_p46_invalid_meta_value_still_uses_the_existing_schema_rule():
    """Values are validated by the existing contract, not by duplicated rules.

    The assertion checks the *wording of the existing report contract*, which
    proves the pipeline reuses that rule instead of copying it.
    """
    source = with_source(lambda s: s["meta"].update({"data_mode": "demo"}))
    with pytest.raises(ContractError) as excinfo:
        build_document(source)
    assert "must be 'mock' or 'real'" in str(excinfo.value)


def test_p47_cli_returns_4_and_writes_nothing_for_missing_meta(tmp_path):
    source = with_source(lambda s: s["meta"].pop("run_date"))
    src = tmp_path / "no-meta.json"
    src.write_text(json.dumps(source, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "report.html"
    assert main(["--input", str(src), "--out", str(out)]) == 4
    assert not out.exists()


def test_p48_cli_subprocess_reports_exit_4_for_missing_meta(tmp_path):
    source = with_source(lambda s: s["meta"].pop("data_mode"))
    src = tmp_path / "no-mode.json"
    src.write_text(json.dumps(source, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "report.html"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "daily_briefing.pipeline",
            "--input",
            str(src),
            "--out",
            str(out),
        ],
        cwd=REPO_ROOT,
        env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 4, result.stderr
    assert not out.exists()
    assert "run_date" in result.stderr or "data_mode" in result.stderr
