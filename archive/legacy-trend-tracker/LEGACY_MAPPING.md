# Legacy Mapping — Trend Tracker v1.4

> **Status:** REFERENCE DOCUMENT (not deprecated — this is the bridge between legacy code and future implementation)
> **Created:** WP2 — Repository Structure Migration
> **Source:** Architecture Migration Blueprint V1.0 Final §5
> **Purpose:** Document which Trend Tracker components will evolve in the new architecture, which are reference only, which are replaced, and which are obsolete. Future developers MUST consult this document before building new modules.

---

## Evolution Path Definitions

| Path | Meaning | Action |
|------|---------|--------|
| **EVOLVE** | Code patterns/knowledge assets directly reusable. Will be refactored into `src/` modules in future implementation phases. | Archive + Map |
| **REFERENCE** | Architecture concepts or patterns informative for future development. Code not directly reusable but serves as design reference. | Archive |
| **REPLACED** | Functionality fully superseded by new repository documents. No evolution needed. | DEPRECATED locally |
| **OBSOLETE** | No equivalent in new architecture. | DEPRECATED locally |

---

## Repository Code Components

| Legacy Component | Lines | Current Function | Future Module | Evolution Path |
|-----------------|-------|-----------------|---------------|----------------|
| `collectors/arxiv_collector.py` | 109 | Fetch AI/ML papers from arXiv API | `src/collectors/arxiv.py` (Layer 1: Daily Briefing data input) | **EVOLVE** — Data collection pattern reusable. Will be refactored to output Event Layer schema. |
| `collectors/github_collector.py` | 74 | Fetch trending AI repos from GitHub API | `src/collectors/github.py` (Layer 1: Daily Briefing data input) | **EVOLVE** — GitHub trending detection pattern reusable. |
| `collectors/techcrunch_collector.py` | 112 | Fetch AI/startup news from TechCrunch RSS | `src/collectors/techcrunch.py` (Layer 1: Daily Briefing data input) | **EVOLVE** — RSS parsing + keyword filtering pattern reusable. |
| `collectors/reuters_collector.py` | 27 | Build search queries for Reuters news | `src/collectors/reuters.py` (Layer 1: Daily Briefing data input) | **EVOLVE** — Query template pattern reusable. |
| `processors/theme_mapper.py` | 171 | Keyword-based event→theme classification (8 themes) | `src/processors/theme_classifier.py` (Layer 2: Research Terminal Theme Radar) | **EVOLVE** — Theme classification concept reusable. Will be refactored to dynamic theme registry + keyword+LLM hybrid. |
| `processors/company_mapper.py` | 130 | Map raw company names to canonical IDs via alias table | `src/processors/company_resolver.py` (Layer 2: Research Terminal Company Radar + Layer 4: Company Research) | **EVOLVE** — Company alias resolution pattern highly reusable. ALIAS_MAP is a knowledge asset. |
| `processors/explainability_processor.py` | 207 | Compute impact scores (source_tier, event_type, amount_usd weights) | `src/processors/impact_analyzer.py` (Layer 1: Daily Briefing Tab 3 Impact Analysis) | **EVOLVE** — Impact scoring weights (SOURCE_SCORES, EVENT_TYPE_SCORES) are knowledge assets. |
| `processors/theme_registry_mapper.py` | 157 | Alias→canonical theme normalization (Data Governance pass-through) | `src/processors/theme_normalizer.py` (Cross-layer: Data Governance) | **EVOLVE** — Theme normalization pattern reusable. |
| `pipeline_mock.py` | 671 | 10-stage mock pipeline | Reference only — Daily Briefing pipeline will be rebuilt from scratch | **REFERENCE** — Architecture concept valuable, but 10-stage structure replaced by 5-layer. Code not directly reusable. |
| `pipeline_real.py` | 763 | 10-stage real pipeline with live data collection | Reference only — same as pipeline_mock.py | **REFERENCE** — Real data collection patterns (API calls, rate limiting) may inform future implementation. |
| `db/db_init_v1.1.sql` | 214 | SQLite schema: 9 tables | `config/schema/` (future database schema) | **EVOLVE** — Table concepts (events, themes, companies) map to new architecture. Schema will be redesigned but entity concepts reusable. |
| `db/migrations/001_company_layer.sql` | 215 | Company layer migration | `config/schema/migrations/` (future) | **REFERENCE** — Migration pattern informative but specific schema outdated. |
| `db/migrations/002_theme_registry.sql` | 108 | Theme registry migration | `config/schema/migrations/` (future) | **REFERENCE** — Same as above. |

---

## Repository Documentation Components

| Legacy Component | Lines | Current Function | Future Module | Evolution Path |
|-----------------|-------|-----------------|---------------|----------------|
| `README.md` | 414 | Trend Tracker v1.4 repository README | `README.md` (repository root — already replaced in WP1) | **REPLACED** — Fully superseded by new Personal Investment Research System README. |
| `ROADMAP.md` | 99 | Trend Tracker v1.1-v1.5 version roadmap | `docs/core/IMPLEMENTATION_ROADMAP.md` (already created in WP4) | **REPLACED** — Fully superseded by Implementation Roadmap V1. |
| `docs/ARCHITECTURE.md` | 520 | Trend Tracker v1.4 10-stage Pipeline architecture | `docs/core/ARCHITECTURE.md` (already created in WP3) | **REPLACED** — Fully superseded by five-layer architecture document. |

---

## Skill Files (Local — not in GitHub repository)

| Legacy Component | Lines | Current Function | Future Module | Evolution Path |
|-----------------|-------|-----------------|---------------|----------------|
| `SKILL.md` | 1,258 | Trend Tracker V3.1 Skill definition | `skills/daily-briefing/` (future WorkBuddy skill) | **REFERENCE** — Governance rules and pipeline structure are reference material. New skill will be built from Architecture Baseline. |
| `BOOTSTRAP.md` | 654 | Observation Phase bootstrap instructions | `docs/AGENT_ONBOARDING.md` (already migrated) | **REPLACED** — Agent onboarding is now defined in repository docs. Fully superseded. |
| `OBSERVATION_GOVERNANCE.md` | 451 | Observation Phase exit criteria and governance | `docs/ENGINEERING_GOVERNANCE.md` (to be created in WP4) | **REPLACED** — Engineering Governance V1 will supersede all Observation Phase governance. |
| `scripts/trend_tracker.py` | 1,579 | V3.1 data engine — main pipeline | `src/pipelines/daily_briefing.py` (future) | **REFERENCE** — Data processing patterns are reference. Code structure not directly reusable due to architecture change. |
| `scripts/evidence_layer.py` | 825 | Evidence layer implementation | `src/core/evidence.py` (future) | **EVOLVE** — Evidence layer concept is critical to new architecture. Source tracking and confidence scoring patterns are reusable. |
| `scripts/report_renderer.py` | 262 | HTML report rendering | `src/renderers/` (future) | **REFERENCE** — Rendering patterns are reference. Will be rebuilt with new Tab formats. |
| `scripts/backfill_20260615.py` | 174 | Historical data backfill | `scripts/backfill.py` (future utility) | **REFERENCE** — Backfill pattern informative but specific to old pipeline. |
| `scripts/promote_20260615.py` | 67 | Data promotion script | — | **OBSOLETE** — No equivalent in new architecture. |

---

## Summary

| Evolution Path | Count | Components |
|---------------|-------|------------|
| **EVOLVE** | 9 | 4 collectors + 4 processors + 1 db schema + 1 skill script (evidence_layer) |
| **REFERENCE** | 6 | 2 pipelines + 2 db migrations + 1 skill + 1 skill script (trend_tracker) + 1 renderer + 1 backfill |
| **REPLACED** | 5 | 2 skill files (BOOTSTRAP.md + OBSERVATION_GOVERNANCE.md) + 3 documentation files (README.md + ROADMAP.md + docs/ARCHITECTURE.md) |
| **OBSOLETE** | 1 | promote_20260615.py |

---

## Knowledge Assets to Preserve

The following are knowledge assets embedded in legacy code that MUST be referenced when building new modules:

| Asset | Location | Description |
|-------|----------|-------------|
| **8 Theme Taxonomy** | `processors/theme_mapper.py` | AI, Infra/Cloud, Semiconductor, Robot/Auto, Biotech, FinTech, CyberSec, Quantum — classification keywords |
| **Company Alias Map** | `processors/company_mapper.py` | Canonical company names → aliases mapping (e.g., "Google" → "Alphabet") |
| **Impact Scoring Weights** | `processors/explainability_processor.py` | SOURCE_SCORES, EVENT_TYPE_SCORES — weight tables for impact analysis |
| **Theme Normalization Rules** | `processors/theme_registry_mapper.py` | Alias→canonical theme mapping for data governance |
| **Evidence Layer Pattern** | `scripts/evidence_layer.py` (local skill) | Source tracking, confidence scoring, evidence chain |
| **Database Entity Model** | `db/db_init_v1.1.sql` | Events, themes, companies, signals, trends — entity relationships |
| **arXiv API Pattern** | `collectors/arxiv_collector.py` | Search query construction, rate limiting, result parsing |
| **GitHub API Pattern** | `collectors/github_collector.py` | Trending repo detection, star/commit analysis |

---

*This document was created in WP2 (Repository Structure Migration) as a reference. Code archiving was completed in WP5 (Legacy Archive & Mapping) on 2026-07-09. All 16 repository files are now archived in this directory. Local skill files (8 files) are marked as DEPRECATED locally — see §5.2 of the Architecture Migration Blueprint V1.0 Final.*
