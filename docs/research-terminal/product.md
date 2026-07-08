# Product — Research Terminal

> **Layer:** 2 — Research Navigator
> **Status:** Frozen (V1, 2026-07-06)
> **Architecture Reference:** [core/ARCHITECTURE.md](../core/ARCHITECTURE.md)

---

## Responsibility

Research entry point, quick navigation to themes or companies, does NOT store knowledge content.

## Critical Clarification

> **Research Terminal is a Navigator, NOT a Knowledge Base.**
> Its purpose is to help users quickly find themes and companies worth researching, not to store deep analysis content.

## What This Layer Is

- Research navigation dashboard
- Theme radar (which themes deserve attention)
- Company radar (which companies deserve research)
- Research priority ranking

## What This Layer Is NOT

- Knowledge Base (deep content storage)
- Industry Report (belongs to Layer 3)
- Company Profile (belongs to Layer 4)
- News aggregator

## Frozen Output Format (V1)

| Tab | Name | Core Question |
|-----|------|---------------|
| Tab 1 | Dashboard | What is the current research landscape? |
| Tab 2 | Theme Radar | Which themes deserve attention? |
| Tab 3 | Company Radar | Which companies deserve research? |

## Deliverable

`research-terminal-YYYY-MM-DD.html`

## Evolution from Trend Tracker

- `theme_mapper.py` → Theme Radar (Tab 2) concept
- `company_mapper.py` → Company Radar (Tab 3) concept
- `theme_registry_mapper.py` → theme normalization

See: [archive/legacy-trend-tracker/LEGACY_MAPPING.md](../../archive/legacy-trend-tracker/LEGACY_MAPPING.md)
