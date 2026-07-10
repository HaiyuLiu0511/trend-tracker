-- ============================================================================
-- Trend Tracker MVP v1.1 — Database Schema
-- Created: 2026-06-02
-- DB Engine: SQLite 3
-- Tables: 9 (events / event_theme_mapping / signals / trends_weekly /
--         capital_flow / themes / companies / weekly_snapshots / pipeline_runs)
-- ============================================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ============================================================================
-- Table 1: themes — Theme Registry
-- 8 MVP themes, supports parent_theme for evolution (split/merge/retire)
-- ============================================================================
CREATE TABLE IF NOT EXISTS themes (
    theme_id        TEXT PRIMARY KEY,
    theme_name      TEXT    NOT NULL,
    parent_theme    TEXT,                           -- NULL = root theme; set when split/merged
    theme_version   INTEGER NOT NULL DEFAULT 1,
    description     TEXT,
    created_date    TEXT    NOT NULL DEFAULT (date('now')),
    retired_date    TEXT,                           -- NULL = active
    is_active       INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (parent_theme) REFERENCES themes(theme_id)
);

-- ============================================================================
-- Table 2: companies — Company Registry
-- Tracks key companies and their primary theme affiliation
-- ============================================================================
CREATE TABLE IF NOT EXISTS companies (
    company_id      TEXT PRIMARY KEY,
    company_name    TEXT    NOT NULL,
    ticker          TEXT,                           -- nullable (private companies)
    primary_theme   TEXT    NOT NULL,
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (primary_theme) REFERENCES themes(theme_id)
);

-- ============================================================================
-- Table 3: events — Raw Event Records
-- All collected events before filtering. primary_theme is redundant (derivable
-- from event_theme_mapping) but retained for backward compatibility.
-- ============================================================================
CREATE TABLE IF NOT EXISTS events (
    event_id        TEXT PRIMARY KEY,
    source_tier     TEXT    NOT NULL CHECK (source_tier IN ('P0', 'P1', 'P2')),
    source_name     TEXT    NOT NULL,
    event_type      TEXT    NOT NULL,
    primary_theme   TEXT,
    title           TEXT    NOT NULL,
    description     TEXT,
    url             TEXT,
    published_date  TEXT    NOT NULL,
    amount_usd      REAL,
    noise_flag      INTEGER NOT NULL DEFAULT 0,     -- 0 = signal, 1 = noise
    week_label      TEXT    NOT NULL,               -- ISO week, e.g. '2026-W23'
    company_name    TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    raw_content     TEXT,                           -- truncated after 1 year
    FOREIGN KEY (primary_theme) REFERENCES themes(theme_id)
);

CREATE INDEX idx_events_week ON events(week_label);
CREATE INDEX idx_events_theme ON events(primary_theme);
CREATE INDEX idx_events_source ON events(source_name);

-- ============================================================================
-- Table 4: event_theme_mapping — M:N Event-to-Theme Mapping
-- MVP: weight defaults to 1.0 (single-theme per event)
-- P1: supports multi-theme with fractional weights summing to 1.0
-- ============================================================================
CREATE TABLE IF NOT EXISTS event_theme_mapping (
    event_id    TEXT    NOT NULL,
    theme_id    TEXT    NOT NULL,
    weight      REAL    NOT NULL DEFAULT 1.0 CHECK (weight > 0 AND weight <= 1.0),
    mapped_by   TEXT    NOT NULL DEFAULT 'rules',   -- 'rules' | 'llm' | 'manual'
    PRIMARY KEY (event_id, theme_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
    FOREIGN KEY (theme_id) REFERENCES themes(theme_id)
);

CREATE INDEX idx_etm_theme_week ON event_theme_mapping(theme_id);

-- ============================================================================
-- Table 5: signals — Weekly Signal Scores Per Theme
-- Composite score derived from capital/strategic/research sub-scores
-- ============================================================================
CREATE TABLE IF NOT EXISTS signals (
    signal_id       TEXT PRIMARY KEY,
    theme_id        TEXT    NOT NULL,
    week_label      TEXT    NOT NULL,
    capital_score   REAL    NOT NULL DEFAULT 0,     -- range 0–10
    strategic_score REAL    NOT NULL DEFAULT 0,     -- range 0–10
    research_score  REAL    NOT NULL DEFAULT 0,     -- range 0–10
    theme_score     REAL    NOT NULL DEFAULT 0,     -- composite: weighted avg
    signal_count    INTEGER NOT NULL DEFAULT 0,
    data_quality    TEXT    NOT NULL DEFAULT 'LOW', -- HIGH / MEDIUM / LOW
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE (theme_id, week_label),
    FOREIGN KEY (theme_id) REFERENCES themes(theme_id)
);

CREATE INDEX idx_signals_week ON signals(week_label);

-- ============================================================================
-- Table 6: trends_weekly — Weekly Trend Acceleration Metrics
-- Compares current week vs prior week to classify trend direction
-- ============================================================================
CREATE TABLE IF NOT EXISTS trends_weekly (
    trend_id        TEXT PRIMARY KEY,
    theme_id        TEXT    NOT NULL,
    week_label      TEXT    NOT NULL,
    current_score   REAL    NOT NULL,
    prev_week_score REAL,                           -- NULL for first week
    accel_4w        REAL,                           -- 4-week rolling change (pct)
    trend_class     TEXT    NOT NULL DEFAULT 'Stable',
                    -- Accelerating (>+20%) / Rising (+8%~+20%) /
                    -- Stable (-8%~+8%) / Cooling (-20%~-8%) / Declining (<-20%)
    validation_class TEXT   NOT NULL DEFAULT 'Watchlist',
                    -- Strong Trend / Watchlist / Cooling / Speculation
    event_count     INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE (theme_id, week_label),
    FOREIGN KEY (theme_id) REFERENCES themes(theme_id)
);

CREATE INDEX idx_trends_week ON trends_weekly(week_label);

-- ============================================================================
-- Table 7: capital_flow — Capital Movement Records
-- Tracks funding amounts and capital share shifts per theme per week
-- ============================================================================
CREATE TABLE IF NOT EXISTS capital_flow (
    flow_id             TEXT PRIMARY KEY,
    theme_id            TEXT    NOT NULL,
    week_label          TEXT    NOT NULL,
    funding_amount_usd  REAL    NOT NULL DEFAULT 0,
    capital_share_pct   REAL,                       -- % of total weekly funding
    flow_direction      TEXT    NOT NULL DEFAULT 'Stable',
                        -- Inflow / Outflow / Stable
    event_count         INTEGER NOT NULL DEFAULT 0,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (theme_id) REFERENCES themes(theme_id)
);

CREATE INDEX idx_capital_week ON capital_flow(week_label);

-- ============================================================================
-- Table 8: weekly_snapshots — Frozen Weekly Report Snapshots
-- Immutable JSON blob per week. Scoring changes won't alter historical snaps.
-- ============================================================================
CREATE TABLE IF NOT EXISTS weekly_snapshots (
    snapshot_id     TEXT PRIMARY KEY,
    week_label      TEXT    NOT NULL UNIQUE,
    json_blob       TEXT    NOT NULL,               -- full weekly.json content
    scoring_version TEXT    NOT NULL DEFAULT 'v1.1',
    checksum        TEXT    NOT NULL,               -- SHA256 of json_blob
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================================
-- Table 9: pipeline_runs — Pipeline Execution Log
-- Tracks each pipeline run for debugging and audit
-- ============================================================================
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id              TEXT PRIMARY KEY,
    pipeline_version    TEXT    NOT NULL DEFAULT 'v1.1',
    status              TEXT    NOT NULL DEFAULT 'started',
                        -- started / collecting / processing / calculating /
                        -- exporting / completed / failed
    started_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    completed_at        TEXT,
    error_log           TEXT,
    events_collected    INTEGER DEFAULT 0,
    events_filtered     INTEGER DEFAULT 0,
    week_label          TEXT
);

-- ============================================================================
-- Seed Data: 8 MVP Themes
-- ============================================================================
INSERT OR IGNORE INTO themes (theme_id, theme_name, description, created_date) VALUES
('llm_frontier',       'LLM 前沿模型',       'GPT-5, Claude 4, Gemini 3 等旗舰模型发布与能力突破', '2026-06-02'),
('ai_agent',           'AI Agent 自主代理',   'Agent 框架、工具使用、多步推理、自主任务执行',       '2026-06-02'),
('inference_compute',  '推理计算',            '推理优化、推理芯片、推理成本下降、边缘推理',         '2026-06-02'),
('ai_coding',          'AI 编程',             'AI 代码生成、IDE 集成、代码审查、自动修复',          '2026-06-02'),
('compute_gpu',        '算力与芯片',          'GPU/TPU/NPU 供应、数据中心建设、算力成本',          '2026-06-02'),
('ai_video',           'AI 视频生成',         '文生视频、视频编辑、实时视频理解、虚拟人',           '2026-06-02'),
('robotics',           '机器人',              '人形机器人、工业自动化、具身智能',                   '2026-06-02'),
('ai_infrastructure',  'AI 基础设施',         '模型部署平台、向量数据库、MLOps、AI 安全',          '2026-06-02');

-- ============================================================================
-- Seed Data: 8 MVP Companies
-- ============================================================================
INSERT OR IGNORE INTO companies (company_id, company_name, ticker, primary_theme) VALUES
('openai',       'OpenAI',            NULL,     'llm_frontier'),
('anthropic',    'Anthropic',         NULL,     'llm_frontier'),
('google_dm',    'Google DeepMind',   'GOOGL',  'llm_frontier'),
('meta_ai',      'Meta AI',           'META',   'llm_frontier'),
('microsoft_ai', 'Microsoft AI',      'MSFT',   'ai_coding'),
('nvidia',       'Nvidia',            'NVDA',   'compute_gpu'),
('figure_ai',    'Figure AI',         NULL,     'robotics'),
('cognition_ai', 'Cognition AI',      NULL,     'ai_coding');

-- ============================================================================
-- Verify: Table count and structure summary
-- ============================================================================
SELECT '=== Trend Tracker v1.1 Schema Initialized ===' AS status;
SELECT name AS table_name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name;
SELECT COUNT(*) AS theme_count FROM themes;
SELECT COUNT(*) AS company_count FROM companies;
