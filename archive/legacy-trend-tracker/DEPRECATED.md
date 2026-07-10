# DEPRECATED — Trend Tracker v1.4 Legacy Archive

> **Status:** DEPRECATED — This directory contains archived legacy code from Trend Tracker v1.4.
> **Archived:** 2026-07-09 (WP5 — Legacy Archive & Mapping)
> **Evolution:** Trend Tracker is not abandoned. It is the first completed Domain of Personal Investment Research System.

---

## What Is Archived

This directory contains 16 files from the Trend Tracker v1.4 repository, migrated here during WP5 (Legacy Archive & Mapping) as part of the Architecture Baseline Migration.

### Repository Code Components (13 files)

| File | Evolution Path | Future Module |
|------|---------------|---------------|
| `collectors/arxiv_collector.py` | **EVOLVE** | `src/collectors/arxiv.py` |
| `collectors/github_collector.py` | **EVOLVE** | `src/collectors/github.py` |
| `collectors/techcrunch_collector.py` | **EVOLVE** | `src/collectors/techcrunch.py` |
| `collectors/reuters_collector.py` | **EVOLVE** | `src/collectors/reuters.py` |
| `processors/theme_mapper.py` | **EVOLVE** | `src/processors/theme_classifier.py` |
| `processors/company_mapper.py` | **EVOLVE** | `src/processors/company_resolver.py` |
| `processors/explainability_processor.py` | **EVOLVE** | `src/processors/impact_analyzer.py` |
| `processors/theme_registry_mapper.py` | **EVOLVE** | `src/processors/theme_normalizer.py` |
| `pipeline_mock.py` | **REFERENCE** | — (architecture concept reference) |
| `pipeline_real.py` | **REFERENCE** | — (architecture concept reference) |
| `db/db_init_v1.1.sql` | **EVOLVE** | `config/schema/` |
| `db/migrations/001_company_layer.sql` | **REFERENCE** | `config/schema/migrations/` |
| `db/migrations/002_theme_registry.sql` | **REFERENCE** | `config/schema/migrations/` |

### Documentation Components (3 files)

| File | Evolution Path | Superseded By |
|------|---------------|---------------|
| `README.md` | **REPLACED** | Root `README.md` (Personal Investment Research System) |
| `ROADMAP.md` | **REPLACED** | `docs/core/IMPLEMENTATION_ROADMAP.md` |
| `docs/ARCHITECTURE.md` | **REPLACED** | `docs/core/ARCHITECTURE.md` |

---

## Why Archived (Not Deleted)

Trend Tracker v1.4 is the **first completed Domain** of Personal Investment Research System — not a discarded system. The code in this archive contains:

1. **Reusable patterns** — Data collection, theme classification, company resolution, impact scoring
2. **Knowledge assets** — 8-theme taxonomy, company alias map, impact scoring weights, theme normalization rules
3. **Architecture reference** — 10-stage pipeline structure informs (but does not directly map to) the new 5-layer architecture

Future developers MUST consult [LEGACY_MAPPING.md](./LEGACY_MAPPING.md) before building new modules to understand which patterns to preserve and which to change.

---

## Evolution Path Definitions

| Path | Count | Meaning |
|------|-------|---------|
| **EVOLVE** | 9 | Code patterns/knowledge assets directly reusable. Will be refactored into `src/` modules. |
| **REFERENCE** | 6 | Architecture concepts informative. Code not directly reusable. |
| **REPLACED** | 3 | Functionality fully superseded by new repository documents. |
| **OBSOLETE** | 0 | (No obsolete components in repository — 1 obsolete component exists in local skill files only) |

---

## Git History

All files in this archive preserve their Git history via `git mv` (15 files) or content retrieval from Git history (1 file — `README.md`, whose original content was replaced in WP1 before archival).

- **Original commit:** `0949721` — `feat: add theme registry enhancement and architecture baseline`
- **Archived in:** WP5 — Legacy Archive & Mapping (2026-07-09)

---

## Related Documents

- [LEGACY_MAPPING.md](./LEGACY_MAPPING.md) — Full mapping table with future module paths
- [../../docs/core/ENGINEERING_GOVERNANCE.md](../../docs/core/ENGINEERING_GOVERNANCE.md) — Engineering Governance V1 (supersedes Observation Phase governance)
- [../../docs/core/ARCHITECTURE.md](../../docs/core/ARCHITECTURE.md) — New five-layer architecture (supersedes legacy `docs/ARCHITECTURE.md`)
- [../../README.md](../../README.md) — Repository identity (Personal Investment Research System)

---

*This document is the entry point for the legacy archive. Any code in this directory should be treated as reference material, not production code.*
