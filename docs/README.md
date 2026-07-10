# Personal Investment Research System — Documentation

> **Status:** Architecture Baseline V1 — Documentation migrated to GitHub
> **Last Updated:** 2026-07-08
> **Phase:** Implementation Phase

---

## Documentation Navigation

This is the single entry point for all documentation. Any new Agent should start here.

### Core Documentation (`core/`)

| Document | Purpose | Status |
|----------|---------|--------|
| [MISSION.md](./core/MISSION.md) | System mission, objectives, success criteria | Frozen |
| [ARCHITECTURE.md](./core/ARCHITECTURE.md) | Five-layer architecture, layer responsibilities, interfaces | Frozen |
| [RESEARCH_SYSTEM.md](./core/RESEARCH_SYSTEM.md) | Knowledge Flow, cognitive accumulation mechanism | Frozen |
| [GOVERNANCE.md](./core/GOVERNANCE.md) | Governance framework: architecture, data, methodology, provider, visual | Frozen |
| [ENGINEERING_GOVERNANCE.md](./core/ENGINEERING_GOVERNANCE.md) | Engineering Governance V1: Core Philosophy, Architecture Principles, Development Standard, AEW, Quality Gates, Documentation Governance, Git Workflow, Repository Structure, Artifact Management | Frozen |
| [IMPLEMENTATION_ROADMAP.md](./core/IMPLEMENTATION_ROADMAP.md) | Implementation Roadmap V1: Phase 1-11 execution plan with current progress | Frozen |
| [REPORT_DESIGN.md](./core/REPORT_DESIGN.md) | Report design principles: structure, visual, evidence, methodology | Frozen |
| [AGENT_ONBOARDING.md](./core/AGENT_ONBOARDING.md) | New Agent onboarding guide and required reading list | Frozen |
| [REFACTOR_BACKLOG.md](./core/REFACTOR_BACKLOG.md) | Refactor backlog (8 items from Observation Phase) | Populated |
| [CHANGELOG.md](./core/CHANGELOG.md) | System change log | Updated |
| [OBSERVATION_PHASE_SNAPSHOT.md](./core/OBSERVATION_PHASE_SNAPSHOT.md) | Observation Phase final snapshot — freeze baseline | Frozen |
| [ARTIFACT_MANAGEMENT.md](./core/ARTIFACT_MANAGEMENT.md) | Artifact classification, .gitignore coverage, Git Hygiene Checklist | Active |

### Domain Documentation

| Domain | Directory | Layer | Responsibility |
|--------|-----------|-------|----------------|
| Daily Briefing | [daily/](./daily/) | Layer 1 — Event Layer | Daily information intake + event marking |
| Research Terminal | [research-terminal/](./research-terminal/) | Layer 2 — Research Navigator | Theme/company navigation, not knowledge storage |
| Industry Research | [industry/](./industry/) | Layer 3 — Industry Framework | Industry analysis framework, reusable |
| Company Research | [company/](./company/) | Layer 4 — Decision Support | Company deep research + investment decision |
| Monthly Outlook | [monthly/](./monthly/) | Layer 5 — Knowledge Evolution | Monthly cognitive evolution + investment map update |

### Cross-Cutting Documentation

| Document | Directory | Purpose |
|----------|-----------|---------|
| Data Source Registry | [provider/](./provider/) | Provider routing chain, data source registry |
| Evidence Layer | [evidence/](./evidence/) | Evidence verification, confidence scoring standards |
| Investment Mapping | [investment-mapping/](./investment-mapping/) | Investment map, cognitive accumulation carrier |

---

## Cross-Reference Map

```
README.md (this file — entry point)
├── core/MISSION.md (why this system exists)
├── core/ARCHITECTURE.md (how the system is designed)
│   ├── core/REPORT_DESIGN.md (how reports are designed)
│   ├── core/RESEARCH_SYSTEM.md (how knowledge flows)
│   └── core/REFACTOR_BACKLOG.md (known architecture issues)
├── core/GOVERNANCE.md (governance rules)
│   ├── core/ENGINEERING_GOVERNANCE.md (engineering governance V1 — 9 sub-items)
│   ├── core/IMPLEMENTATION_ROADMAP.md (implementation phases 1-11)
│   ├── core/ARTIFACT_MANAGEMENT.md (artifact protection & .gitignore coverage)
│   ├── provider/DATA_SOURCE.md (data source governance)
│   └── evidence/EVIDENCE_LAYER.md (evidence governance)
├── core/AGENT_ONBOARDING.md (how to onboard new Agents)
├── core/OBSERVATION_PHASE_SNAPSHOT.md (freeze baseline)
├── daily/ (Layer 1 domain docs)
├── research-terminal/ (Layer 2 domain docs)
├── industry/ (Layer 3 domain docs)
├── company/ (Layer 4 domain docs)
├── monthly/ (Layer 5 domain docs)
├── investment-mapping/ (Investment Mapping docs)
└── core/CHANGELOG.md (change history)
```

---

## Quick Start

**New Agent reading order:**

1. `README.md` (this file) — understand documentation structure
2. `core/MISSION.md` — understand system mission
3. `core/ARCHITECTURE.md` — understand five-layer architecture
4. `core/RESEARCH_SYSTEM.md` — understand Knowledge Flow
5. `core/GOVERNANCE.md` — understand governance rules
6. `core/AGENT_ONBOARDING.md` — understand how to participate

**Developer reference order:**

1. `core/ARCHITECTURE.md` — confirm layer responsibilities
2. `core/ENGINEERING_GOVERNANCE.md` — confirm engineering governance rules
3. `core/IMPLEMENTATION_ROADMAP.md` — confirm current phase and next steps
4. `core/REFACTOR_BACKLOG.md` — understand current issues
5. `provider/DATA_SOURCE.md` — confirm data source rules
6. `core/GOVERNANCE.md` — confirm compliance requirements

---

## Legacy Reference

> **Note:** The legacy Trend Tracker v1.4 architecture document (`docs/ARCHITECTURE.md`) has been archived to `../archive/legacy-trend-tracker/docs/ARCHITECTURE.md` (WP5). The authoritative architecture document is [core/ARCHITECTURE.md](./core/ARCHITECTURE.md). See [archive/legacy-trend-tracker/DEPRECATED.md](../archive/legacy-trend-tracker/DEPRECATED.md) for archival details and evolution mapping.

---

*This document is the Single Source of Truth for documentation navigation. Any new document must be registered here.*
