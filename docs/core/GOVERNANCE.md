# GOVERNANCE.md — 治理框架

> Documentation Skeleton — Phase2 (Documentation)
> Status: Skeleton created, governance rules to be detailed

---

## Table of Contents

1. [Purpose](#purpose)
2. [Scope](#scope)
3. [Current Status](#current-status)
4. [Future Expansion](#future-expansion)
5. [Governance Framework Overview](#governance-framework-overview)
6. [Architecture Governance](#architecture-governance)
7. [Data Governance](#data-governance)
8. [Methodology Governance](#methodology-governance)
9. [Provider Governance](#provider-governance)
10. [Visual Governance](#visual-governance)
11. [Change Management](#change-management)
12. [Related Documents](#related-documents)

---

## Purpose

定义 Personal Investment Research System 的治理框架。

本文档是所有治理规则的汇总入口。详细的治理规则分散在 `~/.workbuddy/frameworks/*_GOVERNANCE.md` 中，本文档负责建立索引和说明引用关系。

---

## Scope

- 治理框架全景
- 架构治理（Architecture Freeze 规则）
- 数据治理（引用 DATA_GOVERNANCE.md）
- 方法论治理（引用 METHODOLOGY_GOVERNANCE.md）
- Provider 治理（引用 PROVIDER_ROUTER_GOVERNANCE.md）
- 视觉治理（引用 VISUAL_IDENTITY_ENGINE.md）
- 变更管理流程

---

## Current Status

| 字段 | 内容 |
|------|------|
| Phase | 2 (Documentation) |
| 状态 | Skeleton 已建立，治理规则索引待完善 |
| 最后更新 | 2026-07-06 |
| 下一步 | 确认各 `*_GOVERNANCE.md` 文件的引用关系 |

---

## Future Expansion

- [ ] 添加治理规则检查清单（Governance Checklist）
- [ ] 添加违规处理流程（Violation Handling）
- [ ] 添加治理规则演化机制（如何更新治理规则）
- [ ] 添加治理审计记录（Governance Audit Log）

---

## Governance Framework Overview

```
GOVERNANCE.md（本文件 — 治理入口）
├── Engineering Governance V1（工程治理）
│   └── 引用：ENGINEERING_GOVERNANCE.md（同目录）
│       ├── Core Philosophy V2
│       ├── Architecture Principles V1
│       ├── Development Standard
│       ├── Agent Engineering Workflow (AEW)
│       ├── Quality Gates
│       ├── Documentation Governance V1
│       ├── Git Workflow
│       ├── Repository Structure
│       └── Artifact Management
├── Implementation Roadmap V1（实施路线图）
│   └── 引用：IMPLEMENTATION_ROADMAP.md（同目录）
├── Architecture Governance（架构治理）
│   └── Architecture Freeze 规则
├── Data Governance（数据治理）
│   └── 引用：~/.workbuddy/frameworks/DATA_GOVERNANCE.md
├── Methodology Governance（方法论治理）
│   └── 引用：~/.workbuddy/frameworks/METHODOLOGY_GOVERNANCE.md
├── Provider Governance（Provider 治理）
│   └── 引用：~/.workbuddy/frameworks/PROVIDER_ROUTER_GOVERNANCE.md
└── Visual Governance（视觉治理）
    └── 引用：~/.workbuddy/frameworks/VISUAL_IDENTITY_ENGINE.md
```

---

## Architecture Governance

### Architecture Freeze 规则

> 定义：Architecture Freeze 期间，禁止修改任何代码、Prompt、Pipeline 或 HTML。

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

---

## Data Governance

数据治理规则引用：`~/.workbuddy/frameworks/DATA_GOVERNANCE.md`

**核心原则**：
- 所有数据必须标注来源
- 所有数据必须标注可信度（🟢 HIGH / 🟡 MEDIUM / 🟠 LOW-MEDIUM / 🔴 LOW）
- API 数据优先，WebSearch 降级，WebFetch 兜底
- 数据缺失时必须明确标注，不假装数据存在

**报告生成前必须加载**：`DATA_GOVERNANCE.md` 全文

---

## Methodology Governance

方法论治理规则引用：`~/.workbuddy/frameworks/METHODOLOGY_GOVERNANCE.md`

**核心原则**：
- 每个分析都必须说明使用的方法
- 每个方法都必须说明适用条件和局限性
- 不确定时必须标注"待验证"，不伪装确定性
- 估算数据必须标注"估算"，不伪装精确性

**报告生成前必须加载**：`METHODOLOGY_GOVERNANCE.md` 全文

---

## Provider Governance

Provider 治理规则引用：`~/.workbuddy/frameworks/PROVIDER_ROUTER_GOVERNANCE.md`

**核心原则**：
- 数据请求必须走 Provider 路由链（P0 → P1 → P2）
- 路由链必须透明记录（渲染隔离）
- Fallback 必须标注

**金融数据请求时（含投研/报告/行情查询）必须加载**：`PROVIDER_ROUTER_GOVERNANCE.md` §二分级定义 + §三路由表 + §五渲染隔离

---

## Visual Governance

视觉治理规则引用：`~/.workbuddy/frameworks/VISUAL_IDENTITY_ENGINE.md`

**核心原则**：
- 品牌驱动配色（Brand-Driven Color Palette）
- 深色主题优先（用户偏好）
- 卡片网格布局（用户偏好）
- 图表必须有标题、数据来源、可信度标注

**报告生成任务（含 HTML/PPT/可视化产物）必须加载**：`VISUAL_IDENTITY_ENGINE.md` §二优先级链 + §三色板规则 + §六 QC

---

## Change Management

### 变更分类

| 变更类型 | 定义 | 审批要求 |
|---------|------|---------|
| 架构变更 | 层职责变更、新增层、层间接口变更 | 用户明确确认 + GitHub Backup 在先 |
| 报告格式变更 | Tab 结构调整、输出格式变更 | 用户明确确认 |
| Skill Prompt 变更 | 任何 Skill 的 Prompt 修改 | Architecture Freeze 期间禁止 |
| Pipeline 代码变更 | 任何 Pipeline 代码修改 | Architecture Freeze 期间禁止 |
| 治理规则变更 | `*_GOVERNANCE.md` 内容变更 | 用户明确确认 + 引用依据 |

### 变更流程

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

## Related Documents

- [README.md](./README.md) — 文档体系入口
- [ARCHITECTURE.md](./ARCHITECTURE.md) — 架构设计（架构治理对象）
- [ENGINEERING_GOVERNANCE.md](./ENGINEERING_GOVERNANCE.md) — Engineering Governance V1（工程治理完整定义）
- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) — Implementation Roadmap V1（Phase 1-11 执行计划）
- [REPORT_DESIGN.md](./REPORT_DESIGN.md) — 报告设计（报告质量治理）
- [DATA_SOURCE.md](../provider/DATA_SOURCE.md) — 数据源注册表（数据治理实施）
- [EVIDENCE_LAYER.md](../evidence/EVIDENCE_LAYER.md) — 证据层规范（证据治理）
- `~/.workbuddy/frameworks/DATA_GOVERNANCE.md` — 数据治理详细规则（外部引用）
- `~/.workbuddy/frameworks/METHODOLOGY_GOVERNANCE.md` — 方法论治理详细规则（外部引用）
- `~/.workbuddy/frameworks/PROVIDER_ROUTER_GOVERNANCE.md` — Provider 治理详细规则（外部引用）
- `~/.workbuddy/frameworks/VISUAL_IDENTITY_ENGINE.md` — 视觉治理详细规则（外部引用）

---

*治理框架随系统演进持续更新。任何治理规则变更都必须更新本文档及对应的 `*_GOVERNANCE.md` 文件。*
