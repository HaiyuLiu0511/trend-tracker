# ENGINEERING_GOVERNANCE.md — Engineering Governance V1

> **Status:** Frozen
> **Frozen Date:** 2026-07-06 (Observation Phase End)
> **Repository Migration Date:** 2026-07-08 (WP4)
> **Architecture Reference:** [ARCHITECTURE.md](./ARCHITECTURE.md)
> **Governance Reference:** [GOVERNANCE.md](./GOVERNANCE.md)

---

## Purpose

本文档是 Personal Investment Research System 的 Engineering Governance V1 完整定义。

所有内容来自已冻结版本（Observation Phase Final Snapshot, 2026-07-06）。本文档不新增任何规则，不修改任何已冻结原则，不重新定义 Workflow。

**本文档的职责**：将分散在多份冻结文档中的工程治理规则整合为一份独立、完整的 Governance 文档，使 GitHub Repository 成为 Governance 的唯一可信来源。

---

## Table of Contents

1. [Core Philosophy V2](#1-core-philosophy-v2)
2. [Architecture Principles V1](#2-architecture-principles-v1)
3. [Development Standard](#3-development-standard)
4. [Agent Engineering Workflow (AEW)](#4-agent-engineering-workflow-aew)
5. [Quality Gates](#5-quality-gates)
6. [Documentation Governance V1](#6-documentation-governance-v1)
7. [Git Workflow](#7-git-workflow)
8. [Repository Structure](#8-repository-structure)
9. [Artifact Management](#9-artifact-management)

---

## 1. Core Philosophy V2

> **Source:** MISSION.md, OBSERVATION_PHASE_SNAPSHOT.md §1

### Mission Statement

> 能够不断积累投资认知的研究系统，而不是单纯生成日报的工具。

### Core Differences

- 日报是输出（Output），不是目标
- 认知积累（Knowledge Asset）是核心资产
- 系统应支持：事件解读 → 行业框架 → 公司决策 → 知识演化 的完整链路

### Objectives

| # | Objective | Description |
|---|-----------|-------------|
| 1 | 认知积累 | 系统持续积累投资认知，不因 Agent 切换而丢失 |
| 2 | 可追溯决策 | 每个投资决策都有完整的分析链路和证据支持 |
| 3 | 系统化分析 | 行业分析、公司研究基于统一框架，不是临时拼凑 |
| 4 | 持续演化 | 系统认知随时间演化，月度更新投资地图 |

### Non-Goals

- 非量化交易系统
- 非新闻聚合器
- 非投资组合管理工具
- 非聊天机器人

### Engineering Baseline Hierarchy

整个项目必须遵循以下顺序，禁止绕过任何层：

```
Core Philosophy（核心哲学）
    ↓
Architecture Principles（架构原则）
    ↓
Engineering Governance（工程治理）
    ↓
Implementation Roadmap（实施路线图）
    ↓
Implementation（实施）
```

**Source:** PROJECT_UNDERSTANDING_REPORT.md §④

---

## 2. Architecture Principles V1

> **Source:** ARCHITECTURE.md §Design Principles, OBSERVATION_PHASE_SNAPSHOT.md §5

### Six Core Design Principles (Frozen 2026-07-06)

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **One Layer = One Responsibility** | 每层只解决一类问题，不跨层 |
| 2 | **One Tab = One Question** | 每个 Tab 只回答一个核心问题 |
| 3 | **Reports are outputs. Knowledge is the asset.** | 报告是副产品，认知积累是目标 |
| 4 | **GitHub = Single Source of Truth** | 所有层交付物必须同步至 GitHub，本地文件不是权威版本 |
| 5 | **Strict Layer Ordering** | 上层必须建立在下层基础上，不得跳过 |
| 6 | **Architecture Freeze** | 冻结期间不修改代码、Prompt、Pipeline 或 HTML |

### GitHub = Single Source of Truth

> **来源:** ARCHITECTURE.md Design Principle #4, OBSERVATION_PHASE_SNAPSHOT.md §5

**核心原则**：所有层交付物必须同步至 GitHub。本地文件不是权威版本。

**为什么必须如此：**

| 问题 | 没有 GitHub SoT | 有 GitHub SoT |
|------|----------------|--------------|
| 文件版本冲突 | 本地文件与仓库不同步，无法判断哪个是最新 | Git 历史即真理，commit 时间排序 |
| 变更不可追溯 | 修改了什么、为什么修改、谁修改的 — 全部丢失 | Commit message + diff 完整记录 |
| 回滚能力 | 修改出错后无法回退到之前的状态 | `git revert` / `git checkout` 精确回滚 |
| 多 Agent 协作 | 不同 Agent 对同一文件的修改会互相覆盖 | Git 分支 + 合并解决冲突 |
| 架构冻结的可执行性 | "冻结"只是一句口号，无法技术强制 | Git Tag 标记冻结点 |

### Architecture Freeze Rules

> **Source:** GOVERNANCE.md §Architecture Governance, OBSERVATION_PHASE_SNAPSHOT.md §9

**Freeze 触发条件**：
- Observation Phase 结束后自动进入
- 重大架构变更前必须进入

**Freeze 期间允许的操作**：
- 生成文档（Documentation）
- GitHub 备份
- 填充 Skeleton 内容

**Freeze 期间禁止的操作**：
- 修改任何 `.html` 文件
- 修改任何 Skill 的 Prompt
- 修改任何 Pipeline 代码
- 修改 `BOOTSTRAP.md` 或 `SOUL.md` 的业务规则

**Freeze 解除条件**：
- 完成 GitHub Backup（Phase 3）
- 用户明确确认解除

**冻结声明（2026-07-06）：**

以下项目进入 Architecture Freeze：
- `daily-report-*.html` — Daily Briefing V2 输出格式
- `research-terminal-*.html` — Research Terminal V1 输出格式
- `trend-tracker/` — Trend Tracker 所有 Pipeline 代码
- `skills/report-generation/` — 报告生成 Skill
- `skills/daily-briefing/` — 日报生成 Skill
- `skills/trend-tracker/` — Trend Tracker Skill
- `BOOTSTRAP.md` — 启动路由器（内容冻结，仅允许文档修正）
- `SOUL.md` — 人格与决策框架（内容冻结）

---

## 3. Development Standard

> **Source:** GOVERNANCE.md §Change Management, OBSERVATION_PHASE_SNAPSHOT.md §6, PROJECT_UNDERSTANDING_REPORT.md §④

### Documentation → Git → Development

任何重大修改必须遵循以下顺序，禁止绕过任何步骤：

```
Discussion（讨论）
  ↓ 确认需求和架构变更
Architecture Freeze（架构冻结）
  ↓ 禁止修改代码/Prompt/Pipeline/HTML
Documentation（文档）
  ↓ 更新文档体系，建立设计依据
GitHub First Backup / Release（GitHub 优先备份）
  ↓ 所有文件同步至 GitHub
  ↓ 打 Tag（例：observation-phase-end）
Implementation（实施）
  ↓ 在 GitHub 最新版本基础上实施变更
  ↓ 实施完成后 Commit
```

**关键原则**：
- 任何变更必须先讨论，再冻结，再文档，再备份，最后实施
- 禁止跳过任何步骤
- GitHub Commit 是变更完成的标志

### Change Classification

| 变更类型 | 定义 | 审批要求 |
|---------|------|---------|
| 架构变更 | 层职责变更、新增层、层间接口变更 | 用户明确确认 + GitHub Backup 在先 |
| 报告格式变更 | Tab 结构调整、输出格式变更 | 用户明确确认 |
| Skill Prompt 变更 | 任何 Skill 的 Prompt 修改 | Architecture Freeze 期间禁止 |
| Pipeline 代码变更 | 任何 Pipeline 代码修改 | Architecture Freeze 期间禁止 |
| 治理规则变更 | `*_GOVERNANCE.md` 内容变更 | 用户明确确认 + 引用依据 |

### Change Flow

```
1. 提出变更需求
  ↓
2. 更新对应文档（ARCHITECTURE.md / GOVERNANCE.md / ...）
  ↓
3. GitHub Commit（记录变更）
  ↓
4. 用户确认
  ↓
5. 实施变更
  ↓
6. 更新 CHANGELOG.md
```

**关键原则**：
- 任何变更必须先更新文档，再实施
- 任何变更必须 GitHub Commit，确保 Single Source of Truth
- 架构变更必须先 GitHub Backup，再实施

---

## 4. Agent Engineering Workflow (AEW)

> **Source:** AGENT_ONBOARDING.md, PROJECT_UNDERSTANDING_REPORT.md §④

### Agent Onboarding Process

```
Step 1: Read README.md（了解文档体系）
  ↓
Step 2: Read MISSION.md（了解系统使命）
  ↓
Step 3: Read ARCHITECTURE.md（了解五层架构）
  ↓
Step 4: Read RESEARCH_SYSTEM.md（了解 Knowledge Flow）
  ↓
Step 5: Read GOVERNANCE.md（了解治理规则）
  ↓
Step 6: Complete First Tasks（验证理解）
  ↓
Step 7: Ready to Work
```

**核心原则**：
- 先读文档，再执行任务
- 不理解的地方必须提问，不猜测
- 首次任务的目的是验证理解，不是产出成果

### Required Reading List

**必读（按优先级排序）**：

| 顺序 | 文档 | 预计阅读时间 | 核心收获 |
|------|------|--------------|---------|
| 1 | `README.md` | 5 min | 文档体系全景 |
| 2 | `MISSION.md` | 10 min | 系统使命和目标 |
| 3 | `ARCHITECTURE.md` | 15 min | 五层架构和层职责 |
| 4 | `RESEARCH_SYSTEM.md` | 15 min | Knowledge Flow |
| 5 | `GOVERNANCE.md` | 10 min | 治理规则和变更流程 |

**选读（根据任务类型）**：

| 任务类型 | 额外必读 |
|---------|---------|
| 报告生成 | `REPORT_DESIGN.md` + `~/.workbuddy/frameworks/*_GOVERNANCE.md` |
| 数据查询 | `DATA_SOURCE.md` + `~/.workbuddy/frameworks/PROVIDER_ROUTER_GOVERNANCE.md` |
| 架构变更 | `REFACTOR_BACKLOG.md` + `ARCHITECTURE.md` |

### First Tasks (Understanding Verification)

**Task 1: 架构理解检查**
- 任务：用一句话说明五层架构的每一层职责，以及层间关系
- 合格标准：能正确说出五层名称、每层职责（不跨层）、Knowledge Flow 方向

**Task 2: 术语理解检查**
- 任务：解释 Research Terminal、Industry Research、Company Research、Monthly Outlook 的正确含义
- 合格标准：4 个术语全部解释正确

**Task 3: 治理规则理解检查**
- 任务：说明 Architecture Freeze 期间修改 Skill Prompt、API Fallback、架构重构的正确处理方式
- 合格标准：3 个场景全部回答正确

### Common Pitfalls

| # | 陷阱 | 如何避免 |
|---|------|---------|
| 1 | 跨层操作 | 严格遵循 One Layer = One Responsibility |
| 2 | 伪造数据 | 遵循 DATA_GOVERNANCE.md，宁愿输出"数据不可用" |
| 3 | 跳过文档 | 遵循 Change Management 流程 |
| 4 | 混淆术语 | 牢记 Terminology Clarifications |
| 5 | 忽略 Evidence | 遵循 Evidence Layer 规范 |

---

## 5. Quality Gates

> **Source:** Domain workflow.md files, PROJECT_UNDERSTANDING_REPORT.md §④, GOVERNANCE.md

### Report Quality Gates

报告生成前必须加载以下治理文档：

| 治理文档 | 加载范围 | 用途 |
|---------|---------|------|
| `DATA_GOVERNANCE.md` | 全文 | 数据可信度规则 |
| `METHODOLOGY_GOVERNANCE.md` | 全文 | 方法论透明度 |
| `VISUAL_IDENTITY_ENGINE.md` | §二+§三+§六 | 视觉规范 |
| `PROVIDER_ROUTER_GOVERNANCE.md` | §二+§三+§五 | Provider 路由 |

### Daily Briefing Quality Gates

> **Source:** docs/daily/workflow.md

- 每 Tab 不超过 500 字
- Tab 4（Knowledge Bite）必须有实质认知内容
- Tab 5（Follow-up Tracker）必须可操作
- 数据必须有来源和可信度标注

### Data Quality Gates

> **Source:** GOVERNANCE.md §Data Governance

- 所有数据必须标注来源
- 所有数据必须标注可信度（🟢 HIGH / 🟡 MEDIUM / 🟠 LOW-MEDIUM / 🔴 LOW）
- API 数据优先，WebSearch 降级，WebFetch 兜底
- 数据缺失时必须明确标注，不假装数据存在
- 宁愿输出"数据不可用"，也不伪造数据

### Methodology Quality Gates

> **Source:** GOVERNANCE.md §Methodology Governance

- 每个分析都必须说明使用的方法
- 每个方法都必须说明适用条件和局限性
- 不确定时必须标注"待验证"，不伪装确定性
- 估算数据必须标注"估算"，不伪装精确性

### Provider Quality Gates

> **Source:** GOVERNANCE.md §Provider Governance, DATA_SOURCE.md

Provider 路由链：

```
P0: westock-mcp (腾讯自选股 MCP)
  ↓ (失败或无数据)
P1: finmind-data (FinMind API)
  ↓ (失败或无数据)
P2: WebSearch
  ↓ (失败或无数据)
P3: WebFetch
```

- 路由链必须透明记录（渲染隔离）
- Fallback 必须标注
- 全部失败 → 输出"数据不可用"，禁止伪造

### Visual Quality Gates

> **Source:** GOVERNANCE.md §Visual Governance

- 品牌驱动配色（Brand-Driven Color Palette）
- 深色主题优先（用户偏好）
- 卡片网格布局（用户偏好）
- 图表必须有标题、数据来源、可信度标注

---

## 6. Documentation Governance V1

> **Source:** docs/README.md, ARCHITECTURE_MIGRATION_BLUEPRINT_V1.0_FINAL.md §WP3

### Documentation Structure

```
docs/
├── README.md                           ← Documentation navigation (entry point)
├── core/                               ← Core Documentation
│   ├── MISSION.md
│   ├── ARCHITECTURE.md
│   ├── RESEARCH_SYSTEM.md
│   ├── GOVERNANCE.md
│   ├── ENGINEERING_GOVERNANCE.md       ← 本文档
│   ├── IMPLEMENTATION_ROADMAP.md
│   ├── REPORT_DESIGN.md
│   ├── AGENT_ONBOARDING.md
│   ├── REFACTOR_BACKLOG.md
│   ├── CHANGELOG.md
│   └── OBSERVATION_PHASE_SNAPSHOT.md
├── daily/                              ← Layer 1 domain docs
├── research-terminal/                  ← Layer 2 domain docs
├── industry/                           ← Layer 3 domain docs
├── company/                            ← Layer 4 domain docs
├── monthly/                            ← Layer 5 domain docs
├── provider/                           ← Cross-cutting: data source
├── evidence/                           ← Cross-cutting: evidence layer
└── investment-mapping/                 ← Cross-cutting: investment map
```

### Documentation Rules

1. **Core + Domain Architecture** — Core docs apply to the entire system; Domain docs apply to a specific layer
2. **Each Domain has 5 standard docs** — product.md, architecture.md, workflow.md, roadmap.md, decisions.md
3. **README.md is the Single Source of Truth** for documentation navigation — any new document must be registered here
4. **Cross-references use relative paths** — never absolute paths or external references for internal docs
5. **Status labels are mandatory** — every document must declare: Frozen / Skeleton / Populated / Draft

### Documentation Cross-Reference Hierarchy

```
README.md (entry point)
├── core/MISSION.md (why this system exists)
├── core/ARCHITECTURE.md (how the system is designed)
│   ├── core/REPORT_DESIGN.md (how reports are designed)
│   ├── core/RESEARCH_SYSTEM.md (how knowledge flows)
│   └── core/REFACTOR_BACKLOG.md (known architecture issues)
├── core/GOVERNANCE.md (governance rules)
│   ├── core/ENGINEERING_GOVERNANCE.md (engineering governance V1 — this document)
│   ├── core/IMPLEMENTATION_ROADMAP.md (implementation phases)
│   ├── provider/DATA_SOURCE.md (data source governance)
│   └── evidence/EVIDENCE_LAYER.md (evidence governance)
├── core/AGENT_ONBOARDING.md (how to onboard new Agents)
├── core/OBSERVATION_PHASE_SNAPSHOT.md (freeze baseline)
├── daily/ ... monthly/ (Layer 1-5 domain docs)
├── investment-mapping/ (Investment Mapping docs)
└── core/CHANGELOG.md (change history)
```

---

## 7. Git Workflow

> **Source:** OBSERVATION_PHASE_SNAPSHOT.md §6, GOVERNANCE.md §Change Management, ARCHITECTURE_MIGRATION_BLUEPRINT_V1.0_FINAL.md §Git Strategy

### Git Commit Principles

1. **GitHub Commit 是变更完成的标志** — 没有 Commit 的变更不算完成
2. **Commit Message 必须描述变更内容** — 使用 conventional commit format
3. **每个 Work Package 独立 Commit** — 不混合多个 WP 的变更
4. **Commit 前必须 Review** — Review → Approval → Commit
5. **不 Force Push** — 除非用户明确要求

### Git Tag Strategy

| Tag | Purpose | Timing |
|-----|---------|--------|
| `v1.4` | Trend Tracker v1.4 release (existing) | Already exists |
| `architecture-baseline-v1` | Architecture Baseline migration complete | WP8 (after all WPs complete) |

### Engineering Process (Git-Centric)

```
Discussion（讨论）
  ↓
Architecture Freeze（架构冻结）
  ↓
Documentation（文档）
  ↓
GitHub Commit（记录文档变更）
  ↓
Implementation（实施）
  ↓
GitHub Commit（记录代码变更）
  ↓
Tag（标记里程碑）
```

### Migration Git Strategy

> **Source:** ARCHITECTURE_MIGRATION_BLUEPRINT_V1.0_FINAL.md §Git Strategy

- **Multi-commit strategy** — one commit per Work Package
- **Sequential execution** — WP2 → WP3 → WP4 → WP1 → WP5 → WP7 → WP6 → WP8
- **Each commit is a rollback point** — if a later WP reveals an issue, revert to the previous commit
- **Tag only at the end** — `architecture-baseline-v1` tag after WP8 verification

---

## 8. Repository Structure

> **Source:** ARCHITECTURE_MIGRATION_BLUEPRINT_V1.0_FINAL.md §3, WP2 Completion Report

### Standard Repository Structure (Frozen)

```
trend-tracker/  (same repo, evolved identity)
├── README.md                           # System entry point
├── .gitignore                          # Artifact protection
├── docs/                               # All documentation
│   ├── README.md                       # Documentation navigation
│   ├── core/                           # Core documentation
│   ├── daily/                          # Layer 1 domain docs
│   ├── research-terminal/              # Layer 2 domain docs
│   ├── industry/                       # Layer 3 domain docs
│   ├── company/                        # Layer 4 domain docs
│   ├── monthly/                        # Layer 5 domain docs
│   ├── provider/                       # Cross-cutting: data source
│   ├── evidence/                       # Cross-cutting: evidence layer
│   └── investment-mapping/             # Cross-cutting: investment map
├── src/                                # Source code (future)
├── config/                             # Configuration files (future)
├── examples/                           # Milestone examples only
├── scripts/                            # Utility scripts (future)
├── tests/                              # Test suite (future)
└── archive/
    └── legacy-trend-tracker/           # Archived Trend Tracker v1.4
```

### Directory Responsibilities

| Directory | Purpose | Content Policy |
|-----------|---------|----------------|
| `docs/` | All documentation | Markdown only, no code |
| `src/` | Future source code | Empty placeholder (WP2) |
| `config/` | Configuration files | Empty placeholder (WP2) |
| `examples/` | Milestone examples only | Empty placeholder (WP2) |
| `scripts/` | Utility scripts | Empty placeholder (WP2) |
| `tests/` | Test suite | Empty placeholder (WP2) |
| `archive/` | Archived legacy code | Trend Tracker v1.4 components |

### Repository Evolution Principle

> **Source:** ARCHITECTURE_MIGRATION_BLUEPRINT_V1.0_FINAL.md §2

Trend Tracker 不是废弃系统，而是 Personal Investment Research System 的第一个已完成的 Domain。Git 历史保持完整，不创建新仓库，不重置历史。

**Three Continuity Guarantees:**

| # | Guarantee | Meaning |
|---|-----------|---------|
| 1 | Repository History Continuity | Git 历史保持完整。旧 commit 保留为历史记录。 |
| 2 | Knowledge Continuity | Trend Tracker 积累的认知不丢失，通过 Legacy Mapping 标注演进关系。 |
| 3 | Architecture Continuity | 新五层架构是旧 Pipeline 的架构升级，不是否定。 |

---

## 9. Artifact Management

> **Source:** REPOSITORY_AUDIT_REPORT.md §Audit 5, ARCHITECTURE_MIGRATION_BLUEPRINT_V1.0_FINAL.md §WP7, .gitignore

### Artifact Classification

| 类型 | 是否版本控制 | 说明 |
|------|------------|------|
| Source code (.py) | ✅ Git | Pipeline 代码 |
| Database Schema (.sql) | ✅ Git | 数据库定义 |
| Documentation (.md) | ✅ Git | 所有文档 |
| Configuration (.yaml, .json config) | ✅ Git | 静态配置文件 |
| HTML Reports | ❌ .gitignore | 生成产物，不入库 |
| JSON Data Output | ❌ .gitignore | 生成产物，不入库 |
| SQLite Database | ❌ .gitignore | 运行时生成 |
| Logs | ❌ .gitignore | 运行时生成 |
| Cache (__pycache__) | ❌ .gitignore | 编译缓存 |
| .env / Secrets | ❌ .gitignore | 敏感信息 |
| OS files (.DS_Store) | ❌ .gitignore | 系统文件 |

### Current .gitignore Coverage

> **Source:** .gitignore (34 lines, v1.4 era)

**已覆盖：**
- Python: `__pycache__/`, `*.py[cod]`, `*.so`, `*.egg-info/`, `dist/`, `build/`, `*.egg`
- SQLite: `db/*.db`
- OS: `.DS_Store`, `Thumbs.db`
- IDE: `.vscode/`, `.idea/`
- Virtual env: `venv/`, `env/`, `.venv/`
- Export artifacts: `trend_data/weekly/*.json`
- Logs: `*.log`
- Local config: `.env`, `.env.local`

**待补充（WP7 — Artifact Protection Upgrade）：**
- `*.html` — 所有 HTML 报告
- `trend_data/daily/*.json` — 日报 JSON 数据
- 通用 cache 排除规则
- 通用 runtime output 排除规则

### Artifact Management Principle

1. **Generated artifacts never enter Git** — HTML reports, JSON data, SQLite databases are runtime outputs
2. **Only milestone examples go in `examples/`** — not every run's output
3. **Configuration files are versioned** — but only static configs, not runtime-generated configs
4. **Secrets never enter Git** — `.env` files are always excluded

---

## Related Documents

- [GOVERNANCE.md](./GOVERNANCE.md) — 治理框架入口（本文档的引用源）
- [ARCHITECTURE.md](./ARCHITECTURE.md) — 架构设计（架构原则来源）
- [MISSION.md](./MISSION.md) — 系统使命（核心哲学来源）
- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) — 实施路线图（Phase 1-11）
- [OBSERVATION_PHASE_SNAPSHOT.md](./OBSERVATION_PHASE_SNAPSHOT.md) — 冻结基线快照
- [AGENT_ONBOARDING.md](./AGENT_ONBOARDING.md) — Agent 入职指南（AEW 来源）
- [DATA_SOURCE.md](../provider/DATA_SOURCE.md) — 数据源注册表
- [EVIDENCE_LAYER.md](../evidence/EVIDENCE_LAYER.md) — 证据层规范

---

*本文档整合自已冻结的 Engineering Governance V1。所有规则来自 Observation Phase Final Snapshot (2026-07-06) 及相关冻结文档。不新增任何规则，不修改任何已冻结原则。*
