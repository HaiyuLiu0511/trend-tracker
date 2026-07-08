# Roadmap — Research Terminal

> **Layer:** 2 — Research Navigator
> **Implementation Phase:** Phase 5

---

## Current State

- V1 format frozen (3 Tabs)
- Navigator positioning clarified (not Knowledge Base)
- No new implementation yet (Architecture Baseline phase)

## Planned Implementation (Phase 5)

1. Clarify boundary with Daily Briefing (P0-002)
2. Define Tab 2/3 information sources and update frequency
3. Build theme and company radar pipeline
4. Establish navigation links to Layer 3/4

## Dependencies

- Architecture Baseline V1 (current phase)
- Daily Briefing V2 (Phase 4) — provides Follow-up Tracker input

## Evolution from Legacy

- `theme_mapper.py` → `src/processors/theme_classifier.py` (Theme Radar)
- `company_mapper.py` → `src/processors/company_resolver.py` (Company Radar)
- `theme_registry_mapper.py` → `src/processors/theme_normalizer.py`

See: [archive/legacy-trend-tracker/LEGACY_MAPPING.md](../../archive/legacy-trend-tracker/LEGACY_MAPPING.md)
