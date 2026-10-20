"""Contract validation tests (docs/evidence/EVIDENCE_LAYER.md, REPORT_DESIGN.md)."""

from __future__ import annotations

import pytest
from conftest import load_fixture, make_document

from daily_briefing.schema import ContractError, validate


def test_s01_valid_fixture_passes():
    validate(load_fixture())


def test_s02_missing_run_date_fails():
    doc = load_fixture()
    del doc["meta"]["run_date"]
    with pytest.raises(ContractError, match="run_date"):
        validate(doc)


def test_s03_missing_tab_fails():
    doc = load_fixture()
    del doc["tabs"]["knowledge_bite"]
    with pytest.raises(ContractError, match="knowledge_bite"):
        validate(doc)


def test_s04_knowledge_bite_requires_cognitive_unit():
    doc = load_fixture()
    del doc["tabs"]["knowledge_bite"]["items"][0]["cognitive_unit"]
    with pytest.raises(ContractError, match="cognitive_unit"):
        validate(doc)


def test_s04b_knowledge_bite_requires_why_it_matters():
    doc = load_fixture()
    del doc["tabs"]["knowledge_bite"]["items"][0]["why_it_matters"]
    with pytest.raises(ContractError, match="why_it_matters"):
        validate(doc)


@pytest.mark.parametrize("field", ["action", "next_check"])
def test_s05_follow_up_requires_actionable_fields(field):
    doc = load_fixture()
    del doc["tabs"]["follow_up"]["items"][0][field]
    with pytest.raises(ContractError, match=field):
        validate(doc)


def test_s06_confidence_must_be_in_enum():
    doc = load_fixture()
    doc["tabs"]["highlights"]["items"][0]["confidence"] = "VERY-HIGH"
    with pytest.raises(ContractError, match="confidence"):
        validate(doc)


def test_s07_declared_tier_must_match_successful_attempt():
    doc = load_fixture()
    item = doc["tabs"]["highlights"]["items"][1]
    item["source"]["provider_tier"] = "P0"  # but routing says P1 succeeded
    with pytest.raises(ContractError, match="must match"):
        validate(doc)


def test_s08_available_item_requires_source():
    doc = load_fixture()
    doc["tabs"]["highlights"]["items"][0]["source"] = None
    with pytest.raises(ContractError, match="source"):
        validate(doc)


def test_s08b_source_requires_locator():
    doc = load_fixture()
    del doc["tabs"]["highlights"]["items"][0]["source"]["locator"]
    with pytest.raises(ContractError, match="locator"):
        validate(doc)


def test_s09_unavailable_requires_reason():
    doc = load_fixture()
    item = doc["tabs"]["market_snapshot"]["items"][1]
    item["unavailable_reason"] = ""
    with pytest.raises(ContractError, match="unavailable_reason"):
        validate(doc)


def test_s09b_unavailable_must_not_carry_confidence():
    doc = load_fixture()
    doc["tabs"]["market_snapshot"]["items"][1]["confidence"] = "HIGH"
    with pytest.raises(ContractError, match="confidence must be null"):
        validate(doc)


def test_s09c_unavailable_must_not_carry_source():
    doc = load_fixture()
    doc["tabs"]["market_snapshot"]["items"][1]["source"] = {
        "name": "x",
        "provider_tier": "P0",
        "locator": "mock://x",
    }
    with pytest.raises(ContractError, match="source must be null"):
        validate(doc)


@pytest.mark.parametrize("key", ["methods", "limitations"])
def test_s10_methodology_must_be_non_empty(key):
    doc = load_fixture()
    doc["methodology"][key] = []
    with pytest.raises(ContractError, match=key):
        validate(doc)


def test_s11_data_mode_is_mandatory_and_constrained():
    doc = load_fixture()
    del doc["meta"]["data_mode"]
    with pytest.raises(ContractError, match="data_mode"):
        validate(doc)

    doc = load_fixture()
    doc["meta"]["data_mode"] = "demo"
    with pytest.raises(ContractError, match="data_mode"):
        validate(doc)


def test_s12_tab_number_must_match_frozen_position():
    doc = load_fixture()
    doc["tabs"]["follow_up"]["tab_number"] = 4
    with pytest.raises(ContractError, match="tab_number"):
        validate(doc)


def test_s13_empty_tab_items_list_is_allowed_by_contract():
    doc = make_document()
    validate(doc)  # empty items pass contract; renderer shows 数据不可用
