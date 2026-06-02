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

## v1.4 — Theme Registry Enhancement ⬜

**状态：** ⬜ Planned

主题注册表扩展与演化。

- 主题数：8 → 12（新增 AI 安全、AI 教育、AI 医疗、AI 芯片设计）
- 父子主题演化（子主题继承父主题信号权重）
- 主题别名映射（同义主题归一化）
- 主题激活/归档生命周期管理

---

## Beyond v1.4

| 项目 | 优先级 | 说明 |
|------|--------|------|
| 真实周报接入日报/周报生成 | P1 | 对接现有日报系统自动推送 |
| 数据源扩展 | P2 | Reuters、Bloomberg、Crunchbase 集成 |
| 预警系统 | P2 | 趋势突变邮件/企微告警 |
| 前端可视化 | P3 | Web Dashboard（ECharts 趋势图） |
| 多语言支持 | P3 | 中文主题名 + 日文/韩文覆盖 |
