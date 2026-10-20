"""Event Data Contract tests — Slice 2 (shared contract layer).

Covers the frozen rules of ``SLICE2_PROPOSAL_V2.md``:

  EV-1..EV-17   event-level rules
  DV-1..DV-10   document-level rules (Tab <-> event cross validation)
  R-A / R-B     verification criteria requirements
  R-C / R-D     the two-way tracking rule between events and the Follow-up tab

The helpers below are local to this module on purpose: ``tests/conftest.py``
must not be modified by this Slice.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

from contracts.evidence import CONFIDENCE_VALUES, ContractError
from contracts.event import (
    ASSERTION_TYPES,
    EVENT_ID_PATTERN,
    EVENT_STATUSES,
    validate_event,
    validate_events,
)
from daily_briefing.render import render
from daily_briefing.schema import TAB_ORDER, validate

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "event_sample.json"
SLICE1_FIXTURE = Path(__file__).parent / "fixtures" / "daily_sample.json"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def load_event_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def load_slice1_fixture() -> dict:
    return json.loads(SLICE1_FIXTURE.read_text(encoding="utf-8"))


def make_event(**overrides) -> dict:
    """A minimal valid fact event."""
    event = {
        "event_id": "evt-20261020-demo-01",
        "title": "示例事实",
        "summary": "【演示数据】示例事实摘要。",
        "assertion_type": "fact",
        "status": "active",
        "occurred_at": "2026-10-20",
        "collected_at": "2026-10-20",
        "data_date": "2026-10-20",
        "themes": ["示例主题"],
        "sources": [
            {
                "name": "mock-provider",
                "provider_tier": "P0",
                "locator": "mock://unit-test/evt",
            }
        ],
        "confidence": "HIGH",
        "estimated": False,
    }
    event.update(overrides)
    return event


def make_document(with_events: bool = True) -> dict:
    """A minimal but valid daily briefing document, optionally with events."""
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
                        "text": "示例要点",
                        "source": {
                            "name": "mock-provider",
                            "provider_tier": "P0",
                            "locator": "mock://unit-test/highlight",
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
    if with_events:
        document["events"] = [make_event()]
        document["tabs"]["highlights"]["items"][0]["event_id"] = "evt-20261020-demo-01"
    return document


def _with_event(mutate) -> dict:
    """Return the fixture document with one event mutated."""
    document = load_event_fixture()
    mutate(document)
    return document


def _event_by_id(document: dict, event_id: str) -> dict:
    for event in document["events"]:
        if event["event_id"] == event_id:
            return event
    raise AssertionError(f"event not found: {event_id}")


# --------------------------------------------------------------------------
# T-01 .. T-06 — structure, identifier, stability
# --------------------------------------------------------------------------


def test_t01_valid_fixture_validates():
    validate(load_event_fixture())


def test_t02_event_id_format_is_enforced():
    with pytest.raises(ContractError, match="event_id"):
        validate_event(make_event(event_id="event-20261020-demo"), "e")


def test_t03_event_id_date_must_be_a_real_calendar_day():
    with pytest.raises(ContractError, match="calendar date"):
        validate_event(make_event(event_id="evt-20260230-demo"), "e")


def test_t04_duplicate_event_id_is_rejected():
    document = make_document()
    document["events"].append(make_event())
    with pytest.raises(ContractError, match="duplicates"):
        validate(document)


def test_t05_identifier_is_stable_under_content_changes():
    """R3: the identifier must not drift when title or dates change."""
    base = make_event()
    changed = make_event(
        title="完全不同的标题",
        occurred_at="2026-11-01",
        collected_at="2026-11-02",
        data_date="2026-11-02",
    )
    assert base["event_id"] == changed["event_id"]
    validate_event(changed, "e")


def test_t06_contract_offers_no_identifier_generation_helper():
    """R3: no helper may derive an id from a title or a report run date."""
    import contracts.event as event_module

    forbidden = ("make_event_id", "generate_event_id", "build_event_id", "new_event_id")
    for name in forbidden:
        assert not hasattr(event_module, name), f"unexpected helper: {name}"


def test_t06b_event_id_pattern_is_ascii_only():
    assert re.match(EVENT_ID_PATTERN, "evt-20261020-ai-chip-01")
    with pytest.raises(ContractError):
        validate_event(make_event(event_id="evt-20261020-中文slug"), "e")


# --------------------------------------------------------------------------
# T-07 .. T-15 — the three assertion types
# --------------------------------------------------------------------------


def test_t07_fact_must_not_carry_derived_from():
    with pytest.raises(ContractError, match="derived_from"):
        validate_event(
            make_event(derived_from=["evt-20261020-other-01"]), "e"
        )


def test_t08_inference_requires_derived_from():
    with pytest.raises(ContractError, match="derived_from"):
        validate_event(make_event(assertion_type="inference"), "e")


def test_t09_hypothesis_requires_verification_criteria():
    with pytest.raises(ContractError, match="verification_criteria"):
        validate_event(make_event(assertion_type="hypothesis"), "e")


def test_t10_open_status_requires_verification_criteria():
    with pytest.raises(ContractError, match="verification_criteria"):
        validate_event(make_event(status="open"), "e")


def test_t11_status_verified_is_not_allowed():
    """The Evidence Layer does not exist yet, so no such status may exist."""
    assert "verified" not in EVENT_STATUSES
    with pytest.raises(ContractError, match="status"):
        validate_event(make_event(status="verified"), "e")


def test_t12_derived_from_must_reference_a_known_event():
    document = _with_event(
        lambda d: _event_by_id(d, "evt-20261020-chip-impact").update(
            {"derived_from": ["evt-20261020-does-not-exist"]}
        )
    )
    with pytest.raises(ContractError, match="unknown event"):
        validate(document)


def test_t13_derived_from_must_be_acyclic():
    cycle = [
        make_event(
            event_id="evt-20261020-cycle-a",
            assertion_type="inference",
            derived_from=["evt-20261020-cycle-b"],
        ),
        make_event(
            event_id="evt-20261020-cycle-b",
            assertion_type="inference",
            derived_from=["evt-20261020-cycle-a"],
        ),
    ]
    with pytest.raises(ContractError, match="cycle"):
        validate_events(cycle, "events")


def test_t14_inference_that_cannot_reach_any_fact_is_rejected():
    """EV-12: an inference must reach a fact in one hop or several.

    The only acyclic terminal that is not a fact is a hypothesis, so an
    inference whose chain ends at a hypothesis cannot be traced to a fact.
    """
    document = _with_event(
        lambda d: (
            d["events"].append(
                make_event(
                    event_id="evt-20261020-terminal-hypothesis",
                    assertion_type="hypothesis",
                    verification_criteria="等待验证的标准说明。",
                )
            ),
            _event_by_id(d, "evt-20261020-chip-impact").update(
                {"derived_from": ["evt-20261020-terminal-hypothesis"]}
            ),
        )
    )
    with pytest.raises(ContractError, match="traced back to any fact"):
        validate(document)


def test_t15_inference_chain_of_several_hops_is_accepted():
    """EV-12 multi-hop: inference -> inference -> fact is valid."""
    document = load_event_fixture()
    validate(document)  # the fixture contains exactly this chain
    chain = _event_by_id(document, "evt-20261020-margin-chain")
    assert chain["assertion_type"] == "inference"
    assert chain["derived_from"] == ["evt-20261020-chip-impact"]


def test_t15b_inference_reaching_fact_in_one_hop_is_accepted():
    document = _with_event(
        lambda d: _event_by_id(d, "evt-20261020-chip-v2").update(
            {"derived_from": []}
        )
    )
    validate(document)


# --------------------------------------------------------------------------
# T-16 .. T-19 — the two-way tracking rule (R2)
# --------------------------------------------------------------------------


def test_t16_ordinary_hypothesis_may_have_no_follow_up():
    """status=active hypothesis without any Tab 5 reference is allowed."""
    document = load_event_fixture()
    hypothesis = _event_by_id(document, "evt-20261020-delivery-hypothesis")
    assert hypothesis["status"] == "active"
    referenced = [
        item.get("event_id")
        for item in document["tabs"]["follow_up"]["items"]
    ]
    assert hypothesis["event_id"] not in referenced
    validate(document)


def test_t17_open_hypothesis_without_follow_up_is_rejected():
    """R-D: an event formally tracked must be picked up by Tab 5."""
    document = _with_event(
        lambda d: d["tabs"]["follow_up"]["items"].clear()
    )
    with pytest.raises(ContractError, match="no Follow-up Tracker item"):
        validate(document)


def test_t18_follow_up_may_only_link_to_open_events():
    """R-C: the backward half of the same rule."""
    document = _with_event(
        lambda d: d["tabs"]["follow_up"]["items"][0].update(
            {"event_id": "evt-20261020-delivery-hypothesis"}
        )
    )
    with pytest.raises(ContractError, match="status is 'active'"):
        validate(document)


def test_t19_open_fact_linked_by_follow_up_is_accepted():
    document = _with_event(
        lambda d: (
            _event_by_id(d, "evt-20261020-delivery-hypothesis").update(
                {"status": "open"}
            ),
            # the previously tracked hypothesis steps out of the tracking scope
            _event_by_id(d, "evt-20261020-dedup-hypothesis").update(
                {"status": "active"}
            ),
            d["tabs"]["follow_up"]["items"][0].update(
                {"event_id": "evt-20261020-delivery-hypothesis"}
            ),
        )
    )
    validate(document)


# --------------------------------------------------------------------------
# T-20 .. T-24 — lifecycle and supersedes direction (R5)
# --------------------------------------------------------------------------


def test_t20_supersedes_points_at_the_older_record():
    """R5: the current record points at the record it supersedes."""
    document = load_event_fixture()
    new = _event_by_id(document, "evt-20261020-chip-v2")
    old = _event_by_id(document, "evt-20261020-chip-launch")
    # the new record points at the old one ...
    assert new["supersedes"] == old["event_id"]
    # ... and the old record does not point back
    assert old.get("supersedes") is None


def test_t21_supersedes_must_reference_a_known_event():
    document = _with_event(
        lambda d: _event_by_id(d, "evt-20261020-chip-v2").update(
            {"supersedes": "evt-20261020-nope"}
        )
    )
    with pytest.raises(ContractError, match="unknown event"):
        validate(document)


def test_t22_supersedes_must_not_self_reference():
    with pytest.raises(ContractError, match="must not point at the event itself"):
        validate_event(
            make_event(supersedes="evt-20261020-demo-01"), "e"
        )


def test_t23_supersedes_relation_must_be_acyclic():
    document = _with_event(
        lambda d: (
            _event_by_id(d, "evt-20261020-chip-launch").update(
                {"supersedes": "evt-20261020-chip-v2"}
            ),
        )
    )
    with pytest.raises(ContractError, match="cycle"):
        validate(document)


def test_t24_contract_offers_no_lifecycle_transition_engine():
    import contracts.event as event_module

    for name in ("transition", "advance_status", "apply_transition", "state_machine"):
        assert not hasattr(event_module, name), f"unexpected helper: {name}"


# --------------------------------------------------------------------------
# T-25 .. T-30 — Tab references (R6)
# --------------------------------------------------------------------------


def test_t25_tab1_must_link_to_a_fact():
    document = _with_event(
        lambda d: d["tabs"]["highlights"]["items"][0].update(
            {"event_id": "evt-20261020-chip-impact"}
        )
    )
    with pytest.raises(ContractError, match="must link to a fact"):
        validate(document)


def test_t26_tab3_must_link_to_an_inference():
    document = _with_event(
        lambda d: (
            d["tabs"]["impact_analysis"]["items"][0].update(
                {"event_id": "evt-20261020-chip-v2"}
            ),
        )
    )
    with pytest.raises(ContractError, match="must link to an inference"):
        validate(document)


def test_t27_tab2_must_not_carry_event_references():
    document = _with_event(
        lambda d: d["tabs"]["market_snapshot"]["items"].append(
            {
                "availability": "available",
                "text": "市场状态",
                "event_id": "evt-20261020-chip-v2",
                "source": {
                    "name": "mock-provider",
                    "provider_tier": "P0",
                    "locator": "mock://unit-test/market",
                },
                "confidence": "HIGH",
                "estimated": False,
                "unavailable_reason": None,
            }
        )
    )
    with pytest.raises(ContractError, match="market snapshot is a state"):
        validate(document)


def test_t28_tab4_may_link_to_several_events():
    document = load_event_fixture()
    bite = document["tabs"]["knowledge_bite"]["items"][0]
    assert len(bite["event_ids"]) == 2
    validate(document)


def test_t29_tab4_must_not_use_the_singular_event_id():
    document = _with_event(
        lambda d: (
            d["tabs"]["knowledge_bite"]["items"][0].pop("event_ids"),
            d["tabs"]["knowledge_bite"]["items"][0].update(
                {"event_id": "evt-20261020-chip-v2"}
            ),
        )
    )
    with pytest.raises(ContractError, match="use 'event_ids' \\(plural\\)"):
        validate(document)


def test_t30_unknown_event_reference_is_rejected():
    document = _with_event(
        lambda d: d["tabs"]["highlights"]["items"][0].update(
            {"event_id": "evt-20261020-missing"}
        )
    )
    with pytest.raises(ContractError, match="unknown event"):
        validate(document)


def test_t30b_single_event_tabs_reject_the_plural_form():
    document = _with_event(
        lambda d: d["tabs"]["highlights"]["items"][0].update(
            {"event_ids": ["evt-20261020-demo-01"]}
        )
    )
    with pytest.raises(ContractError, match="use 'event_id' \\(singular\\)"):
        validate(document)


# --------------------------------------------------------------------------
# T-31 .. T-36 — shared layer, compatibility, boundaries
# --------------------------------------------------------------------------


def test_t31_confidence_scale_has_a_single_definition():
    import daily_briefing.schema as schema
    import contracts.evidence as evidence

    assert schema.CONFIDENCE_VALUES is evidence.CONFIDENCE_VALUES
    assert schema.CONFIDENCE_BADGE is evidence.CONFIDENCE_BADGE
    assert schema.ContractError is evidence.ContractError
    assert schema.PROVIDER_TIERS is evidence.PROVIDER_TIERS
    assert schema.ROUTING_OUTCOMES is evidence.ROUTING_OUTCOMES
    assert schema.get_fallback_chain is evidence.get_fallback_chain


def test_t32_daily_briefing_schema_public_interface_is_preserved():
    import daily_briefing.schema as schema

    for name in schema.__all__:
        assert hasattr(schema, name), f"missing public name: {name}"


def test_t33_contracts_package_never_imports_daily_briefing():
    import ast
    from pathlib import Path

    contracts_dir = Path(__file__).resolve().parents[1] / "src" / "contracts"
    for path in sorted(contracts_dir.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("daily_briefing"), path
            elif isinstance(node, ast.ImportFrom):
                base = (node.module or "")
                assert not base.startswith("daily_briefing"), path


def test_t34_slice1_fixture_still_validates_and_renders():
    document = load_slice1_fixture()
    validate(document)
    html = render(document)
    assert "Daily Briefing — 2026-10-20" in html


def test_t35_rendering_is_deterministic_and_free_of_event_markup():
    document = load_slice1_fixture()
    first = render(document)
    second = render(copy.deepcopy(document))
    assert first == second
    # Slice 2 adds no rendering surface: no event markup may leak out.
    assert "event_id" not in first
    assert "evt-" not in first


def test_t36_document_without_events_triggers_no_event_rules():
    """A document with neither an events block nor event references is fine."""
    document = load_slice1_fixture()
    assert "events" not in document
    validate(document)


def test_t36b_a_reference_without_an_events_block_is_rejected():
    """A Tab may not point at an event that is not declared.

    The cross-validation must not be skipped just because the events block
    is absent — that would be a reference-integrity bypass.
    """
    document = load_slice1_fixture()
    document["tabs"]["highlights"]["items"][0]["event_id"] = "evt-20261020-whatever"
    with pytest.raises(ContractError, match="unknown event"):
        validate(document)


def test_t37_events_block_must_be_a_list():
    document = make_document()
    document["events"] = {"not": "a list"}
    with pytest.raises(ContractError, match="events must be a list"):
        validate(document)


def test_t38_event_confidence_uses_the_shared_scale():
    assert set(CONFIDENCE_VALUES) == {"HIGH", "MEDIUM", "LOW-MEDIUM", "LOW"}
    with pytest.raises(ContractError, match="confidence"):
        validate_event(make_event(confidence="VERY-HIGH"), "e")


def test_t39_event_requires_evidence_support():
    with pytest.raises(ContractError, match="sources must be a non-empty list"):
        validate_event(make_event(sources=[]), "e")


def test_t40_assertion_types_are_exactly_three():
    assert ASSERTION_TYPES == ["fact", "inference", "hypothesis"]


def test_t41_event_requires_its_core_fields():
    for field in ("title", "summary", "occurred_at", "collected_at", "data_date"):
        event = make_event()
        del event[field]
        with pytest.raises(ContractError):
            validate_event(event, "e")


def test_t42_five_tabs_are_unchanged():
    assert TAB_ORDER == [
        "highlights",
        "market_snapshot",
        "impact_analysis",
        "knowledge_bite",
        "follow_up",
    ]


# --------------------------------------------------------------------------
# T-43 .. T-50 — reference integrity must not be bypassed by an empty or
# absent events block. Every event-bearing tab path is exercised.
# --------------------------------------------------------------------------

#: The tabs that may carry an event reference, with the field they use.
#: Tab 2 (Market Snapshot) is excluded on purpose: a market state is not an
#: event, and carrying a reference there is rejected by shape (T-27).
EVENT_REFERENCE_TABS = [
    ("highlights", "event_id"),
    ("impact_analysis", "event_id"),
    ("knowledge_bite", "event_ids"),
    ("follow_up", "event_id"),
]


def _item_with_reference(tab_key: str, ref_field: str, ref_value) -> dict:
    """Build a schema-valid item for ``tab_key`` carrying an event reference."""
    item = {
        "availability": "available",
        "source": {
            "name": "mock-provider",
            "provider_tier": "P0",
            "locator": f"mock://unit-test/{tab_key}",
        },
        "confidence": "HIGH",
        "estimated": False,
        "unavailable_reason": None,
    }
    if tab_key == "knowledge_bite":
        item["cognitive_unit"] = "示例认知单元"
        item["why_it_matters"] = "示例意义说明"
    elif tab_key == "follow_up":
        item["action"] = "示例动作"
        item["next_check"] = "2026-11-03"
    else:
        item["text"] = "示例文本内容"
    if ref_field == "event_ids":
        # the plural form always carries a list
        item[ref_field] = ref_value if isinstance(ref_value, list) else [ref_value]
    else:
        item[ref_field] = ref_value
    return item


@pytest.mark.parametrize("tab_key,ref_field", EVENT_REFERENCE_TABS)
def test_t43_empty_events_block_does_not_bypass_reference_check(tab_key, ref_field):
    """events=[] plus a reference must fail, not slip through."""
    document = make_document(with_events=False)
    document["events"] = []
    document["tabs"][tab_key]["items"] = [
        _item_with_reference(tab_key, ref_field, "evt-20261020-missing")
    ]
    with pytest.raises(ContractError, match="unknown event"):
        validate(document)


@pytest.mark.parametrize("tab_key,ref_field", EVENT_REFERENCE_TABS)
def test_t44_absent_events_block_does_not_bypass_reference_check(tab_key, ref_field):
    """No events key at all plus a reference must fail too."""
    document = make_document(with_events=False)
    document["tabs"][tab_key]["items"] = [
        _item_with_reference(tab_key, ref_field, "evt-20261020-missing")
    ]
    with pytest.raises(ContractError, match="unknown event"):
        validate(document)


@pytest.mark.parametrize("tab_key,ref_field", EVENT_REFERENCE_TABS)
def test_t45_empty_events_block_without_references_is_allowed(tab_key, ref_field):
    """events=[] with no reference anywhere stays valid."""
    document = make_document(with_events=False)
    document["events"] = []
    document["tabs"][tab_key]["items"] = [
        _item_with_reference(tab_key, ref_field, "evt-20261020-missing")
    ]
    # drop the reference again — the tab itself is fine
    document["tabs"][tab_key]["items"][0].pop(ref_field)
    validate(document)


def test_t46_absent_events_block_without_references_keeps_slice1_behaviour():
    """The plain Slice 1 shape is untouched by this Slice."""
    document = make_document(with_events=False)
    validate(document)
    assert "events" not in document


def test_t47_tab2_reference_is_rejected_with_an_empty_events_block():
    """Tab 2 never links to events, whatever the events block holds."""
    document = make_document(with_events=False)
    document["events"] = []
    document["tabs"]["market_snapshot"]["items"] = [
        {
            "availability": "available",
            "text": "市场状态",
            "event_id": "evt-20261020-missing",
            "source": {
                "name": "mock-provider",
                "provider_tier": "P0",
                "locator": "mock://unit-test/market",
            },
            "confidence": "HIGH",
            "estimated": False,
            "unavailable_reason": None,
        }
    ]
    with pytest.raises(ContractError, match="market snapshot is a state"):
        validate(document)


def test_t48_non_empty_events_block_still_runs_every_check():
    """A populated events block keeps the full rule set active."""
    document = load_event_fixture()
    validate(document)
    # dangling reference is still caught
    document["tabs"]["highlights"]["items"][0]["event_id"] = "evt-20261020-nope"
    with pytest.raises(ContractError, match="unknown event"):
        validate(document)


def test_t49_two_way_tracking_constraint_is_unaffected():
    """R-C / R-D still hold with a populated events block."""
    document = _with_event(lambda d: d["tabs"]["follow_up"]["items"].clear())
    with pytest.raises(ContractError, match="no Follow-up Tracker item"):
        validate(document)


def test_t50_reference_to_an_existing_event_in_a_populated_block_passes():
    document = load_event_fixture()
    validate(document)
