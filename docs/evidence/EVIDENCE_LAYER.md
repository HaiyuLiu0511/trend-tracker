# Evidence Layer — Evidence Verification & Confidence Standards

> **Status:** Frozen
> **Architecture Reference:** [core/ARCHITECTURE.md](../core/ARCHITECTURE.md)
> **Governance Reference:** [core/GOVERNANCE.md](../core/GOVERNANCE.md)

---

## Purpose

Define evidence verification mechanisms and unified confidence rating standards for all reports (Layer 1-5).

## Core Principles

1. **Every conclusion must have Evidence support**
2. **All data must have source annotation**
3. **All data must have confidence rating**
4. **Data missing must be explicitly marked — never fake data**
5. **Fallback must be annotated — never hide routing chain**

## Confidence Rating Standard

| Rating | Label | Meaning |
|--------|-------|---------|
| HIGH | Green circle | Verified from primary source (API, official data) |
| MEDIUM | Yellow circle | Verified from secondary source (reputable media) |
| LOW-MEDIUM | Orange circle | Estimated or inferred from partial data |
| LOW | Red circle | Unverified, speculative, or web-scraped |

## Evidence Chain Requirements

- Every data point must trace back to its source
- API data > WebSearch > WebFetch (priority chain)
- Fallback must be recorded: "Source: FinMind (P1, P0 no data)"
- All estimates must be labeled "estimated"

## Data Source Rules

See: [provider/DATA_SOURCE.md](../provider/DATA_SOURCE.md) for Provider Routing Chain

## Known Issues

See: [core/REFACTOR_BACKLOG.md](../core/REFACTOR_BACKLOG.md) — P0-003 (Evidence Layer lacks verification mechanism)

## Related Documents

- [core/GOVERNANCE.md](../core/GOVERNANCE.md) — Data Governance
- [core/REPORT_DESIGN.md](../core/REPORT_DESIGN.md) — Evidence Layer in reports
- [provider/DATA_SOURCE.md](../provider/DATA_SOURCE.md) — Provider Routing Chain

---

*Evidence Layer is the foundation of report credibility. No conclusion without evidence.*
