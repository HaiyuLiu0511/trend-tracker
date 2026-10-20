"""Shared contract layer — Personal Investment Research System.

This package holds contracts that are **layer-neutral**: they are used by
Layer 1 (Daily Briefing) today and are meant to be consumed directly by
Layer 2 (Research Terminal), Layer 3 (Industry Research) and Layer 4
(Company Research) later.

Modules:
  - ``evidence``  base primitives: error type, confidence scale, provider
                   routing vocabulary, source validation
  - ``event``     the reusable Event Data Contract

Dependency direction (no cycles):

    contracts.evidence  <-  contracts.event
    contracts           <-  daily_briefing.schema

The ``contracts`` package never imports ``daily_briefing``; that keeps the
one-way Knowledge Flow intact and lets downstream layers consume the contract
without depending on Layer 1's report format.
"""

from .evidence import (
    CONFIDENCE_BADGE,
    CONFIDENCE_VALUES,
    PROVIDER_TIERS,
    ROUTING_OUTCOMES,
    ContractError,
    get_fallback_chain,
    validate_source,
)
from .event import (
    ASSERTION_TYPES,
    EVENT_ID_PATTERN,
    EVENT_STATUSES,
    REQUIRED_EVENT_FIELDS,
    TRACKED_STATUS,
    validate_event,
    validate_events,
)

__all__ = [
    # evidence
    "ContractError",
    "CONFIDENCE_VALUES",
    "CONFIDENCE_BADGE",
    "PROVIDER_TIERS",
    "ROUTING_OUTCOMES",
    "validate_source",
    "get_fallback_chain",
    # event
    "ASSERTION_TYPES",
    "EVENT_ID_PATTERN",
    "EVENT_STATUSES",
    "REQUIRED_EVENT_FIELDS",
    "TRACKED_STATUS",
    "validate_event",
    "validate_events",
]
