"""Shared evidence primitives for the Personal Investment Research System.

This is the **base module** of the shared contract layer. It owns the single
definition of everything that must not be duplicated across layers:

- the base error type (:class:`ContractError`)
- the four-level confidence scale
- the provider routing chain vocabulary
- source validation, including the rule that a provider fallback must be
  evidenced by a real routing record

Frozen references:
  - docs/evidence/EVIDENCE_LAYER.md   confidence standard, fallback annotation
  - docs/provider/DATA_SOURCE.md       provider routing chain
  - docs/core/REPORT_DESIGN.md         evidence annotation in reports

Dependency rule: this module imports **stdlib only** and must never import
``daily_briefing`` (or any other layer). Layer 2 / 3 / 4 depend on this
module directly, so the dependency direction stays one-way.
"""

from __future__ import annotations

from typing import Any, Dict, List

# --------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------


class ContractError(ValueError):
    """Raised when an input document violates the frozen contract."""


# --------------------------------------------------------------------------
# Confidence — docs/evidence/EVIDENCE_LAYER.md
# --------------------------------------------------------------------------

#: Confidence Rating Standard. The four levels are frozen; this Slice neither
#: adds, renames nor promotes any level.
CONFIDENCE_VALUES: List[str] = ["HIGH", "MEDIUM", "LOW-MEDIUM", "LOW"]

CONFIDENCE_BADGE: Dict[str, str] = {
    "HIGH": "🟢",
    "MEDIUM": "🟡",
    "LOW-MEDIUM": "🟠",
    "LOW": "🔴",
}

# --------------------------------------------------------------------------
# Provider routing chain — docs/provider/DATA_SOURCE.md
# --------------------------------------------------------------------------

PROVIDER_TIERS: List[str] = ["P0", "P1", "P2", "P3"]

#: Terminal outcomes of a routing attempt.
ROUTING_OUTCOMES: List[str] = ["success", "no_data", "error", "timeout"]


# --------------------------------------------------------------------------
# Small shared helpers
# --------------------------------------------------------------------------


def require(cond: bool, message: str) -> None:
    if not cond:
        raise ContractError(message)


def non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


# --------------------------------------------------------------------------
# Source validation
# --------------------------------------------------------------------------


def validate_source(source: Any, path: str) -> List[Dict[str, Any]]:
    """Validate a source block and return the evidenced fallback chain.

    The fallback chain is derived from ``routing.attempted`` records only.
    A non-P0 tier alone is *not* evidence that a higher-priority provider
    failed, so no fallback is rendered without a matching record.

    This is the single source-validation implementation in the project; the
    daily briefing report contract and the event contract both call it.
    """
    require(isinstance(source, dict), f"{path}.source must be an object")

    require(
        non_empty_str(source.get("name")),
        f"{path}.source.name must be a non-empty string",
    )
    tier = source.get("provider_tier")
    require(
        tier in PROVIDER_TIERS,
        f"{path}.source.provider_tier must be one of {PROVIDER_TIERS}, got {tier!r}",
    )
    require(
        non_empty_str(source.get("locator")),
        f"{path}.source.locator must be a non-empty string (every data point "
        f"must trace back to its source)",
    )

    routing = source.get("routing")
    if routing is None:
        # No routing evidence. A non-P0 tier is still allowed, but no
        # fallback annotation may be rendered.
        return []

    require(
        isinstance(routing, dict),
        f"{path}.source.routing must be an object when present",
    )
    attempted = routing.get("attempted")
    require(
        isinstance(attempted, list) and len(attempted) > 0,
        f"{path}.source.routing.attempted must be a non-empty list",
    )

    successes: List[str] = []
    for idx, attempt in enumerate(attempted):
        apath = f"{path}.source.routing.attempted[{idx}]"
        require(isinstance(attempt, dict), f"{apath} must be an object")
        require(
            attempt.get("tier") in PROVIDER_TIERS,
            f"{apath}.tier must be one of {PROVIDER_TIERS}",
        )
        require(
            non_empty_str(attempt.get("provider")),
            f"{apath}.provider must be a non-empty string",
        )
        require(
            attempt.get("outcome") in ROUTING_OUTCOMES,
            f"{apath}.outcome must be one of {ROUTING_OUTCOMES}",
        )
        if attempt["outcome"] == "success":
            successes.append(attempt["tier"])

    require(
        len(successes) == 1,
        f"{path}.source.routing.attempted must contain exactly one successful "
        f"attempt, found {len(successes)}",
    )
    require(
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
    "ContractError",
    "CONFIDENCE_VALUES",
    "CONFIDENCE_BADGE",
    "PROVIDER_TIERS",
    "ROUTING_OUTCOMES",
    "require",
    "non_empty_str",
    "validate_source",
    "get_fallback_chain",
]
