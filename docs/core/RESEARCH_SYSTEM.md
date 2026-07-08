# RESEARCH_SYSTEM.md — 研究系统与 Knowledge Flow

> Documentation Skeleton — Phase2 (Documentation)
> Status: Skeleton created, Knowledge Flow to be detailed

---

## Table of Contents

1. [Purpose](#purpose)
2. [Scope](#scope)
3. [Current Status](#current-status)
4. [Future Expansion](#future-expansion)
5. [Knowledge Flow Overview](#knowledge-flow-overview)
6. [Stage Details](#stage-details)
7. [Feedback Loops](#feedback-loops)
8. [Knowledge Asset Types](#knowledge-asset-types)
9. [Related Documents](#related-documents)

---

## Purpose

定义 Personal Investment Research System 的 Knowledge Flow（认知流动机制）。

本文档是系统最核心的设计文档之一。它定义了认知如何从每日信息摄入，逐步积累为可复用的知识资产。

---

## Scope

- Knowledge Flow 全景（5 个阶段）
- 每个阶段的信息输入 / 认知输出
- 阶段间的反馈回路
- 知识资产类型定义

---

## Current Status

| 字段 | 内容 |
|------|------|
| Phase | 2 (Documentation) |
| 状态 | Skeleton 已建立，Knowledge Flow 定义待细化 |
| 最后更新 | 2026-07-06 |
| 下一步 | 用 Mermaid 绘制 Knowledge Flow 图 |

---

## Future Expansion

- [ ] 添加 Knowledge Flow 图（Mermaid）
- [ ] 添加每个阶段的交付物模板索引
- [ ] 添加知识资产版本控制规范
- [ ] 添加认知演化追踪机制（如何判断认知在演化）
- [ ] 添加 Investment Mapping 格式定义

---

## Knowledge Flow Overview

```
Daily Briefing（事件摄入）
  ↓ 标记重要事件 + Follow-up Tracker
Research Terminal（研究导航）
  ↓ 筛选值得研究的主题和公司
Industry Research（行业框架）
  ↓ 建立行业分析框架
Company Research（公司研究）
  ↓ 在框架内分析公司，输出投资决策
Monthly Outlook（认知演化）
  ↓ 更新投资地图，演化分析框架
  ↓ （循环回 Daily Briefing）
```

**核心原则**：
- 认知单向流动（Daily → Research Terminal → Industry → Company → Monthly）
- 每层输出成为下层的输入依据
- Monthly Outlook 的输出（认知演化）影响下一轮的 Daily Briefing

---

## Stage Details

### Stage 1: Daily Briefing（Event Layer）

**输入**：市场数据、新闻、公告、宏观数据

**输出**：
- 重要事件标记（Impact Analysis）
- Knowledge Bite（认知积累单元）
- Follow-up Tracker（需持续跟踪的事项）

**认知积累方式**：
- 每次 Daily Briefing 产生至少 1 个 Knowledge Bite
- Knowledge Bite 必须是可复用的认知单元（不是有趣的事实）

**交付物**：`daily-report-YYYY-MM-DD.html`

---

### Stage 2: Research Terminal（Research Navigator）

**输入**：Follow-up Tracker（来自 Daily Briefing）+ 用户主动查询

**输出**：
- 主题列表（Theme Radar）
- 公司列表（Company Radar）
- 研究优先级排序

**认知积累方式**：
- Research Terminal 本身不存储知识本体
- 它导航至 Layer 3（Industry Research）或 Layer 4（Company Research）
- 知识积累发生在 Layer 3 和 Layer 4

**交付物**：`research-terminal-YYYY-MM-DD.html`

> **关键**：Research Terminal 是 Navigator，不是 Knowledge Base。

---

### Stage 3: Industry Research（Industry Framework）

**输入**：
- 主题列表（来自 Research Terminal）
- 相关事件（来自 Daily Briefing）

**输出**：
- Industry Framework 文档（供给侧/需求侧/Drivers/关键变量）
- 行业分析模板（可复用）

**认知积累方式**：
- 每个行业建立一份 Industry Framework 文档
- Framework 随研究不断演化（Version 1 → Version 2 → ...）
- Framework 是公司分析的前置条件

**交付物**：`industry-framework-{行业名}.md`

> **关键**：Industry Research 输出的是 Framework，不是 Report。

---

### Stage 4: Company Research（Decision Support）

**输入**：
- 公司列表（来自 Research Terminal）
- Industry Framework（来自 Stage 3）

**输出**：
- Company Research Report
- 投资建议（Buy/Hold/Sell + 理由）

**认知积累方式**：
- 每个公司建立一份 Company Research Report
- 报告必须引用 Industry Framework
- 报告结论必须可追溯至 Evidence

**交付物**：`company-research-{公司名}.md`

> **关键**：Company Research 必须建立在 Industry Research 基础之上。

---

### Stage 5: Monthly Outlook（Knowledge Evolution）

**输入**：
- 过去一个月的所有研究记录（Layer 1-4）
- 投资地图（当前状态）

**输出**：
- 认知演化记录（框架有哪些变化？）
- 投资地图更新（新增/退出/调整）
- 新出现的主题

**认知积累方式**：
- 对比上月认知，标注演化
- 更新 Investment Mapping（投资地图）
- 演化 Industry Framework（如果有新认知）

**交付物**：`monthly-outlook-YYYY-MM.md` + `investment-mapping.md`

> **关键**：Monthly Outlook 是 Knowledge Evolution，不是新闻汇总。

---

## Feedback Loops

```
Monthly Outlook（认知演化）
  ↓ 更新 Industry Framework
  ↓ 更新 Investment Mapping
  ↓ 影响下一轮 Daily Briefing 的关注重点
Daily Briefing
  ↓ ...
```

**关键反馈回路**：

| 回路 | 说明 |
|------|------|
| Monthly → Industry | Monthly Outlook 更新的认知，反馈至 Industry Framework |
| Monthly → Investment Mapping | Monthly Outlook 更新投资地图 |
| Company → Industry | 公司研究中发现的新认知，反馈至 Industry Framework |
| Daily → Follow-up | Daily Briefing 的 Follow-up Tracker，驱动 Research Terminal |

---

## Knowledge Asset Types

| 资产类型 | 定义 | 存储位置 | 版本控制 |
|---------|------|---------|---------|
| Knowledge Bite | 单次认知积累单元 | Daily Briefing Tab 4 | 不版本控制 |
| Industry Framework | 行业分析框架 | `industry-framework-{行业名}.md` | 版本控制（Git） |
| Company Research | 公司深度研究 | `company-research-{公司名}.md` | 版本控制（Git） |
| Investment Mapping | 投资地图 | `investment-mapping.md` | 版本控制（Git） |
| Follow-up Tracker | 待跟踪事项清单 | Daily Briefing Tab 5 | 不版本控制（每日期望覆盖） |

---

## Related Documents

- [README.md](./README.md) — 文档体系入口
- [ARCHITECTURE.md](./ARCHITECTURE.md) — 五层架构（Knowledge Flow → Architecture）
- [MISSION.md](./MISSION.md) — 系统使命（认知积累是核心资产）
- [REPORT_DESIGN.md](./REPORT_DESIGN.md) — 报告设计（知识资产的呈现格式）
- [GOVERNANCE.md](./GOVERNANCE.md) — 治理规则（知识资产的质量控制）

---

*Knowledge Flow 是系统的灵魂。任何破坏 Knowledge Flow 单向性的设计，都是架构错误。*
