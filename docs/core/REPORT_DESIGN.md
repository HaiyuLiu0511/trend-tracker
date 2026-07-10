# REPORT_DESIGN.md — 报告设计原则

> Documentation Skeleton — Phase2 (Documentation)
> Status: Skeleton created, design principles to be populated

---

## Table of Contents

1. [Purpose](#purpose)
2. [Scope](#scope)
3. [Current Status](#current-status)
4. [Future Expansion](#future-expansion)
5. [Core Design Principles](#core-design-principles)
6. [Report Structure Rules](#report-structure-rules)
7. [Visual Identity](#visual-identity)
8. [Evidence Layer](#evidence-layer)
9. [Methodology Transparency](#methodology-transparency)
10. [Related Documents](#related-documents)

---

## Purpose

定义所有报告（Daily Briefing / Research Terminal / Industry Research / Company Research / Monthly Outlook）的设计原则和规范。

本文档是报告生成的权威设计依据。任何报告格式变更，都必须对照本文档。

---

## Scope

- 报告结构设计原则（One Tab = One Question）
- 视觉设计规范（引用 VISUAL_IDENTITY_ENGINE.md）
- Evidence Layer 规范（引用 DATA_GOVERNANCE.md）
- 方法论透明度规范（引用 METHODOLOGY_GOVERNANCE.md）

---

## Current Status

| 字段 | 内容 |
|------|------|
| Phase | 2 (Documentation) |
| 状态 | Skeleton 已建立，设计原则待细化 |
| 最后更新 | 2026-07-06 |
| 下一步 | 从现有报告（Daily Briefing V2）中提取设计原则并正式化 |

---

## Future Expansion

- [ ] 添加报告模板库（每个 Layer 一份）
- [ ] 添加视觉规范速查表（引用 VISUAL_IDENTITY_ENGINE.md）
- [ ] 添加 Evidence Layer 标注模板
- [ ] 添加方法论说明模板
- [ ] 添加报告质量检查清单（QC Checklist）

---

## Core Design Principles

| # | 原则 | 说明 |
|---|------|------|
| 1 | **One Tab = One Question** | 每个 Tab 只回答一个核心问题，不混合多个问题 |
| 2 | **Reports are outputs. Knowledge is the asset.** | 报告是副产品，认知积累是目标 |
| 3 | **Evidence First** | 每个结论必须有 Evidence 支撑，并标注可信度 |
| 4 | **Methodology Transparent** | 每个分析都必须说明使用的方法和数据来源 |
| 5 | **Visual Consistency** | 所有报告使用统一的视觉规范（引用 VISUAL_IDENTITY_ENGINE.md） |

---

## Report Structure Rules

### Universal Rules（适用于所有报告）

1. **标题规范**：`{报告类型} — {日期}`（例：`Daily Briefing — 2026-07-06`）
2. **Tab 命名规范**：`Tab {N}: {核心问题}`（例：`Tab 1: 今天发生了什么？`）
3. **Evidence 标注规范**：🟢 HIGH / 🟡 MEDIUM / 🟠 LOW-MEDIUM / 🔴 LOW
4. **Methodology 标注规范**：必须在报告末尾说明使用的方法和数据来源
5. **Follow-up 规范**：必须在报告末尾列出需要持续跟踪的事项

### Layer-Specific Rules（按层差异化）

| Layer | 特殊规则 |
|-------|----------|
| Layer 1 (Daily Briefing) | 每个 Tab 不超过 500 字；必须有 Follow-up Tracker |
| Layer 2 (Research Terminal) | 只导航，不存储深度内容；必须链接至 Layer 3/4 |
| Layer 3 (Industry Research) | 必须输出 Framework，不是 Report；必须可被复用 |
| Layer 4 (Company Research) | 必须引用 Layer 3 的 Industry Framework；必须输出投资建议 |
| Layer 5 (Monthly Outlook) | 必须对比上月认知，标注演化；必须更新 Investment Mapping |

---

## Visual Identity

视觉规范引用：`~/.workbuddy/frameworks/VISUAL_IDENTITY_ENGINE.md`

**核心原则**：
- 品牌驱动配色（Brand-Driven Color Palette）
- 深色主题优先（用户偏好）
- 卡片网格布局（用户偏好）
- 图表必须有标题、数据来源、可信度标注

**报告生成前必须加载**：`VISUAL_IDENTITY_ENGINE.md` §二优先级链 + §三色板规则 + §六 QC

---

## Evidence Layer

Evidence Layer 规范引用：`~/.workbuddy/frameworks/DATA_GOVERNANCE.md`

**核心原则**：
- 所有数据必须标注来源
- 所有数据必须标注可信度（🟢 HIGH / 🟡 MEDIUM / 🟠 LOW-MEDIUM / 🔴 LOW）
- API 数据优先，WebSearch 降级，WebFetch 兜底
- 数据缺失时必须明确标注，不假装数据存在

**报告生成前必须加载**：`DATA_GOVERNANCE.md` 全文

---

## Methodology Transparency

方法论透明度规范引用：`~/.workbuddy/frameworks/METHODOLOGY_GOVERNANCE.md`

**核心原则**：
- 每个分析都必须说明使用的方法
- 每个方法都必须说明适用条件和局限性
- 不确定时必须标注"待验证"，不伪装确定性
- 估算数据必须标注"估算"，不伪装精确性

**报告生成前必须加载**：`METHODOLOGY_GOVERNANCE.md` 全文

---

## Related Documents

- [README.md](../README.md) — 文档体系入口
- [ARCHITECTURE.md](./ARCHITECTURE.md) — 架构设计（报告是层的输出）
- [RESEARCH_SYSTEM.md](./RESEARCH_SYSTEM.md) — Knowledge Flow（报告是认知载体）
- [GOVERNANCE.md](./GOVERNANCE.md) — 治理规则（报告质量检查）
- `~/.workbuddy/frameworks/VISUAL_IDENTITY_ENGINE.md` — 视觉规范（外部引用）
- `~/.workbuddy/frameworks/DATA_GOVERNANCE.md` — 数据治理（外部引用）
- `~/.workbuddy/frameworks/METHODOLOGY_GOVERNANCE.md` — 方法治理（外部引用）

---

*报告设计原则随系统演进持续更新。任何报告格式变更都必须更新本文档。*
