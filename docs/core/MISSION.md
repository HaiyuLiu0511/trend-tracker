# MISSION.md — 系统使命

> Documentation Skeleton — Phase2 (Documentation)

---

## Table of Contents

1. [Purpose](#purpose)
2. [Scope](#scope)
3. [Current Status](#current-status)
4. [Future Expansion](#future-expansion)
5. [Mission Statement](#mission-statement)
6. [Objectives](#objectives)
7. [Success Criteria](#success-criteria)
8. [Non-Goals](#non-goals)
9. [Related Documents](#related-documents)

---

## Purpose

定义 Personal Investment Research System 的存在理由、目标和成功标准。

本文档是所有设计决策的锚点——任何功能/架构变更都必须对照本文档判断是否符合系统使命。

---

## Scope

- 系统使命宣言
- 核心目标（3-5 条）
- 成功标准（可验证）
- 非目标（明确不做什么）

---

## Current Status

| 字段 | 内容 |
|------|------|
| Phase | 2 (Documentation) |
| 状态 | Skeleton 已建立，Mission Statement 待细化 |
| 最后更新 | 2026-07-06 |
| 下一步 | 与用户确认 Mission Statement 最终表述 |

---

## Future Expansion

- [ ] 细化 Success Criteria 的量化指标
- [ ] 添加 Anti-Goals（明确禁止的设计方向）
- [ ] 添加与同类系统（e.g. Perplexity、AlphaSense）的差异化说明
- [ ] 添加用户画像更新记录

---

## Mission Statement

**Personal Investment Research System 是一个能够不断积累投资认知的研究系统，而不是单纯生成日报的工具。**

核心差异：
- 日报是输出（Output），不是目标
- 认知积累（Knowledge Asset）是核心资产
- 系统应支持：事件解读 → 行业框架 → 公司决策 → 知识演化 的完整链路

---

## Objectives

1. **认知积累**：每次研究都留下可复用的认知资产
2. **可追溯决策**：每笔投资决策都有完整的研究链可追溯
3. **系统化分析**：用统一框架分析所有公司和行业，避免碎片化
4. **持续演化**：系统随使用不断升级分析框架，而不是重复造轮子

---

## Success Criteria

| # | 标准 | 验证方式 |
|---|------|---------|
| 1 | 三个月后，系统对某行业的理解明显深于初始状态 | 对比 Industry Framework 版本历史 |
| 2 | 任何投资决策都能在系统中找到完整研究链 | 检查 Investment Mapping 记录 |
| 3 | 新 Agent 能在 30 分钟内理解系统架构并开始工作 | Onboard 测试 |
| 4 | 数据源路由链完全透明，任何数据都有明确来源 | Source Registry 覆盖率 = 100% |

---

## Non-Goals

- **不是量化交易系统** — 不做自动交易、不提供实时信号
- **不是新闻聚合器** — 不追求全面覆盖，只关注有认知价值的内容
- **不是投资组合管理器** — 不记录持仓、不计算收益、不提供资产配置建议
- **不是聊天机器人** — 不追求对话体验，追求研究深度和认知积累

---

## Related Documents

- [README.md](../README.md) — 文档体系入口
- [ARCHITECTURE.md](./ARCHITECTURE.md) — 架构设计（Mission → Architecture）
- [RESEARCH_SYSTEM.md](./RESEARCH_SYSTEM.md) — Knowledge Flow（Mission → Implementation）
- [GOVERNANCE.md](./GOVERNANCE.md) — 治理规则（Mission → Governance）

---

*Mission Statement 是系统的北极星。任何与 Mission 冲突的功能，一律不做。*
