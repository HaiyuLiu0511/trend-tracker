# Roadmap — Daily Briefing

> **Layer:** 1 — Event Layer
> **Implementation Phase:** Phase 4

---

## Current State

- V2 format frozen (5 Tabs)
- Legacy Trend Tracker pipeline archived with Legacy Mapping
- No new implementation yet (Architecture Baseline phase)

## Planned Implementation (Phase 4)

1. Rebuild daily briefing pipeline based on frozen V2 Tab definitions
2. Refactor content density (P0-001: content too heavy, low information density)
3. Strengthen Evidence Layer + confidence annotation (P0-003)
4. Integrate with Provider Routing Chain
5. Establish Knowledge Bite quality standard

## Dependencies

- Architecture Baseline V1 (current phase)
- Provider Routing Chain (Phase 10)
- Evidence Layer verification mechanism (Phase 9)

## Evolution from Legacy

- `collectors/arxiv_collector.py` → `src/collectors/arxiv.py`
- `collectors/github_collector.py` → `src/collectors/github.py`
- `collectors/techcrunch_collector.py` → `src/collectors/techcrunch.py`
- `collectors/reuters_collector.py` → `src/collectors/reuters.py`
- `explainability_processor.py` → `src/processors/impact_analyzer.py`

See: [archive/legacy-trend-tracker/LEGACY_MAPPING.md](../../archive/legacy-trend-tracker/LEGACY_MAPPING.md)
