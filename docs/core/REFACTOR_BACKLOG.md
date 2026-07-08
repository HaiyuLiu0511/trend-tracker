# REFACTOR_BACKLOG.md — 重构待办清单

> Documentation Skeleton — Phase2 (Documentation)
> Status: Populated with Observation Phase findings

---

## Table of Contents

1. [Purpose](#purpose)
2. [Scope](#scope)
3. [Current Status](#current-status)
4. [Future Expansion](#future-expansion)
5. [Backlog Format](#backlog-format)
6. [P0 Items (Must Do)](#p0-items-must-do)
7. [P1 Items (Should Do)](#p1-items-should-do)
8. [P2 Items (Nice to Have)](#p2-items-nice-to-have)
9. [Completed Items](#completed-items)
10. [Related Documents](#related-documents)

---

## Purpose

跟踪 Personal Investment Research System 的所有重构待办事项。

本文档是重构工作的优先级依据。任何重构工作都必须先对照本文档，确认优先级和依赖关系。

---

## Scope

- 重构待办清单（按优先级分类）
- 每个待办项的详细描述、影响范围、依赖关系
- 已完成项记录

---

## Current Status

| 字段 | 内容 |
|------|------|
| Phase | 2 (Documentation) |
| 状态 | 已从 Observation Phase 核心问题导入 8 个待办项 |
| 最后更新 | 2026-07-06 |
| 下一步 | 与用户确认优先级排序，开始 P0 项重构 |

---

## Future Expansion

- [ ] 添加每个待办项的详细实施方案
- [ ] 添加待办项之间的依赖关系图
- [ ] 添加重构进度追踪（Started / In Progress / Done）
- [ ] 添加重构验证标准（如何判断重构成功）

---

## Backlog Format

```markdown
### {优先级} - {标题}

**ID**: BACKLOG-{N}
**影响范围**: {受影响的层/文档/代码}
**依赖**: {依赖的待办项/文档}
**描述**: {详细描述}
**验收标准**: {如何判断完成}
**状态**: Pending / In Progress / Done
```

---

## P0 Items (Must Do Before Next Release)

### P0-001: 日报内容过重，信息密度低

**ID**: BACKLOG-001
**影响范围**: Layer 1 (Daily Briefing)
**依赖**: 无
**描述**: 当前 Daily Briefing 内容过长，信息密度低，用户阅读负担重。需要重构内容密度，强化 Knowledge Bite 和 Impact Analysis。
**验收标准**:
- 每个 Tab 不超过 500 字
- Tab 4 (Knowledge Bite) 必须有实质认知内容，不是有趣的事实
- Tab 5 (Follow-up Tracker) 必须可操作，不是泛泛而谈
**状态**: Pending

---

### P0-002: Research Terminal 职责不清，与日报重叠

**ID**: BACKLOG-002
**影响范围**: Layer 2 (Research Terminal)
**依赖**: BACKLOG-001 (必须先明确 Daily Briefing 边界）
**描述**: Research Terminal 当前与 Daily Briefing 边界不清，部分内容重复。需要重新定义 Layer 2 职责，强调 Navigator 定位（不是 Knowledge Base）。
**验收标准**:
- Research Terminal Tab 2/3 的信息来源和更新频率明确定义
- Research Terminal 不存储深度内容，只导航
- 与 Daily Briefing 的边界文档化（ARCHITECTURE.md）
**状态**: Pending

---

### P0-003: Evidence Layer 缺乏验证机制，可信度标注不一致

**ID**: BACKLOG-003
**影响范围**: 所有报告（Layer 1-5）
**依赖**: 无
**描述**: 当前 Evidence Layer 缺乏统一验证机制，不同报告的可信度标注标准不一致。需要建立 Evidence Layer 验证机制，统一可信度标注标准。
**验收标准**:
- Evidence Layer 验证机制文档化（引用 DATA_GOVERNANCE.md）
- 所有报告使用统一的可信度标注格式（🟢 HIGH / 🟡 MEDIUM / 🟠 LOW-MEDIUM / 🔴 LOW）
- 报告生成前必须加载 DATA_GOVERNANCE.md
**状态**: Pending

---

## P1 Items (Should Do)

### P1-001: 日报/周报/月报边界重叠，用户困惑

**ID**: BACKLOG-004
**影响范围**: 整体架构（Layer 1 vs Layer 5）
**依赖**: BACKLOG-001, BACKLOG-002 (必须先明确 Layer 1-2 边界）
**描述**: 当前日报、周报、月报的边界不清，用户困惑哪些内容应该出现在哪个报告中。需要重新定义各层输出边界。
**验收标准**:
- Layer 1 (Daily Briefing) 与 Layer 5 (Monthly Outlook) 边界明确定义
- 各层输出格式文档化（REPORT_DESIGN.md）
- 用户能清晰区分日报和月报的内容差异
**状态**: Pending

---

### P1-002: 数据源无 Source Registry，Provider 路由不透明

**ID**: BACKLOG-005
**影响范围**: 数据层（所有报告的数据请求）
**依赖**: 无
**描述**: 当前数据源无统一注册表，Provider 路由链不透明，用户无法判断数据来源。需要建立 Source Registry，定义 Provider 路由链。
**验收标准**:
- Source Registry 建立（DATA_SOURCE.md）
- 所有数据请求走 Provider 路由链
- 路由链透明记录（渲染隔离）
**状态**: Pending

---

### P1-003: GitHub 不是 Single Source of Truth，本地文件与仓库不同步

**ID**: BACKLOG-006
**影响范围**: 工程规范（所有文件）
**依赖**: 无
**描述**: 当前本地文件与 GitHub 仓库不同步，GitHub 不是 Single Source of Truth。需要建立 GitHub First Backup 规范，确保所有文件先同步至 GitHub。
**验收标准**:
- GitHub First Backup 规范文档化（GOVERNANCE.md §Change Management）
- 所有本地文件与 GitHub 仓库同步
- 打 Tag：`observation-phase-end`
**状态**: Pending

---

### P1-004: 投资地图（Investment Mapping）缺失，认知无积累载体

**ID**: BACKLOG-007
**影响范围**: Layer 5 (Knowledge Evolution)
**依赖**: BACKLOG-001 to BACKLOG-005 (必须先完成基础架构重构）
**描述**: 当前投资地图缺失，认知积累无载体。需要建立投资地图载体，定义认知积累格式。
**验收标准**:
- Investment Mapping 格式定义（RESEARCH_SYSTEM.md §Knowledge Asset Types）
- Investment Mapping 文档建立（`investment-mapping.md`）
- Monthly Outlook 输出更新 Investment Mapping
**状态**: Pending

---

## P2 Items (Nice to Have)

### P2-001: 月报（Monthly Outlook）未定义，Knowledge Evolution 层空置

**ID**: BACKLOG-008
**影响范围**: Layer 5 (Knowledge Evolution)
**依赖**: BACKLOG-007 (必须先建立 Investment Mapping）
**描述**: 当前 Monthly Outlook 未定义，Knowledge Evolution 层空置。需要定义 Monthly Outlook 格式和生成流程。
**验收标准**:
- Monthly Outlook 格式定义（ARCHITECTURE.md Layer 5）
- Monthly Outlook 生成 Pipeline 建立
- 第一份 Monthly Outlook 报告生成
**状态**: Pending

---

## Completed Items

> 本部分记录已完成的重构项。

（暂无）

---

## Related Documents

- [README.md](./README.md) — 文档体系入口
- [ARCHITECTURE.md](./ARCHITECTURE.md) — 架构设计（重构依据）
- [GOVERNANCE.md](./GOVERNANCE.md) — 治理规则（重构合规要求）
- [CHANGELOG.md](./CHANGELOG.md) — 变更记录（重构完成后更新）
- `OBSERVATION_PHASE_FINAL_SNAPSHOT.md` — Observation Phase 问题清单（来源）

---

*本文档随重构工作持续更新。任何重构项完成后，必须移至 Completed Items 并更新 CHANGELOG.md。*
