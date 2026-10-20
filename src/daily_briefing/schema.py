"""Daily Briefing V2 (Slice 1) — input contract and validation.

Pure standard library. No third-party runtime dependency.

The contract enforces the frozen rules that live in
``docs/evidence/EVIDENCE_LAYER.md`` and ``docs/core/REPORT_DESIGN.md``:

1. Every conclusion must have evidence support.
2. All data must carry a source annotation.
3. All data must carry a confidence rating.
4. Missing data must be explicitly marked — never faked.
5. Provider fallback must be evidenced by a real routing record, never
   inferred merely from a non-P0 provider tier.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, Iterable, List, Optional

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

#: docs/evidence/EVIDENCE_LAYER.md — Confidence Rating Standard
CONFIDENCE_VALUES: List[str] = ["HIGH", "MEDIUM", "LOW-MEDIUM", "LOW"]
CONFIDENCE_BADGE: Dict[str, str] = {
    "HIGH": "🟢",
    "MEDIUM": "🟡",
    "LOW-MEDIUM": "🟠",
    "LOW": "🔴",
}

#: Provider Routing Chain (docs/core/ENGINEERING_GOVERNANCE.md, docs/provider/DATA_SOURCE.md)
PROVIDER_TIERS: List[str] = ["P0", "P1", "P2", "P3"]

#: Terminal outcomes of a routing attempt.
ROUTING_OUTCOMES: List[str] = ["success", "no_data", "error", "timeout"]

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


class ContractError(ValueError):
    """Raised when the input document violates the frozen contract."""


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


def _require(cond: bool, message: str) -> None:
    if not cond:
        raise ContractError(message)


def _non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _validate_source(source: Any, path: str) -> List[Dict[str, Any]]:
    """Validate a source block and return the evidenced fallback chain.

    The fallback chain is derived from ``routing.attempted`` records only.
    A non-P0 tier alone is *not* evidence that a higher-priority provider
    failed, so no fallback is rendered without a matching record.
    """
    _require(isinstance(source, dict), f"{path}.source must be an object")

    _require(
        _non_empty_str(source.get("name")),
        f"{path}.source.name must be a non-empty string",
    )
    tier = source.get("provider_tier")
    _require(
        tier in PROVIDER_TIERS,
        f"{path}.source.provider_tier must be one of {PROVIDER_TIERS}, got {tier!r}",
    )
    _require(
        _non_empty_str(source.get("locator")),
        f"{path}.source.locator must be a non-empty string (every data point "
        f"must trace back to its source)",
    )

    routing = source.get("routing")
    if routing is None:
        # No routing evidence. A non-P0 tier is still allowed, but no
        # fallback annotation may be rendered.
        return []

    _require(
        isinstance(routing, dict),
        f"{path}.source.routing must be an object when present",
    )
    attempted = routing.get("attempted")
    _require(
        isinstance(attempted, list) and len(attempted) > 0,
        f"{path}.source.routing.attempted must be a non-empty list",
    )

    successes: List[str] = []
    for idx, attempt in enumerate(attempted):
        apath = f"{path}.source.routing.attempted[{idx}]"
        _require(isinstance(attempt, dict), f"{apath} must be an object")
        _require(
            attempt.get("tier") in PROVIDER_TIERS,
            f"{apath}.tier must be one of {PROVIDER_TIERS}",
        )
        _require(
            _non_empty_str(attempt.get("provider")),
            f"{apath}.provider must be a non-empty string",
        )
        _require(
            attempt.get("outcome") in ROUTING_OUTCOMES,
            f"{apath}.outcome must be one of {ROUTING_OUTCOMES}",
        )
        if attempt["outcome"] == "success":
            successes.append(attempt["tier"])

    _require(
        len(successes) == 1,
        f"{path}.source.routing.attempted must contain exactly one successful "
        f"attempt, found {len(successes)}",
    )
    _require(
        successes[0] == tier,
        f"{path}.source.provider_tier is {tier} but the successful routing "
        f"attempt is at {successes[0]}; the declared tier must match the "
        f"provider that actually succeeded",
    )

    # Evidenced fallback: a higher-priority tier was tried and did not succeed.
    tier_rank = PROVIDER_TIERS.index(tier)
    fallback_chain = [
        {
            "tier": a["tier"],
            "provider": a["provider"],
            "outcome": a["outcome"],
        }
        for a in attempted
        if PROVIDER_TIERS.index(a["tier"]) < tier_rank and a["outcome"] != "success"
    ]
    return fallback_chain


def _validate_item(item: Any, path: str, tab_key: str) -> None:
    _require(isinstance(item, dict), f"{path} must be an object")

    availability = item.get("availability")
    _require(
        availability in ("available", "unavailable"),
        f"{path}.availability must be 'available' or 'unavailable', "
        f"got {availability!r}",
    )

    if availability == "unavailable":
        _require(
            _non_empty_str(item.get("unavailable_reason")),
            f"{path}.unavailable_reason is required when availability is "
            f"'unavailable' (missing data must be explained, never silently blank)",
        )
        # No fabricated evidence is allowed on an unavailable item.
        _require(
            item.get("source") is None,
            f"{path}.source must be null when availability is 'unavailable'",
        )
        _require(
            item.get("confidence") is None,
            f"{path}.confidence must be null when availability is "
            f"'unavailable' (no confidence badge for missing data)",
        )
        return

    for field in TAB_DEFS[tab_key]["required_fields"]:
        _require(
            _non_empty_str(item.get(field)),
            f"{path}.{field} must be a non-empty string for tab '{tab_key}'",
        )

    confidence = item.get("confidence")
    _require(
        confidence in CONFIDENCE_VALUES,
        f"{path}.confidence must be one of {CONFIDENCE_VALUES}, got {confidence!r}",
    )

    estimated = item.get("estimated", False)
    _require(
        isinstance(estimated, bool),
        f"{path}.estimated must be a boolean, got {estimated!r}",
    )

    _validate_source(item.get("source"), path)


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------


def validate(document: Any) -> Dict[str, Any]:
    """Validate a briefing document against the frozen contract.

    Returns the document unchanged so callers can chain
    ``render.render(validate(doc), ...)``.

    Raises:
        ContractError: on any contract violation, with a precise path.
    """
    _require(isinstance(document, dict), "document root must be an object")

    meta = document.get("meta")
    _require(isinstance(meta, dict), "meta must be an object")
    _require(
        _non_empty_str(meta.get("report_type")),
        "meta.report_type must be a non-empty string",
    )
    _require(
        _non_empty_str(meta.get("run_date")),
        "meta.run_date is required (decisions.md D4: file name uses the run date)",
    )
    _require(
        _non_empty_str(meta.get("data_date")),
        "meta.data_date is required (shown in the report header)",
    )
    data_mode = meta.get("data_mode")
    _require(
        data_mode in ("mock", "real"),
        "meta.data_mode must be 'mock' or 'real'; Slice 1 fixtures must "
        "declare 'mock' so demonstration data can never pose as verified output",
    )

    tabs = document.get("tabs")
    _require(isinstance(tabs, dict), "tabs must be an object")

    for tab_key in TAB_ORDER:
        _require(
            tab_key in tabs,
            f"tabs.{tab_key} is missing; all five frozen tabs are required "
            f"({TAB_DEFS[tab_key]['number']}. {TAB_DEFS[tab_key]['name']})",
        )
        tab = tabs[tab_key]
        _require(isinstance(tab, dict), f"tabs.{tab_key} must be an object")
        _require(
            tab.get("tab_number") == TAB_DEFS[tab_key]["number"],
            f"tabs.{tab_key}.tab_number must be {TAB_DEFS[tab_key]['number']}",
        )
        items = tab.get("items")
        _require(
            isinstance(items, list),
            f"tabs.{tab_key}.items must be a list",
        )
        for idx, item in enumerate(items):
            _validate_item(item, f"tabs.{tab_key}.items[{idx}]", tab_key)

    methodology = document.get("methodology")
    _require(
        isinstance(methodology, dict),
        "methodology is required (Methodology Transparency: every analysis must "
        "state the method used)",
    )
    _require(
        isinstance(methodology.get("methods"), list)
        and len(methodology["methods"]) > 0,
        "methodology.methods must be a non-empty list",
    )
    _require(
        isinstance(methodology.get("limitations"), list)
        and len(methodology["limitations"]) > 0,
        "methodology.limitations must be a non-empty list (every method must "
        "state its applicability and limits)",
    )

    return document


def get_fallback_chain(item: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return the evidenced fallback chain for an available item."""
    if item.get("availability") != "available":
        return []
    source = item.get("source") or {}
    routing = source.get("routing")
    if routing is None:
        return []
    tier = source.get("provider_tier")
    attempted = routing.get("attempted") or []
    rank = PROVIDER_TIERS.index(tier)
    return [
        {"tier": a["tier"], "provider": a["provider"], "outcome": a["outcome"]}
        for a in attempted
        if PROVIDER_TIERS.index(a["tier"]) < rank and a.get("outcome") != "success"
    ]


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
