# Product — Daily Briefing

> **Layer:** 1 — Event Layer
> **Status:** Frozen (V2, 2026-07-06)
> **Architecture Reference:** [core/ARCHITECTURE.md](../core/ARCHITECTURE.md)

---

## Responsibility

Daily information intake, identify important events, mark items for tracking.

## What This Layer Is

- Daily information intake and event marking
- Quick overview of what happened today
- Impact analysis of significant events
- Knowledge accumulation (Knowledge Bite)
- Follow-up tracking

## What This Layer Is NOT

- Deep industry analysis (Layer 3)
- Company valuation (Layer 4)
- Knowledge evolution (Layer 5)
- Deep research

## Frozen Output Format (V2)

| Tab | Name | Core Question |
|-----|------|---------------|
| Tab 1 | Today's Highlights | What happened today? |
| Tab 2 | Market Snapshot | What is the overall market state? |
| Tab 3 | Impact Analysis | What is the event impact chain? |
| Tab 4 | Knowledge Bite | What did I learn today? |
| Tab 5 | Follow-up Tracker | What needs continuous tracking? |

## Design Principles

- One Tab = One Question
- Reports are outputs. Knowledge is the asset.
- Each Tab max 500 words
- Must have Follow-up Tracker
- Must produce at least 1 Knowledge Bite per day

## Deliverable

`daily-report-YYYY-MM-DD.html`

## Evolution from Trend Tracker

Daily Briefing is the evolution of Trend Tracker v1.4. Legacy components that will evolve into this layer:
- `collectors/*` → data input pipeline
- `explainability_processor.py` → Impact Analysis (Tab 3)
- `theme_mapper.py` → event classification

See: [archive/legacy-trend-tracker/LEGACY_MAPPING.md](../../archive/legacy-trend-tracker/LEGACY_MAPPING.md)
