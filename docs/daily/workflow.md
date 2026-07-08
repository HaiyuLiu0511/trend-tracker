# Workflow — Daily Briefing

> **Layer:** 1 — Event Layer
> **Status:** Frozen (V2, 2026-07-06)

---

## Daily Generation Process

```
Step 1: Data Collection
  ↓ Collect from registered data sources via Provider Routing Chain
Step 2: Event Identification
  ↓ Identify significant events from collected data
Step 3: Impact Analysis
  ↓ Analyze impact chain for significant events
Step 4: Knowledge Bite Extraction
  ↓ Extract at least 1 reusable cognitive unit
Step 5: Follow-up Tracker Update
  ↓ Mark items requiring continuous tracking
Step 6: Report Generation
  ↓ Generate daily-report-YYYY-MM-DD.html
```

## File Naming Convention

- **Run Date** (file name): `daily-report-YYYY-MM-DD.html` — uses system date
- **Data Date** (header): data cutoff date — may differ from Run Date
- Never use data date as file name (prevents overwriting)

## Quality Gates

- Each Tab must not exceed 500 words
- Tab 4 (Knowledge Bite) must have substantive cognitive content
- Tab 5 (Follow-up Tracker) must be actionable
- All data must have source and confidence annotation
- Methodology must be transparent

## Known Issues

See: [core/REFACTOR_BACKLOG.md](../core/REFACTOR_BACKLOG.md) — P0-001, P0-003
