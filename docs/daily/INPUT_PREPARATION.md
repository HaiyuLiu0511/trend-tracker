# Input Preparation — Daily Briefing

> **Layer:** 1 — Event Layer
> **Status:** Populated
> **Type:** 补充指南（Supplementary Guide）— 不改变标准五文档结构
> **Baseline:** `main = 08e45d3`（Slice 3 合并后）
> **日期:** 2026-10-21

---

## 0. 本文档的定位

本文档是**补充指南**，不是标准文档。Layer 1 的标准五文档仍然是：

| 标准文档 | 职责 |
|---------|------|
| [product.md](./product.md) | Tab 定义与职责边界 |
| [architecture.md](./architecture.md) | 本层架构与组件 |
| [workflow.md](./workflow.md) | 生成流程与质量门 |
| [decisions.md](./decisions.md) | 冻结决策 D1–D5 |
| [roadmap.md](./roadmap.md) | 本层演进路线 |

本文档只解决一个具体问题：**如何把已收集的研究资料整理成 `daily_briefing.pipeline` 接受的结构化输入**。

本文档**不新增任何契约规则**。所有技术规则均转写自现有代码，引用位置与测试函数名一并给出，可逐条核对。

### 0.1 规则分层（阅读本文档前必读）

本文档中的每一条规则都属于以下三层之一。混淆这三层是本系统最常见的错误来源。

| 层 | 含义 | 谁来判定 | 违反后果 |
|----|------|---------|---------|
| **[H] Contract Hard Requirements** | 由现有代码强制执行 | 机器（契约校验） | Pipeline 报错，退出码 4，**不生成任何文件** |
| **[Q] Research Quality Requirements** | 由冻结决策（D2/D3 等）规定为强制质量原则，但**目前仍需人或 Agent 判断内容质量** | 人 / Agent 自评 | 代码不会报错，但报告失去认知价值 |
| **[R] Recommended Writing Practices** | 推荐的具体表达方式 | 建议 | 无强制力，仅提升可读性 |

**关键原则**：[H] 是不可协商的；[Q] 是不可省略的（但由人判断）；[R] 可以调整。凡本文档标注 [R] 的内容，均**不是**新的硬校验规则。

### 0.2 如何核对本文档的技术规则

每条 [H] 规则都给出代码位置与对应的**测试函数全名**，可用以下命令逐条核对：

```bash
# 核对某条规则的测试是否存在
grep -rn "def test_p20_action_is_required" tests/

# 运行全部契约测试
PYTHONPATH=src pytest tests/ -q
```

少数引用写作前缀（如 `test_p20`、`test_r11`），是因为一个前缀下存在多个并列测试（如 `test_p20` 与 `test_p20b`），此时按前缀检索即可覆盖全部相关用例。

---

## 1. 端到端数据流与职责边界

```
已收集的研究资料（新闻 / 公告 / 行情 / 人工与 AI 分析）
        │
        ▼【推理职责：人或上游 Research Agent】
   整理为 7 个顶层块的源文档 JSON
        │
        ▼【确定性职责：daily_briefing.pipeline】
   build_document()  →  validate()  →  render()
        │
        ▼
   output/daily-report-<run_date>.html
```

| 环节 | 职责方 | 层 |
|------|--------|---|
| 什么算一个事件 | 研究 Agent | [Q] |
| 断言分类（fact / inference / hypothesis） | Agent 判断；代码校验结构一致性 | [Q] + [H] |
| `derived_from` 推理链 | Agent 提供；代码强制可达 fact、无环 | [Q] + [H] |
| Tab 1/3 选哪些事件（selection） | Agent 显式 id 列表；代码校验存在性与类型 | [Q] + [H] |
| Knowledge Bite 撰写 | Agent 显式提供；代码**拒绝**代生成 | [Q] + [H] |
| Follow-up action / next_check | Agent 决策；代码**拒绝**推导 | [Q] + [H] |
| confidence 标注 | Agent 自述；代码原样拷贝、禁止改写 | [Q] 定级 + [H] 取值范围 |
| routing.attempted 记录 | 采集方如实记录；代码验记录内部一致性 | [Q] 真实性 + [H] 一致性 |
| 结构 / 引用 / 环 / 双向跟踪校验 | 代码 | [H] |
| 500 词/Tab 质量门 | 代码（超限不截断、不写文件） | [H] |
| 横幅 / 披露 /（估算）标注 / 文件命名 / 退出码 | 代码 | [H] |
| Evidence 验证机制 | **无人** — BACKLOG P0-003 仍 Pending，属 Phase 9 | 未来 |
| Provider 路由实现 | **无人** — 属 Phase 10 | 未来 |

**边界规则：Pipeline 永不写分析；Agent 永不绕过契约。**

---

## 2. 源文档的七个顶层块

源文档是一个 JSON 对象，包含 7 个顶层块。

| 块 | 必填 | 职责 | 代码位置 |
|----|------|------|---------|
| `meta` | [H] 是 | 报告标识与披露声明 | `pipeline.build_document()` |
| `events` | [H] 是（列表，可为空） | Event Record 数组 | `contracts.event.validate_events()` |
| `selection` | [H] 是 | Tab 1/3 的显式事件选择 | `pipeline._select_events()` |
| `market_data` | 否（可缺失） | Tab 2 市场快照 | `pipeline._market_items()` |
| `knowledge_bites` | [H] 是（非空） | Tab 4 认知单元 | `pipeline._knowledge_bite_items()` |
| `follow_up_plan` | [H] 是（可为空数组） | Tab 5 跟踪计划 | `pipeline._follow_up_items()` |
| `methodology` | [H] 是 | 方法与局限声明 | `schema.validate()` |

### 2.1 `meta` [H]

```json
"meta": {
  "report_type": "Daily Briefing",
  "run_date": "2026-10-20",
  "data_date": "2026-10-20",
  "data_mode": "mock"
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `report_type` | [H] 非空字符串 | 缺省时 Pipeline 填入 `"Daily Briefing"` |
| `run_date` | [H] | **决定输出文件名**（decisions.md D4）。缺失时错误消息会提示此项 |
| `data_date` | [H] | 显示在报告标题与页眉 |
| `data_mode` | [H] | 只能是 `mock` 或 `real`，驱动披露横幅 |

三个必填字段缺失时抛出 `ContractError`（附字段用途提示），**不是** `KeyError`。参考 `test_p45_missing_meta_field_raises_contract_error`、`test_p45b_missing_meta_field_is_not_a_key_error`、`test_p47_cli_returns_4_and_writes_nothing_for_missing_meta`。

[R] `run_date` 与 `data_date` 可以不同：回补历史数据时 `data_date` 早于 `run_date`，文件名仍用 `run_date`。

---

## 3. Event Record 格式

### 3.1 完整字段表 [H]

下表列出 Event Record 的**全部字段**。必填 10 项用 ● 标注；其余为可选字段。

**注意**：可选字段的适用条件由断言类型决定——`derived_from` 只能出现在 inference 上，`verification_criteria` 必须在 hypothesis 与 `status=open` 时出现。逐条规则见 §4。

```json
{
  "event_id": "evt-20261020-chip-v2",
  "title": "示例科技修订芯片规格说明",
  "summary": "官方次日修订首发吞吐数据，数值下调。",
  "assertion_type": "fact",
  "status": "active",
  "occurred_at": "2026-10-20",
  "collected_at": "2026-10-20",
  "data_date": "2026-10-20",
  "themes": ["AI 算力供应链"],
  "companies": ["示例科技"],
  "supersedes": "evt-20261020-chip-launch",
  "related_event_ids": ["evt-20261020-chip-launch"],
  "sources": [
    {
      "name": "provider-alpha",
      "provider_tier": "P0",
      "locator": "https://...",
      "routing": {
        "attempted": [
          {"tier": "P0", "provider": "provider-alpha", "outcome": "success"}
        ]
      }
    }
  ],
  "confidence": "HIGH",
  "estimated": false
}
```

**10 个必填字段** [H]：`event_id`、`title`、`summary`、`assertion_type`、`status`、`occurred_at`、`collected_at`、`data_date`、`sources`、`confidence`。

代码位置：`contracts.event.REQUIRED_EVENT_FIELDS`。参考 `test_t41_event_requires_its_core_fields`、`test_t39_event_requires_evidence_support`。

**可选字段的适用条件**：

| 字段 | 适用条件 |
|------|---------|
| `themes` / `companies` | 任意类型；非空字符串列表 |
| `supersedes` | 新记录取代旧记录时使用；不得指向自身 |
| `related_event_ids` | 任意类型的横向关联 |
| `derived_from` | **仅 inference** 必填；fact 上必须为空或缺省 |
| `verification_criteria` | **hypothesis 必填**；`status=open` 时必填 |

同一份文档中三种断言类型的对照（**以下为节选，省略了 `title` / `sources` 等必填字段**，仅用于对比差异字段）：

```json
{
  "event_id": "evt-20261020-chip-impact",
  "assertion_type": "inference",
  "derived_from": ["evt-20261020-chip-v2"],
  "status": "active"
}
```

```json
{
  "event_id": "evt-20261020-dedup-hypothesis",
  "assertion_type": "hypothesis",
  "verification_criteria": "比对两条报道的发布时间与引用链条，确认是否指向同一原始信源。",
  "status": "open"
}
```

前者是 **inference**：必须给出推导基础（`derived_from`），且该链条最终要落到某个 `fact`。后者是 **hypothesis**：必须说明如何验证（`verification_criteria`）；其 `status="open"` 表示已纳入正式跟踪，因此还需在 `follow_up_plan` 中有对应条目（见 §9）。若把该假设设为 `status="active"`，则不强制进入 Tab 5。

### 3.2 标识符 `event_id` [H]

格式：`evt-<YYYYMMDD 首次识别日期>-<ascii slug>`

- 正则：`^evt-\d{8}-[a-z0-9][a-z0-9-]*$`（`contracts.event.EVENT_ID_PATTERN`）
- **日期段必须是真实存在的日历日期**（如 `2026-02-30` 会被拒绝）
- slug 仅允许小写字母、数字与连字符

**日期段是事件「首次被识别」的日期，不是报告生成日期。**

[R] slug 用英文小写短横线，概括事件主体而非标题全文，例如 `chip-spec-revision`。

### 3.3 标识符稳定性 [H 格式与唯一性 / Q 跨日报稳定性]

`event_id` 由调用方赋值，**必须**在事件存续期间保持不变。

**由代码强制的部分 [H]**：

- 格式必须匹配 `^evt-\d{8}-[a-z0-9][a-z0-9-]*$`，且日期段是真实日历日期
- 同一份文档内 `event_id` 不得重复
- 契约**刻意不提供**任何 id 生成辅助函数

**由输入方保证的部分 [Q]**：

- **跨日报稳定性目前没有机器校验**。系统没有事件持久化、没有历史库、没有跨报告的身份解析，因此「昨天用的 id 今天必须还用同一个」这一要求**无法由代码验证**，只能由输入方（或调用方）自行保证。
- 具体要求：不得从标题重新生成；不得因内容更新或重新运行而改变。

参考 `test_t02_event_id_format_is_enforced`、`test_t03_event_id_date_must_be_a_real_calendar_day`、`test_t04_duplicate_event_id_is_rejected`、`test_t05_identifier_is_stable_under_content_changes`（该用例验证的是**单份文档内** id 不随标题与日期变化而漂移，而非跨日报校验）、`test_t06_contract_offers_no_identifier_generation_helper`。

事件被修订时：新建一条 Event Record，用 `supersedes` 指向旧记录，**不要**改写旧记录。

### 3.4 三个日期字段 [H]

| 字段 | 语义 |
|------|------|
| `occurred_at` | 事件发生的时间 |
| `collected_at` | 被采集到的时间 |
| `data_date` | 该数据对应的数据日期 |

三者都必须是 `YYYY-MM-DD` 格式的真实日历日期（`contracts.event._validate_date`）。

### 3.5 `sources` [H]

`sources` 必须是非空列表（每个事件都必须有证据支撑）。每条 source：

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | [H] 非空 | 来源名称 |
| `provider_tier` | [H] | 只能是 `P0` / `P1` / `P2` / `P3` |
| `locator` | [H] 非空 | 可追溯定位符（URL、文件路径、DOI 等） |
| `routing` | 否 | 路由记录，见 §7.2 |

代码位置：`contracts.evidence.validate_source()`（全项目唯一实现，被日报契约与事件契约共用）。

参考 `test_s08b_source_requires_locator`、`test_t31_confidence_scale_has_a_single_definition`。

### 3.6 `confidence` 与 `estimated` [H 取值 / Q 定级]

`confidence` 只能是四级之一：`HIGH` / `MEDIUM` / `LOW-MEDIUM` / `LOW` — [H]（取值范围由代码校验；**定级是否恰当由输入方判断** — [Q]，见 §7.1）

`estimated` 必须是布尔值 — [H]。为 `true` 时报告会渲染「（估算）」标注。

---

## 4. 断言分类：Fact / Inference / Hypothesis

### 4.1 语义区分 [Q]

| 类型 | 语义 | 典型例子 |
|------|------|---------|
| **fact** | 可溯源的观测、公告或数据本身 | 「公司公告称单卡吞吐提升 2.4 倍」 |
| **inference** | 从 facts 推导出的分析判断 | 「吞吐提升将带来单位推理成本下降」 |
| **hypothesis** | 尚待验证的判断 | 「两条二手报道实为同源」 |

分类错误是本系统最严重的缺陷类型：把推断写成 fact 会让读者误以为结论已被证实。

### 4.2 结构约束 [H]

代码对三者施加**不同的结构约束**，使三者无法被静默混淆：

| 类型 | `derived_from` | `verification_criteria` |
|------|----------------|------------------------|
| **fact** | **必须为空或缺省** — 原始事实不是从其他记录推导出来的 | 不要求 |
| **inference** | **必填且非空** — 分析判断必须可溯源 | 不要求 |
| **hypothesis** | 不要求 | **必填** — 待验证的判断必须说明如何验证 |

代码位置：`contracts.event.validate_event()`。参考 `test_t07_fact_must_not_carry_derived_from`、`test_t08_inference_requires_derived_from`、`test_t09_hypothesis_requires_verification_criteria`、`test_t40_assertion_types_are_exactly_three`。

### 4.3 推理链可达性 [H]

每个 `inference` 必须通过 `derived_from` 链条**一步或多步**到达至少一个 `fact`。

- ✅ `inference → fact`（一步）
- ✅ `inference → inference → fact`（多跳）
- ❌ `inference → inference`（链条末端不是 fact，悬空推断）

参考 `test_t14_inference_that_cannot_reach_any_fact_is_rejected`、`test_t15_inference_chain_of_several_hops_is_accepted`、`test_t15b_inference_reaching_fact_in_one_hop_is_accepted`。

### 4.4 引用完整性与无环 [H]

- `derived_from`、`related_event_ids`、`supersedes` 引用的 event 必须存在于同一份 `events` 数组中
- `derived_from` **不得成环**
- `supersedes` **不得成环**，且**不得指向自身**
- `related_event_ids` **不适用**无环约束——代码只对 `derived_from` 与 `supersedes` 两个关系做环检测

参考 `test_t12_derived_from_must_reference_a_known_event`、`test_t13_derived_from_must_be_acyclic`、`test_t21_supersedes_must_reference_a_known_event`、`test_t22_supersedes_must_not_self_reference`、`test_t23_supersedes_relation_must_be_acyclic`。

### 4.5 `status` [H]

只能是四个值之一：`active` / `open` / `superseded` / `rejected`。

**没有 `verified` 状态**——Evidence 验证机制尚未完成（BACKLOG P0-003 仍 Pending），若存在该状态会暗示系统不具备的能力。参考 `test_t11_status_verified_is_not_allowed`。

`status=open` 触发两条额外约束：

1. **必须**有非空的 `verification_criteria`（被正式跟踪的事项必须可验证）— `test_t10_open_status_requires_verification_criteria`
2. **必须**在 `follow_up_plan` 中有对应条目 — `test_t17_open_hypothesis_without_follow_up_is_rejected`，详见 §9

---

## 5. Tab 1/3 的事件选择

### 5.1 `selection` 块 [H]

```json
"selection": {
  "tab1_event_ids": ["evt-20261020-chip-v2"],
  "tab3_event_ids": ["evt-20261020-margin-chain", "evt-20261020-chip-impact"]
}
```

| 约束 | 层 | 说明 |
|------|----|------|
| 必须是列表 | [H] | |
| 每个 id 必须存在于 `events` | [H] | `test_p06_selection_rejects_unknown_id` |
| 同一列表内不得重复 | [H] | `test_p08_duplicate_selection_id_is_rejected` |
| **Tab 1 只能选 `fact`** | [H] | `test_p04_tab1_rejects_a_non_fact_id` |
| **Tab 3 只能选 `inference`** | [H] | `test_p05_tab3_rejects_a_non_inference_id` |
| 空列表是允许的 | [H] | `test_p07_empty_selection_is_allowed` |

### 5.2 选择是编辑决策 [Q]

Pipeline **不评分、不排序、不筛选**。`tab3_event_ids` 的顺序**就是**报告中的展示顺序。

- 「选什么」由 Agent 决定 — [Q]
- 「顺序如何」也由 Agent 决定 — [Q]
- 代码只校验存在性与类型 — [H]

参考 `test_p01_tab1_uses_selected_facts_in_input_order`、`test_p02_tab3_uses_selected_inferences_in_input_order`、`test_p09_pipeline_exposes_no_scoring_or_ranking`。

未被选中的事件：

- **不进入** Tab 1 / Tab 3 的自动映射（Tab 1/3 只映射 `selection` 中显式列出的 id）— [H]
- **仍保留**在输出文档的 `events` 块中 — [H]（`test_p03_unselected_events_are_not_shown_but_are_preserved`）
- **可以作为** Tab 4 Knowledge Bite 的引用对象（`knowledge_bites[].event_ids` 引用的事件不必出现在 Tab 1/3）— [H]
- 若其 `status=open`，**仍必须**由 Tab 5 跟踪（双向规则不因未被选中而豁免）— [H]

[R] 选择理由（为何今天最值得呈现这三条）建议在 `methodology.methods` 中说明。

### 5.3 Tab 1 文本格式 [H]

Tab 1 的文本由 Pipeline 按固定格式生成：

```
{title}：{summary}
```

代码位置：`pipeline.TAB1_TEXT_FORMAT`。这是全流程**唯一**拼接两个字段的地方。参考 `test_p12_tab1_text_is_the_exact_fixed_format`、`test_p14_source_text_is_not_rewritten`、`test_p15_pipeline_introduces_no_extra_wording`。

[R] 因此 `title` 与 `summary` 各自必须能独立读懂：读者会在拼接后看到「标题：摘要」，若标题是「关于芯片」这类无信息量的表述，整行就没有价值。

### 5.4 Tab 3 文本格式 [H]

Tab 3 **原样使用**事件的 `summary`，不做任何改写（`test_p13_tab3_text_is_the_verbatim_summary`）。

[R] 因此影响链分析应直接写进 inference 事件的 `summary` 里。

---

## 6. Tab 2 Market Snapshot

### 6.1 有数据时 [H]

```json
"market_data": {
  "items": [
    {
      "text": "模拟指数收盘 3,412.65，涨 0.82%",
      "source": {"name": "...", "provider_tier": "P0", "locator": "..."},
      "confidence": "HIGH",
      "estimated": false
    }
  ],
  "unavailable_reason": null
}
```

| 约束 | 层 |
|------|----|
| `items` 存在时**必须**为列表 | [H] |
| 每项 `text` 必填非空 | [H] |
| 有 items 时 `unavailable_reason` **必须**为 `null` | [H] `test_p26_items_present_with_a_reason_is_rejected` |
| Tab 2 **禁止**携带任何事件引用 | [H] `test_t27_tab2_must_not_carry_event_references` |

市场状态不是事件，因此 Tab 2 不带 `event_id` / `event_ids`。

### 6.2 缺失时 [H]

三种等价写法，都表示「本次没有市场数据」：

1. 省略整个 `market_data` 键
2. `"market_data": {}`
3. `"market_data": {"items": [], "unavailable_reason": "真实理由"}`

| 约束 | 层 |
|------|----|
| 给了 `unavailable_reason` 就必须是非空字符串 | [H] 空字符串被拒 `test_p27` |
| 没有理由时使用固定中性措辞「本次输入未包含市场数据」 | [H] `pipeline.NEUTRAL_MARKET_MISSING_REASON` |

**绝对禁止**编造 Provider 失败原因（如「XX 数据源超时」）——除非确实发生过且有 routing 记录支撑。参考 `test_p24_absent_market_data_with_a_real_reason`、`test_p25_absent_market_data_without_a_reason_is_neutral`、`test_p27b_missing_market_data_key_uses_the_neutral_wording`。

参考 `test_p27c_market_items_are_mapped_verbatim`。

### 6.3 「缺数据」本身是合法状态 [Q]

Phase 10（Source Registry）完成前没有自动数据来源。缺数据就如实标记——这比编造数字更有价值。

[R] 若某类市场数据缺失但值得说明，可在 `methodology.limitations` 中记录原因。

---

## 7. Sources、Confidence、Estimated 与 Methodology

### 7.1 Confidence 四级 [H 标注 / Q 定级]

徽章定义（`contracts.evidence.CONFIDENCE_BADGE`）：

| 值 | 徽章 | 含义 |
|----|------|------|
| `HIGH` | 🟢 | 一手或官方来源 |
| `MEDIUM` | 🟡 | 可靠二手来源 |
| `LOW-MEDIUM` | 🟠 | 部分数据为估算或推断 |
| `LOW` | 🔴 | 未验证、推测或单一非权威来源 |

**徽章是输入数据的自带标注，系统原样拷贝、绝不改写、绝不升级**（`test_p17_confidence_is_copied_verbatim`、`test_r11c_confidence_scale_is_unchanged_by_real_mode`）。

**定级是 [Q] 责任**：代码只校验取值合法，不判断定级是否恰当。

[H] `unavailable` 项**禁止**携带 source 与 confidence——缺失数据没有徽章（`test_q05`、`test_s09b_unavailable_must_not_carry_confidence`、`test_s09c_unavailable_must_not_carry_source`）。

### 7.2 `routing.attempted` [H]

Fallback 标注**只**在有真实路由记录时渲染。仅仅声明一个 P1/P2/P3 tier **不构成** P0 失败的证据。

```json
"routing": {
  "attempted": [
    {"tier": "P0", "provider": "primary-feed", "outcome": "timeout"},
    {"tier": "P1", "provider": "secondary-feed", "outcome": "success"}
  ]
}
```

| 约束 | 层 |
|------|----|
| `attempted` 必须是非空列表 | [H] |
| 每条需有合法 `tier`、非空 `provider`、合法 `outcome` | [H] |
| `outcome` ∈ `success` / `no_data` / `error` / `timeout` | [H] |
| **恰好一条** `success` | [H] |
| 该 success 的 tier **必须等于**声明的 `provider_tier` | [H] `test_s07_declared_tier_must_match_successful_attempt` |

代码位置：`contracts.evidence.validate_source()`、`contracts.evidence.get_fallback_chain()`。

**绝对禁止为了满足示例而虚构路由记录。** 没有真实记录就整个省略 `routing` 块——系统不会因此报错，但也不会渲染任何 fallback 标注。参考 `test_r05_evidenced_fallback_is_rendered`、`test_r06_no_fallback_claim_without_routing_evidence`、`test_q09_no_successful_p0_claim_without_evidence`、`test_p19_fallback_annotation_is_still_rendered_by_existing_rules`。

### 7.3 `estimated` [H]

布尔值。为 `true` 时渲染「（估算）」徽章（`contracts.evidence` → `schema.ESTIMATED_LABEL`）。

估算值不得伪装成精确值。参考 `test_r08_estimated_item_is_labelled`、`test_q06_estimated_badge_only_when_flagged`。

### 7.4 `methodology` [H 结构 / Q 内容]

```json
"methodology": {
  "methods": ["按 workflow.md 六步链路组织", "..."],
  "limitations": ["未接入任何真实数据源", "未执行 Evidence 验证（P0-003 未完成）"]
}
```

| 约束 | 层 |
|------|----|
| `methodology` 必须是对象 | [H] |
| `methods` 必须是非空列表 | [H] `test_s10_methodology_must_be_non_empty` |
| `limitations` 必须是非空列表 | [H] `test_s10_methodology_must_be_non_empty` |

**内容由输入方拥有**，Pipeline 绝不代写（`test_p40_methodology_is_owned_by_the_input`）。

[R] `limitations` 应至少覆盖：数据真实性、是否执行验证、认知单元与计划的来源。

### 7.5 Mock / Real Mode 披露纪律 [H]

| `data_mode` | 渲染横幅 | 含义 |
|------------|---------|------|
| `mock` | `MOCK DATA / 演示数据 — 非真实市场数据，不得作为验证结果引用` | 演示数据 |
| `real` | `UNVERIFIED EVIDENCE / 未验证声明 — …不等于已验证（NOT VERIFIED）` | 数据来源为真实，但**未经本系统验证** |

代码位置：`schema.MOCK_BANNER`、`schema.REAL_MODE_BANNER`。

**`data_mode=real` 仅说明数据来源，不等于已验证。** 参考 `test_p41_real_mode_still_declares_that_evidence_is_unverified`、`test_r10_mock_mode_renders_persistent_banner`、`test_r11`、`test_r11b_both_modes_state_that_badges_are_not_verified`。

**Real Mode 的使用前提** [Q]：

1. 数据确由真实来源取得，不是构造或占位
2. 所有 `routing.attempted` 记录真实发生
3. `limitations` 中说明系统未做核验

**不要为 real 模式编造演示样例。** 在 Provider 接入（Phase 10）之前，`mock` 是唯一有配套示例的模式。

---

## 8. Tab 4 Knowledge Bite

### 8.1 结构 [H]

```json
"knowledge_bites": [
  {
    "cognitive_unit": "判断「芯片性能提升」是否构成产业拐点，关键不在峰值算力，而在单位推理成本能否跨过应用可负担阈值。",
    "why_it_matters": "该判断规则可复用于后续所有算力类公告。",
    "event_ids": ["evt-20261020-chip-v2", "evt-20261020-chip-impact"],
    "source": {"name": "...", "provider_tier": "P0", "locator": "..."},
    "confidence": "MEDIUM",
    "estimated": false
  }
]
```

| 约束 | 层 | 参考 |
|------|----|------|
| `knowledge_bites` 必须是**非空**列表 | [H] | `test_p28_missing_knowledge_bites_is_rejected`、`test_p29` |
| 每项必须是对象 | [H] | |
| `cognitive_unit` 必填非空 | [H] | `test_p29b_knowledge_bite_fields_are_required` |
| `why_it_matters` 必填非空 | [H] | `test_p29b_knowledge_bite_fields_are_required` |
| `event_ids` 若给必须是非空列表且全部存在 | [H] | `test_p30b_knowledge_bite_event_ids_must_exist` |
| **禁止**使用单数 `event_id`（Tab 4 用复数） | [H] | `test_t29_tab4_must_not_use_the_singular_event_id` |

### 8.2 必须显式撰写 [H]

Pipeline **拒绝**从事件摘要生成 Knowledge Bite。缺少知识单元被视为分析不完整，直接报错，而**不是**用「数据不可用」掩盖（`test_p30_knowledge_bites_are_not_generated_from_events`）。

### 8.3 认知价值验收 [Q]

D2 规定：Tab 4 必须产出**可复用的认知单元，而不是有趣的事实**。系统使命是认知积累，不是信息传递。这一条**目前没有代码校验**，由人或 Agent 自评。

**不合格（事实重述）**：

> 「示例科技发布了新一代推理芯片。」

**合格（可复用判断规则）**：

> 「判断『芯片性能提升』是否构成产业拐点，关键不在峰值算力，而在单位推理成本能否跨过应用可负担阈值。」

[R] 自检方法：把这条认知单元放到**另一个完全不同的行业或时间点**下，如果它仍然成立且仍有指导意义，它就是可复用的；如果它只是描述了今天发生了什么，它就是事实重述。

[R] `why_it_matters` 说明复用范围与支撑来源；给出 `event_ids` 可以让读者回溯支撑链条。

---

## 9. Tab 5 Follow-up Tracker

### 9.1 双向规则 [H]

这是一个**双向约束**，两端都由代码强制：

| 方向 | 规则 | 参考 |
|------|------|------|
| 正向 | 每个 `status=open` 的事件**必须**有 `follow_up_plan` 条目 | `test_p10_open_event_without_a_plan_entry_is_rejected` |
| 反向 | 每个 `follow_up_plan` 条目**必须**指向存在的、`status=open` 的事件 | `test_p42_plan_for_an_unknown_event_is_rejected`、`test_p43`、`test_p43b_plan_for_a_fact_event_is_rejected` |

**孤立计划（指向未知事件或非 open 事件）是错误，绝不静默丢弃。**

不想跟踪的事件用 `status=active` 显式退出（`test_p11_active_event_may_stay_out_of_tab5`），不要留着 `open` 却没有计划。

### 9.2 结构 [H]

```json
"follow_up_plan": [
  {
    "event_id": "evt-20261020-dedup-hypothesis",
    "action": "核实两条二手报道是否同源：比对发布时间与引用链条，若指向同一原始信源则合并计为一条。",
    "next_check": "2026-10-22",
    "linked_theme": "信源质量治理"
  }
]
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `event_id` | [H] | 必须存在且状态为 `open`；同一事件不得重复出现 |
| `action` | [H] | **显式提供，永不从 `verification_criteria` 推导** |
| `next_check` | [H] | **显式提供，永不生成** |
| `linked_theme` | 否 | 衔接主题 |

参考 `test_p20_action_is_required_and_never_derived`、`test_p20b_action_does_not_fall_back_to_verification_criteria`、`test_p21_next_check_is_required_and_never_generated`、`test_p23_verification_criteria_stays_on_the_event`。

### 9.3 可操作性验收 [Q]

D3 规定：Tab 5 必须包含**可执行的跟踪项，不是模糊的观察**。这条驱动 Layer 2 Research Terminal；不可执行的条目会切断 Knowledge Flow。**目前没有代码校验内容质量。**

[R] `action` 自检：应是「动词 + 对象 + 判据」的可执行动作。

- ❌ 「关注该产品进展」（无法判断何时算完成）
- ✅ 「核对首批出货客户名单与产能爬坡时间表是否与公告口径一致」

[R] `next_check` 自检：应是**具体日期**而非「下周」「近期」。系统把它渲染为报告中的显式提醒。

[R] `action` 不应照抄事件的 `verification_criteria`——前者是**你要做什么**，后者是**什么条件算被验证**。

---

## 10. 常见错误 → 成因 → 修复

以下错误消息均直接取自代码中的 `require()` 断言。

### 10.1 事件类

| 错误消息（含路径） | 成因 | 修复 |
|-------------------|------|------|
| `events[N].event_id must match ^evt-\d{8}-[a-z0-9][a-z0-9-]*$` | id 格式不符 | 改为 `evt-YYYYMMDD-slug`；slug 只用小写字母、数字、连字符 |
| `events[N].event_id carries an invalid calendar date` | id 日期段不存在 | 检查是否写了 `20260231` 之类 |
| `events[N](id) duplicates an earlier event` | 同文档内 id 重复 | 每个事件使用唯一 id |
| `events[N].derived_from must be empty or absent for a fact` | fact 带了 `derived_from` | 事实不是推导出来的，清空该字段 |
| `events[N].derived_from is required for an inference` | inference 缺 `derived_from` | 补上推导基础 |
| `events[N].verification_criteria is required for a hypothesis` | hypothesis 缺验证标准 | 补上「如何验证」 |
| `events[N].verification_criteria is required when status is 'open'` | open 事件缺验证标准 | 补上，或把状态改回 `active` |
| `events[N].derived_from references an unknown event` | 引用了不存在的 id | 检查 id 拼写 |
| `events.derived_from contains a cycle: A -> B -> A` | 推导关系成环 | 打断循环 |
| `events[N] (id) is an inference that cannot be traced back to any fact` | 推理链末端不是 fact | 让链条最终落到一个 fact |
| `events[N].supersedes must not point at the event itself` | 自引用 | 检查 id |

参考：`test_t02_event_id_format_is_enforced`、`test_t03_event_id_date_must_be_a_real_calendar_day`、`test_t04_duplicate_event_id_is_rejected`、`test_t07_fact_must_not_carry_derived_from`–`test_t15`、`test_t22_supersedes_must_not_self_reference`。

### 10.2 Selection 类

| 错误消息 | 成因 | 修复 |
|---------|------|------|
| `selection.tab1_event_ids[N] references an unknown event` | id 不存在 | 检查拼写 |
| `selection.tab1_event_ids[N] selects '...' whose assertion_type is 'inference'; this tab requires 'fact'` | Tab 1 选了 inference | Tab 1 只能选 fact |
| `selection.tab3_event_ids[N] selects '...' whose assertion_type is 'fact'; this tab requires 'inference'` | Tab 3 选了 fact | Tab 3 只能选 inference |
| `selection.tab1_event_ids[N] repeats event id '...'` | 列表内重复 | 去掉重复项 |

参考：`test_p04_tab1_rejects_a_non_fact_id`–`test_p08_duplicate_selection_id_is_rejected`。

### 10.3 Knowledge Bite 类

| 错误消息 | 成因 | 修复 |
|---------|------|------|
| `knowledge_bites must be a non-empty list: a Knowledge Bite is a reusable cognitive unit (decisions.md D2) and cannot be generated from event summaries` | 列表为空或缺省 | **必须显式撰写**，Pipeline 不会代生成 |
| `knowledge_bites[N].cognitive_unit is required` | 缺字段 | 补上 |
| `knowledge_bites[N].why_it_matters is required` | 缺字段 | 补上 |
| `knowledge_bites[N].event_ids must be a non-empty list when present` | 给了空数组 | 删掉该字段或填写内容 |

参考：`test_p28_missing_knowledge_bites_is_rejected`、`test_p29`、`test_p29b_knowledge_bite_fields_are_required`、`test_p30b_knowledge_bite_event_ids_must_exist`。

### 10.4 Follow-up 类

| 错误消息 | 成因 | 修复 |
|---------|------|------|
| `event '...' has status 'open' and is therefore formally tracked, but follow_up_plan has no entry for it` | open 事件缺计划 | 补计划项，或把状态改为 `active` |
| `follow_up_plan[N].event_id references an unknown event` | 计划指向不存在的事件 | 检查拼写 |
| `follow_up_plan[N].event_id targets '...' whose status is 'active'; only events with status 'open' may appear in the Follow-up Tracker` | 计划指向非 open 事件 | 改事件状态或删除计划项 |
| `follow_up_plan[N].action is required and must be supplied explicitly; it is never derived from the event's verification_criteria` | 缺 action | 显式撰写 |
| `follow_up_plan[N].next_check is required; a check date is a tracking decision and is never generated` | 缺 next_check | 显式填写 |

参考：`test_p10_open_event_without_a_plan_entry_is_rejected`、`test_p42_plan_for_an_unknown_event_is_rejected`、`test_p43`、`test_p20`、`test_p21_next_check_is_required_and_never_generated`。

### 10.5 Market Data 类

| 错误消息 | 成因 | 修复 |
|---------|------|------|
| `market_data.unavailable_reason must be null when market_data.items carries data` | 同时给了数据和理由 | 二选一 |
| `market_data.unavailable_reason must be a non-empty string when provided` | 空字符串理由 | 写真实理由或省略 |
| `market_data.items[N].text is required` | 缺 text | 补上 |

参考：`test_p24_absent_market_data_with_a_real_reason`–`test_p27`、`test_p27b_missing_market_data_key_uses_the_neutral_wording`、`test_p27c_market_items_are_mapped_verbatim`。

### 10.6 Meta 与方法论类

| 错误消息 | 成因 | 修复 |
|---------|------|------|
| `meta.run_date is required; run_date drives the output file name (decisions.md D4)` | 缺 run_date | 补上 |
| `meta.data_date is required; data_date is shown in the report header` | 缺 data_date | 补上 |
| `meta.data_mode is required; data_mode drives the mock/real disclosure banner` | 缺 data_mode | 补上 |
| `meta.data_mode must be 'mock' or 'real'` | 取值非法 | 用 `mock` 或 `real` |
| `methodology is required and is owned by the input` | 缺方法论 | 补上 |
| `methodology.methods must be a non-empty list` | 空列表 | 补上 |
| `methodology.limitations must be a non-empty list` | 空列表 | 补上 |

参考：`test_p45`、`test_p45b_missing_meta_field_is_not_a_key_error`、`test_p46_invalid_meta_value_still_uses_the_existing_schema_rule`、`test_p40_methodology_is_owned_by_the_input`、`test_s02_missing_run_date_fails`、`test_s10_methodology_must_be_non_empty`、`test_s11_data_mode_is_mandatory_and_constrained`。

### 10.7 质量门类

| 错误消息 | 成因 | 修复 |
|---------|------|------|
| `Tab 'highlights' exceeds the 500-word budget (CJK characters + Latin/numeric tokens): N > 500. Content was NOT truncated. Reduce the source text and re-run.` | 某 Tab 超 500 词 | **精简源文本后重跑**——系统不会截断，也不会写文件 |

参考：`test_q02_over_budget_fails_and_does_not_truncate`、`test_q03c_over_budget_never_writes_output_via_cli`。

---

## 11. CLI Runbook

### 11.1 命令

```bash
PYTHONPATH=src python -m daily_briefing.pipeline \
  --input <source>.json \
  [--out <output>.html]
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `--input` | 是 | 源文档 JSON 路径 |
| `--out` | 否 | 输出路径。缺省为 `output/daily-report-<run_date>.html`（decisions.md D4：**文件名用 Run Date，永不用 Data Date**） |

[R] 在仓库根目录执行时需要 `PYTHONPATH=src`；若以包方式安装则不需要。仓库的 `tests/conftest.py` 会自动注入 `src`，因此测试无需设置该变量。

### 11.2 退出码 [H]

| 退出码 | 含义 | 触发条件 |
|-------|------|---------|
| `0` | 成功 | HTML 已写入 |
| `2` | 输入问题 | 文件不存在、不是合法 JSON |
| `3` | 超 500 词门 | 某个 Tab 超预算 |
| `4` | 契约违规 | 任何 `ContractError` |

**任何失败都不产生输出文件。**

参考：`test_p35_cli_end_to_end`、`test_p36_cli_rejects_a_contract_violation`、`test_p37_cli_missing_input_returns_2`、`test_p37b_cli_does_not_write_when_the_word_gate_fails`、`test_p37c_module_runs_as_a_script`、`test_p48_cli_subprocess_reports_exit_4_for_missing_meta`。

### 11.3 端到端操作流程

**第 1 步 — 用官方示例起步**

```bash
PYTHONPATH=src python -m daily_briefing.pipeline \
  --input tests/fixtures/pipeline_sample.json \
  --out output/daily-report-sample.html
```

该 fixture 覆盖了全部七种情形，建议作为模板对照。

**第 2 步 — 准备自己的源文档**

复制 `tests/fixtures/pipeline_sample.json` 作为骨架，逐块替换。

**第 3 步 — 运行并按错误消息修复**

错误消息含精确路径（如 `knowledge_bites[0].cognitive_unit`），对照 §10 修复。

**第 4 步 — 验收产物**

- [ ] 文件已生成，`wrote ...` 行显示字节数与 `data_mode`
- [ ] 横幅正确：`mock` 应显示 MOCK DATA，`real` 应显示 UNVERIFIED EVIDENCE
- [ ] 五个 Tab 面板齐全，顺序为 Tab 1–5
- [ ] 每个可用卡片都有 confidence 徽章
- [ ] 估算项带「（估算）」标注
- [ ] 缺失数据显示「数据不可用」+ 理由，且**没有** confidence 徽章
- [ ] 来源行显示 `Source: name (tier)`；有真实 routing 记录时才出现 `fallback from ...`
- [ ] 页脚 Methodology 两个列表非空
- [ ] Tab 5 每项显示「下次检查」

参考：`test_r01`、`test_r02_tab_headings_use_frozen_question_form`、`test_r07_every_available_item_shows_confidence_badge`、`test_r08_estimated_item_is_labelled`、`test_r09_missing_data_renders_label_and_reason`、`test_r12_footer_documents_methodology_limits_and_routing`、`test_p38_rendering_the_pipeline_output_yields_five_tabs`、`test_p39_mock_banner_is_still_rendered`。

---

## 12. 最终 Input Preparation Checklist

提交前逐项核对。

### 12.1 结构完整性 [H]

- [ ] `meta` 含 `run_date`、`data_date`、`data_mode` [H]
- [ ] `events` 存在且是列表 [H]
- [ ] `selection` 存在，含 `tab1_event_ids` 与 `tab3_event_ids` 列表 [H]
- [ ] `knowledge_bites` 为非空列表 [H]
- [ ] `follow_up_plan` 存在（无 open 事件时可为 `[]`）[H]
- [ ] `methodology` 含非空 `methods` 与 `limitations` [H]
- [ ] `market_data` 已提供，或确认为可缺失 [H]
- [ ] 今日是否有值得记录的重要事件，以及是否至少记录一条 [Q]

### 12.2 事件合法性 [H]

- [ ] 所有 `event_id` 匹配 `^evt-\d{8}-[a-z0-9][a-z0-9-]*$` 且日期真实 [H]
- [ ] 所有 `event_id` 在文档内唯一 [H]
- [ ] 每个事件有 10 个必填字段 [H]
- [ ] 三个日期字段均为真实日历日期 [H]
- [ ] `sources` 非空，每条含 `name` / `provider_tier` / `locator` [H]
- [ ] `confidence` 为四级之一；`estimated` 为布尔 [H]
- [ ] `status` 为四个允许值之一（**无** `verified`）[H]

### 12.3 断言分类正确 [H + Q]

- [ ] fact 没有 `derived_from` [H]
- [ ] inference 有 `derived_from` [H]
- [ ] 每条 inference 的链条可达 fact [H]
- [ ] `derived_from` 不成环 [H]
- [ ] `supersedes` 不成环 [H]
- [ ] `related_event_ids` 不适用无环约束（代码只对前两个关系做环检测）[H]
- [ ] 分类反映了真实的认知层级，不是把推断写成事实 [Q]

### 12.4 Tab 选择 [H + Q]

- [ ] Tab 1 只选了 `fact` [H]
- [ ] Tab 3 只选了 `inference` [H]
- [ ] 两个列表内均无重复 id [H]
- [ ] 选择与排序体现了编辑判断，不是简单罗列全部事件 [Q]

### 12.5 Knowledge Bite 认知价值 [H + Q]

- [ ] 至少一条 Knowledge Bite [H]
- [ ] `cognitive_unit` 是可复用的判断规则，不是今日事实的重述 [Q]
- [ ] 放到另一个行业或时间点仍然成立 [Q]
- [ ] `why_it_matters` 说明复用范围与支撑 [Q]
- [ ] `event_ids`（若给）全部存在 [H]

### 12.6 Follow-up 可操作性 [H + Q]

- [ ] 每个 `open` 事件都有计划项 [H]
- [ ] 每个计划项都指向 `open` 事件 [H]
- [ ] 每个 `action` 是「动词 + 对象 + 判据」的可执行动作 [Q]
- [ ] 没有 `action` 照抄 `verification_criteria` [Q]
- [ ] 每个 `next_check` 是具体日期 [Q]
- [ ] 不需要跟踪的事件已改为 `status=active` [Q]

### 12.7 Evidence 与透明度 [H + Q]

- [ ] `data_mode` 声明与实际数据性质一致 [Q]
- [ ] `real` 模式下所有 routing 记录真实发生 [Q]
- [ ] 没有为演示目的虚构任何 routing 记录 [Q]
- [ ] 缺失数据使用固定措辞 + 真实理由，**没有**编造 Provider 失败 [H 结构 / Q 真实性]
- [ ] 估算项已标记 `estimated: true` [H]
- [ ] `methodology.limitations` 说明了数据真实性、未执行验证、认知单元与计划的来源 [Q]
- [ ] 没有任何文本声称结论「已验证」[Q]

**关于最后一条 [Q] 的说明**：Pipeline **不会**自动扫描用户提供的文本（`title` / `summary` / `cognitive_unit` / `action` 等）以判断其中是否包含虚假或越界的验证声明。系统对这类声明的约束是**披露式的**——`data_mode=mock` 强制 MOCK 横幅、`data_mode=real` 强制 UNVERIFIED 横幅、置信度徽章标注为输入自述、页脚明示 P0-003 未完成。文本内容本身是否越界，**由人或 Agent 自检**。

参考 `test_p18_pipeline_makes_no_verification_claim`——该用例断言的是 **Pipeline 模块自身源码**不含「已验证」「验证通过」字样（即系统不会自己宣称验证过），**不是**对用户输入文本的扫描。

### 12.8 质量门 [H + Q]

- [ ] 每个 Tab 的实质内容不超过 500 词（CJK 字符 + Latin 词元）[H]
- [ ] Tab 1/3 的文本本身通顺、信息自足 [R]
- [ ] CLI 退出码为 `0` [H]
- [ ] 产物横幅与 `data_mode` 一致 [H]

---

## 13. 相关文档

| 文档 | 用途 |
|------|------|
| [product.md](./product.md) | 五个 Tab 的定义与职责 |
| [decisions.md](./decisions.md) | D2 认知单元、D3 可操作跟踪、D4 文件命名 |
| [workflow.md](./workflow.md) | 生成流程与质量门 |
| [architecture.md](./architecture.md) | 本层架构 |
| [roadmap.md](./roadmap.md) | 本层演进路线 |
| [../evidence/EVIDENCE_LAYER.md](../evidence/EVIDENCE_LAYER.md) | Confidence 标准与证据标注 |
| [../provider/DATA_SOURCE.md](../provider/DATA_SOURCE.md) | Provider 路由链 |
| `src/contracts/event.py` | Event Data Contract 实现 |
| `src/contracts/evidence.py` | 共享 Evidence 原语实现 |
| `src/daily_briefing/pipeline.py` | 源文档 → 报告文档 |
| `src/daily_briefing/schema.py` | 报告契约与 500 词门 |
| `tests/fixtures/pipeline_sample.json` | 官方示例源文档 |

---

> **本文档不新增契约规则。** 所有 [H] 标记的约束均可在 `src/contracts/` 与 `src/daily_briefing/` 中找到对应实现，每条均给出测试函数名以便核对。
>
> **Evidence 验证机制（BACKLOG P0-003）尚未完成。** Confidence 徽章仅反映输入数据的自带标注，不代表本系统已验证该结论。
>
> *Status: Populated · Slice 4 交付 · 2026-10-21*