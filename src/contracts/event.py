"""Reusable Event Data Contract — Personal Investment Research System.

An **Event Record** is a structured research input produced by Layer 1
(Daily Briefing) and consumed by Layer 2 (Research Terminal) and Layer 3
(Industry Research).

Boundary — Event Record is **not** a Knowledge Asset
----------------------------------------------------
``docs/core/RESEARCH_SYSTEM.md`` freezes five Knowledge Asset types
(Knowledge Bite, Industry Framework, Company Research, Investment Mapping,
Follow-up Tracker). Event Record is **not** one of them. That is a statement
of fact, not a prohibition: persisting event records later is allowed, but it
would be an independent architectural decision (and would require evaluating
whether Event Record should be promoted to a sixth Knowledge Asset type).

**This Slice implements structure and validation only.** There is no
persistence, no storage, no history lookup, no de-duplication, no cross-report
identity resolution and no lifecycle transition engine.

Frozen references:
  - docs/daily/product.md          Layer 1 tab definitions and responsibilities
  - docs/daily/decisions.md        D2 cognitive unit, D3 actionable follow-up
  - docs/core/RESEARCH_SYSTEM.md   Knowledge Flow, Knowledge Asset Types
  - docs/evidence/EVIDENCE_LAYER.md confidence standard

Dependency rule: this module imports ``contracts.evidence`` and stdlib only.
It must never import ``daily_briefing`` — Layers 2/3/4 depend on the shared
contract layer directly.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any, Dict, List, Optional, Set

from .evidence import (
    CONFIDENCE_VALUES,
    ContractError,
    non_empty_str,
    require,
    validate_source,
)

# --------------------------------------------------------------------------
# Frozen vocabulary
# --------------------------------------------------------------------------

#: Stable event identifier: evt-{first-identified date}-{ascii slug}.
#:
#: The date part is the date the event was FIRST identified — deliberately not
#: the report run date. Identifiers are assigned by the caller and must never
#: be regenerated from a title, a date update or a re-run. This module
#: deliberately provides **no** identifier-generation helper.
EVENT_ID_PATTERN: str = r"^evt-\d{8}-[a-z0-9][a-z0-9-]*$"
_EVENT_ID_RE = re.compile(EVENT_ID_PATTERN)

#: The three kinds of assertion. They are structurally distinguishable so a
#: raw fact, an analytical inference and a judgement awaiting verification can
#: never be silently mixed up.
ASSERTION_TYPES: List[str] = ["fact", "inference", "hypothesis"]

#: Event lifecycle states.
#:
#: ``verified`` is deliberately absent: no verification mechanism exists yet
#: (BACKLOG P0-003 remains Pending), so advertising such a state would imply a
#: capability the system does not have.
EVENT_STATUSES: List[str] = ["active", "open", "superseded", "rejected"]

#: Status that means "formally tracked" — an open item must be picked up by
#: the Follow-up Tracker and must state how it can be verified.
TRACKED_STATUS: str = "open"

#: Required fields on every event record.
REQUIRED_EVENT_FIELDS: List[str] = [
    "event_id",
    "title",
    "summary",
    "assertion_type",
    "status",
    "occurred_at",
    "collected_at",
    "data_date",
    "sources",
    "confidence",
]

_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------


def _validate_date(value: Any, path: str) -> None:
    require(
        isinstance(value, str) and _ISO_DATE_RE.match(value) is not None,
        f"{path} must be a date string in YYYY-MM-DD form, got {value!r}",
    )
    try:
        date.fromisoformat(value)
    except ValueError:
        raise ContractError(f"{path} is not a valid calendar date: {value!r}") from None


def _validate_str_list(value: Any, path: str) -> None:
    require(isinstance(value, list), f"{path} must be a list")
    for idx, item in enumerate(value):
        require(
            non_empty_str(item),
            f"{path}[{idx}] must be a non-empty string",
        )


def _validate_date_list(value: Any, path: str) -> None:
    require(isinstance(value, list), f"{path} must be a list")
    for idx, item in enumerate(value):
        _validate_date(item, f"{path}[{idx}]")


# --------------------------------------------------------------------------
# Event level validation
# --------------------------------------------------------------------------


def validate_event(event: Any, path: str) -> None:
    """Validate a single event record's own structure.

    Collection-level rules (uniqueness, referential integrity, cycles,
    reachability) live in :func:`validate_events`.
    """
    require(isinstance(event, dict), f"{path} must be an object")

    # --- identifier -----------------------------------------------------
    event_id = event.get("event_id")
    require(
        non_empty_str(event_id),
        f"{path}.event_id must be a non-empty string",
    )
    require(
        _EVENT_ID_RE.match(event_id) is not None,
        f"{path}.event_id must match {EVENT_ID_PATTERN} "
        f"(evt-<YYYYMMDD first-identified date>-<ascii slug>), got {event_id!r}",
    )
    _validate_date_from_event_id(event_id, f"{path}.event_id")

    # --- required text --------------------------------------------------
    for field in ("title", "summary"):
        require(
            non_empty_str(event.get(field)),
            f"{path}.{field} must be a non-empty string",
        )

    # --- assertion type -------------------------------------------------
    assertion_type = event.get("assertion_type")
    require(
        assertion_type in ASSERTION_TYPES,
        f"{path}.assertion_type must be one of {ASSERTION_TYPES}, "
        f"got {assertion_type!r}",
    )

    # --- status ----------------------------------------------------------
    status = event.get("status")
    require(
        status in EVENT_STATUSES,
        f"{path}.status must be one of {EVENT_STATUSES}, got {status!r}",
    )

    # --- dates -----------------------------------------------------------
    for field in ("occurred_at", "collected_at", "data_date"):
        _validate_date(event.get(field), f"{path}.{field}")

    # --- sources (single shared implementation) --------------------------
    sources = event.get("sources")
    require(
        isinstance(sources, list) and len(sources) > 0,
        f"{path}.sources must be a non-empty list (every event must have "
        f"evidence support)",
    )
    for idx, source in enumerate(sources):
        validate_source(source, f"{path}.sources[{idx}]")

    # --- confidence (single shared scale) --------------------------------
    confidence = event.get("confidence")
    require(
        confidence in CONFIDENCE_VALUES,
        f"{path}.confidence must be one of {CONFIDENCE_VALUES}, got {confidence!r}",
    )

    estimated = event.get("estimated", False)
    require(
        isinstance(estimated, bool),
        f"{path}.estimated must be a boolean, got {estimated!r}",
    )

    # --- optional collections --------------------------------------------
    if "themes" in event:
        _validate_str_list(event["themes"], f"{path}.themes")
    if "companies" in event:
        _validate_str_list(event["companies"], f"{path}.companies")

    # --- R-A: a hypothesis must state how it can be verified -------------
    derived_from = event.get("derived_from") or []
    _validate_str_list(derived_from, f"{path}.derived_from")
    verification_criteria = event.get("verification_criteria")

    if assertion_type == "hypothesis":
        require(
            non_empty_str(verification_criteria),
            f"{path}.verification_criteria is required for a hypothesis "
            f"(a judgement awaiting verification must say how it is verified)",
        )

    # --- R-B: anything formally tracked must state how it is verified ----
    if status == TRACKED_STATUS:
        require(
            non_empty_str(verification_criteria),
            f"{path}.verification_criteria is required when status is "
            f"'{TRACKED_STATUS}' (a tracked item must be verifiable)",
        )

    # --- a fact is not an inference --------------------------------------
    if assertion_type == "fact":
        require(
            not derived_from,
            f"{path}.derived_from must be empty or absent for a fact "
            f"(a raw fact is not derived from other records)",
        )

    # --- an inference must have a basis -----------------------------------
    if assertion_type == "inference":
        require(
            len(derived_from) > 0,
            f"{path}.derived_from is required for an inference "
            f"(an analytical inference must be traceable to its basis)",
        )

    # --- relations --------------------------------------------------------
    if event.get("supersedes") is not None:
        supersedes = event["supersedes"]
        require(
            non_empty_str(supersedes),
            f"{path}.supersedes must be a non-empty string when present",
        )
        require(
            supersedes != event_id,
            f"{path}.supersedes must not point at the event itself",
        )

    if "related_event_ids" in event:
        _validate_str_list(event["related_event_ids"], f"{path}.related_event_ids")


def _validate_date_from_event_id(event_id: str, path: str) -> None:
    """The date segment of an event id must be a real calendar date."""
    segment = event_id[4:12]
    require(
        _ISO_DATE_RE.match(f"{segment[:4]}-{segment[4:6]}-{segment[6:]}") is not None,
        f"{path} carries a malformed date segment: {event_id!r}",
    )
    try:
        date(int(segment[:4]), int(segment[4:6]), int(segment[6:]))
    except ValueError:
        raise ContractError(
            f"{path} carries an invalid calendar date: {event_id!r}"
        ) from None


# --------------------------------------------------------------------------
# Collection level validation
# --------------------------------------------------------------------------


def _build_index(events: List[Dict[str, Any]], path: str) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    for idx, event in enumerate(events):
        event_id = event["event_id"]
        require(
            event_id not in index,
            f"{path}[{idx}].event_id duplicates an earlier event: {event_id!r}",
        )
        index[event_id] = event
    return index


def _detect_cycle(
    index: Dict[str, Dict[str, Any]], edges: str
) -> Optional[List[str]]:
    """Return a cycle in the given relation, or None.

    ``edges`` names the field holding the outgoing relation. The traversal is a
    plain standard-library depth-first search with colouring — no graph
    framework involved.
    """
    WHITE, GREY, BLACK = 0, 1, 2
    colour: Dict[str, int] = {node: WHITE for node in index}

    def visit(node: str, stack: List[str]) -> Optional[List[str]]:
        colour[node] = GREY
        stack.append(node)
        event = index.get(node)
        if event is not None:
            targets = event.get(edges) or []
            if isinstance(targets, str):
                targets = [targets]
            for target in targets:
                if target not in index:
                    continue
                state = colour.get(target, WHITE)
                if state == GREY:
                    start = stack.index(target)
                    return stack[start:] + [target]
                if state == WHITE:
                    found = visit(target, stack)
                    if found is not None:
                        return found
        stack.pop()
        colour[node] = BLACK
        return None

    for node in index:
        if colour.get(node, WHITE) == WHITE:
            found = visit(node, [])
            if found is not None:
                return found
    return None


def _reaches_fact(
    event_id: str,
    index: Dict[str, Dict[str, Any]],
    seen: Optional[Set[str]] = None,
) -> bool:
    """Whether the event reaches a fact through ``derived_from``.

    One hop (``inference -> fact``) and multi-hop
    (``inference -> inference -> fact``) are both accepted. The relation is
    guaranteed acyclic by the cycle check, and ``seen`` keeps the walk safe
    regardless.
    """
    if seen is None:
        seen = set()
    if event_id in seen:
        return False
    seen.add(event_id)
    event = index.get(event_id)
    if event is None:
        return False
    for parent in event.get("derived_from") or []:
        parent_event = index.get(parent)
        if parent_event is None:
            continue
        if parent_event.get("assertion_type") == "fact":
            return True
        if _reaches_fact(parent, index, seen):
            return True
    return False


def validate_events(events: Any, path: str = "events") -> Dict[str, Dict[str, Any]]:
    """Validate a collection of event records.

    Enforces uniqueness, referential integrity, acyclic relations and the
    inference-to-fact reachability rule.

    Returns:
        A mapping of event_id to event record.

    Raises:
        ContractError: on any violation.
    """
    require(isinstance(events, list), f"{path} must be a list")
    for idx, event in enumerate(events):
        validate_event(event, f"{path}[{idx}]")

    index = _build_index(events, path)

    # --- referential integrity -------------------------------------------
    for idx, event in enumerate(events):
        epath = f"{path}[{idx}]"
        for field in ("derived_from", "related_event_ids"):
            for ref in event.get(field) or []:
                require(
                    ref in index,
                    f"{epath}.{field} references an unknown event: {ref!r}",
                )
        supersedes = event.get("supersedes")
        if supersedes is not None:
            require(
                supersedes in index,
                f"{epath}.supersedes references an unknown event: {supersedes!r}",
            )

    # --- acyclic relations -------------------------------------------------
    derived_cycle = _detect_cycle(index, "derived_from")
    if derived_cycle is not None:
        raise ContractError(
            f"{path}.derived_from contains a cycle: {' -> '.join(derived_cycle)}"
        )
    supersede_cycle = _detect_cycle(index, "supersedes")
    if supersede_cycle is not None:
        raise ContractError(
            f"{path}.supersedes contains a cycle: {' -> '.join(supersede_cycle)}"
        )

    # --- EV-12: every inference must reach a fact --------------------------
    for idx, event in enumerate(events):
        if event.get("assertion_type") != "inference":
            continue
        require(
            _reaches_fact(event["event_id"], index),
            f"{path}[{idx}] ({event['event_id']}) is an inference that cannot be "
            f"traced back to any fact through derived_from; an inference must "
            f"reach a fact in one hop or several",
        )

    return index


__all__ = [
    "ASSERTION_TYPES",
    "EVENT_ID_PATTERN",
    "EVENT_STATUSES",
    "REQUIRED_EVENT_FIELDS",
    "TRACKED_STATUS",
    "validate_event",
    "validate_events",
]
