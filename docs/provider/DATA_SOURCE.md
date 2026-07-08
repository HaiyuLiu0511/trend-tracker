# DATA_SOURCE.md — 数据源注册表

> Documentation Skeleton — Phase2 (Documentation)
> Status: Skeleton created, Source Registry to be populated in Phase 10

---

## Table of Contents

1. [Purpose](#purpose)
2. [Scope](#scope)
3. [Current Status](#current-status)
4. [Future Expansion](#future-expansion)
5. [Data Source Registry](#data-source-registry)
6. [Provider Routing Chain](#provider-routing-chain)
7. [Fallback Strategy](#fallback-strategy)
8. [Data Quality Rules](#data-quality-rules)
9. [Related Documents](#related-documents)

---

## Purpose

注册 Personal Investment Research System 使用的所有数据源。

本文档是 Source Registry 的载体。所有数据请求必须走注册的 Provider 路由链，不得使用未注册的数据源。

---

## Scope

- 数据源注册表（名称 / 类型 / 优先级 / 状态）
- Provider 路由链定义
- Fallback 策略
- 数据质量规则

---

## Current Status

| 字段 | 内容 |
|------|------|
| Phase | 2 (Documentation) |
| 状态 | Skeleton 已建立，Source Registry 待填充（Phase 10） |
| 最后更新 | 2026-07-06 |
| 下一步 | Phase 10（Source Registry）填充注册表 |

---

## Future Expansion

- [ ] 填充 Source Registry（所有使用中的数据源）
- [ ] 添加 Provider 路由链详细定义
- [ ] 添加每个数据源的质量评估
- [ ] 添加数据源变更记录（新增/停用/优先级调整）
- [ ] 添加数据源成本追踪（API 调用预算）

---

## Data Source Registry

> **Status 说明**：
> - `Active`：当前正在使用
> - `Planned`：计划中，尚未接入
> - `Deprecated`：已停用

| 名称 | 类型 | 优先级 | 状态 | 用途 |
|------|------|--------|------|------|
| *待填充（Phase 10）* | | | | |

---

## Provider Routing Chain

Provider 路由链定义引用：`~/.workbuddy/frameworks/PROVIDER_ROUTER_GOVERNANCE.md`

**路由链格式**（示例）：

```
P0: westock-mcp (腾讯自选股 MCP)
  ↓ (失败或无数据)
P1: finmind-data (FinMind API)
  ↓ (失败或无数据)
P2: WebSearch (搜索引擎)
  ↓ (失败或无数据)
P3: WebFetch (直接抓取)
```

**路由链必须透明记录**：
- 每个数据请求都必须记录实际使用的 Provider
- Fallback 必须标注（例：`数据来源：FinMind（P1，P0 无数据）`）

---

## Fallback Strategy

| 场景 | Fallback 动作 | 标注要求 |
|------|--------------|---------|
| P0 失败 | 自动切换至 P1 | 必须标注 |
| P1 失败 | 自动切换至 P2 | 必须标注 |
| P2 失败 | 自动切换至 P3 | 必须标注 |
| 全部失败 | 输出"数据不可用" | 禁止伪造数据 |

**核心原则**：
- 宁愿输出"数据不可用"，也不伪造数据
- 所有 Fallback 必须明确标注，不隐藏路由链

---

## Data Quality Rules

数据质量规则引用：`~/.workbuddy/frameworks/DATA_GOVERNANCE.md`

**最低要求**：
- 所有数据必须标注来源
- 所有数据必须标注可信度（🟢 HIGH / 🟡 MEDIUM / 🟠 LOW-MEDIUM / 🔴 LOW）
- 数据缺失时必须明确标注，不假装数据存在
- 估算数据必须标注"估算"，不伪装精确性

---

## Related Documents

- [README.md](./README.md) — 文档体系入口
- [GOVERNANCE.md](./GOVERNANCE.md) — 治理框架（数据治理实施）
- [ARCHITECTURE.md](./ARCHITECTURE.md) — 架构设计（数据层职责）
- `~/.workbuddy/frameworks/DATA_GOVERNANCE.md` — 数据治理详细规则（外部引用）
- `~/.workbuddy/frameworks/PROVIDER_ROUTER_GOVERNANCE.md` — Provider 治理详细规则（外部引用）
- `~/.workbuddy/config/providers.yaml` — Provider 路由配置（外部引用）

---

*Source Registry 是系统数据透明性的基础。任何新增数据源都必须先注册至本文档。*
