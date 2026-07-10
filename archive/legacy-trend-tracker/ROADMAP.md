> ⚠️ **DEPRECATED** — Trend Tracker v1.4 legacy file. Archived 2026-07-09 (WP5).
> See [LEGACY_MAPPING.md](./LEGACY_MAPPING.md) for evolution path.
> Original content preserved below for reference.

---

# Trend Tracker — Roadmap

> 版本演进路线图

---

## v1.1 — Core Pipeline ✅

**状态：** 已完成 (2026-06-02)

多源数据采集 → 事件去重 → 主题映射 → 三维信号计算 → 趋势加速度 → 周报导出。

- 3 数据源：arXiv + TechCrunch + GitHub Trending
- 8 大追踪主题
- Capital × 0.45 + Strategic × 0.35 + Research × 0.20 评分模型
- `weekly.json` 结构化导出 + SHA256 快照

---

## v1.2 — Company Layer ✅

**状态：** 已完成 (2026-06-02)

在不破坏 v1.1 的前提下增加公司维度数据沉淀。

- `companies` 表扩展（23 家公司，12 列描述字段）
- `company_actions` 表（事件→公司动作记录）
- `company_weekly_summary` 表（每公司每周信号汇总）
- `company_mapper.py`（别名匹配 + 多级映射）
- `weekly.json` 新增 `company_actions` + `company_weekly_summary` 区块
- Schema 迁移脚本 `001_company_layer.sql`

---

## v1.3 — Snapshot Explainability ✅

**状态：** ✅ Completed (2026-06-02)

在 Trend Score 基础上增加驱动事件可解释性。

- `explainability_processor.py` — 驱动事件提取 + impact_score 计算
- Pipeline Stage 5：快照可解释性（原 Stage 5→6 顺延）
- `weekly.json` 新增 `snapshot_explainability` 区块（每主题 Top 3-5 drivers）
- **零 Schema 变更**，**零评分模型变更**，**完全向后兼容**

**验收清单：**
- [x] Mock Pipeline 通过
- [x] Real Pipeline 通过
- [x] `weekly.json` 验证通过（含 `snapshot_explainability` 区块）
- [x] 向后兼容验证通过

---

## v1.4 — Theme Registry Enhancement ✅

**状态：** ✅ Completed (2026-06-02)

主题注册表治理与别名规范化。

- `theme_registry` 表（8 canonical themes，支持 ACTIVE/DEPRECATED/MERGED 生命周期）
- `theme_aliases` 表（~40 别名规则，含 confidence 评分）
- `theme_registry_mapper.py` — 主题规范化引擎（`load_registry` → `normalize_theme` → `stage_theme_registry_normalization`）
- Pipeline 新增 Stage 3：Theme Registry Normalization
- `docs/ARCHITECTURE.md` — 系统架构基线文档
- **零新增主题**，**零评分模型变更**，**完全向后兼容**

**验收清单：**
- [x] Theme Registry 表创建成功
- [x] 别名映射验证通过（Agentic AI → ai_agent 等 7 组测试用例）
- [x] Pipeline Stage 3 规范化阶段集成通过
- [x] ARCHITECTURE.md 基线文档完整
- [x] 向后兼容验证通过（未知主题 pass-through）

---

## v1.5 — Observation Phase ⬜

**状态：** ⬜ Planned

数据积累与模式观察。

- 持续运行 Real Pipeline 收集真实周度数据
- 验证评分模型在真实数据下的表现
- 识别趋势分类边界情况
- 积累驱动事件和可解释性数据以校准 impact_score
- 为后续主题扩展和数据源扩展提供实证基础

---

## Beyond v1.4

| 项目 | 优先级 | 说明 |
|------|--------|------|
| 真实周报接入日报/周报生成 | P1 | 对接现有日报系统自动推送 |
| 数据源扩展 | P2 | Reuters、Bloomberg、Crunchbase 集成 |
| 预警系统 | P2 | 趋势突变邮件/企微告警 |
| 前端可视化 | P3 | Web Dashboard（ECharts 趋势图） |
| 多语言支持 | P3 | 中文主题名 + 日文/韩文覆盖 |
