# CHANGELOG.md — 系统变更记录

> Documentation Skeleton — Phase2 (Documentation)
> Status: Initialized, entries to be added as system evolves

---

## Table of Contents

1. [Purpose](#purpose)
2. [Scope](#scope)
3. [Current Status](#current-status)
4. [Future Expansion](#future-expansion)
5. [Changelog Format](#changelog-format)
6. [Entries](#entries)
7. [Related Documents](#related-documents)

---

## Purpose

记录 Personal Investment Research System 的所有变更。

本文档是系统演化的历史记录。任何架构变更、报告格式变更、Skill Prompt 变更、Pipeline 代码变更，都必须记录至本文档。

---

## Scope

- 变更记录格式定义
- 所有变更条目（按时间倒序）
- 变更类型分类
- 变更影响的文档/代码

---

## Current Status

| 字段 | 内容 |
|------|------|
| Phase | 2 (Documentation) |
| 状态 | 已初始化，Observation Phase 条目已添加 |
| 最后更新 | 2026-07-06 |
| 下一步 | 每次变更后更新本文档 |

---

## Future Expansion

- [ ] 添加变更影响分析（哪些文档/代码受影响）
- [ ] 添加变更回滚记录（如果变更被回滚）
- [ ] 添加变更与 GitHub Commit 的对应关系

---

## Changelog Format

```markdown
## [版本号] - YYYY-MM-DD

### Added（新增）
- ...

### Changed（变更）
- ...

### Deprecated（弃用）
- ...

### Removed（移除）
- ...

### Fixed（修复）
- ...

### Affected Documents/Code（受影响文件）
- ...
```

**版本号规则**：
- 架构变更：`v{Major}.{Minor}`（例：`v1.0`）
- 报告格式变更：`v{Major}.{Minor}`（例：`v2.1`）
- Skill Prompt 变更：`v{Minor}`（例：`v2.1.1`）
- Pipeline 代码变更：`v{Minor}`（例：`v2.1.2`）

---

## Entries

### [Governance Migration] - 2026-07-08

#### Added
- `docs/core/ENGINEERING_GOVERNANCE.md` — Engineering Governance V1 (9 sub-items: Core Philosophy, Architecture Principles, Development Standard, AEW, Quality Gates, Documentation Governance, Git Workflow, Repository Structure, Artifact Management)
- `docs/core/IMPLEMENTATION_ROADMAP.md` — Implementation Roadmap V1 (Phase 1-11 with current progress annotations)

#### Changed
- `docs/core/GOVERNANCE.md` — Updated governance framework overview to reference ENGINEERING_GOVERNANCE.md and IMPLEMENTATION_ROADMAP.md; added EVIDENCE_LAYER.md to related documents
- `docs/README.md` — Updated core documentation table (11 docs), cross-reference map, and developer reference order to include new governance docs

#### Affected Documents
- `docs/core/ENGINEERING_GOVERNANCE.md` — New (Engineering Governance V1, 9 sub-items)
- `docs/core/IMPLEMENTATION_ROADMAP.md` — New (Phase 1-11 roadmap with progress)
- `docs/core/GOVERNANCE.md` — Modified (governance framework overview + related documents)
- `docs/README.md` — Modified (navigation table + cross-reference map + developer reference)

---

### [Architecture Baseline Migration] - 2026-07-08

#### Added
- Documentation migrated to GitHub repository (Single Source of Truth)
- Core documentation established in `docs/core/` (9 documents)
- Domain documentation established for all 5 layers (25 documents)
- Cross-cutting documentation established: `docs/provider/`, `docs/evidence/`, `docs/investment-mapping/`
- Documentation navigation (`docs/README.md`) with complete cross-reference map
- LEGACY_MAPPING.md in `archive/legacy-trend-tracker/` (WP2)
- Repository skeleton: `src/`, `config/`, `examples/`, `scripts/`, `tests/`, `archive/` (WP2)

#### Changed
- Trend Tracker v1.4 evolved into Personal Investment Research System (first domain → five-layer system)
- Documentation structure reorganized from flat to Core + Domain architecture
- WP2 placeholder docs (`docs/domains/`) replaced with proper domain documentation
- Repository structure upgraded to frozen standard (7 directories)

#### Evolution Note
Trend Tracker is not abandoned — it is the first completed Domain of Personal Investment Research System. Legacy components are archived with Legacy Mapping for future evolution. Git history, knowledge, and architecture maintain continuity.

#### Affected Documents/Code
- `docs/core/` — 9 migrated documents (MISSION, ARCHITECTURE, RESEARCH_SYSTEM, GOVERNANCE, REPORT_DESIGN, AGENT_ONBOARDING, REFACTOR_BACKLOG, CHANGELOG, OBSERVATION_PHASE_SNAPSHOT)
- `docs/daily/` — 5 Daily Briefing domain docs (product, architecture, workflow, roadmap, decisions)
- `docs/research-terminal/` — 5 Research Terminal domain docs
- `docs/industry/` — 5 Industry Research domain docs
- `docs/company/` — 5 Company Research domain docs
- `docs/monthly/` — 5 Monthly Outlook domain docs
- `docs/provider/` — DATA_SOURCE.md
- `docs/evidence/` — EVIDENCE_LAYER.md
- `docs/investment-mapping/` — INVESTMENT_MAPPING.md
- `docs/README.md` — Documentation navigation
- `archive/legacy-trend-tracker/LEGACY_MAPPING.md` — Legacy component mapping

---

### [Observation Phase End] - 2026-07-06

#### Added
- 建立 Documentation 体系（Phase 2）
  - 新增文档：`README.md`, `MISSION.md`, `ARCHITECTURE.md`, `REPORT_DESIGN.md`, `RESEARCH_SYSTEM.md`, `GOVERNANCE.md`, `DATA_SOURCE.md`, `CHANGELOG.md`, `AGENT_ONBOARDING.md`, `REFACTOR_BACKLOG.md`
  - 更新文档：`OBSERVATION_PHASE_FINAL_SNAPSHOT.md`

#### Changed
- 五层架构术语澄清：
  - Research Terminal = Research Navigator（不是 Knowledge Base）
  - Industry Research = Industry Framework（不是 Industry Report）
  - Company Research 必须建立在 Industry Research 基础之上
  - Monthly Outlook = Knowledge Evolution（不是新闻汇总）
- 新增 Knowledge Flow 定义（Daily → Research Terminal → Industry → Company → Monthly）
- 新增 GitHub = Single Source of Truth 原则
- 新增工程流程定义（Discussion → Architecture Freeze → Documentation → GitHub → Implementation）

#### Affected Documents/Code
- `OBSERVATION_PHASE_FINAL_SNAPSHOT.md`（更新）
- `~/.workbuddy/docs/`（新增 10 份文档）

---

### [Observation Phase] - 2026-05 to 2026-07

#### Added
- Daily Briefing V2（5 Tabs 冻结）
- Research Terminal V1（3 Tabs 冻结）
- 五层架构设计（Event Layer → Research Navigator → Industry Framework → Decision Support → Knowledge Evolution）
- Observation Phase 核心问题识别（8 个问题）

#### Changed
- 项目定位从"日报生成系统"演进为"认知积累研究系统"

#### Affected Documents/Code
- `skills/daily-briefing/`
- `skills/trend-tracker/`
- `~/.workbuddy/frameworks/`

---

## Related Documents

- [README.md](./README.md) — 文档体系入口
- [ARCHITECTURE.md](./ARCHITECTURE.md) — 架构变更记录（本文档引用）
- [GOVERNANCE.md](./GOVERNANCE.md) — 变更管理流程（本文档遵循）
- [REFACTOR_BACKLOG.md](./REFACTOR_BACKLOG.md) — 重构待办（变更需求来源）

---

*本文档随系统演化持续更新。任何变更都必须先记录至本文档，再实施。*
