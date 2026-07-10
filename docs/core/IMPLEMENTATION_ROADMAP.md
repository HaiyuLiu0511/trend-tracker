# IMPLEMENTATION_ROADMAP.md — Implementation Roadmap V1

> **Status:** Frozen
> **Frozen Date:** 2026-07-06 (Observation Phase End)
> **Repository Migration Date:** 2026-07-08 to 2026-07-10 (WP2-WP7)
> **Architecture Reference:** [ARCHITECTURE.md](./ARCHITECTURE.md)
> **Engineering Governance Reference:** [ENGINEERING_GOVERNANCE.md](./ENGINEERING_GOVERNANCE.md)

---

## Purpose

本文档定义 Personal Investment Research System 的 Implementation Roadmap V1。

所有 Phase 定义来自已冻结版本（Observation Phase Final Snapshot §8, 2026-07-06）。本文档不新增任何 Phase，不修改已冻结的执行顺序，不重新定义 Phase 内容。

**本文档的职责**：将冻结的 Phase 1-11 执行计划整合为独立文档，并标注当前执行进度，使任何 Agent 只阅读本文档即可理解系统实施全貌。

---

## Roadmap Overview

```
Phase 1:  Architecture Freeze          ✅ Completed
Phase 2:  Documentation                 ✅ Completed
Phase 3:  GitHub First Backup / Release 🔄 In Progress
Phase 4:  Daily Briefing V2             ⬜ Pending
Phase 5:  Research Terminal V1          ⬜ Pending
Phase 6:  Industry Research             ⬜ Pending
Phase 7:  Company Research              ⬜ Pending
Phase 8:  Monthly Outlook               ⬜ Pending
Phase 9:  Evidence & Verification       ⬜ Pending
Phase 10: Source Registry               ⬜ Pending
Phase 11: Investment Mapping            ⬜ Pending
```

---

## Phase Details

### Phase 1: Architecture Freeze

> **Status:** ✅ Completed
> **Completed Date:** 2026-07-06

**目标**：冻结当前系统状态，禁止修改代码/Prompt/Pipeline/HTML。

**内容**：
- 不修改任何代码/Prompt/Pipeline/HTML
- 完成 Documentation Skeleton（Phase 2）

**冻结声明**：以下项目进入 Architecture Freeze：
- `daily-report-*.html` — Daily Briefing V2 输出格式
- `research-terminal-*.html` — Research Terminal V1 输出格式
- `trend-tracker/` — Trend Tracker 所有 Pipeline 代码
- `skills/report-generation/` — 报告生成 Skill
- `skills/daily-briefing/` — 日报生成 Skill
- `skills/trend-tracker/` — Trend Tracker Skill
- `BOOTSTRAP.md` — 启动路由器
- `SOUL.md` — 人格与决策框架

**产出**：[OBSERVATION_PHASE_SNAPSHOT.md](./OBSERVATION_PHASE_SNAPSHOT.md)

---

### Phase 2: Documentation

> **Status:** ✅ Completed
> **Completed Date:** 2026-07-06 (initial), 2026-07-08 (repository migration)

**目标**：建立 docs/ 目录体系，更新 BOOTSTRAP.md / SOUL.md / PLAYBOOKS，补充 Architecture Spec。

**内容**：
- 建立 docs/ 目录体系（10 份文档）
- 更新 BOOTSTRAP.md / SOUL.md / PLAYBOOKS
- 补充 Architecture Spec（每层职责详细说明）

**产出**：
- `docs/core/` — 9 份核心文档（MISSION, ARCHITECTURE, RESEARCH_SYSTEM, GOVERNANCE, REPORT_DESIGN, AGENT_ONBOARDING, REFACTOR_BACKLOG, CHANGELOG, OBSERVATION_PHASE_SNAPSHOT）
- `docs/daily/` — Layer 1 域文档（5 份）
- `docs/research-terminal/` — Layer 2 域文档（5 份）
- `docs/industry/` — Layer 3 域文档（5 份）
- `docs/company/` — Layer 4 域文档（5 份）
- `docs/monthly/` — Layer 5 域文档（5 份）
- `docs/provider/` — DATA_SOURCE.md
- `docs/evidence/` — EVIDENCE_LAYER.md
- `docs/investment-mapping/` — INVESTMENT_MAPPING.md

---

### Phase 3: GitHub First Backup / Release

> **Status:** 🔄 In Progress
> **Started Date:** 2026-07-08

**目标**：所有本地文件同步至 GitHub，建立 Single Source of Truth 规范，打 Tag。

**内容**：
- 所有本地文件同步至 GitHub
- 建立 Single Source of Truth 规范
- 打 Tag：`architecture-baseline-v1`

**当前进度**：

| Step | Status | Description |
|------|--------|-------------|
| WP2 | ✅ Committed (`1abcf71`) | Repository skeleton (directories, .gitkeep, LEGACY_MAPPING.md) |
| WP3 | ✅ Committed (`30db569`) | Documentation baseline (38 docs, Core + Domain structure) |
| WP4 | ✅ Committed (`18c3525`) | Governance migration (Engineering Governance V1, Implementation Roadmap V1) |
| WP1 | ✅ Committed (`7727b6d`) | Repository identity (new README.md) |
| WP5 | ✅ Committed (`fdf131c`) | Legacy archive & mapping (16 files archived) |
| WP7 | ✅ Committed (`5fa8912`) | Artifact protection upgrade (.gitignore, ARTIFACT_MANAGEMENT.md) |
| WP6 | 🔄 In Progress | Architecture baseline verification (cross-reference corrections) |
| WP8 | ⬜ Pending | GitHub baseline tag / release |

**验收标准**：
- 所有本地文件与 GitHub 仓库同步
- Engineering Governance V1 和 Implementation Roadmap 同步至仓库
- 打 Tag：`architecture-baseline-v1`

---

### Phase 4: Daily Briefing V2（重构）

> **Status:** ⬜ Pending

**目标**：基于冻结 Tab 定义，重构内容密度。

**内容**：
- 基于冻结 Tab 定义，重构内容密度
- 强化 Evidence Layer + 可信度标注

**冻结输出格式（V2）**：

| Tab | 名称 | 核心问题 |
|-----|-------|----------|
| Tab 1 | Today's Highlights | 今天发生了什么？ |
| Tab 2 | Market Snapshot | 市场整体状态如何？ |
| Tab 3 | Impact Analysis | 事件的影响链是什么？ |
| Tab 4 | Knowledge Bite | 今天学到了什么？ |
| Tab 5 | Follow-up Tracker | 哪些事需要持续跟踪？ |

**参考文档**：[docs/daily/](../daily/)

---

### Phase 5: Research Terminal V1（重构）

> **Status:** ⬜ Pending

**目标**：明确与日报的边界，重新定义 Tab 2/3 的信息来源和更新频率。

**内容**：
- 明确与日报的边界
- 重新定义 Tab 2/3 的信息来源和更新频率

**冻结输出格式（V1）**：

| Tab | 名称 | 核心问题 |
|-----|-------|----------|
| Tab 1 | Dashboard | 当前研究全景是什么？ |
| Tab 2 | Theme Radar | 哪些主题值得关注？ |
| Tab 3 | Company Radar | 哪些公司值得研究？ |

**关键澄清**：Research Terminal 是 Navigator（导航器），不是 Knowledge Base（知识库）。

**参考文档**：[docs/research-terminal/](../research-terminal/)

---

### Phase 6: Industry Research（新建）

> **Status:** ⬜ Pending

**目标**：定义 Industry Framework 层，建立行业分析模板。

**内容**：
- 定义 Industry Framework 层
- 建立行业分析模板

**参考文档**：[docs/industry/](../industry/)

---

### Phase 7: Company Research（新建）

> **Status:** ⬜ Pending

**目标**：定义 Decision Support 层，建立公司研究模板。

**内容**：
- 定义 Decision Support 层
- 建立公司研究模板

**关键原则**：Company Research 必须建立在 Industry Research 基础之上。

**参考文档**：[docs/company/](../company/)

---

### Phase 8: Monthly Outlook（新建）

> **Status:** ⬜ Pending

**目标**：定义 Knowledge Evolution 层，建立月报模板。

**内容**：
- 定义 Knowledge Evolution 层
- 建立月报模板

**参考文档**：[docs/monthly/](../monthly/)

---

### Phase 9: Evidence & Verification（重构）

> **Status:** ⬜ Pending

**目标**：建立 Evidence Layer 验证机制，统一可信度标注标准。

**内容**：
- 建立 Evidence Layer 验证机制
- 统一可信度标注标准

**可信度标注体系**：

| 标签 | 级别 | 说明 |
|------|------|------|
| 🟢 | HIGH | 官方数据 / API 直接获取 / 已验证 |
| 🟡 | MEDIUM | 可靠二手来源 / 估算但有依据 |
| 🟠 | LOW-MEDIUM | WebSearch 结果 / 需进一步验证 |
| 🔴 | LOW | 推测 / 无直接证据 / 单一非权威来源 |

**参考文档**：[docs/evidence/EVIDENCE_LAYER.md](../evidence/EVIDENCE_LAYER.md)

---

### Phase 10: Source Registry（新建）

> **Status:** ⬜ Pending

**目标**：建立数据源注册表，定义 Provider 路由链。

**内容**：
- 建立数据源注册表
- 定义 Provider 路由链

**Provider 路由链**：

```
P0: westock-mcp (腾讯自选股 MCP)
  ↓ (失败或无数据)
P1: finmind-data (FinMind API)
  ↓ (失败或无数据)
P2: WebSearch
  ↓ (失败或无数据)
P3: WebFetch
```

**参考文档**：[docs/provider/DATA_SOURCE.md](../provider/DATA_SOURCE.md)

---

### Phase 11: Investment Mapping（新建）

> **Status:** ⬜ Pending

**目标**：建立投资地图载体，定义认知积累格式。

**内容**：
- 建立投资地图载体
- 定义认知积累格式

**参考文档**：[docs/investment-mapping/INVESTMENT_MAPPING.md](../investment-mapping/INVESTMENT_MAPPING.md)

---

## Execution Order Principle

> **Source:** OBSERVATION_PHASE_SNAPSHOT.md §8, ARCHITECTURE_MIGRATION_BLUEPRINT_V1.0_FINAL.md

**严格顺序执行，禁止跳过 Phase：**

```
Phase 1 (Freeze) → Phase 2 (Docs) → Phase 3 (GitHub) → Phase 4 (Daily V2)
  → Phase 5 (Terminal V1) → Phase 6 (Industry) → Phase 7 (Company)
  → Phase 8 (Monthly) → Phase 9 (Evidence) → Phase 10 (Source Registry)
  → Phase 11 (Investment Mapping)
```

**依赖关系**：
- Phase 4+ 依赖 Phase 3 完成（GitHub = Single Source of Truth）
- Phase 7 依赖 Phase 6 完成（Company Research 建立在 Industry Research 基础上）
- Phase 9 可与 Phase 4-8 并行，但必须在 Phase 4-8 完成前完成
- Phase 11 依赖 Phase 7 完成（投资地图需要公司研究基础）

---

## Current Position

```
Phase 1: Architecture Freeze          ✅ Done
Phase 2: Documentation                 ✅ Done
Phase 3: GitHub First Backup / Release 🔄 Here (WP6 — Baseline Verification)
Phase 4-11:                            ⬜ Future
```

**当前执行**：Architecture Migration（WP2-WP8），属于 Phase 3 的子任务。WP2-WP5、WP7 已完成并提交，WP6 进行中。

**下一步**：完成 WP6 → WP8 (Tag & Release) → Phase 3 Complete → Phase 4 (Daily Briefing V2 重构)

---

## Related Documents

- [ENGINEERING_GOVERNANCE.md](./ENGINEERING_GOVERNANCE.md) — Engineering Governance V1（执行规则来源）
- [OBSERVATION_PHASE_SNAPSHOT.md](./OBSERVATION_PHASE_SNAPSHOT.md) — 冻结基线快照（Phase 定义来源）
- [ARCHITECTURE.md](./ARCHITECTURE.md) — 五层架构（Phase 4-8 实施目标）
- [REFACTOR_BACKLOG.md](./REFACTOR_BACKLOG.md) — 重构待办清单（8 个已知问题）
- [CHANGELOG.md](./CHANGELOG.md) — 变更记录

---

*本文档整合自已冻结的 Implementation Roadmap V1。Phase 1-11 定义来自 Observation Phase Final Snapshot §8 (2026-07-06)。不新增任何 Phase，不修改已冻结的执行顺序。当前进度标注反映 2026-07-08 的系统状态。*
