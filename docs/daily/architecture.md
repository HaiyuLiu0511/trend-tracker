# Architecture — Daily Briefing

> **Layer:** 1 — Event Layer
> **Status:** Frozen (V2, 2026-07-06)
> **Architecture Reference:** [core/ARCHITECTURE.md](../core/ARCHITECTURE.md)

---

## Data Inputs

- Market data (indices, ETFs, key stocks)
- News (tech, finance, macro)
- Announcements (company, regulatory)
- Macro data (interest rates, CPI, PMI, etc.)

## Processing Pipeline

```
Data Collection → Event Identification → Impact Analysis → Knowledge Extraction → Follow-up Marking
```

## Output Structure

5 Tabs (frozen V2):
1. Today's Highlights — event summary
2. Market Snapshot — market overview
3. Impact Analysis — impact chain analysis
4. Knowledge Bite — cognitive accumulation unit
5. Follow-up Tracker — items requiring continuous tracking

## Cross-Layer Interface

**Output to Layer 2 (Research Terminal):**
- Marked important events
- Follow-up Tracker items

## Data Source Rules

- All data must follow Provider Routing Chain (P0 → P1 → P2 → P3)
- All data must have source annotation
- All data must have confidence rating (HIGH / MEDIUM / LOW-MEDIUM / LOW)
- Fallback must be annotated

See: [provider/DATA_SOURCE.md](../provider/DATA_SOURCE.md)

## Evidence Layer

- Every conclusion must have Evidence support
- Confidence ratings must follow unified standard
- Data missing must be explicitly marked

See: [evidence/EVIDENCE_LAYER.md](../evidence/EVIDENCE_LAYER.md)
