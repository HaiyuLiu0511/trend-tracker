# AGENT_ONBOARDING.md — 新 Agent 入职指南

> Documentation Skeleton — Phase2 (Documentation)
> Status: Skeleton created, onboarding process to be detailed

---

## Table of Contents

1. [Purpose](#purpose)
2. [Scope](#scope)
3. [Current Status](#current-status)
4. [Future Expansion](#future-expansion)
5. [Onboarding Process Overview](#onboarding-process-overview)
6. [Required Reading List](#required-reading-list)
7. [First Tasks](#first-tasks)
8. [Common Pitfalls](#common-pitfalls)
9. [Escalation Process](#escalation-process)
10. [Related Documents](#related-documents)

---

## Purpose

指导新 Agent 快速理解 Personal Investment Research System 并投入工作。

本文档是 Agent 入职的必读文档。任何 Agent 在第一次执行任务前，必须完成本文档定义的入职流程。

---

## Scope

- 入职流程全景
- 必读文档列表（按顺序）
- 首次任务定义
- 常见陷阱清单
- 升级处理流程

---

## Current Status

| 字段 | 内容 |
|------|------|
| Phase | 2 (Documentation) |
| 状态 | Skeleton 已建立，入职流程待细化 |
| 最后更新 | 2026-07-06 |
| 下一步 | 与用户确认入职流程最终版本 |

---

## Future Expansion

- [ ] 添加入职检查清单（Onboarding Checklist）
- [ ] 添加常见错误案例分析
- [ ] 添加 Agent 能力评估标准
- [ ] 添加入职时间追踪（目标：30 分钟内完成）

---

## Onboarding Process Overview

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

---

## Required Reading List

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

---

## First Tasks

> **目标**：验证 Agent 是否理解了系统架构和设计原则，而不是产出完美成果。

### Task 1: 架构理解检查

**任务**：用一句话说明五层架构的每一层职责，以及层间关系。

**合格标准**：
- 能正确说出五层名称
- 能正确说明每层的职责（不跨层）
- 能正确说明 Knowledge Flow 的方向

### Task 2: 术语理解检查

**任务**：解释以下术语的正确含义：
- Research Terminal（是 Navigator，不是 Knowledge Base）
- Industry Research（是 Framework，不是 Report）
- Company Research（必须建立在 Industry Research 基础之上）
- Monthly Outlook（是 Knowledge Evolution，不是新闻汇总）

**合格标准**：
- 4 个术语全部解释正确

### Task 3: 治理规则理解检查

**任务**：说明以下场景的正确处理方式：
- 需要修改 Skill Prompt（Architecture Freeze 期间）
- 数据 API 失败，需要 Fallback
- 发现架构问题，想要重构

**合格标准**：
- 场景 1：知道 Architecture Freeze 期间禁止修改，必须先 GitHub Backup
- 场景 2：知道必须走 Provider 路由链，并标注 Fallback
- 场景 3：知道必须先更新 ARCHITECTURE.md，再实施

---

## Common Pitfalls

| # | 陷阱 | 说明 | 如何避免 |
|---|------|------|---------|
| 1 | 跨层操作 | 在 Layer 2 做 Layer 3 的事 | 严格遵循 One Layer = One Responsibility |
| 2 | 伪造数据 | API 失败时不标注，假装数据存在 | 遵循 DATA_GOVERNANCE.md，宁愿输出"数据不可用" |
| 3 | 跳过文档 | 直接修改代码/Prompt，不更新文档 | 遵循 Change Management 流程 |
| 4 | 混淆术语 | 把 Research Terminal 当 Knowledge Base | 牢记 Terminology Clarifications（ARCHITECTURE.md §9） |
| 5 | 忽略 Evidence | 下结论但没有 Evidence 支撑 | 遵循 Evidence Layer 规范（REPORT_DESIGN.md §7） |

---

## Escalation Process

当出现以下情况时，Agent 必须停止并询问用户：

| # | 场景 | 如何询问 |
|---|------|---------|
| 1 | 文档间冲突 | "我在 {文档A} 和 {文档B} 看到冲突，应该以哪个为准？" |
| 2 | 任务不符合架构 | "这个任务要求我做 {X}，但架构规定 {Y}，是否确认要做？" |
| 3 | 数据全部失败 | "所有 Provider 都失败了，是否继续（输出'数据不可用'）？" |
| 4 | 不确定优先级 | "这里有 {X} 和 {Y} 两件事，应该先做哪个？" |

**核心原则**：
- 不确定时必须询问，不猜测
- 询问时必须携带上下文（"我在做 {X}，遇到了 {Y} 问题"）
- 禁止假装确定

---

## Related Documents

- [README.md](../README.md) — 文档体系入口
- [MISSION.md](./MISSION.md) — 系统使命（必读 #2）
- [ARCHITECTURE.md](./ARCHITECTURE.md) — 五层架构（必读 #3）
- [RESEARCH_SYSTEM.md](./RESEARCH_SYSTEM.md) — Knowledge Flow（必读 #4）
- [GOVERNANCE.md](./GOVERNANCE.md) — 治理规则（必读 #5）
- [REFACTOR_BACKLOG.md](./REFACTOR_BACKLOG.md) — 重构待办（架构变更参考）

---

*入职流程随系统演进持续更新。任何入职流程变更都必须更新本文档。*
