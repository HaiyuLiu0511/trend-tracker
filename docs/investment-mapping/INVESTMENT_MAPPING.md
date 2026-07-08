# Investment Mapping — Cognitive Accumulation Carrier

> **Status:** Concept frozen, implementation pending (Phase 11)
> **Architecture Reference:** [core/ARCHITECTURE.md](../core/ARCHITECTURE.md)
> **Research System Reference:** [core/RESEARCH_SYSTEM.md](../core/RESEARCH_SYSTEM.md)

---

## Purpose

Investment Mapping is the cognitive accumulation carrier of Personal Investment Research System. It records the system's evolving understanding of investment opportunities.

## What It Is

- Investment map (companies, themes, industries)
- Cognitive accumulation record
- Updated monthly by Layer 5 (Monthly Outlook)
- Version controlled via Git

## What It Is NOT

- Portfolio tracker (no holdings, no returns)
- Trading journal
- Stock screener

## Map Structure (Planned)

```
Investment Mapping
├── Watch List (companies under observation)
├── Active Research (companies with active research)
├── Investment Decisions (Buy/Hold/Sell with rationale)
├── Theme Tracking (themes under monitoring)
├── Industry Coverage (industries with frameworks)
└── Evolution Log (how understanding changed over time)
```

## Knowledge Asset Type

| Asset Type | Definition | Storage | Version Control |
|------------|-----------|---------|-----------------|
| Investment Mapping | Investment map | `investment-mapping.md` | Git |

## Update Mechanism

- Updated by Monthly Outlook (Layer 5)
- Add new opportunities discovered
- Remove outdated entries
- Adjust existing entries based on new research
- Log evolution (what changed and why)

## Known Issues

See: [core/REFACTOR_BACKLOG.md](../core/REFACTOR_BACKLOG.md) — P1-004 (Investment Mapping missing)

## Implementation Phase

Phase 11: Investment Mapping (new)

## Related Documents

- [core/RESEARCH_SYSTEM.md](../core/RESEARCH_SYSTEM.md) — Knowledge Asset Types
- [monthly/](../monthly/) — Monthly Outlook (Layer 5, updates Investment Mapping)
- [core/REFACTOR_BACKLOG.md](../core/REFACTOR_BACKLOG.md) — P1-004

---

*Investment Mapping is the tangible evidence of cognitive accumulation. Without it, research is forgotten.*
