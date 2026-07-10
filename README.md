# Personal Investment Research System

> **一个能够不断积累投资认知的研究系统，而不是单纯生成日报的工具。**

---

## 系统使命

构建 **认知积累型** 投资研究系统，支持从事件解读 → 行业框架 → 公司决策 → 知识演化的完整链路。

核心差异：
- 日报是输出（Output），不是目标
- 认知积累（Knowledge Asset）是核心资产
- 报告是副产品，认知是目标

> 详见 [MISSION.md](./docs/core/MISSION.md)

---

## 五层架构

```
Layer 1: Event Layer          → Daily Briefing（每日简报）
Layer 2: Research Navigator   → Research Terminal（研究终端）
Layer 3: Industry Framework   → Industry Research（行业研究）
Layer 4: Decision Support     → Company Research（公司研究）
Layer 5: Knowledge Evolution  → Monthly Outlook（月度展望）
```

| 层级 | 名称 | 职责 | 交付物 |
|------|------|------|--------|
| Layer 1 | Event Layer | 每日信息摄入 + 事件标记 | Daily Briefing Report |
| Layer 2 | Research Navigator | 主题/公司入口 + 快速导航 | Research Terminal Dashboard |
| Layer 3 | Industry Framework | 行业分析框架 + 认知沉淀 | Industry Framework Doc |
| Layer 4 | Decision Support | 公司深度研究 + 投资决策支持 | Company Research Report |
| Layer 5 | Knowledge Evolution | 月度认知演化 + 投资地图更新 | Monthly Outlook Report |

**架构原则：**

1. One Layer = One Responsibility — 每层只解决一类问题
2. One Tab = One Question — 每个 Tab 只回答一个核心问题
3. Reports are outputs. Knowledge is the asset. — 报告是副产品，认知积累是目标
4. Strict Layer Ordering — 上层必须建立在下层基础上
5. GitHub = Single Source of Truth — 所有交付物同步至 GitHub

> 详见 [ARCHITECTURE.md](./docs/core/ARCHITECTURE.md)

---

## 系统演化

### 从 Trend Tracker 到 Personal Investment Research System

本仓库的前身是 **Trend Tracker v1.4** — 一个 AI 产业趋势追踪系统（MVP v1.4），通过多源数据采集、事件主题映射、多维度信号计算和趋势加速度分析，生成结构化周度趋势报告。

2026-07-06，Observation Phase 结束后，系统架构冻结并升级为 **Personal Investment Research System** — 从单一趋势追踪工具演化为五层认知积累研究系统。

**Trend Tracker 不是被废弃的系统，而是 Personal Investment Research System 的第一个完整 Domain（Layer 1: Daily Briefing 的前身）。**

### Legacy Mapping

Trend Tracker 的 18 个组件已根据演化路径分类：

| 演化路径 | 数量 | 含义 |
|---------|------|------|
| EVOLVE | 9 | 代码模式/知识资产可直接复用，将在未来实现阶段重构为 `src/` 模块 |
| REFERENCE | 6 | 架构概念/模式有参考价值，代码不直接复用 |
| REPLACED | 2 | 功能已被新仓库文档完全取代 |
| OBSOLETE | 1 | 新架构中无对应项 |

> 详见 [archive/legacy-trend-tracker/LEGACY_MAPPING.md](./archive/legacy-trend-tracker/LEGACY_MAPPING.md)

### 知识资产

以下知识资产嵌入在 Trend Tracker 遗留代码中，构建新模块时必须参考：

| 资产 | 来源 | 说明 |
|------|------|------|
| 8 主题分类体系 | `archive/legacy-trend-tracker/processors/theme_mapper.py` | AI 产业 8 大主题分类关键词 |
| 公司别名映射表 | `archive/legacy-trend-tracker/processors/company_mapper.py` | 规范公司名 → 别名映射 |
| Impact 评分权重 | `archive/legacy-trend-tracker/processors/explainability_processor.py` | SOURCE_SCORES, EVENT_TYPE_SCORES 权重表 |
| 主题规范化规则 | `archive/legacy-trend-tracker/processors/theme_registry_mapper.py` | 别名 → 规范主题映射 |
| Evidence Layer 模式 | `scripts/evidence_layer.py`（本地） | 来源追踪、置信度评分、证据链 |
| 数据库实体模型 | `archive/legacy-trend-tracker/db/db_init_v1.1.sql` | Events, themes, companies 实体关系 |

---

## 仓库结构

```
trend-tracker/
├── README.md                    ← 本文件（Repository Identity）
├── .gitignore                   ← Artifact Protection (WP7)
│
├── docs/                        ← 文档基线
│   ├── README.md                ← 文档导航入口
│   ├── core/                    ← 核心文档（使命/架构/治理/路线图等）
│   ├── daily/                   ← Layer 1 域文档
│   ├── research-terminal/       ← Layer 2 域文档
│   ├── industry/                ← Layer 3 域文档
│   ├── company/                 ← Layer 4 域文档
│   ├── monthly/                 ← Layer 5 域文档
│   ├── provider/                ← 数据源注册表
│   ├── evidence/                ← 证据层标准
│   └── investment-mapping/      ← 投资映射载体
│
├── src/                         ← 源代码（待实现）
├── config/                      ← 配置（待实现）
├── examples/                    ← 示例（待实现）
├── scripts/                     ← 脚本（待实现）
├── tests/                       ← 测试（待实现）
│
└── archive/                     ← 归档
    └── legacy-trend-tracker/    ← Trend Tracker v1.4 遗留代码归档（WP5）
        ├── DEPRECATED.md        ← 归档说明 + 演化路径
        ├── LEGACY_MAPPING.md    ← 遗留组件演化映射
        ├── README.md            ← Trend Tracker v1.4 README（DEPRECATED）
        ├── ROADMAP.md           ← Trend Tracker v1.4 路线图（DEPRECATED）
        ├── docs/ARCHITECTURE.md ← Trend Tracker v1.4 架构文档（DEPRECATED）
        ├── pipeline_mock.py     ← 10-stage Mock Pipeline
        ├── pipeline_real.py     ← 10-stage Real Pipeline
        ├── collectors/          ← 数据采集器（4 files）
        ├── processors/          ← 数据处理器（4 files）
        └── db/                  ← 数据库 Schema + Migrations（3 files）
```

---

## 当前阶段

```
Phase 1:  Architecture Freeze          ✅ Completed (2026-07-06)
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

> 详见 [IMPLEMENTATION_ROADMAP.md](./docs/core/IMPLEMENTATION_ROADMAP.md)

---

## 快速导航

### 新 Agent 入门

1. 阅读 [docs/core/MISSION.md](./docs/core/MISSION.md) — 理解系统使命
2. 阅读 [docs/core/ARCHITECTURE.md](./docs/core/ARCHITECTURE.md) — 理解五层架构
3. 阅读 [docs/core/ENGINEERING_GOVERNANCE.md](./docs/core/ENGINEERING_GOVERNANCE.md) — 理解工程治理
4. 阅读 [docs/core/AGENT_ONBOARDING.md](./docs/core/AGENT_ONBOARDING.md) — 完成 Onboarding

### 开发者参考

1. [docs/core/ARCHITECTURE.md](./docs/core/ARCHITECTURE.md) — 确认层级职责
2. [docs/core/REFACTOR_BACKLOG.md](./docs/core/REFACTOR_BACKLOG.md) — 了解已知架构问题
3. [docs/provider/DATA_SOURCE.md](./docs/provider/DATA_SOURCE.md) — 确认数据源规则
4. [docs/core/GOVERNANCE.md](./docs/core/GOVERNANCE.md) — 确认合规要求

### 文档导航

> 完整文档索引见 [docs/README.md](./docs/README.md)

---

## 治理

本仓库遵循 **Engineering Governance V1** 和 **Documentation Governance V1**。

### 核心治理文档

| 文档 | 职责 |
|------|------|
| [GOVERNANCE.md](./docs/core/GOVERNANCE.md) | 治理框架入口（架构/数据/方法论/Provider/视觉） |
| [ENGINEERING_GOVERNANCE.md](./docs/core/ENGINEERING_GOVERNANCE.md) | 工程治理详细定义（开发标准/AEW/Quality Gates/Git Workflow） |
| [IMPLEMENTATION_ROADMAP.md](./docs/core/IMPLEMENTATION_ROADMAP.md) | 实施路线图 Phase 1-11 |
| [OBSERVATION_PHASE_SNAPSHOT.md](./docs/core/OBSERVATION_PHASE_SNAPSHOT.md) | Observation Phase 冻结快照 |

### Architecture Freeze

以下项目处于 Architecture Freeze 状态：

- Daily Briefing V2 输出格式
- Research Terminal V1 输出格式
- Trend Tracker 所有 Pipeline 代码
- 报告生成 Skill / 日报生成 Skill / Trend Tracker Skill
- 启动路由器 (BOOTSTRAP.md) / 人格框架 (SOUL.md)

> 详见 [docs/core/ENGINEERING_GOVERNANCE.md](./docs/core/ENGINEERING_GOVERNANCE.md) § Architecture Freeze

---

## 版本

| 项目 | 版本 |
|------|------|
| System Name | Personal Investment Research System |
| Architecture Baseline | V1 (Frozen 2026-07-06) |
| Engineering Governance | V1 |
| Documentation Governance | V1 |
| Implementation Roadmap | V1 |
| Repository Migration | In Progress (Phase 3) |
| Legacy System | Trend Tracker MVP v1.4 |

---

## GitHub Repository

| Field | Value |
|-------|-------|
| Repository | `HaiyuLiu0511/trend-tracker` |
| Branch | `main` |
| Source of Truth | GitHub = Single Source of Truth |

> **Note:** GitHub repository description 待更新为 "Personal Investment Research System — 五层认知积累研究系统"（WP8 执行）

---

*本 README 是 Repository 的身份标识。任何身份变更（系统名称、使命、架构）必须经过用户确认并更新本文档。*
