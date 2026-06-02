# Trend Tracker — AI 产业趋势追踪系统

> **MVP v1.2** — 多源数据采集 → 趋势信号计算 + 公司维度数据沉淀

## 项目目标

构建 **AI 产业趋势量化追踪系统**，通过自动化数据采集、事件主题映射、多维度信号计算和趋势加速度分析，生成结构化的周度趋势报告（`weekly.json`），为 AI 产业研究与投资决策提供数据支撑。

核心定位：回答 **"什么正在变化"（What Changed）**，而非仅仅汇总新闻事件。

---

## 已完成能力（MVP v1.2）

| 模块 | 状态 | 说明 |
|------|------|------|
| **多源数据采集** | ✅ 完成 | arXiv（论文）、TechCrunch（RSS）、GitHub Trending（API）三源采集，Reuters 预留 |
| **事件去重** | ✅ 完成 | 基于标题归一化的交叉源去重 |
| **主题映射** | ✅ 完成 | 关键词规则引擎，8 大主题自动分类 |
| **信号计算** | ✅ 完成 | 三维度评分：资本信号（45%）+ 战略信号（35%）+ 研究信号（20%） |
| **趋势加速度** | ✅ 完成 | 周环比变化率，五档趋势分类（Accelerating/Rising/Stable/Cooling/Declining） |
| **资本流向** | ✅ 完成 | 按主题聚合融资金额与份额 |
| **公司维度** ⭐ | ✅ v1.2 新增 | 公司名称映射、公司动作记录、每周公司信号汇总 |
| **周报导出** | ✅ 完成 | 结构化 `weekly.json`（含 `company_actions` + `company_weekly_summary` 区块）+ SHA256 校验快照 |
| **Mock Pipeline** | ✅ 完成 | 两周期模拟数据完整走通全部计算链路 |
| **Pipeline 日志** | ✅ 完成 | 每次运行记录到 `pipeline_runs` 表 |
| **数据完整性校验** | ✅ 完成 | `verify()` 跨表一致性检查 |

### 评分模型

```
Theme Score = Capital × 0.45 + Strategic × 0.35 + Research × 0.20

Capital Score:   log10(funding) 对数缩放 + 事件计数
Strategic Score: 产品发布/合作/基础设施事件计数 × 2.5
Research Score:  论文事件计数 × 3.0
All sub-scores capped at 0–10
```

### 8 大追踪主题

| Theme ID | 中文名 | 覆盖范围 |
|----------|--------|---------|
| `llm_frontier` | LLM 前沿模型 | GPT-5, Claude, Gemini, Llama 等旗舰模型 |
| `ai_agent` | AI Agent 自主代理 | Agent 框架、工具使用、多步推理 |
| `inference_compute` | 推理计算 | 推理优化、芯片、边缘推理 |
| `ai_coding` | AI 编程 | Copilot, Devin, Cursor, 代码生成 |
| `compute_gpu` | 算力与芯片 | GPU/TPU 供应、数据中心建设 |
| `ai_video` | AI 视频生成 | 文生视频、视频编辑、虚拟人 |
| `robotics` | 机器人 | 人形机器人、具身智能 |
| `ai_infrastructure` | AI 基础设施 | 向量数据库、MLOps、模型部署 |

---

## Company Layer ⭐ (v1.2 新增)

### 设计目标

在不破坏 MVP v1.1 现有功能的前提下，增加 **公司维度数据沉淀能力**。每条事件如果在公司注册表中匹配到对应公司，则自动写入公司动作记录，并汇总为每周公司信号评分。

### 核心组件

| 组件 | 说明 |
|------|------|
| `companies` 表 | 公司注册表（12 列，含描述/成立年份/总部/行业标签），覆盖 23 家关键 AI 公司 |
| `company_actions` 表 | 事件→公司动作记录（每条事件可能写入一条 `company_action`） |
| `company_weekly_summary` 表 | 物化视图：每公司每周汇总（动作数、融资额、信号评分） |
| `company_mapper.py` | 公司名称→`company_id` 映射器（别名表 + 数据库多级匹配） |

### `weekly.json` 新增区块

```json
{
  "company_actions": [
    {
      "company_id": "openai",
      "company_name": "OpenAI",
      "ticker": null,
      "action_type": "PRODUCT_LAUNCH",
      "action_date": "2026-06-01",
      "theme_id": "ai_agent",
      "amount_usd": null,
      "description": "OpenAI launches Operator...",
      "source_tier": "P1"
    }
  ],
  "company_weekly_summary": [
    {
      "company_id": "openai",
      "company_name": "OpenAI",
      "ticker": null,
      "primary_theme": "llm_frontier",
      "action_count": 2,
      "funding_usd": 0,
      "launch_count": 2,
      "research_count": 0,
      "signal_score": 5.0
    }
  ]
}
```

### 数据流

```
Events (company_name=raw) → company_mapper.py → companies.company_id
    ↓
company_actions (每个可匹配事件一条)
    ↓
stage_company_weekly_summary (按周聚合)
    ↓
weekly.json { company_actions + company_weekly_summary }
```

### 覆盖率

- 种子公司：23 家（8 MVP + 15 扩展）
- 别名映射：~65 条别名规则
- 匹配方式：精确别名 → 数据库名称查询 → 模糊子串匹配

---

## 项目目录结构

```
trend_tracker/
├── collectors/                  # 数据采集器
│   ├── arxiv_collector.py       # arXiv API 论文采集
│   ├── github_collector.py      # GitHub Trending 仓库采集
│   ├── techcrunch_collector.py  # TechCrunch RSS 文章采集
│   └── reuters_collector.py     # Reuters 预留
├── processors/
│   ├── theme_mapper.py          # 关键词规则引擎 → 主题分类
│   └── company_mapper.py        # 公司名称 → company_id 映射器 ⭐
├── db/
│   ├── db_init_v1.1.sql         # v1.1 完整 Schema（9 表 + 种子数据）
│   ├── migrations/
│   │   └── 001_company_layer.sql # v1.2 迁移脚本 ⭐
│   └── trend_tracker.db         # SQLite 运行时数据库（.gitignore）
├── trend_data/
│   └── weekly/                  # 周报 JSON 导出（.gitignore）
├── pipeline_mock.py             # Mock 数据 Pipeline（v1.2，含 Company Layer） ⭐
├── pipeline_real.py             # 真实数据 Pipeline（v1.2，8 阶段） ⭐
├── pipeline_real_v1.2.py        # v1.2 真实 Pipeline（别名）
├── tests/                       # 测试目录（预留）
├── calculators/                 # 计算器目录（预留）
├── export/                      # 导出目录（预留）
├── .gitignore
└── README.md
```

### 数据库 Schema（11 表）

| 表名 | 用途 | 版本 |
|------|------|------|
| `themes` | 主题注册表（支持父子主题演化） | v1.1 |
| `companies` | 公司注册表（12 列） | v1.2 ⭐ |
| `events` | 原始事件记录 | v1.1 |
| `event_theme_mapping` | M:N 事件↔主题映射 | v1.1 |
| `signals` | 周度三维信号评分 | v1.1 |
| `trends_weekly` | 周度趋势加速度 | v1.1 |
| `capital_flow` | 资本流向记录 | v1.1 |
| `company_actions` | 事件→公司动作记录 | v1.2 ⭐ |
| `company_weekly_summary` | 每公司每周汇总 | v1.2 ⭐ |
| `weekly_snapshots` | 周报不可变快照（SHA256） | v1.2 |
| `pipeline_runs` | Pipeline 执行日志 | v1.2 |

---

## 如何运行

### 前置条件

```bash
# Python 3.9+
pip install feedparser  # 仅 real pipeline 需要（RSS 解析）
```

### 初始化数据库

```bash
cd trend_tracker
# 从零初始化（v1.1 → v1.2 迁移）
sqlite3 db/trend_tracker.db < db/db_init_v1.1.sql
sqlite3 db/trend_tracker.db < db/migrations/001_company_layer.sql
```

### 运行 Mock Pipeline

```bash
cd trend_tracker
python pipeline_mock.py
```

输出：
- 两周期模拟数据（31 事件 × 16 company_actions）
- 计算 8 主题 + 公司信号评分
- 导出 `trend_data/weekly/2026-W23.json`（含 `company_actions` + `company_weekly_summary`）

### 运行 Real Pipeline

```bash
cd trend_tracker
python pipeline_real.py    # 或 python pipeline_real_v1.2.py
```

**⚠️ 注意事项：**
- arXiv API 有速率限制（~1 req/3s），sandbox 环境可能 IP 级限流
- GitHub Trending 需要网络访问
- TechCrunch RSS 需要 `feedparser` 库
- Reuters 数据源尚未集成

---

## 版本

| 项目 | 版本 |
|------|------|
| 当前版本 | MVP v1.2 |
| Pipeline Version | v1.2 |
| Scoring Version | v1.2 |
| 数据库 Schema | v1.2（通过迁移 001） |

### 迁移路径

```
v1.1 → v1.2: db/migrations/001_company_layer.sql
  - ALTER companies 增加 6 列（description/founded_year/headquarters/...)
  - 新增 company_actions 表
  - 新增 company_weekly_summary 表
  - 插入 15 家扩展公司
```

---

## 当前数据源状态

| 数据源 | 类型 | 状态 | 说明 |
|--------|------|------|------|
| arXiv API | 论文 | 🟡 受限 | 免费、速率限制 ~1 req/3s，sandbox IP 限流 |
| TechCrunch RSS | 新闻 | 🟢 可用 | RSS 免费，需要 `feedparser` |
| GitHub Trending | 仓库 | 🟢 可用 | 网页抓取，无需 API Key |
| Reuters | 新闻 | 🔴 未集成 | 需 WebSearch 工具集成 |

---

## 后续计划

详见 [GitHub Issues](https://github.com/haiyuliu/trend-tracker/issues)：

1. ✅ **Company Layer Enhancement** — 已完成于 v1.2
2. **Theme Registry Enhancement** — 主题注册表扩展（8 → 12）、父子主题演化
3. **Snapshot Explainability Enhancement** — 周报快照增加可解释性字段
4. 真实周报接入日报/周报生成流程
