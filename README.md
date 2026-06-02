# Trend Tracker — AI 产业趋势追踪系统

> **MVP v1.1** — 从多源数据采集到趋势信号计算的完整 Pipeline

## 项目目标

构建 **AI 产业趋势量化追踪系统**，通过自动化数据采集、事件主题映射、多维度信号计算和趋势加速度分析，生成结构化的周度趋势报告（`weekly.json`），为 AI 产业研究与投资决策提供数据支撑。

核心定位：回答 **"什么正在变化"（What Changed）**，而非仅仅汇总新闻事件。

---

## 已完成能力（MVP v1.1）

| 模块 | 状态 | 说明 |
|------|------|------|
| **多源数据采集** | ✅ 完成 | arXiv（论文）、TechCrunch（RSS）、GitHub Trending（API）三源采集，Reuters 预留 |
| **事件去重** | ✅ 完成 | 基于标题归一化的交叉源去重 |
| **主题映射** | ✅ 完成 | 关键词规则引擎，8 大主题自动分类 |
| **信号计算** | ✅ 完成 | 三维度评分：资本信号（45%）+ 战略信号（35%）+ 研究信号（20%） |
| **趋势加速度** | ✅ 完成 | 周环比变化率，五档趋势分类（Accelerating/Rising/Stable/Cooling/Declining） |
| **资本流向** | ✅ 完成 | 按主题聚合融资金额与份额 |
| **周报导出** | ✅ 完成 | 结构化 `weekly.json` + SHA256 校验快照 |
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

## 项目目录结构

```
trend_tracker/
├── collectors/                  # 数据采集器
│   ├── arxiv_collector.py       # arXiv API 论文采集
│   ├── github_collector.py      # GitHub Trending 仓库采集
│   ├── techcrunch_collector.py  # TechCrunch RSS 文章采集
│   └── reuters_collector.py     # Reuters 预留（待 WebSearch 集成）
├── processors/
│   └── theme_mapper.py          # 关键词规则引擎 → 主题分类
├── db/
│   ├── db_init_v1.1.sql         # 完整 Schema（9 表 + 种子数据）
│   └── trend_tracker.db         # SQLite 运行时数据库（.gitignore）
├── trend_data/
│   └── weekly/                  # 周报 JSON 导出（.gitignore）
│       ├── 2026-W22.json
│       └── 2026-W23.json
├── pipeline_mock.py             # Mock 数据 Pipeline（两周期模拟）
├── pipeline_real.py             # 真实数据 Pipeline（6 阶段：Collect → Export）
├── tests/                       # 测试目录（预留）
├── calculators/                 # 计算器目录（预留）
├── export/                      # 导出目录（预留）
├── .gitignore
└── README.md
```

### 数据库 Schema（9 表）

| 表名 | 用途 |
|------|------|
| `themes` | 主题注册表（支持父子主题演化） |
| `companies` | 公司注册表 |
| `events` | 原始事件记录 |
| `event_theme_mapping` | M:N 事件↔主题映射（权重、来源） |
| `signals` | 周度三维信号评分 |
| `trends_weekly` | 周度趋势加速度 |
| `capital_flow` | 资本流向记录 |
| `weekly_snapshots` | 周报不可变快照（SHA256 校验） |
| `pipeline_runs` | Pipeline 执行日志 |

---

## 如何运行

### 前置条件

```bash
# Python 3.9+
pip install feedparser  # 仅 real pipeline 需要（RSS 解析）
```

### 运行 Mock Pipeline

使用内置的两周期模拟数据，完整走通 **Collect → Signal → Trend → Capital → Export** 全链路：

```bash
cd trend_tracker
python pipeline_mock.py
```

输出：
- 初始化 SQLite 数据库（从 `db/db_init_v1.1.sql`）
- 插入 2026-W22（15 个事件）和 2026-W23（15 个事件）模拟数据
- 计算 8 主题 × 2 周 = 最多 16 条信号 + 趋势记录
- 导出 `trend_data/weekly/2026-W23.json`

### 运行 Real Pipeline

从 arXiv、TechCrunch、GitHub 采集真实数据：

```bash
cd trend_tracker
python pipeline_real.py
```

**⚠️ 注意事项：**
- arXiv API 有速率限制（~1 req/3s），首次运行可能较慢
- GitHub Trending 需要网络访问 https://github.com/trending
- TechCrunch RSS 需要 `feedparser` 库
- Reuters 数据源尚未集成（标记为 Warning）

---

## 当前数据源状态

| 数据源 | 类型 | 状态 | 说明 |
|--------|------|------|------|
| arXiv API | 论文 | 🟢 可用 | 免费、无需 API Key，速率限制 ~1 req/3s |
| TechCrunch RSS | 新闻 | 🟢 可用 | RSS 免费，需要 `feedparser` |
| GitHub Trending | 仓库 | 🟢 可用 | 网页抓取，无需 API Key |
| Reuters | 新闻 | 🔴 未集成 | 需 WebSearch 工具集成，当前占位 |

---

## 版本

- **当前版本**: MVP v1.1
- **Pipeline Version**: v1.1
- **Scoring Version**: v1.1
- **数据库 Schema**: v1.1

---

## 后续计划

详见 [GitHub Issues](https://github.com/haiyuliu/trend-tracker/issues)：

1. **Company Layer Enhancement** — 完善公司维度分析，建立事件→公司→主题的关联
2. **Theme Registry Enhancement** — 主题注册表扩展（从 8 → 12 主题）、父子主题演化支持
3. **Snapshot Explainability Enhancement** — 周报快照增加可解释性字段（评分依据、关键事件引用）
