# ARCHITECTURE.md — 系统架构

> Documentation Skeleton — Phase2 (Documentation)
> Status: Skeleton created, layer details to be populated

---

## Table of Contents

1. [Purpose](#purpose)
2. [Scope](#scope)
3. [Current Status](#current-status)
4. [Future Expansion](#future-expansion)
5. [Design Principles](#design-principles)
6. [Five-Layer Overview](#five-layer-overview)
7. [Layer Details](#layer-details)
8. [Cross-Layer Interfaces](#cross-layer-interfaces)
9. [Terminology Clarifications](#terminology-clarifications)
10. [Related Documents](#related-documents)

---

## Purpose

定义 Personal Investment Research System 的五层架构设计。

本文档是架构决策的权威记录。任何层职责变更、新增层、或层间接口变更，都必须更新本文档并经用户确认。

---

## Scope

- 五层架构定义
- 每层职责与边界
- 层间接口与数据流
- 设计原则
- 术语澄清（防止职责漂移）

---

## Current Status

| 字段 | 内容 |
|------|------|
| Phase | 2 (Documentation) |
| 状态 | 五层架构已冻结（Observation Phase 结束），Layer 1-2 有输出格式，Layer 3-5 待实现 |
| 最后更新 | 2026-07-06 |
| 下一步 | 填充每层详细职责说明和接口定义 |

---

## Future Expansion

- [ ] 添加层间数据流图（Mermaid）
- [ ] 添加每层的信息输入/输出格式定义
- [ ] 添加每层的交付物模板索引
- [ ] 添加层与 GitHub 仓库目录的对应关系
- [ ] 添加架构决策记录（ADR: Architecture Decision Records）

---

## Design Principles

| # | 原则 | 说明 |
|---|------|------|
| 1 | **One Layer = One Responsibility** | 每层只解决一类问题，不跨层 |
| 2 | **One Tab = One Question** | 每个 Tab 只回答一个核心问题 |
| 3 | **Reports are outputs. Knowledge is the asset.** | 报告是副产品，认知积累是目标 |
| 4 | **Strict Layer Ordering** | 上层必须建立在下层基础上，不得跳过 |
| 5 | **GitHub = Single Source of Truth** | 所有层交付物必须同步至 GitHub |

---

## Five-Layer Overview

```
Layer 1: Event Layer          → Daily Briefing
Layer 2: Research Navigator   → Research Terminal
Layer 3: Industry Framework  → Industry Research
Layer 4: Decision Support    → Company Research
Layer 5: Knowledge Evolution → Monthly Outlook
```

| 层级 | 名称 | 职责 | 交付物 |
|------|------|------|--------|
| Layer 1 | Event Layer | 每日信息摄入 + 事件标记 | Daily Briefing Report |
| Layer 2 | Research Navigator | 主题/公司入口 + 快速导航 | Research Terminal Dashboard |
| Layer 3 | Industry Framework | 行业分析框架 + 认知沉淀 | Industry Framework Doc |
| Layer 4 | Decision Support | 公司深度研究 + 投资决策支持 | Company Research Report |
| Layer 5 | Knowledge Evolution | 月度认知演化 + 投资地图更新 | Monthly Outlook Report |

---

## Layer Details

### Layer 1: Event Layer（Daily Briefing）

**职责**：每日信息摄入，识别重要事件，标记需跟踪项。

**不属于本层**：
- 深度行业分析（属于 Layer 3）
- 公司估值（属于 Layer 4）
- 知识演化（属于 Layer 5）

**冻结输出格式（V2）**：

| Tab | 名称 | 核心问题 |
|-----|-------|----------|
| Tab 1 | Today's Highlights | 今天发生了什么？ |
| Tab 2 | Market Snapshot | 市场整体状态如何？ |
| Tab 3 | Impact Analysis | 事件的影响链是什么？ |
| Tab 4 | Knowledge Bite | 今天学到了什么？ |
| Tab 5 | Follow-up Tracker | 哪些事需要持续跟踪？ |

---

### Layer 2: Research Navigator（Research Terminal）

**职责**：研究入口，快速导航至主题或公司，不存储知识本体。

> **关键澄清**：Research Terminal 是 Navigator（导航器），不是 Knowledge Base（知识库）。
> 它的作用是帮助用户快速找到值得研究的主题和公司，而不是存储深度分析内容。

**不属于本层**：
- 行业深度分析（属于 Layer 3）
- 公司估值（属于 Layer 4）

**冻结输出格式（V1）**：

| Tab | 名称 | 核心问题 |
|-----|-------|----------|
| Tab 1 | Dashboard | 当前研究全景是什么？ |
| Tab 2 | Theme Radar | 哪些主题值得关注？ |
| Tab 3 | Company Radar | 哪些公司值得研究？ |

---

### Layer 3: Industry Framework（Industry Research）

**职责**：建立行业分析框架，沉淀行业认知，形成可复用的分析模板。

> **关键澄清**：Industry Research 是 Framework（框架），不是 Report（报告）。
> 它输出的是行业分析框架（供给侧/需求侧/Drivers/关键变量），而不是一次性报告。

**必须建立在 Layer 1-2 基础上**：
- Layer 1 提供事件输入
- Layer 2 提供主题筛选

**交付物**：Industry Framework 文档（每个行业一份）

---

### Layer 4: Decision Support（Company Research）

**职责**：公司深度研究，输出投资决策支持。

> **关键澄清**：Company Research 必须建立在 Industry Research 基础之上。
> 没有行业框架，就不做公司研究。行业框架是公司分析的前置条件。

**必须建立在 Layer 3 基础上**：
- Layer 3 提供行业框架
- Layer 4 在行业框架内分析具体公司

**交付物**：Company Research Report（每份报告对应一家公司）

---

### Layer 5: Knowledge Evolution（Monthly Outlook）

**职责**：月度认知演化，更新投资地图，演化分析框架。

> **关键澄清**：Monthly Outlook 是 Knowledge Evolution（认知演化），不是新闻汇总。
> 它输出的是认知变化（框架演化/投资地图更新/新出现的主题），而不是过去一个月的新闻列表。

**必须建立在 Layer 1-4 基础上**：
- Layer 1-4 提供所有研究记录
- Layer 5 从中提取认知演化

**交付物**：Monthly Outlook Report + Investment Mapping 更新

---

## Cross-Layer Interfaces

```
Layer 1 (Event Layer)
  ↓ 输出：事件标记、Follow-up Tracker
Layer 2 (Research Navigator)
  ↓ 输出：主题列表、公司列表
Layer 3 (Industry Framework)
  ↓ 输出：行业框架
Layer 4 (Decision Support)
  ↓ 输出：公司分析结果
Layer 5 (Knowledge Evolution)
  ↓ 输出：认知演化记录、投资地图
```

**关键规则**：
- 数据只允许单向流动（Layer 1 → Layer 2 → Layer 3 → Layer 4 → Layer 5）
- 上层不得跳过下层直接获取数据
- 每层必须引用下层的输出作为依据

---

## Terminology Clarifications

| 术语 | 正确含义 | 错误理解 |
|------|---------|---------|
| Research Terminal | Research Navigator（导航器） | Knowledge Base（知识库） |
| Industry Research | Industry Framework（框架） | Industry Report（一次性报告） |
| Company Research | Decision Support（决策支持） | Company Profile（公司简介） |
| Monthly Outlook | Knowledge Evolution（认知演化） | News Summary（新闻汇总） |
| Knowledge Bite | 认知积累单元 | 有趣的事实 |

---

## Related Documents

- [README.md](./README.md) — 文档体系入口
- [RESEARCH_SYSTEM.md](./RESEARCH_SYSTEM.md) — Knowledge Flow 详解
- [REPORT_DESIGN.md](./REPORT_DESIGN.md) — 报告设计原则
- [REFACTOR_BACKLOG.md](./REFACTOR_BACKLOG.md) — 架构已知问题
- [GOVERNANCE.md](./GOVERNANCE.md) — 架构治理规则

---

*架构冻结日期：2026-07-06（Observation Phase 结束）。任何架构变更必须先更新本文档。*
