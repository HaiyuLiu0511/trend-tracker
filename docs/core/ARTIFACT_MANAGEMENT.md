# ARTIFACT_MANAGEMENT.md — 产物管理规范

> **Source:** ENGINEERING_GOVERNANCE.md §9 (Artifact Management), ARCHITECTURE_MIGRATION_BLUEPRINT_V1.0_FINAL.md §WP7
> **Status:** Active (WP7 — Artifact Protection Upgrade)
> **Date:** 2026-07-10

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Artifact Classification](#2-artifact-classification)
3. [What Can Be Committed to Git](#3-what-can-be-committed-to-git)
4. [What Cannot Be Committed to Git](#4-what-cannot-be-committed-to-git)
5. [Generated Report Lifecycle](#5-generated-report-lifecycle)
6. [Runtime Data Lifecycle](#6-runtime-data-lifecycle)
7. [Build Before Remove Principle](#7-build-before-remove-principle)
8. [Git Hygiene Checklist](#8-git-hygiene-checklist)
9. [.gitignore Coverage](#9-gitignore-coverage)
10. [Related Documents](#10-related-documents)

---

## 1. Purpose

定义 Repository 中哪些文件可以进入 Git 版本控制，哪些是运行时产物必须排除。

**核心原则：Generated artifacts never enter Git.** 生成产物永远不入库。

---

## 2. Artifact Classification

| 类别 | 文件类型 | 版本控制 | 说明 |
|------|---------|---------|------|
| **Source Code** | `.py` | ✅ Git | Pipeline 代码、工具脚本 |
| **Database Schema** | `.sql` | ✅ Git | 数据库定义、Migration 脚本 |
| **Documentation** | `.md` | ✅ Git | 所有文档（Core + Domain + Archive） |
| **Static Configuration** | `config/*.json`, `config/*.yaml` | ✅ Git | 静态配置文件（非运行时生成） |
| **Generated Artifacts** | `*.html`, `*.json` (output) | ❌ .gitignore | 生成产物，不入库 |
| **Temporary Files** | `*.tmp`, `*.bak`, `*.swp` | ❌ .gitignore | 临时文件 |
| **Cache** | `__pycache__/`, `.cache/`, `*.pyc` | ❌ .gitignore | 编译缓存 |
| **Logs** | `*.log`, `logs/` | ❌ .gitignore | 运行时日志 |
| **Local Runtime** | `runtime/`, `.env`, `*.db`, `*.sqlite` | ❌ .gitignore | 运行时数据、密钥 |
| **IDE Files** | `.vscode/`, `.idea/` | ❌ .gitignore | 编辑器配置 |
| **OS Files** | `.DS_Store`, `Thumbs.db` | ❌ .gitignore | 操作系统文件 |

---

## 3. What Can Be Committed to Git

### 永远可以提交

| 类型 | 示例 | 位置 |
|------|------|------|
| Python 源代码 | `src/**/*.py` | `src/` |
| 脚本 | `scripts/*.py` | `scripts/` |
| 数据库 Schema | `*.sql` | `config/` 或 `src/` |
| 文档 | `*.md` | `docs/`, `archive/` |
| 静态配置 | `config/*.json`, `config/*.yaml` | `config/` |
| 测试代码 | `tests/*.py` | `tests/` |
| 示例模板 | `examples/*.py` (非生成产物) | `examples/` |
| 里程碑示例 | `examples/*.html` (手动添加的里程碑输出) | `examples/` |
| .gitkeep | `.gitkeep` | 空目录占位 |

### 条件可提交

| 类型 | 条件 | 说明 |
|------|------|------|
| HTML 文件 | 仅 `examples/*.html` 里程碑示例 | `*.html` 默认忽略，需 `git add -f` 强制添加 |
| JSON 文件 | 仅 `config/*.json` 静态配置 | `*.json` 默认忽略，`config/*.json` 通过 negation 规则放行 |

---

## 4. What Cannot Be Committed to Git

### 永远不能提交

| 类型 | .gitignore 规则 | 原因 |
|------|----------------|------|
| HTML 报告 | `*.html` | 生成产物，体积大，每次运行不同 |
| JSON 数据输出 | `*.json` (除 config/) | 生成产物，API 响应，运行时数据 |
| SQLite 数据库 | `*.db`, `*.sqlite`, `*.sqlite3` | 运行时生成，二进制文件 |
| 日志文件 | `*.log`, `logs/` | 运行时生成，含敏感信息 |
| Python 缓存 | `__pycache__/`, `*.pyc` | 编译缓存，可重新生成 |
| 通用缓存 | `.cache/`, `*.cache` | 临时缓存 |
| 环境变量 | `.env`, `.env.*` | 含密钥和 Token |
| 虚拟环境 | `venv/`, `env/`, `.venv/` | 可重建，体积大 |
| IDE 配置 | `.vscode/`, `.idea/` | 个人偏好，非项目配置 |
| OS 文件 | `.DS_Store`, `Thumbs.db` | 系统生成，无意义 |
| 临时文件 | `tmp/`, `*.tmp`, `*.bak` | 临时文件 |
| 运行时输出 | `reports/`, `output/`, `artifacts/`, `runtime/` | 生成产物目录 |

---

## 5. Generated Report Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    Report Lifecycle                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Generate    →  output/  or  reports/  (Git ignored)    │
│  2. Review      →  User reviews in local filesystem         │
│  3. Archive     →  Optional: move to external storage       │
│  4. Milestone   →  Optional: copy to examples/ (git add -f) │
│  5. Cleanup     →  output/ cleared periodically             │
│                                                             │
│  Rule: Reports are outputs, not assets.                    │
│        Only milestone examples enter Git (manually).        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 生命周期规则

| 阶段 | 动作 | Git 状态 |
|------|------|---------|
| 生成 | Pipeline 输出到 `output/` 或 `reports/` | ❌ Ignored |
| 审阅 | 用户本地查看 | ❌ Not in Git |
| 归档 | 可选：移动到外部存储 | ❌ Not in Git |
| 里程碑 | 可选：手动复制到 `examples/`，`git add -f` | ✅ Tracked |
| 清理 | 定期清理 `output/`、`reports/` | ❌ Ignored |

---

## 6. Runtime Data Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                  Runtime Data Lifecycle                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Runtime creates  →  runtime/  (Git ignored)             │
│  2. Database files   →  *.db, *.sqlite  (Git ignored)       │
│  3. Cache files      →  .cache/, __pycache__/  (Git ignored)│
│  4. Log files        →  *.log, logs/  (Git ignored)         │
│  5. Secrets          →  .env, .env.*  (Git ignored)         │
│                                                             │
│  Rule: Runtime data is ephemeral.                           │
│        Only schema (.sql) and config (config/) are tracked. │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 生命周期规则

| 数据类型 | 存储位置 | Git 状态 | 清理策略 |
|---------|---------|---------|---------|
| 运行时数据 | `runtime/` | ❌ Ignored | 每次运行后可清理 |
| SQLite 数据库 | `*.db`, `*.sqlite*` | ❌ Ignored | 按需清理 |
| Python 缓存 | `__pycache__/` | ❌ Ignored | 自动管理 |
| 通用缓存 | `.cache/` | ❌ Ignored | 按需清理 |
| 日志 | `*.log`, `logs/` | ❌ Ignored | 按需清理 |
| 密钥 | `.env`, `.env.*` | ❌ Ignored | 永不清理（本地保留） |

---

## 7. Build Before Remove Principle

> **Source:** ARCHITECTURE_MIGRATION_BLUEPRINT_V1.0_FINAL.md §Migration Principles

### 原则

**先建新结构，再移除旧结构。** 在确认新结构完整可用之前，不移除任何旧文件。

### 在 Artifact Management 中的应用

| 步骤 | 动作 | 验证 |
|------|------|------|
| 1 | 新 .gitignore 规则编写完成 | 规则覆盖所有 7 类产物 |
| 2 | 验证新规则不会排除已有文件 | `git status` 无意外删除 |
| 3 | 确认旧规则仍保留 | Python/SQLite/OS/IDE 规则未丢失 |
| 4 | 提交新 .gitignore | Review → Approval → Commit |

### 反模式

```
❌ 先删除旧 .gitignore 规则 → 发现新规则有遗漏 → 已提交的文件被忽略
✅ 先编写完整新 .gitignore → 验证 git status → 确认无误 → 提交
```

---

## 8. Git Hygiene Checklist

每次 Commit 前必须检查：

### Pre-Commit Checklist

| # | 检查项 | 验证方法 | 通过标准 |
|---|--------|---------|---------|
| 1 | 无 HTML 文件进入 Commit | `git diff --cached --name-only \| grep '\.html$'` | 无输出 |
| 2 | 无 JSON 数据文件进入 Commit | `git diff --cached --name-only \| grep '\.json$'` | 无输出（config/*.json 除外） |
| 3 | 无 .env 文件进入 Commit | `git diff --cached --name-only \| grep '\.env'` | 无输出 |
| 4 | 无 .db/.sqlite 文件进入 Commit | `git diff --cached --name-only \| grep -E '\.(db\|sqlite)'` | 无输出 |
| 5 | 无 __pycache__ 进入 Commit | `git diff --cached --name-only \| grep '__pycache__'` | 无输出 |
| 6 | 无 .log 文件进入 Commit | `git diff --cached --name-only \| grep '\.log$'` | 无输出 |
| 7 | 无 .DS_Store 进入 Commit | `git diff --cached --name-only \| grep '.DS_Store'` | 无输出 |
| 8 | 无 .vscode/.idea 进入 Commit | `git diff --cached --name-only \| grep -E '\.(vscode\|idea)'` | 无输出 |

### 定期审计 Checklist

| 频率 | 检查项 | 验证方法 |
|------|--------|---------|
| 每周 | .gitignore 覆盖率 | 确认所有产物类型都有对应规则 |
| 每月 | Git 历史无产物污染 | `git log --diff-filter=A --name-only --format="" \| grep -E '\.(html\|json\|db)$'` |
| 每月 | Repository 大小 | `git count-objects -vH` |

---

## 9. .gitignore Coverage

### 当前 .gitignore 规则统计

| 类别 | 规则数 | 覆盖 |
|------|--------|------|
| Generated Artifacts | 8 | `*.html`, `*.json`, `reports/`, `output/`, `artifacts/`, `examples/generated/`, `trend_data/`, `!config/*.json` |
| Temporary Files | 4 | `tmp/`, `*.tmp`, `*.bak`, `*.swp` |
| Cache | 7 | `__pycache__/`, `*.py[cod]`, `*.pyc`, `*.pyo`, `*.so`, `.cache/`, `*.cache`, `*.egg-info/`, `dist/`, `build/`, `*.egg` |
| Logs | 2 | `*.log`, `logs/` |
| Local Runtime | 8 | `runtime/`, `.env`, `.env.*`, `!.env.example`, `*.db`, `*.sqlite`, `*.sqlite3`, `venv/`, `env/`, `.venv/` |
| IDE Files | 7 | `.vscode/`, `.idea/`, `*.iml`, `*.ipr`, `*.iws`, `.project`, `.pydevproject`, `.settings/` |
| OS Files | 7 | `.DS_Store`, `._*`, `.Spotlight-V100`, `.Trashes`, `ehthumbs.db`, `Thumbs.db`, `desktop.ini` |

### Negation Rules (Exceptions)

| 规则 | 目的 |
|------|------|
| `!config/*.json` | 允许 `config/` 目录下的静态 JSON 配置文件进入 Git |
| `!.env.example` | 允许 `.env.example`（环境变量模板，不含真实密钥）进入 Git |

---

## 10. Related Documents

- [ENGINEERING_GOVERNANCE.md](./ENGINEERING_GOVERNANCE.md) §9 — Artifact Management（治理定义来源）
- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) — Phase 3: GitHub First Backup（产物保护实施阶段）
- [CHANGELOG.md](./CHANGELOG.md) — 变更记录
- [.gitignore](../../.gitignore) — 产物保护规则实施

---

*本文档随 .gitignore 更新而同步更新。任何 .gitignore 规则变更必须先更新本文档。*
