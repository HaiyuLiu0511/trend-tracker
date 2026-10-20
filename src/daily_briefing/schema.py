"""Daily Briefing V2 — input contract and validation.

Pure standard library. No third-party runtime dependency.

The contract enforces the frozen rules that live in
``docs/evidence/EVIDENCE_LAYER.md`` and ``docs/core/REPORT_DESIGN.md``:

1. Every conclusion must have evidence support.
2. All data must carry a source annotation.
3. All data must carry a confidence rating.
4. Missing data must be explicitly marked — never faked.
5. Provider fallback must be evidenced by a real routing record, never
   inferred merely from a non-P0 provider tier.

Slice 2 addition: an optional ``events`` block carrying reusable Event
Records (:mod:`contracts.event`). The block is purely additive — a document
without it validates and renders exactly as before.

The shared primitives (error type, confidence scale, provider vocabulary,
source validation) now live in :mod:`contracts.evidence` and are re-exported
here under their original names, so this module's public interface is
unchanged.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, Iterable, List, Optional

from contracts.evidence import (
    CONFIDENCE_BADGE,
    CONFIDENCE_VALUES,
    PROVIDER_TIERS,
    ROUTING_OUTCOMES,
    ContractError,
    get_fallback_chain,
    non_empty_str,
    require,
    validate_source,
)
from contracts.event import TRACKED_STATUS, validate_events

# --------------------------------------------------------------------------
# Frozen constants
# --------------------------------------------------------------------------

#: Tab keys in their frozen order. Order and naming are frozen by
#: docs/daily/product.md and must not be reordered.
TAB_ORDER: List[str] = [
    "highlights",
    "market_snapshot",
    "impact_analysis",
    "knowledge_bite",
    "follow_up",
]

#: Display definition per tab: (tab number, English name, Chinese core question).
#: REPORT_DESIGN.md requires the heading form ``Tab {N}: {核心问题}``.
#:
#: ``content_fields`` — substantive content, counted against the word budget.
#: ``required_fields`` — everything that must be non-empty for the item to be
#: valid. A superset of ``content_fields``: it also carries required
#: display-only metadata (e.g. ``next_check`` for an actionable follow-up per
#: decisions.md D3), which is deliberately NOT counted as content words.
TAB_DEFS: Dict[str, Dict[str, Any]] = {
    "highlights": {
        "number": 1,
        "name": "Today's Highlights",
        "question": "今天发生了什么？",
        "content_fields": ("text",),
        "required_fields": ("text",),
    },
    "market_snapshot": {
        "number": 2,
        "name": "Market Snapshot",
        "question": "市场整体状态如何？",
        "content_fields": ("text",),
        "required_fields": ("text",),
    },
    "impact_analysis": {
        "number": 3,
        "name": "Impact Analysis",
        "question": "事件的影响链是什么？",
        "content_fields": ("text",),
        "required_fields": ("text",),
    },
    "knowledge_bite": {
        "number": 4,
        "name": "Knowledge Bite",
        "question": "今天学到了什么？",
        "content_fields": ("cognitive_unit", "why_it_matters"),
        "required_fields": ("cognitive_unit", "why_it_matters"),
    },
    "follow_up": {
        "number": 5,
        "name": "Follow-up Tracker",
        "question": "哪些事需要持续跟踪？",
        "content_fields": ("action",),
        "required_fields": ("action", "next_check"),
    },
}

#: docs/core/REPORT_DESIGN.md L87 / docs/daily/workflow.md L33
WORD_LIMIT: int = 500

# --------------------------------------------------------------------------
# Shared primitives
# --------------------------------------------------------------------------
#
# CONFIDENCE_VALUES / CONFIDENCE_BADGE / PROVIDER_TIERS / ROUTING_OUTCOMES /
# ContractError are defined once in contracts.evidence and imported above.
# They are re-exported here so `daily_briefing.schema` keeps its historical
# public interface (see __all__ at the bottom of this module).

#: Fixed wording used whenever data is unavailable. Never a blank cell.
UNAVAILABLE_LABEL: str = "数据不可用"

#: Rendering of an estimated value (METHODOLOGY_GOVERNANCE: estimates must be labelled).
ESTIMATED_LABEL: str = "（估算）"

#: Persistent banner shown when the input declares itself as demonstration data.
MOCK_BANNER: str = "MOCK DATA / 演示数据 — 非真实市场数据，不得作为验证结果引用"

#: Persistent banner shown when the input declares data_mode="real".
#:
#: Slice 1 implements no verification mechanism, so ``real`` describes where the
#: data came from, never whether this system checked it. Declaring "real" must
#: never be read as VERIFIED — hence a mandatory disclosure rather than a badge.
REAL_MODE_BANNER: str = (
    "UNVERIFIED EVIDENCE / 未验证声明 — Evidence 与 Confidence 均来自输入数据的自述标注，"
    "Slice 1 未实现自动验证机制。data_mode=real 仅说明数据来源，不等于已验证（NOT VERIFIED）。"
)


# --------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------


class WordLimitExceeded(ContractError):
    """Raised when a tab exceeds the frozen word budget.

    Deliberately fatal: the renderer never silently truncates content.
    """

    def __init__(self, tab_key: str, count: int, limit: int = WORD_LIMIT) -> None:
        super().__init__(
            f"Tab '{tab_key}' exceeds the {limit}-word budget "
            f"(CJK characters + Latin/numeric tokens): {count} > {limit}. "
            f"Content was NOT truncated. Reduce the source text and re-run."
        )
        self.tab_key = tab_key
        self.count = count
        self.limit = limit


# --------------------------------------------------------------------------
# Word counting
# --------------------------------------------------------------------------

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_LATIN_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[.\-/'&_][A-Za-z0-9]+)*")

# CJK ideographs + extension A + compatibility ideographs.
_CJK_RANGES = (
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
)


def _is_cjk(ch: str) -> bool:
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in _CJK_RANGES)


def count_words(text: str) -> int:
    """Count words as: CJK characters + Latin/numeric token runs.

    HTML tags and surrounding whitespace are stripped first. Display-only
    metadata (source names, tiers, badges, locators) is never passed into
    this function by the renderer — it counts substantive content only.
    """
    if not text:
        return 0
    cleaned = _HTML_TAG_RE.sub(" ", text)
    cleaned = unicodedata.normalize("NFKC", cleaned)

    cjk = sum(1 for ch in cleaned if _is_cjk(ch))
    latin = len(_LATIN_TOKEN_RE.findall(cleaned))
    return cjk + latin


def count_tab_words(items: Iterable[Dict[str, Any]], tab_key: str) -> int:
    """Count the substantive words of one tab, excluding display metadata."""
    fields = TAB_DEFS[tab_key]["content_fields"]
    total = 0
    for item in items:
        for field in fields:
            total += count_words(item.get(field) or "")
    return total


# --------------------------------------------------------------------------
# Validation helpers
# --------------------------------------------------------------------------


def _validate_source(source: Any, path: str) -> List[Dict[str, Any]]:
    """Backward-compatible alias for :func:`contracts.evidence.validate_source`.

    The implementation now lives in the shared contract layer, so the daily
    briefing contract and the event contract share one source-validation rule
    set. The behaviour is unchanged.
    """
    return validate_source(source, path)


#: Tabs whose items link to a single event, and the tabs that are not allowed
#: to link to events at all. Tab 4 links to several events (a cognitive unit is
#: usually composed of more than one fact).
_SINGLE_EVENT_TABS = ("highlights", "impact_analysis", "follow_up")
_MULTI_EVENT_TABS = ("knowledge_bite",)
_NO_EVENT_TABS = ("market_snapshot",)


def _validate_event_reference_shape(
    item: Dict[str, Any], path: str, tab_key: str
) -> None:
    """Validate the *shape* of an item's event reference.

    Two kinds of reference exist and must not be mixed up:

    - a Tab item's **direct** link to the event it displays (``event_id``,
      or ``event_ids`` for Tab 4);
    - an event's **own** basis references (``derived_from`` and friends),
      which live on the event record, not on the Tab item.

    Whether a referenced event exists, and whether it has the right assertion
    type, is checked at document level by :func:`_validate_event_references`.
    """
    if tab_key in _NO_EVENT_TABS:
        require(
            item.get("event_id") is None,
            f"{path}.event_id is not allowed in tab '{tab_key}' — a market "
            f"snapshot is a state, not an event",
        )
        require(
            item.get("event_ids") is None,
            f"{path}.event_ids is not allowed in tab '{tab_key}' — a market "
            f"snapshot is a state, not an event",
        )
        return

    if tab_key in _MULTI_EVENT_TABS:
        require(
            item.get("event_id") is None,
            f"{path}.event_id is not allowed in tab '{tab_key}' — use "
            f"'event_ids' (plural); a cognitive unit may be composed of "
            f"several events",
        )
        event_ids = item.get("event_ids")
        if event_ids is not None:
            require(
                isinstance(event_ids, list) and len(event_ids) > 0,
                f"{path}.event_ids must be a non-empty list",
            )
            for idx, event_id in enumerate(event_ids):
                require(
                    non_empty_str(event_id),
                    f"{path}.event_ids[{idx}] must be a non-empty string",
                )
        return

    if tab_key in _SINGLE_EVENT_TABS:
        require(
            item.get("event_ids") is None,
            f"{path}.event_ids is not allowed in tab '{tab_key}' — use "
            f"'event_id' (singular)",
        )
        event_id = item.get("event_id")
        if event_id is not None:
            require(
                non_empty_str(event_id),
                f"{path}.event_id must be a non-empty string",
            )


def _validate_item(item: Any, path: str, tab_key: str) -> None:
    require(isinstance(item, dict), f"{path} must be an object")

    _validate_event_reference_shape(item, path, tab_key)

    availability = item.get("availability")
    require(
        availability in ("available", "unavailable"),
        f"{path}.availability must be 'available' or 'unavailable', "
        f"got {availability!r}",
    )

    if availability == "unavailable":
        require(
            non_empty_str(item.get("unavailable_reason")),
            f"{path}.unavailable_reason is required when availability is "
            f"'unavailable' (missing data must be explained, never silently blank)",
        )
        # No fabricated evidence is allowed on an unavailable item.
        require(
            item.get("source") is None,
            f"{path}.source must be null when availability is 'unavailable'",
        )
        require(
            item.get("confidence") is None,
            f"{path}.confidence must be null when availability is "
            f"'unavailable' (no confidence badge for missing data)",
        )
        return

    for field in TAB_DEFS[tab_key]["required_fields"]:
        require(
            non_empty_str(item.get(field)),
            f"{path}.{field} must be a non-empty string for tab '{tab_key}'",
        )

    confidence = item.get("confidence")
    require(
        confidence in CONFIDENCE_VALUES,
        f"{path}.confidence must be one of {CONFIDENCE_VALUES}, got {confidence!r}",
    )

    estimated = item.get("estimated", False)
    require(
        isinstance(estimated, bool),
        f"{path}.estimated must be a boolean, got {estimated!r}",
    )

    _validate_source(item.get("source"), path)


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------


def _validate_event_references(
    tabs: Dict[str, Any], events_index: Dict[str, Dict[str, Any]]
) -> None:
    """Cross-validate Tab items against the events block.

    Rules enforced here:

    - DV-2  a referenced event must exist
    - DV-3  Tab 1 (Today's Highlights) links to a **fact**
    - DV-4  Tab 3 (Impact Analysis) links to an **inference**
    - DV-5  Tab 5 (Follow-up Tracker) links to an event whose status is
            ``open`` — the backward half of the two-way tracking rule
    - DV-8  every event whose status is ``open`` is picked up by at least one
            Tab 5 item — the forward half of the same rule

    The two halves together mean: an event is formally tracked **iff** a
    Follow-up item points at it. An ordinary hypothesis (``status=active``)
    may exist without any Follow-up; once it becomes ``open`` it must be
    tracked. No extra state field is needed — ``status`` already carries it.
    """
    tracked: Dict[str, str] = {}

    for tab_key in TAB_ORDER:
        items = tabs[tab_key].get("items") or []
        for idx, item in enumerate(items):
            if tab_key in _MULTI_EVENT_TABS:
                refs = list(item.get("event_ids") or [])
            else:
                single = item.get("event_id")
                refs = [single] if single is not None else []

            for ref in refs:
                require(
                    ref in events_index,
                    f"tabs.{tab_key}.items[{idx}] references an unknown "
                    f"event: {ref!r}",
                )
                event = events_index[ref]
                if tab_key == "highlights":
                    require(
                        event.get("assertion_type") == "fact",
                        f"tabs.{tab_key}.items[{idx}] links to {ref!r} whose "
                        f"assertion_type is {event.get('assertion_type')!r}; "
                        f"Today's Highlights must link to a fact",
                    )
                elif tab_key == "impact_analysis":
                    require(
                        event.get("assertion_type") == "inference",
                        f"tabs.{tab_key}.items[{idx}] links to {ref!r} whose "
                        f"assertion_type is {event.get('assertion_type')!r}; "
                        f"Impact Analysis must link to an inference",
                    )
                elif tab_key == "follow_up":
                    require(
                        event.get("status") == TRACKED_STATUS,
                        f"tabs.{tab_key}.items[{idx}] links to {ref!r} whose "
                        f"status is {event.get('status')!r}; the Follow-up "
                        f"Tracker may only link to events whose status is "
                        f"'{TRACKED_STATUS}'",
                    )
                    tracked[ref] = f"tabs.{tab_key}.items[{idx}]"

    for event_id, event in events_index.items():
        if event.get("status") != TRACKED_STATUS:
            continue
        require(
            event_id in tracked,
            f"events[{event_id!r}] has status '{TRACKED_STATUS}' and is "
            f"therefore formally tracked, but no Follow-up Tracker item "
            f"links to it; a tracked event must be picked up by Tab 5",
        )


def validate(document: Any) -> Dict[str, Any]:
    """Validate a briefing document against the frozen contract.

    Returns the document unchanged so callers can chain
    ``render.render(validate(doc), ...)``.

    Raises:
        ContractError: on any contract violation, with a precise path.
    """
    require(isinstance(document, dict), "document root must be an object")

    meta = document.get("meta")
    require(isinstance(meta, dict), "meta must be an object")
    require(
        non_empty_str(meta.get("report_type")),
        "meta.report_type must be a non-empty string",
    )
    require(
        non_empty_str(meta.get("run_date")),
        "meta.run_date is required (decisions.md D4: file name uses the run date)",
    )
    require(
        non_empty_str(meta.get("data_date")),
        "meta.data_date is required (shown in the report header)",
    )
    data_mode = meta.get("data_mode")
    require(
        data_mode in ("mock", "real"),
        "meta.data_mode must be 'mock' or 'real'; Slice 1 fixtures must "
        "declare 'mock' so demonstration data can never pose as verified output",
    )

    tabs = document.get("tabs")
    require(isinstance(tabs, dict), "tabs must be an object")

    # Slice 2: the events block is optional. When absent, the document
    # behaves exactly as it did in Slice 1 — but the cross-validation below
    # still runs, so a Tab that references an event without declaring one
    # is rejected rather than silently accepted.
    events_index: Dict[str, Dict[str, Any]] = {}
    if "events" in document:
        events_index = validate_events(document["events"], "events")

    for tab_key in TAB_ORDER:
        require(
            tab_key in tabs,
            f"tabs.{tab_key} is missing; all five frozen tabs are required "
            f"({TAB_DEFS[tab_key]['number']}. {TAB_DEFS[tab_key]['name']})",
        )
        tab = tabs[tab_key]
        require(isinstance(tab, dict), f"tabs.{tab_key} must be an object")
        require(
            tab.get("tab_number") == TAB_DEFS[tab_key]["number"],
            f"tabs.{tab_key}.tab_number must be {TAB_DEFS[tab_key]['number']}",
        )
        items = tab.get("items")
        require(
            isinstance(items, list),
            f"tabs.{tab_key}.items must be a list",
        )
        for idx, item in enumerate(items):
            _validate_item(item, f"tabs.{tab_key}.items[{idx}]", tab_key)

    # Cross-validation always runs. Gating it on a non-empty index would let
    # an empty (or absent) events block bypass reference integrity: a Tab
    # pointing at an event that does not exist must fail either way.
    _validate_event_references(tabs, events_index)

    methodology = document.get("methodology")
    require(
        isinstance(methodology, dict),
        "methodology is required (Methodology Transparency: every analysis must "
        "state the method used)",
    )
    require(
        isinstance(methodology.get("methods"), list)
        and len(methodology["methods"]) > 0,
        "methodology.methods must be a non-empty list",
    )
    require(
        isinstance(methodology.get("limitations"), list)
        and len(methodology["limitations"]) > 0,
        "methodology.limitations must be a non-empty list (every method must "
        "state its applicability and limits)",
    )

    return document



__all__ = [
    "TAB_ORDER",
    "TAB_DEFS",
    "WORD_LIMIT",
    "CONFIDENCE_VALUES",
    "CONFIDENCE_BADGE",
    "PROVIDER_TIERS",
    "ROUTING_OUTCOMES",
    "UNAVAILABLE_LABEL",
    "ESTIMATED_LABEL",
    "MOCK_BANNER",
    "REAL_MODE_BANNER",
    "ContractError",
    "WordLimitExceeded",
    "count_words",
    "count_tab_words",
    "validate",
    "get_fallback_chain",
]
