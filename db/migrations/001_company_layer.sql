-- ============================================================================
-- Trend Tracker MVP v1.2 — Migration 001: Company Layer
-- Created: 2026-06-02
-- Depends: db_init_v1.1.sql (must be run after v1.1 schema)
-- Run: sqlite3 trend_tracker.db < db/migrations/001_company_layer.sql
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ============================================================================
-- Step 1: Enhance `companies` table with richer metadata
-- SQLite ALTER TABLE does NOT support expression defaults → add NULL first, UPDATE later
-- ============================================================================
ALTER TABLE companies ADD COLUMN description    TEXT;
ALTER TABLE companies ADD COLUMN founded_year   INTEGER;
ALTER TABLE companies ADD COLUMN headquarters    TEXT;
ALTER TABLE companies ADD COLUMN industry_tags  TEXT;       -- comma-separated
ALTER TABLE companies ADD COLUMN logo_url      TEXT;
ALTER TABLE companies ADD COLUMN updated_at    TEXT;        -- will be set via UPDATE

-- ============================================================================
-- Step 2: Backfill companies metadata (v1.1 seed data upgrade)
-- ============================================================================
UPDATE companies SET
    description   = 'Maker of GPT series and leading AI research lab',
    founded_year  = 2015,
    headquarters   = 'San Francisco, CA',
    industry_tags  = 'llm,ai_research,ai_safety',
    updated_at    = '2026-06-02'
WHERE company_id = 'openai';

UPDATE companies SET
    description   = 'AI safety startup, maker of Claude series',
    founded_year  = 2021,
    headquarters   = 'San Francisco, CA',
    industry_tags  = 'ai_safety,llm,alignment',
    updated_at    = '2026-06-02'
WHERE company_id = 'anthropic';

UPDATE companies SET
    description   = 'Google DeepMind AI research division',
    founded_year  = 2014,
    headquarters   = 'London, UK / Mountain View, CA',
    industry_tags  = 'llm,ai_research,alphago',
    updated_at    = '2026-06-02'
WHERE company_id = 'google_dm';

UPDATE companies SET
    description   = 'Meta AI research team, maker of Llama open models',
    founded_year  = 2013,
    headquarters   = 'Menlo Park, CA',
    industry_tags  = 'open_source,llm,ai_research',
    updated_at    = '2026-06-02'
WHERE company_id = 'meta_ai';

UPDATE companies SET
    description   = 'Microsoft AI platform and Copilot products',
    founded_year  = 1975,
    headquarters   = 'Redmond, WA',
    industry_tags  = 'copilot,productivity,ai_coding',
    updated_at    = '2026-06-02'
WHERE company_id = 'microsoft_ai';

UPDATE companies SET
    description   = 'Leading GPU designer for AI workloads',
    founded_year  = 1993,
    headquarters   = 'Santa Clara, CA',
    industry_tags  = 'gpu,ai_hardware,datacenter',
    updated_at    = '2026-06-02'
WHERE company_id = 'nvidia';

UPDATE companies SET
    description   = 'Humanoid robotics company backed by OpenAI/MSFT',
    founded_year  = 2022,
    headquarters   = 'Sunnyvale, CA',
    industry_tags  = 'humanoid_robot,embodied_ai,warehouse_automation',
    updated_at    = '2026-06-02'
WHERE company_id = 'figure_ai';

UPDATE companies SET
    description   = 'AI coding agent maker (Devin)',
    founded_year  = 2023,
    headquarters   = 'San Francisco, CA',
    industry_tags  = 'ai_coding,autonomous_agent,dev_tools',
    updated_at    = '2026-06-02'
WHERE company_id = 'cognition_ai';

-- ============================================================================
-- Step 3: Insert additional companies for broader coverage
-- ============================================================================
INSERT OR IGNORE INTO companies (
    company_id, company_name, ticker, primary_theme, description,
    founded_year, headquarters, industry_tags, updated_at
) VALUES
('deepseek',      'DeepSeek',        NULL,  'llm_frontier',
 'Chinese AI lab, maker of DeepSeek-V3/R1',
 2023, 'Hangzhou, China', 'llm,open_source,reasoning', '2026-06-02'),

('mistral_ai',    'Mistral AI',       NULL,  'llm_frontier',
 'European AI lab, maker of Mistral series open models',
 2023, 'Paris, France', 'llm,open_source,europe', '2026-06-02'),

('cohere',        'Cohere',          NULL,  'llm_frontier',
 'Enterprise LLM API company',
 2019, 'Toronto, Canada', 'llm,enterprise,api', '2026-06-02'),

('ai21',          'AI21 Labs',       NULL,  'llm_frontier',
 'Maker of Jamba hybrid SSM-Transformer models',
 2017, 'Tel Aviv, Israel', 'llm,enterprise', '2026-06-02'),

('huggingface',   'Hugging Face',    NULL,  'ai_infrastructure',
 'Open platform for ML models and datasets',
 2016, 'New York, NY', 'open_source,mlops,model_hub', '2026-06-02'),

('replicate',     'Replicate',        NULL,  'ai_infrastructure',
 'Cloud API for running open-source ML models',
 2020, 'San Francisco, CA', 'model_serving,api,mlops', '2026-06-02'),

('together_ai',   'Together AI',      NULL,  'ai_infrastructure',
 'GPU cloud for open-source AI model training and inference',
 2022, 'San Francisco, CA', 'gpu_cloud,inference,training', '2026-06-02'),

('groq',          'Groq',             NULL,  'compute_gpu',
 'LPU (Language Processing Unit) inference chip maker',
 2022, 'Mountain View, CA', 'ai_hardware,inference,latency', '2026-06-02'),

('cerebras',      'Cerebras',        'CBRS', 'compute_gpu',
 'Wafer-scale AI chip maker',
 2016, 'Sunnyvale, CA', 'ai_hardware,wafer_scale,training', '2026-06-02'),

('amd',           'AMD',             'AMD', 'compute_gpu',
 'GPU and CPU designer, MI300X AI accelerator',
 1969, 'Santa Clara, CA', 'gpu,cpu,ai_hardware', '2026-06-02'),

('tesla_ai',     'Tesla AI / Optimus', NULL, 'robotics',
 'Tesla AI team, working on FSD and Optimus humanoid',
 2018, 'Palo Alto, CA', 'autonomous_driving,humanoid_robot,simulation', '2026-06-02'),

('boston_dynamics','Boston Dynamics',  NULL, 'robotics',
 'Leader in legged robotics (Atlas, Spot)',
 1992, 'Waltham, MA', 'legged_robot,dynamic_motion,hyundai', '2026-06-02'),

('waymo',         'Waymo',           NULL,  'ai_agent',
 'Alphabet self-driving car unit',
 2009, 'Mountain View, CA', 'autonomous_driving,l4,robotaxi', '2026-06-02'),

('apple_ai',      'Apple AI',        'AAPL', 'ai_agent',
 'Apple Intelligence and on-device AI',
 2017, 'Cupertino, CA', 'on_device,private_ai,mlx', '2026-06-02'),

('stability_ai',  'Stability AI',     NULL,  'ai_video',
 'Maker of Stable Diffusion and Stable Video',
 2020, 'London, UK', 'generative_media,diffusion,video', '2026-06-02');

-- ============================================================================
-- Step 4: Create `company_actions` table
-- Records every company-level action derived from events.
-- One event → one or more company_actions (one per company mentioned).
-- ============================================================================
CREATE TABLE IF NOT EXISTS company_actions (
    action_id       TEXT    PRIMARY KEY,
    company_id      TEXT    NOT NULL,
    event_id        TEXT,                           -- NULL if action derived without event row
    action_type     TEXT    NOT NULL,
        -- FUNDING_ROUND / PRODUCT_LAUNCH / PRODUCT_BETA / RESEARCH_PAPER /
        -- ACQUISITION / PARTNERSHIP / OPEN_SOURCE / INFRASTRUCTURE / OTHER
    action_date     TEXT    NOT NULL,               -- YYYY-MM-DD
    week_label      TEXT    NOT NULL,               -- YYYY-Www
    theme_id        TEXT,                           -- NULL if not theme-related
    amount_usd      REAL,
    description     TEXT,
    source_tier     TEXT    NOT NULL DEFAULT 'P2',
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (company_id)  REFERENCES companies(company_id)  ON DELETE CASCADE,
    FOREIGN KEY (event_id)    REFERENCES events(event_id)        ON DELETE SET NULL,
    FOREIGN KEY (theme_id)     REFERENCES themes(theme_id)       ON DELETE SET NULL
);

CREATE INDEX idx_ca_company   ON company_actions(company_id);
CREATE INDEX idx_ca_week      ON company_actions(week_label);
CREATE INDEX idx_ca_event     ON company_actions(event_id);
CREATE INDEX idx_ca_theme     ON company_actions(theme_id);

-- ============================================================================
-- Step 5: Create `company_weekly_summary` table (materialized view)
-- One row per company per week: aggregated action counts + signal score.
-- ============================================================================
CREATE TABLE IF NOT EXISTS company_weekly_summary (
    summary_id      TEXT    PRIMARY KEY,
    company_id      TEXT    NOT NULL,
    week_label      TEXT    NOT NULL,
    action_count    INTEGER NOT NULL DEFAULT 0,
    funding_usd     REAL    NOT NULL DEFAULT 0,
    launch_count    INTEGER NOT NULL DEFAULT 0,
    research_count  INTEGER NOT NULL DEFAULT 0,
    signal_score    REAL,                           -- derived from actions
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE (company_id, week_label),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

CREATE INDEX idx_cws_company ON company_weekly_summary(company_id);
CREATE INDEX idx_cws_week    ON company_weekly_summary(week_label);

-- ============================================================================
-- Step 6: Verify migration
-- ============================================================================
SELECT 'Migration 001 completed' AS status;
SELECT 'companies' AS table_name, COUNT(*) AS rows, 
       (SELECT GROUP_CONCAT(name,', ') FROM pragma_table_info('companies')) AS columns
FROM companies
UNION ALL
SELECT 'company_actions', COUNT(*), 'new table' FROM company_actions
UNION ALL
SELECT 'company_weekly_summary', COUNT(*), 'new table' FROM company_weekly_summary;
