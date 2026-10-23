# Roadmap — Daily Briefing

> **Layer:** 1 — Event Layer
> **Implementation Phase:** Phase 4 — Implementation Complete; Exit Closeout Pending

---

## Current State

- V2 format frozen (5 Tabs)
- Legacy Trend Tracker pipeline archived with Legacy Mapping
- Phase 4 implementation complete (Slice 1–5, 2026-10-20 → 2026-10-23): five-tab renderer + input contract, reusable Event Contract, deterministic minimum pipeline, input preparation guide, input fidelity review tool
- Phase 4 **exit closeout pending final gate** — Phase 4 is not yet formally CLOSED, and Phase 5 has not started

## Planned Implementation (Phase 4)

> **Status as of 2026-10-23.** Items 1, 2 and 5 are implemented; items 3 and 4 remain **Pending** and are owned by Phase 9 and Phase 10 respectively. The confidence-annotation capability delivered in Phase 4 does **not** implement the Evidence Layer verification mechanism (Phase 9) or the Source Registry / Provider routing chain (Phase 10).

1. Rebuild daily briefing pipeline based on frozen V2 Tab definitions — ✅ **Implemented** (Slice 1 renderer + Slice 3 deterministic pipeline; `src/daily_briefing/`)
2. Refactor content density (P0-001: content too heavy, low information density) — 🟡 **Mechanised** — the 500-word-per-Tab budget is enforced in code (`WORD_LIMIT = 500`); the content-quality criteria (Tab 4 must carry substantive cognitive content, Tab 5 must be actionable) are human-judged and documented in `INPUT_PREPARATION.md`, so BACKLOG-001 remains **Pending**
3. Strengthen Evidence Layer + confidence annotation (P0-003) — ⬜ **Pending — owned by Phase 9.** Phase 4 delivers annotation only (confidence badge, source line, explicit missing-data marking, fallback requiring a real routing record); the Evidence Layer **verification mechanism** is not implemented, and BACKLOG P0-003 stays **Pending**
4. Integrate with Provider Routing Chain — ⬜ **Pending — owned by Phase 10.** No Source Registry and no Provider routing chain exist in Phase 4; the contract only requires that any fallback already present in the input carry a real routing record
5. Establish Knowledge Bite quality standard — ✅ **Implemented** (Research Quality Requirements in `INPUT_PREPARATION.md`); the standard is defined, but whether each bite actually carries cognitive value remains human-judged

## Dependencies

- Architecture Baseline V1 (completed 2026-07-06)
- Provider Routing Chain (Phase 10) — not implemented
- Evidence Layer verification mechanism (Phase 9) — not implemented

## Evolution from Legacy

> **Historical evolution reference only.** The targets below are the intended future destinations of the archived Trend Tracker v1.4 components; **they do not exist in the current codebase**. See [archive/legacy-trend-tracker/LEGACY_MAPPING.md](../../archive/legacy-trend-tracker/LEGACY_MAPPING.md) for the full mapping and the per-component evolution path of every entry.

- `collectors/arxiv_collector.py` → `src/collectors/arxiv.py`
- `collectors/github_collector.py` → `src/collectors/github.py`
- `collectors/techcrunch_collector.py` → `src/collectors/techcrunch.py`
- `collectors/reuters_collector.py` → `src/collectors/reuters.py`
- `explainability_processor.py` → `src/processors/impact_analyzer.py`

See: [archive/legacy-trend-tracker/LEGACY_MAPPING.md](../../archive/legacy-trend-tracker/LEGACY_MAPPING.md)
