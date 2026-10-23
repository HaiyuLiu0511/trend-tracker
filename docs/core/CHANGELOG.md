# CHANGELOG.md — 系统变更记录

> Documentation Skeleton — Phase2 (Documentation)
> Status: Initialized, entries to be added as system evolves

---

## Table of Contents

1. [Purpose](#purpose)
2. [Scope](#scope)
3. [Current Status](#current-status)
4. [Future Expansion](#future-expansion)
5. [Changelog Format](#changelog-format)
6. [Entries](#entries)
7. [Related Documents](#related-documents)

---

## Purpose

记录 Personal Investment Research System 的所有变更。

本文档是系统演化的历史记录。任何架构变更、报告格式变更、Skill Prompt 变更、Pipeline 代码变更，都必须记录至本文档。

---

## Scope

- 变更记录格式定义
- 所有变更条目（按时间倒序）
- 变更类型分类
- 变更影响的文档/代码

---

## Current Status

| 字段 | 内容 |
|------|------|
| Phase | 2 (Documentation) |
| 状态 | 已初始化，Observation Phase 条目已添加 |
| 最后更新 | 2026-07-06 |
| 下一步 | 每次变更后更新本文档 |

---

## Future Expansion

- [ ] 添加变更影响分析（哪些文档/代码受影响）
- [ ] 添加变更回滚记录（如果变更被回滚）
- [ ] 添加变更与 GitHub Commit 的对应关系

---

## Changelog Format

```markdown
## [版本号] - YYYY-MM-DD

### Added（新增）
- ...

### Changed（变更）
- ...

### Deprecated（弃用）
- ...

### Removed（移除）
- ...

### Fixed（修复）
- ...

### Affected Documents/Code（受影响文件）
- ...
```

**版本号规则**：
- 架构变更：`v{Major}.{Minor}`（例：`v1.0`）
- 报告格式变更：`v{Major}.{Minor}`（例：`v2.1`）
- Skill Prompt 变更：`v{Minor}`（例：`v2.1.1`）
- Pipeline 代码变更：`v{Minor}`（例：`v2.1.2`）

---

## Entries

### [Slice 5 — Input Fidelity Review] - 2026-10-23

#### Added
- `scripts/input_fidelity_review.py` — 研究输入质量守卫 V1：把 Daily Briefing **源文档**转换为完整、确定、逐字段保真的 Markdown 研究输入审查清单。每个 Event Record、每一条 source、每段非 Event 正文（Knowledge Bite / Follow-up / Market Snapshot）、每一条 Knowledge Bite → Event 引用均被**逐字节原样**转录，并标注该字段**是否进入 HTML 正文**与**预计渲染位置**。CLI：`--input <source.json> [--out <path>]`，默认输出 `output/input-fidelity-review-<data_date>.md`；退出码 `0` 成功 / `2` 输入缺失或非法 JSON / `4` **Event Contract 违反（仅 `events[]`）**（无 `3`：本工具无词数门）；完整源文档契约（报告契约、Tab 形状、词数预算）**不由本工具校验**，其余结构问题以非致命异常登记
- `tests/test_input_fidelity_review.py` — 82 项测试（原 64 项 + Code Review R1 新增 18 项）。T 系列（单元，零 pipeline 依赖）覆盖逐字节保真、内容完整性、字段归属、未选中事件覆盖、未渲染 title 标记、多 source 全量、17 组敌意载荷、围栏原语无损、结构注入防御、KB 反向引用与悬空登记、无自动判定、确定性、输入只读、退出码、自由文本与标识字段的格式策略、行内标识安全降级、非 Event 结构冲突登记、校验范围声明；X 系列（交叉验证，导入现有 pipeline）覆盖渲染位置与 `build_document()` 一致、字段可见性与真实 renderer 一致、探测项与真实 Pipeline 拒绝行为一致、端到端 CLI
- `tests/fixtures/fidelity_adversarial.json` — 对抗性源文档：多信源事件（含一条有真实 routing 记录的降级）、未选中 fact、hypothesis、open 事件、含反引号/管道符/换行/CRLF/全角/伪造块的敌意文本、悬空 Knowledge Bite 引用

#### Changed
- `README.md` — 仓库结构块中 `scripts/` 一行由「待实现」更新为「工具脚本（input_fidelity_review.py）」，反映当前实际内容

#### Fixed
（Code Review R1）

- **校验边界分离**：原实现仅强制 `validate_events()`（Event Contract），未区分「Event Contract 校验」与「完整 Daily Briefing 源文档契约校验」。现将边界显式化——Event Contract 违反仍为致命错误（退出码 `4`），非 Event 结构问题改为非致命探测；清单顶部增设「校验范围」小节，CLI 帮助明示 `validation=Event Contract（events[]）`，任何情况下不声称「完整源文档契约通过」
- **`SOURCE_STRUCTURE` 非致命异常登记**：新增 `probe_source_document()`，手工镜像 `pipeline.py` 源文档层的非 Event 结构规则（meta / selection / id 列表形态与重复 / methodology / market_data / knowledge_bites / follow_up_plan 形状），命中的冲突以 `SOURCE_STRUCTURE` 类型登记于「异常与契约冲突登记」小节，不中断输出、不改变退出码。Pipeline 生成报告时会以 `ContractError` 拒绝这些文档，而工具仍可为其生成审查清单，保留对部分 Pipeline 无法渲染的源文档的审查能力
- **自由文本统一 FVB 转录**：`events[].verification_criteria` 不再因长度较短落入行内格式，一律使用围栏块（自由文本）转录；`follow_up_plan[].next_check` 按已批准设计 E-08 由行内标识改为自由文本转录
- **行内标识字段安全降级**：Knowledge Bite / Market Snapshot / Follow-up 的行内标识字段统一走 `identifier_class()` 判定，值含反引号等破坏性字符时自动降级为围栏块，避免行内代码跨度被截断或破坏清单结构
- **字段统计更正**：真实 Pilot 的转录字段数由早前记录的 90 更正为 **186**。该差异源于临时核验脚本的路径过滤器写法（要求块名后紧跟 `.`，而真实路径为 `events[0].xxx`），**工具与测试套件从未丢字段**；已在测试中加入「清单路径集合 ↔ 扫描器提取集合」双向等值断言，防止同类漏计复发
- CLI 文案与错误消息同步更新：退出码 `4` 明确标注为 Event Contract 违反，stdout 增 `validation=` 与 `anomalies=N`

#### Verification
- 263 项测试全部通过（`PYTHONPATH=src pytest` 与 `env -u PYTHONPATH pytest` 双模式），其中既有 181 项零修改、零回归，Slice 5 测试 82 项（原 64 项 + Code Review R1 新增 18 项）
- 真实 Pilot 输入实测：双跑输出字节一致（SHA256 `ca662ba1aff0e4d666f166e3ad45906abe2df38242064b64921eea37401e22ab`，39,784 bytes）；**186** 个转录字段逐字节零失配（围栏块 83 + 行内 103），字符普查全等，逐载荷 SHA256 全等，全部路径可回溯至输入字段，无重复路径
- 校验范围实测：stdout 报 `validation=Event Contract（events[]）`，真实 Pilot 的非 Event 结构探测异常 0 项；清单正文不含「完整源文档契约通过」「源文档契约校验通过」等整体通过声明；错误输入仍以退出码 `4` 终止并明确标注为 Event Contract 违反
- 渲染状态交叉核验：工具推导的 8 个 Event 渲染位置与 `build_document()` 实际产物 **8/8 一致**（Tab 1: 4 / Tab 3: 2 / Tab 5: 1 / 完全未渲染: 1；title 不进入正文的事件 4 个；KB 引用 6 条，异常登记 0 项）
- 输入文件零修改：运行前后 SHA256 均为 `d92670729a40802e234b032084eb6bd0d06a4ff142f213d5ffb0eab78331a810`
- 工具运行时**零** `daily_briefing` 依赖（仅 stdlib + `contracts` 只读复用），不调用 `render()` / `build_document()`，因此超预算或被契约拒绝的输入仍可审查

#### Scope
- Tooling Feature，无产品代码变更；`src/**`（Event Contract / Pipeline / Renderer / Schema）零修改
- 未修改 Architecture、Governance、Contract、Renderer、Pipeline、测试基线与 `docs/daily/INPUT_PREPARATION.md`
- Code Review R1 轮仅修改 `scripts/input_fidelity_review.py` 与 `tests/test_input_fidelity_review.py`；结构探测为 Pipeline 规则的手工镜像（已标注冻结行号），不构成新的契约规则
- BACKLOG P0-003 保持 Pending（本工具是转录与覆盖核对工具，**不是**验证机制，不关闭 P0-003）
- 不依赖 Phase 9 / Phase 10；未实施自动事实验证、语义推断、自动修改或 Confidence 调整

---

### [Slice 4 — Structured Research Input Preparation] - 2026-10-21

#### Added
- `docs/daily/INPUT_PREPARATION.md` — 上游研究资料到 Daily Briefing 源文档的准备指南（Status: Populated，补充指南，不改变标准五文档结构）。覆盖：七个顶层输入块格式与职责、Event Record 必填字段、断言分类决策表（fact / inference / hypothesis）、`derived_from` / `verification_criteria` / `status=open` 的使用条件、Tab 1/3 显式事件选择、Market Snapshot 缺失数据处理、Knowledge Bite 认知价值验收、Follow-up 可操作性验收、Sources / Confidence / Estimated 标注规则、Mock / Real Mode 披露纪律、常见 ContractError → 成因 → 修复映射、CLI 命令与退出码、最终 Input Preparation Checklist。规则分三层标注：Contract Hard Requirements（代码强制）/ Research Quality Requirements（冻结 D2/D3，需人工判断内容质量）/ Recommended Writing Practices（推荐表达方式）

#### Changed
- `docs/README.md` — 在 Domain Documentation 下登记 Input Preparation 补充指南，并在 Cross-Reference Map 中补充条目
- `docs/core/CHANGELOG.md` — 追加本条目

#### Verification
- 181 项既有测试零修改、全部通过（`PYTHONPATH=src pytest` 与 `env -u PYTHONPATH pytest` 双模式）
- 指南引用的全部测试函数名、文件路径与规则名称已逐一核对存在
- 端到端 CLI 实测：`tests/fixtures/pipeline_sample.json` → 五 Tab HTML 生成成功，MOCK 横幅与来源标注正确
- 未新增任何契约规则；`src/` 与 `tests/` 零修改

#### Scope
- Documentation / Workflow Feature，无产品代码变更
- 未修改标准五份 Daily 文档、Architecture、Governance、Roadmap、Contract、Pipeline、Renderer 或测试
- BACKLOG P0-003 保持 Pending（Evidence 验证机制未完成）
- 不依赖 Phase 9 / Phase 10

---

### [Slice 3 — Minimum Daily Pipeline] - 2026-10-21

#### Added
- `src/daily_briefing/pipeline.py` — 最小 Daily Pipeline：把**研究源文档**映射为**可渲染的 Daily Document**。源文档顶层为 `meta` / `events[]` / `selection` / `market_data` / `knowledge_bites` / `follow_up_plan` / `methodology`；输出文档为 `meta` / `events` / `tabs` / `methodology`。核心纯函数 `build_document(source_document)`——无 IO、无网络、不修改入参。事件选择完全由输入显式决定：`selection.tab1_event_ids`（限 `assertion_type=fact`）与 `selection.tab3_event_ids`（限 `assertion_type=inference`），**无打分、无排序、无自动筛选**，仅校验 id 存在、类型匹配、不重复；Tab 2 / Tab 4 / Tab 5 分别由 `market_data` / `knowledge_bites` / `follow_up_plan` 派生；`methodology` 由输入拥有，Pipeline 自身不生成方法论文字。产物经既有报告契约 `validate()` 复验后才返回，共享的双向 Follow-up 规则（DV-8）不被绕过
- 附带 CLI `python -m daily_briefing.pipeline --input <source.json> [--out <path>]`，沿用 Slice 1 建立的退出码纪律：`0` 成功 / `2` 输入缺失或非法 JSON / `3` 词数门突破 / `4` 契约违反；默认输出 `output/daily-report-<run_date>.html`（文件名用 run date 而非 data date，避免重复运行覆盖既有报告）
- `tests/fixtures/pipeline_sample.json` — 最小 Pipeline 端到端夹具（源文档形态：6 events / 1 market / 1 knowledge bite / 1 follow-up / 3 selection ids）
- `tests/test_pipeline.py` — 64 项 Pipeline 测试

#### Verification
- **181 项**测试全部通过（`PYTHONPATH=src pytest -q` 与 `env -u PYTHONPATH pytest -q` 双模式），较 Slice 2 的 117 项净增 64 项（`tests/test_pipeline.py`）
- 确定性实测：以 `tests/fixtures/pipeline_sample.json` 双跑同一输入，两次输出**字节一致**（各 9,948 bytes，SHA256 `18481db1add5346accb2bcf3d0bb3aafb07820376deb219e8c7d2963eefc76a8`）
- 产物结构实测：`build_document()` 输出 `meta` / `events` / `tabs` / `methodology`，`tabs` 键为 `highlights` / `market_snapshot` / `impact_analysis` / `knowledge_bite` / `follow_up`，与冻结五 Tab 一一对应
- 复核：`src/daily_briefing/pipeline.py` 与 `tests/test_pipeline.py` 自本提交引入后**零修改**（至 `main@0758e34` 一致）

#### Scope
- Feature Implementation（产品代码）
- Slice 1 的 `src/daily_briefing/{schema,render,__main__}.py` 与 Slice 1/2 的既有测试**零修改**
- 未修改 Architecture、Governance、Contract（`src/contracts/**`）、冻结五 Tab 定义与五份 Daily 文档
- BACKLOG P0-003 保持 Pending（Evidence 验证机制未完成，归属 Phase 9）；Provider Routing 未实现，归属 Phase 10
- 不依赖 Phase 9 / Phase 10

#### Affected Documents/Code
- `src/daily_briefing/pipeline.py` — Added（536 行）
- `tests/fixtures/pipeline_sample.json` — Added（218 行）
- `tests/test_pipeline.py` — Added（675 行）

#### Commit
- `08e45d3c19f2921efb4c57c315f38b9cdd6431f1` — `feat(daily-briefing): add minimum daily pipeline`（2026-10-21 09:06:01 +0800）

---

### [Slice 2 — Reusable Event Data Contract] - 2026-10-20

#### Added
- `src/contracts/event.py` — 可复用、**层级中立**的 Event Contract（429 行）：Event Record 必填字段、枚举取值与 `validate_events()` 校验入口。断言类型 `fact` / `inference` / `hypothesis`；状态取值 `active` / `open` / `superseded` / `rejected`——**刻意不定义 `verified` 状态**，在没有验证机制之前不提供虚假状态值；`hypothesis` 必须声明 `verification_criteria`，`status=open` 同样必须声明验证标准，`fact` 不得携带 `derived_from`
- `src/contracts/evidence.py` — Evidence 基础类型（195 行）：置信度等级 `HIGH` / `MEDIUM` / `LOW-MEDIUM` / `LOW` 与对应徽章 🟢 / 🟡 / 🟠 / 🔴，来源标注数据结构、Provider 路由链词表，以及 `get_fallback_chain()`——降级必须由真实 routing 记录佐证，不得仅因 provider tier 非 P0 就推断降级
- `src/contracts/__init__.py` — 契约包公开接口与 `__all__` 导出（59 行）
- `tests/fixtures/event_sample.json` — Event Contract 夹具（262 行）
- `tests/test_event_contract.py` — 63 项 Event Contract 测试（734 行）

#### Changed
- `src/daily_briefing/schema.py` — 重构为消费 `contracts` 层的 Event Contract（+212 / −143），消除日报侧对事件结构的重复定义，使契约成为单一事实来源；其中 `get_fallback_chain()`（校验 Provider 降级须有真实 routing 记录）随 Evidence 基础类型一并迁入 `src/contracts/evidence.py`，由 `src/contracts/__init__.py` 统一导出，规则本身未放宽

#### Verification
- **117 项**测试全部通过（`PYTHONPATH=src pytest -q` 与 `env -u PYTHONPATH pytest -q` 双模式），较 Slice 1 的 54 项净增 63 项（`tests/test_event_contract.py`）
- 复核：`src/contracts/event.py`、`src/contracts/evidence.py` 与 `tests/test_event_contract.py` 自本提交引入后**零修改**（至 `main@0758e34` 一致）

#### Scope
- Feature Implementation（产品代码）
- Slice 1 的 `render.py` / `__main__.py` 与既有 54 项测试**零修改**
- 未修改 Architecture、Governance、冻结五 Tab 定义与五份 Daily 文档
- BACKLOG P0-003 保持 Pending；Evidence 验证机制（Phase 9）与 Source Registry / Provider Routing（Phase 10）未实施

#### Affected Documents/Code
- `src/contracts/__init__.py` — Added（59 行）
- `src/contracts/event.py` — Added（429 行）
- `src/contracts/evidence.py` — Added（195 行）
- `src/daily_briefing/schema.py` — Modified（+212 / −143）
- `tests/fixtures/event_sample.json` — Added（262 行）
- `tests/test_event_contract.py` — Added（734 行）

#### Commit
- `cf88c9ccbb9fb16a6c70737828aa0cfb904c0c34` — `feat(daily-briefing): add reusable event data contract`（2026-10-20 16:05:17 +0800）

---

### [Slice 1 — Mock-Driven Five-Tab Renderer] - 2026-10-20

#### Added
- `src/daily_briefing/schema.py` — Daily Briefing V2 输入契约与校验（Slice 1 版 458 行）：`TAB_ORDER` / `TAB_DEFS` 定义冻结五 Tab 的顺序与字段，`WORD_LIMIT = 500` 设定每 Tab 词数上限，`count_words()` / `count_tab_words()` 按 CJK 与西文混合规则计数，`validate()` 为契约入口，`ContractError` / `WordLimitExceeded` 为错误类型，`get_fallback_chain()` 校验 Provider 降级链须有真实路由记录。契约强制五条冻结规则：结论须有证据支撑、数据须带来源标注、数据须带置信度、缺失数据必须显式标注而不得伪造、Provider 降级必须有真实路由记录
- `src/daily_briefing/render.py` — 五 Tab HTML 渲染器（380 行）：`render()` 产出完整 HTML，`_render_tab()` / `_render_item()` 处理条目，`_source_line()` 输出来源行，`_badges()` 输出置信度徽章与「估算」标记，`_collect_tiers()` 汇总来源层级，`_render_footer()` 输出页脚
- `src/daily_briefing/__init__.py` — 包公开接口与版本号（17 行），并在 docstring 中声明本切片范围：无真实数据采集、无自动交叉验证、无完整 Evidence Layer，故**不关闭 BACKLOG P0-003**
- `src/daily_briefing/__main__.py` — CLI 入口（83 行）：`python -m daily_briefing --input <document.json> [--out <path>]`，退出码 `0` 成功 / `2` 输入缺失或非法 JSON / `3` 词数门突破 / `4` 契约违反；默认输出 `output/daily-report-<run_date>.html`；`data_mode=mock` 时于 stdout 声明输出为演示数据
- `tests/conftest.py` — 测试夹具装载与公共路径辅助（88 行）
- `tests/fixtures/daily_sample.json` — 渲染夹具（168 行，顶层 `meta` / `tabs` / `methodology`）
- `tests/test_schema.py` — 19 项契约测试（135 行）
- `tests/test_render.py` — 19 项渲染测试（178 行）
- `tests/test_quality_gates.py` — 16 项质量门测试（198 行）
- `.gitignore` — 新增 `!tests/**/*.json` 例外（5 行），使测试夹具不被 `*.json` 产物规则误排除，保证全新 clone 上测试可运行

#### Verification
- **54 项**测试全部通过（`PYTHONPATH=src pytest -q` 与 `env -u PYTHONPATH pytest -q` 双模式）：`tests/test_schema.py` 19 + `tests/test_render.py` 19 + `tests/test_quality_gates.py` 16
- 本切片之前仓库**无任何测试**（在 `e1420a7` 处收集结果为 "no tests ran"），本切片首次建立测试基线
- 复核：`src/daily_briefing/render.py`、`src/daily_briefing/__main__.py` 及全部 3 个测试文件自本提交引入后**零修改**；`src/daily_briefing/schema.py` 仅在 Slice 2 被重构为消费 `contracts` 层

#### Scope
- Feature Implementation（产品代码），Phase 4 首个 Slice
- 未修改 Architecture、Governance、冻结五 Tab 定义与五份 Daily 文档
- BACKLOG P0-001 / P0-003 保持 Pending；Provider Routing 未实现，归属 Phase 10

#### Affected Documents/Code
- `.gitignore` — Modified（+5）
- `src/daily_briefing/__init__.py` — Added（17 行）
- `src/daily_briefing/__main__.py` — Added（83 行）
- `src/daily_briefing/render.py` — Added（380 行）
- `src/daily_briefing/schema.py` — Added（Slice 1 版 458 行）
- `tests/conftest.py` — Added（88 行）
- `tests/fixtures/daily_sample.json` — Added（168 行）
- `tests/test_quality_gates.py` — Added（198 行）
- `tests/test_render.py` — Added（178 行）
- `tests/test_schema.py` — Added（135 行）

#### Commit
- `b9949e9f09f2667f24d444bf5ed60ae02c562f4f` — `feat(daily-briefing): add slice 1 mock-driven five-tab renderer`（2026-10-20 14:48:19 +0800）

---

### [Baseline Status Synchronization] - 2026-10-20

#### Changed
- `README.md` — 项目阶段状态同步：Phase 3 → Completed (2026-07-10)、Phase 4 → Authorized / Implementation Not Started、Repository Migration → Completed、GitHub repository description 备注由"待更新"改为"已更新"
- `docs/core/IMPLEMENTATION_ROADMAP.md` — Phase 3 / WP6 / WP8 状态 → Completed；Phase 4 → Authorized, Implementation Not Started；Current Position 更新为 Phase 4；Baseline Tag 引用由 `architecture-baseline-v1` 统一修正为 `v2.0-baseline`（原引用与实际 Baseline Release 不符）
- `docs/core/CHANGELOG.md` — 追加本条目

#### Verified Baseline
- WP1–WP8 全部完成，Architecture Migration 完成
- Baseline Commit: `16796dc`
- Baseline Tag: `v2.0-baseline`（GitHub Release 已发布，2026-07-10）
- Daily Briefing V2 尚未产生 Feature Implementation — 新系统业务代码实现进度 0%

#### Context
- 2026-10-20 完成 Development Resumption Audit（只读审计）：确认 local == origin/main、Working Tree 干净、Phase 4 尚未开始
- 2026-10-20 用户批准进入 Phase 4，并授权先执行 Baseline Status Synchronization

#### Scope
- 仅修正已经过时的状态描述，未修改冻结架构、产品设计、治理原则、五层架构或 Phase 1–11 定义与执行顺序

#### Affected Documents
- `README.md` — Modified（阶段状态同步）
- `docs/core/IMPLEMENTATION_ROADMAP.md` — Modified（Phase/WP 状态 + Tag 引用修正）
- `docs/core/CHANGELOG.md` — Modified（追加本条目）

---

### [Final Baseline Verification] - 2026-07-10

#### Fixed
- Cross-reference corrections in 8 docs: `docs/core/AGENT_ONBOARDING.md`, `docs/core/ARCHITECTURE.md`, `docs/core/GOVERNANCE.md`, `docs/core/MISSION.md`, `docs/core/REFACTOR_BACKLOG.md`, `docs/core/REPORT_DESIGN.md`, `docs/core/RESEARCH_SYSTEM.md` — `./README.md` → `../README.md` (Related Documents sections assumed flat docs/ structure, corrected to docs/core/ subdirectory)
- Cross-reference corrections in `docs/provider/DATA_SOURCE.md` — `./README.md` → `../README.md`, `./GOVERNANCE.md` → `../core/GOVERNANCE.md`, `./ARCHITECTURE.md` → `../core/ARCHITECTURE.md`
- Summary count corrections in `archive/legacy-trend-tracker/LEGACY_MAPPING.md` — EVOLVE 9→10, REFERENCE 6→8 (skill files were undercounted)
- Summary count correction in `docs/core/CHANGELOG.md` WP5 entry — REFERENCE 6→4, REPLACED 1→3 (repository files only)

#### Verification Results
- 150 markdown links checked, 0 broken (1 archived legacy link expected)
- All 9 Blueprint WP6 checks passed
- 0 Python/HTML/JSON/SQL/Pipeline/Prompt modifications
- Working Tree: 10 files modified (cross-reference fixes only)

#### Affected Documents
- `docs/core/AGENT_ONBOARDING.md` — Modified (cross-reference fix)
- `docs/core/ARCHITECTURE.md` — Modified (cross-reference fix)
- `docs/core/GOVERNANCE.md` — Modified (cross-reference fix)
- `docs/core/MISSION.md` — Modified (cross-reference fix)
- `docs/core/REFACTOR_BACKLOG.md` — Modified (cross-reference fix)
- `docs/core/REPORT_DESIGN.md` — Modified (cross-reference fix)
- `docs/core/RESEARCH_SYSTEM.md` — Modified (cross-reference fix)
- `docs/provider/DATA_SOURCE.md` — Modified (cross-reference fixes, 3 links)
- `archive/legacy-trend-tracker/LEGACY_MAPPING.md` — Modified (summary count corrections)
- `docs/core/CHANGELOG.md` — Modified (WP6 entry + WP5 count correction)

---

### [Artifact Protection Upgrade] - 2026-07-10

#### Added
- `docs/core/ARTIFACT_MANAGEMENT.md` — Artifact management specification: 7-category classification, commit rules, generated report lifecycle, runtime data lifecycle, Build Before Remove principle, Git Hygiene Checklist, .gitignore coverage map
- `.gitignore` — Comprehensive artifact protection rules (7 categories, 43+ patterns)

#### Changed
- `.gitignore` — Upgraded from 34 lines (v1.4-era) to comprehensive 7-category protection. New rules: `*.html`, `*.json` (with `!config/*.json` exception), `reports/`, `output/`, `artifacts/`, `examples/generated/`, `trend_data/`, `tmp/`, `.cache/`, `*.cache`, `logs/`, `runtime/`, `*.db`, `*.sqlite`, `*.sqlite3`, `.env.*` (with `!.env.example` exception), additional IDE/OS patterns. Superseded legacy `trend_data/weekly/*.json` and `db/*.db` with broader rules.
- `docs/README.md` — Added ARTIFACT_MANAGEMENT.md to Core Documentation table (now 12 core docs) and cross-reference map
- `README.md` — Added Artifact Management reference in repository structure section

#### Evolution Note
Artifact Protection completes the Repository Governance Baseline. Generated artifacts (HTML reports, JSON data, SQLite databases, logs, cache) are now comprehensively excluded from Git via .gitignore. Static configuration files (`config/*.json`) and milestone examples (`examples/*.html` via `git add -f`) remain trackable through negation rules.

#### Affected Documents
- `.gitignore` — Modified (comprehensive upgrade, 7 categories)
- `docs/core/ARTIFACT_MANAGEMENT.md` — New (artifact management specification)
- `docs/README.md` — Modified (navigation table + cross-reference)
- `README.md` — Modified (artifact reference in structure section)

---

### [Legacy Archive & Mapping] - 2026-07-09

#### Added
- `archive/legacy-trend-tracker/DEPRECATED.md` — Archival notice with evolution language, file inventory, and evolution path summary
- `archive/legacy-trend-tracker/README.md` — Archived Trend Tracker v1.4 README (retrieved from Git history, DEPRECATED header added)

#### Changed
- `archive/legacy-trend-tracker/LEGACY_MAPPING.md` — Updated final note: archiving complete (was "no code moved yet")
- `README.md` (repository root) — Updated repository structure section: removed legacy directories (collectors/, processors/, db/, pipeline_mock.py, pipeline_real.py, ROADMAP.md), added full archive/ tree
- `docs/README.md` — Updated Legacy Reference section: legacy docs/ARCHITECTURE.md now archived to archive/legacy-trend-tracker/docs/ARCHITECTURE.md
- `docs/core/OBSERVATION_PHASE_SNAPSHOT.md` — Fixed cross-reference: docs/ARCHITECTURE.md → docs/core/ARCHITECTURE.md

#### Archived (16 files via git mv)
- `ROADMAP.md` → `archive/legacy-trend-tracker/ROADMAP.md` (DEPRECATED header added)
- `docs/ARCHITECTURE.md` → `archive/legacy-trend-tracker/docs/ARCHITECTURE.md` (DEPRECATED header added)
- `pipeline_mock.py` → `archive/legacy-trend-tracker/pipeline_mock.py`
- `pipeline_real.py` → `archive/legacy-trend-tracker/pipeline_real.py`
- `collectors/*.py` (4 files) → `archive/legacy-trend-tracker/collectors/`
- `processors/*.py` (4 files) → `archive/legacy-trend-tracker/processors/`
- `db/db_init_v1.1.sql` + `db/migrations/*.sql` (3 files) → `archive/legacy-trend-tracker/db/`

#### Removed
- Empty directories: `collectors/`, `processors/`, `db/`
- `archive/.DS_Store`

#### Evolution Note
Build Before Remove principle fully satisfied: new structure (WP2-WP4) was built and committed before legacy files were archived. All 16 files preserve Git history. Legacy Mapping documents 9 EVOLVE, 4 REFERENCE, 3 REPLACED (repository files) evolution paths.

---

### [Repository Identity Migration] - 2026-07-09

#### Changed
- `README.md` (repository root) — Replaced Trend Tracker v1.4 README with Personal Investment Research System identity. New README includes: system mission, five-layer architecture overview, evolution story from Trend Tracker, legacy mapping summary, knowledge assets, repository structure, current implementation phase, quick-start guide, and governance references. All 18 cross-references validated.

#### Affected Documents
- `README.md` — Modified (repository identity transformation)

---

### [Governance Migration] - 2026-07-08

#### Added
- `docs/core/ENGINEERING_GOVERNANCE.md` — Engineering Governance V1 (9 sub-items: Core Philosophy, Architecture Principles, Development Standard, AEW, Quality Gates, Documentation Governance, Git Workflow, Repository Structure, Artifact Management)
- `docs/core/IMPLEMENTATION_ROADMAP.md` — Implementation Roadmap V1 (Phase 1-11 with current progress annotations)

#### Changed
- `docs/core/GOVERNANCE.md` — Updated governance framework overview to reference ENGINEERING_GOVERNANCE.md and IMPLEMENTATION_ROADMAP.md; added EVIDENCE_LAYER.md to related documents
- `docs/README.md` — Updated core documentation table (11 docs), cross-reference map, and developer reference order to include new governance docs

#### Affected Documents
- `docs/core/ENGINEERING_GOVERNANCE.md` — New (Engineering Governance V1, 9 sub-items)
- `docs/core/IMPLEMENTATION_ROADMAP.md` — New (Phase 1-11 roadmap with progress)
- `docs/core/GOVERNANCE.md` — Modified (governance framework overview + related documents)
- `docs/README.md` — Modified (navigation table + cross-reference map + developer reference)

---

### [Architecture Baseline Migration] - 2026-07-08

#### Added
- Documentation migrated to GitHub repository (Single Source of Truth)
- Core documentation established in `docs/core/` (9 documents)
- Domain documentation established for all 5 layers (25 documents)
- Cross-cutting documentation established: `docs/provider/`, `docs/evidence/`, `docs/investment-mapping/`
- Documentation navigation (`docs/README.md`) with complete cross-reference map
- LEGACY_MAPPING.md in `archive/legacy-trend-tracker/` (WP2)
- Repository skeleton: `src/`, `config/`, `examples/`, `scripts/`, `tests/`, `archive/` (WP2)

#### Changed
- Trend Tracker v1.4 evolved into Personal Investment Research System (first domain → five-layer system)
- Documentation structure reorganized from flat to Core + Domain architecture
- WP2 placeholder docs (`docs/domains/`) replaced with proper domain documentation
- Repository structure upgraded to frozen standard (7 directories)

#### Evolution Note
Trend Tracker is not abandoned — it is the first completed Domain of Personal Investment Research System. Legacy components are archived with Legacy Mapping for future evolution. Git history, knowledge, and architecture maintain continuity.

#### Affected Documents/Code
- `docs/core/` — 9 migrated documents (MISSION, ARCHITECTURE, RESEARCH_SYSTEM, GOVERNANCE, REPORT_DESIGN, AGENT_ONBOARDING, REFACTOR_BACKLOG, CHANGELOG, OBSERVATION_PHASE_SNAPSHOT)
- `docs/daily/` — 5 Daily Briefing domain docs (product, architecture, workflow, roadmap, decisions)
- `docs/research-terminal/` — 5 Research Terminal domain docs
- `docs/industry/` — 5 Industry Research domain docs
- `docs/company/` — 5 Company Research domain docs
- `docs/monthly/` — 5 Monthly Outlook domain docs
- `docs/provider/` — DATA_SOURCE.md
- `docs/evidence/` — EVIDENCE_LAYER.md
- `docs/investment-mapping/` — INVESTMENT_MAPPING.md
- `docs/README.md` — Documentation navigation
- `archive/legacy-trend-tracker/LEGACY_MAPPING.md` — Legacy component mapping

---

### [Observation Phase End] - 2026-07-06

#### Added
- 建立 Documentation 体系（Phase 2）
  - 新增文档：`README.md`, `MISSION.md`, `ARCHITECTURE.md`, `REPORT_DESIGN.md`, `RESEARCH_SYSTEM.md`, `GOVERNANCE.md`, `DATA_SOURCE.md`, `CHANGELOG.md`, `AGENT_ONBOARDING.md`, `REFACTOR_BACKLOG.md`
  - 更新文档：`OBSERVATION_PHASE_FINAL_SNAPSHOT.md`

#### Changed
- 五层架构术语澄清：
  - Research Terminal = Research Navigator（不是 Knowledge Base）
  - Industry Research = Industry Framework（不是 Industry Report）
  - Company Research 必须建立在 Industry Research 基础之上
  - Monthly Outlook = Knowledge Evolution（不是新闻汇总）
- 新增 Knowledge Flow 定义（Daily → Research Terminal → Industry → Company → Monthly）
- 新增 GitHub = Single Source of Truth 原则
- 新增工程流程定义（Discussion → Architecture Freeze → Documentation → GitHub → Implementation）

#### Affected Documents/Code
- `OBSERVATION_PHASE_FINAL_SNAPSHOT.md`（更新）
- `~/.workbuddy/docs/`（新增 10 份文档）

---

### [Observation Phase] - 2026-05 to 2026-07

#### Added
- Daily Briefing V2（5 Tabs 冻结）
- Research Terminal V1（3 Tabs 冻结）
- 五层架构设计（Event Layer → Research Navigator → Industry Framework → Decision Support → Knowledge Evolution）
- Observation Phase 核心问题识别（8 个问题）

#### Changed
- 项目定位从"日报生成系统"演进为"认知积累研究系统"

#### Affected Documents/Code
- `skills/daily-briefing/`
- `skills/trend-tracker/`
- `~/.workbuddy/frameworks/`

---

## Related Documents

- [README.md](../README.md) — 文档体系入口
- [ARCHITECTURE.md](./ARCHITECTURE.md) — 架构变更记录（本文档引用）
- [GOVERNANCE.md](./GOVERNANCE.md) — 变更管理流程（本文档遵循）
- [REFACTOR_BACKLOG.md](./REFACTOR_BACKLOG.md) — 重构待办（变更需求来源）

---

*本文档随系统演化持续更新。任何变更都必须先记录至本文档，再实施。*
