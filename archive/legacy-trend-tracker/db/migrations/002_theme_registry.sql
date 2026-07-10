-- ============================================================================
-- Migration 002: Theme Registry Enhancement (v1.4)
-- Adds theme_registry + theme_aliases tables for canonical theme governance.
-- ============================================================================

-- Table 1: theme_registry — Canonical theme governance records
CREATE TABLE IF NOT EXISTS theme_registry (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_theme TEXT    NOT NULL UNIQUE,     -- canonical theme_id (matches themes.theme_id)
    description     TEXT,                        -- human-readable governance description
    status          TEXT    NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'DEPRECATED', 'MERGED')),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Table 2: theme_aliases — Alias → canonical theme mapping
CREATE TABLE IF NOT EXISTS theme_aliases (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    alias_name  TEXT    NOT NULL,                -- alternative name
    theme_id    TEXT    NOT NULL,                -- canonical theme_registry.canonical_theme
    confidence  REAL    NOT NULL DEFAULT 0.80 CHECK (confidence >= 0 AND confidence <= 1),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (theme_id) REFERENCES theme_registry(canonical_theme)
);

-- Index for alias lookup
CREATE INDEX IF NOT EXISTS idx_theme_aliases_alias ON theme_aliases(alias_name);
CREATE INDEX IF NOT EXISTS idx_theme_registry_canonical ON theme_registry(canonical_theme);

-- ============================================================================
-- Seed: 8 canonical themes
-- ============================================================================
INSERT INTO theme_registry (canonical_theme, description, status) VALUES
    ('llm_frontier',       'Large Language Model frontier capabilities: new architectures, benchmarks, scaling laws', 'ACTIVE'),
    ('ai_agent',           'AI Agent autonomy: multi-step reasoning, tool use, browser agents, agent frameworks', 'ACTIVE'),
    ('inference_compute',  'Inference optimization: quantization, speculative decoding, edge inference, serving', 'ACTIVE'),
    ('ai_coding',          'AI-assisted software engineering: code generation, copilot, IDE integration', 'ACTIVE'),
    ('compute_gpu',        'AI compute hardware: GPU/TPU/chip design, datacenter, interconnects, supply chain', 'ACTIVE'),
    ('ai_video',           'AI video generation: text-to-video, video editing, diffusion models', 'ACTIVE'),
    ('robotics',           'Robotics & embodied AI: humanoid robots, manipulation, locomotion, sim-to-real', 'ACTIVE'),
    ('ai_infrastructure',  'AI infrastructure: vector DB, MLOps, fine-tuning, RAG, model deployment', 'ACTIVE');

-- ============================================================================
-- Seed: Theme aliases (realistic alternates from diverse sources)
-- ============================================================================
INSERT INTO theme_aliases (alias_name, theme_id, confidence) VALUES
    -- ai_agent variants (most prone to naming drift)
    ('Agentic AI',              'ai_agent', 0.95),
    ('Autonomous Agent',        'ai_agent', 0.95),
    ('Multi-Agent System',      'ai_agent', 0.90),
    ('AI Agent Framework',      'ai_agent', 0.90),
    ('Tool-using AI',           'ai_agent', 0.85),
    ('Agent SDK',               'ai_agent', 0.90),
    ('AI Assistant',            'ai_agent', 0.70),

    -- llm_frontier variants
    ('Foundation Model',        'llm_frontier', 0.95),
    ('Large Language Model',    'llm_frontier', 0.95),
    ('LLM Benchmark',           'llm_frontier', 0.90),
    ('Frontier AI',             'llm_frontier', 0.90),
    ('GPT-class Model',         'llm_frontier', 0.85),
    ('Pretrained Model',        'llm_frontier', 0.80),

    -- compute_gpu variants
    ('GPU Computing',           'compute_gpu', 0.95),
    ('AI Chip',                 'compute_gpu', 0.90),
    ('Semiconductor AI',        'compute_gpu', 0.85),
    ('AI Hardware',             'compute_gpu', 0.85),
    ('Chip Design',             'compute_gpu', 0.80),

    -- ai_coding variants
    ('AI Code Generation',      'ai_coding', 0.95),
    ('AI Copilot',              'ai_coding', 0.90),
    ('Code Assistant',          'ai_coding', 0.85),
    ('AI Code Review',           'ai_coding', 0.85),
    ('Program Synthesis',        'ai_coding', 0.80),

    -- ai_infrastructure variants
    ('MLOps',                   'ai_infrastructure', 0.90),
    ('Model Deployment',        'ai_infrastructure', 0.90),
    ('Vector Database',         'ai_infrastructure', 0.85),
    ('AI Platform',             'ai_infrastructure', 0.80),
    ('RAG System',              'ai_infrastructure', 0.85),

    -- ai_video variants
    ('Video Generation',        'ai_video', 0.95),
    ('Text-to-Video',           'ai_video', 0.95),
    ('AI Video Synthesis',      'ai_video', 0.90),
    ('Video Diffusion',         'ai_video', 0.90),

    -- robotics variants
    ('Embodied AI',             'robotics', 0.95),
    ('Humanoid Robot',          'robotics', 0.95),
    ('Robot Learning',          'robotics', 0.90),
    ('Autonomous Robot',        'robotics', 0.90),
    ('Robot Manipulation',      'robotics', 0.85),

    -- inference_compute variants
    ('Inference Optimization',  'inference_compute', 0.95),
    ('Model Quantization',      'inference_compute', 0.90),
    ('Edge Inference',          'inference_compute', 0.85),
    ('Speculative Decoding',    'inference_compute', 0.90);

-- Note: If the theme_registry tables already existed with seed data, this INSERT
-- would fail. Wrap in INSERT OR IGNORE for idempotency on re-runs.
-- The CREATE TABLE IF NOT EXISTS handles schema creation.
-- For seed data re-run safety, use INSERT OR IGNORE:
-- (Already using standard INSERT — safe for first migration run)
