"""Minimum Daily Pipeline — Daily Briefing V2 (Slice 3).

Assembles a Daily Briefing input document from a **daily source document**, so
the frozen five-tab renderer can produce the report. This module only moves
structured data; it never writes analysis.

Frozen references:
  - docs/daily/product.md        five-tab definitions and responsibilities
  - docs/daily/decisions.md      D2 cognitive unit, D3 actionable follow-up, D4 run date
  - docs/core/IMPLEMENTATION_ROADMAP.md  Phase 4 content
  - SLICE3_REVISED_RULES.md      the approved rules R1-R6 implemented here

Design boundaries
-----------------
* **Structured transport only.** No text is rewritten, summarised or inferred.
  ``TAB1_TEXT_FORMAT`` is the single place where a title and a summary are
  joined; nothing else is composed.
* **No editorial judgement.** The input selects which events appear; this
  module never scores, ranks or filters them.
* **No fabrication.** Knowledge bites and follow-up plans must be supplied.
  Market data may be genuinely absent, in which case the fixed
  ``数据不可用`` wording is rendered with a neutral reason.
* **No evidence verification.** Confidence levels and source routing records
  are copied verbatim. Nothing here closes BACKLOG P0-003.

Dependency direction
--------------------
``daily_briefing.pipeline`` → ``contracts`` + ``daily_briefing.schema`` /
``daily_briefing.render``. The shared contract layer never imports this module.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from contracts.evidence import non_empty_str, require
from contracts.event import TRACKED_STATUS, validate_events
from daily_briefing.render import render
from daily_briefing.schema import (
    TAB_DEFS,
    ContractError,
    WordLimitExceeded,
    validate,
)

# --------------------------------------------------------------------------
# Frozen presentation rules
# --------------------------------------------------------------------------

#: R3 / X3 — how a fact event becomes a Tab 1 line. The only place where two
#: source fields are joined; the source strings themselves are never altered.
TAB1_TEXT_FORMAT: str = "{title}：{summary}"

#: R6 — neutral wording used when market data is absent and the input gave no
#: specific reason. It must never name a provider or claim a failure that was
#: not observed.
NEUTRAL_MARKET_MISSING_REASON: str = "本次输入未包含市场数据"

#: Why each mandatory meta field matters, used in the presence error message.
_META_FIELD_HINTS: Dict[str, str] = {
    "run_date": "run_date drives the output file name (decisions.md D4)",
    "data_date": "data_date is shown in the report header",
    "data_mode": "data_mode drives the mock/real disclosure banner",
}

_TAB1 = "highlights"
_TAB3 = "impact_analysis"


# --------------------------------------------------------------------------
# Selection (R4)
# --------------------------------------------------------------------------


def _select_events(
    index: Dict[str, Dict[str, Any]],
    ids: Any,
    assertion_type: str,
    path: str,
) -> List[Dict[str, Any]]:
    """Resolve an explicit id list into events, preserving input order.

    No scoring, ranking or filtering happens here: the input decides what is
    shown, this function only checks that every requested id exists, has the
    required assertion type, and is not repeated.
    """
    require(
        isinstance(ids, list), f"{path} must be a list of event ids",
    )
    seen: set = set()
    selected: List[Dict[str, Any]] = []
    for idx, event_id in enumerate(ids):
        require(
            non_empty_str(event_id),
            f"{path}[{idx}] must be a non-empty event id string",
        )
        require(
            event_id not in seen, f"{path}[{idx}] repeats event id {event_id!r}",
        )
        seen.add(event_id)
        require(
            event_id in index,
            f"{path}[{idx}] references an unknown event: {event_id!r}",
        )
        event = index[event_id]
        actual = event.get("assertion_type")
        require(
            actual == assertion_type,
            f"{path}[{idx}] selects {event_id!r} whose assertion_type is "
            f"{actual!r}; this tab requires {assertion_type!r}",
        )
        selected.append(event)
    return selected


# --------------------------------------------------------------------------
# Item construction
# --------------------------------------------------------------------------


def _event_item(event: Dict[str, Any], text: str, *, with_event_id: bool) -> Dict[str, Any]:
    """Build a Tab item from an event, carrying its evidence fields verbatim.

    ``sources[0]`` is the primary source *chosen by the input*; this module does
    not judge which source is most reliable and does not adjust confidence.
    The complete source list stays in the emitted ``events`` block.
    """
    sources = event["sources"]
    require(
        isinstance(sources, list) and len(sources) > 0,
        f"event {event['event_id']!r} has no sources; the event contract "
        f"requires at least one",
    )
    item: Dict[str, Any] = {
        "availability": "available",
        "text": text,
        "source": copy.deepcopy(sources[0]),
        "confidence": event["confidence"],
        "estimated": event.get("estimated", False),
        "unavailable_reason": None,
    }
    if with_event_id:
        item["event_id"] = event["event_id"]
    return item


def _market_items(market_data: Any) -> List[Dict[str, Any]]:
    """Map market data to Tab 2 items (R6).

    Market state is not an event, so Tab 2 carries no event reference at all.
    """
    if market_data is None:
        # R6: the key being absent is itself a genuine absence of market data.
        market_data = {}
    require(isinstance(market_data, dict), "market_data must be an object")
    items = market_data.get("items")
    reason = market_data.get("unavailable_reason")
    require(
        items is None or isinstance(items, list),
        "market_data.items must be a list when present",
    )

    if not items:
        # Genuinely absent. Use the input's real reason when supplied,
        # otherwise a neutral statement — never an invented provider failure.
        if reason is not None:
            require(
                non_empty_str(reason),
                "market_data.unavailable_reason must be a non-empty string "
                "when provided",
            )
        text = reason if non_empty_str(reason) else NEUTRAL_MARKET_MISSING_REASON
        return [
            {
                "availability": "unavailable",
                "text": None,
                "source": None,
                "confidence": None,
                "estimated": False,
                "unavailable_reason": text,
            }
        ]

    require(
        reason is None,
        "market_data.unavailable_reason must be null when market_data.items "
        "carries data",
    )
    mapped: List[Dict[str, Any]] = []
    for idx, entry in enumerate(items):
        path = f"market_data.items[{idx}]"
        require(isinstance(entry, dict), f"{path} must be an object")
        require(non_empty_str(entry.get("text")), f"{path}.text is required")
        mapped.append(
            {
                "availability": "available",
                "text": entry["text"],
                "source": copy.deepcopy(entry.get("source")),
                "confidence": entry.get("confidence"),
                "estimated": entry.get("estimated", False),
                "unavailable_reason": None,
            }
        )
    return mapped


def _knowledge_bite_items(knowledge_bites: Any) -> List[Dict[str, Any]]:
    """Map explicitly supplied knowledge bites to Tab 4 items.

    A Knowledge Bite is a reusable cognitive unit, not a restated fact
    (decisions.md D2). It is therefore never generated from event summaries;
    if the input supplies none, that is an incomplete analysis and is
    reported as an error rather than papered over with "data unavailable".
    """
    require(
        isinstance(knowledge_bites, list) and len(knowledge_bites) > 0,
        "knowledge_bites must be a non-empty list: a Knowledge Bite is a "
        "reusable cognitive unit (decisions.md D2) and cannot be generated "
        "from event summaries",
    )
    items: List[Dict[str, Any]] = []
    for idx, bite in enumerate(knowledge_bites):
        path = f"knowledge_bites[{idx}]"
        require(isinstance(bite, dict), f"{path} must be an object")
        for field in ("cognitive_unit", "why_it_matters"):
            require(
                non_empty_str(bite.get(field)), f"{path}.{field} is required"
            )
        event_ids = bite.get("event_ids")
        if event_ids is not None:
            require(
                isinstance(event_ids, list) and len(event_ids) > 0,
                f"{path}.event_ids must be a non-empty list when present",
            )
            for eidx, event_id in enumerate(event_ids):
                require(
                    non_empty_str(event_id),
                    f"{path}.event_ids[{eidx}] must be a non-empty string",
                )
        items.append(
            {
                "availability": "available",
                "cognitive_unit": bite["cognitive_unit"],
                "why_it_matters": bite["why_it_matters"],
                "event_ids": copy.deepcopy(event_ids),
                "source": copy.deepcopy(bite.get("source")),
                "confidence": bite.get("confidence"),
                "estimated": bite.get("estimated", False),
                "unavailable_reason": None,
            }
        )
    return items


def _follow_up_items(
    index: Dict[str, Dict[str, Any]], follow_up_plan: Any
) -> List[Dict[str, Any]]:
    """Map the follow-up plan to Tab 5 (R1).

    Tab 5 is a completeness requirement, not an editorial choice: every event
    whose status is ``open`` has been formally tracked, so the Slice 2 two-way
    rule requires a Follow-up item for it. Events that should stay out of the
    report use ``status=active`` instead — that is the explicit opt-out.

    The relation is checked in **both** directions so nothing is dropped
    silently:

    - every ``open`` event has a plan entry (forward);
    - every plan entry targets an existing event whose status is ``open``
      (backward) — an orphan plan is an error, never ignored.

    ``action`` and ``next_check`` must both be supplied. Neither is derived:
    an action is not a verification criterion, and a check date is a tracking
    decision, not a fact.
    """
    require(
        isinstance(follow_up_plan, list),
        "follow_up_plan must be a list",
    )
    plans: Dict[str, Dict[str, Any]] = {}
    for idx, entry in enumerate(follow_up_plan):
        path = f"follow_up_plan[{idx}]"
        require(isinstance(entry, dict), f"{path} must be an object")
        event_id = entry.get("event_id")
        require(non_empty_str(event_id), f"{path}.event_id is required")
        require(
            event_id not in plans, f"{path}.event_id repeats {event_id!r}",
        )
        require(
            non_empty_str(entry.get("action")),
            f"{path}.action is required and must be supplied explicitly; it is "
            f"never derived from the event's verification_criteria",
        )
        require(
            non_empty_str(entry.get("next_check")),
            f"{path}.next_check is required; a check date is a tracking "
            f"decision and is never generated",
        )
        # Backward direction: an orphan plan must not be dropped silently.
        require(
            event_id in index,
            f"{path}.event_id references an unknown event: {event_id!r}; a "
            f"follow-up plan for an event that does not exist is never ignored",
        )
        plan_status = index[event_id].get("status")
        require(
            plan_status == TRACKED_STATUS,
            f"{path}.event_id targets {event_id!r} whose status is "
            f"{plan_status!r}; only events with status '{TRACKED_STATUS}' may "
            f"appear in the Follow-up Tracker",
        )
        plans[event_id] = entry

    tracked = [
        event_id
        for event_id, event in index.items()
        if event.get("status") == TRACKED_STATUS
    ]

    items: List[Dict[str, Any]] = []
    for event_id in tracked:
        require(
            event_id in plans,
            f"event {event_id!r} has status '{TRACKED_STATUS}' and is "
            f"therefore formally tracked, but follow_up_plan has no entry for "
            f"it; an open event may not be dropped silently — set its status "
            f"to 'active' if it should stay out of the report",
        )
        entry = plans[event_id]
        event = index[event_id]
        sources = event["sources"]
        item: Dict[str, Any] = {
            "availability": "available",
            "action": entry["action"],
            "next_check": entry["next_check"],
            "event_id": event_id,
            "source": copy.deepcopy(sources[0]),
            "confidence": event["confidence"],
            "estimated": event.get("estimated", False),
            "unavailable_reason": None,
        }
        if entry.get("linked_theme") is not None:
            item["linked_theme"] = entry["linked_theme"]
        items.append(item)
    return items


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------


def build_document(source_document: Dict[str, Any]) -> Dict[str, Any]:
    """Assemble a Daily Briefing input document from a daily source document.

    Pure function: no IO, no network, no mutation of the argument. The result
    is validated with the existing report contract before being returned.

    Args:
        source_document: the daily source document (see module docstring).

    Returns:
        A document accepted by ``daily_briefing.schema.validate``.

    Raises:
        ContractError: on any violation of the source or report contract.
    """
    require(
        isinstance(source_document, dict),
        "source document root must be an object",
    )
    working = copy.deepcopy(source_document)

    meta = working.get("meta")
    require(isinstance(meta, dict), "meta must be an object")
    # Presence only. The values themselves are validated by the existing
    # report contract further down, so the rules are never duplicated here.
    for field, hint in _META_FIELD_HINTS.items():
        require(
            field in meta and meta[field] is not None,
            f"meta.{field} is required; {hint}",
        )

    index = validate_events(working.get("events"), "events")

    selection = working.get("selection")
    require(isinstance(selection, dict), "selection must be an object")
    facts = _select_events(
        index, selection.get("tab1_event_ids", []), "fact", "selection.tab1_event_ids"
    )
    inferences = _select_events(
        index,
        selection.get("tab3_event_ids", []),
        "inference",
        "selection.tab3_event_ids",
    )

    methodology = working.get("methodology")
    require(
        isinstance(methodology, dict),
        "methodology is required and is owned by the input; this pipeline "
        "never writes methodology text of its own",
    )

    document = {
        "meta": {
            "report_type": meta.get("report_type", "Daily Briefing"),
            "run_date": meta["run_date"],
            "data_date": meta["data_date"],
            "data_mode": meta["data_mode"],
        },
        "events": working["events"],
        "tabs": {
            _TAB1: {
                "tab_number": TAB_DEFS[_TAB1]["number"],
                "items": [
                    _event_item(
                        event,
                        TAB1_TEXT_FORMAT.format(
                            title=event["title"], summary=event["summary"]
                        ),
                        with_event_id=True,
                    )
                    for event in facts
                ],
            },
            "market_snapshot": {
                "tab_number": TAB_DEFS["market_snapshot"]["number"],
                "items": _market_items(working.get("market_data")),
            },
            _TAB3: {
                "tab_number": TAB_DEFS[_TAB3]["number"],
                "items": [
                    _event_item(event, event["summary"], with_event_id=True)
                    for event in inferences
                ],
            },
            "knowledge_bite": {
                "tab_number": TAB_DEFS["knowledge_bite"]["number"],
                "items": _knowledge_bite_items(working.get("knowledge_bites")),
            },
            "follow_up": {
                "tab_number": TAB_DEFS["follow_up"]["number"],
                "items": _follow_up_items(index, working.get("follow_up_plan", [])),
            },
        },
        "methodology": methodology,
    }

    # The emitted document must satisfy the frozen report contract; the shared
    # two-way follow-up rule (DV-8) is enforced here, not bypassed.
    return validate(document)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def _default_output(document: Dict[str, Any]) -> Path:
    """File name uses the run date (decisions.md D4)."""
    return Path("output") / f"daily-report-{document['meta']['run_date']}.html"


def main(argv: Optional[List[str]] = None) -> int:
    """Read a source document, build the report document, render the HTML.

    Exit codes follow the discipline established in Slice 1:
    ``0`` success, ``2`` input problem, ``3`` word-limit breach, ``4`` contract
    violation. The quality gates are never bypassed.
    """
    parser = argparse.ArgumentParser(
        prog="daily_briefing.pipeline",
        description=(
            "Assemble a Daily Briefing input document from a daily source "
            "document and render the five-tab HTML report."
        ),
    )
    parser.add_argument("--input", required=True, help="Path to the source JSON")
    parser.add_argument(
        "--out",
        default=None,
        help="Output HTML path (default: output/daily-report-<run_date>.html)",
    )
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"error: input file not found: {input_path}", file=sys.stderr)
        return 2
    try:
        source = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: input is not valid JSON: {exc}", file=sys.stderr)
        return 2

    try:
        document = build_document(source)
    except WordLimitExceeded as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    except ContractError as exc:
        print(f"error: contract violation: {exc}", file=sys.stderr)
        return 4

    try:
        html = render(document)
    except WordLimitExceeded as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    except ContractError as exc:
        print(f"error: contract violation: {exc}", file=sys.stderr)
        return 4

    out_path = Path(args.out) if args.out else _default_output(document)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"wrote {out_path}  ({len(html)} bytes, data_mode={document['meta']['data_mode']})")
    return 0


__all__ = [
    "TAB1_TEXT_FORMAT",
    "NEUTRAL_MARKET_MISSING_REASON",
    "build_document",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
