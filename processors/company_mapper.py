"""
Company Mapper — Maps raw company names to companies.company_id.

Uses exact match on company_name and ticker, plus fuzzy keyword matching
for common variations (e.g. "OpenAI" → "openai", "Google DeepMind" → "google_dm").
"""

import sqlite3
import re
from typing import Optional

# ---------------------------------------------------------------------------
# In-memory alias table (fast path, no DB lookup needed)
# ---------------------------------------------------------------------------
ALIAS_MAP = {
    # OpenAI
    'openai': 'openai', 'open ai': 'openai', 'openai, inc.': 'openai',
    # Anthropic
    'anthropic': 'anthropic', 'anthropic, pbc': 'anthropic',
    # Google DeepMind
    'google deepmind': 'google_dm', 'deepmind': 'google_dm', 'google dm': 'google_dm',
    'alphabet deepmind': 'google_dm',
    # Meta AI
    'meta ai': 'meta_ai', 'meta': 'meta_ai', 'facebook ai': 'meta_ai',
    'meta llama': 'meta_ai', 'llama': 'meta_ai',
    # Microsoft AI
    'microsoft ai': 'microsoft_ai', 'microsoft': 'microsoft_ai', 'msft ai': 'microsoft_ai',
    'github copilot': 'microsoft_ai', 'copilot': 'microsoft_ai',
    # Nvidia
    'nvidia': 'nvidia', 'nvidia corporation': 'nvidia', 'nvda': 'nvidia',
    # Figure AI
    'figure ai': 'figure_ai', 'figure': 'figure_ai',
    # Cognition AI
    'cognition ai': 'cognition_ai', 'cognition': 'cognition_ai', 'devin': 'cognition_ai',
    'cognition labs': 'cognition_ai',
    # DeepSeek
    'deepseek': 'deepseek', 'deep seek': 'deepseek',
    # Mistral AI
    'mistral': 'mistral_ai', 'mistral ai': 'mistral_ai',
    # Cohere
    'cohere': 'cohere', 'cohere ai': 'cohere',
    # AI21 Labs
    'ai21': 'ai21', 'ai21 labs': 'ai21', 'ai21labs': 'ai21',
    # Hugging Face
    'huggingface': 'huggingface', 'hugging face': 'huggingface', 'hf': 'huggingface',
    # Replicate
    'replicate': 'replicate', 'replicate.com': 'replicate',
    # Together AI
    'together ai': 'together_ai', 'together': 'together_ai',
    # Groq
    'groq': 'groq', 'groq, inc.': 'groq',
    # Cerebras
    'cerebras': 'cerebras', 'cerebras systems': 'cerebras',
    # AMD
    'amd': 'amd', 'advanced micro devices': 'amd',
    # Tesla AI
    'tesla ai': 'tesla_ai', 'tesla': 'tesla_ai', 'optimus': 'tesla_ai', 'fsd': 'tesla_ai',
    # Boston Dynamics
    'boston dynamics': 'boston_dynamics', 'boston dynamics': 'boston_dynamics',
    # Waymo
    'waymo': 'waymo', 'google waymo': 'waymo', 'alphabet waymo': 'waymo',
    # Apple AI
    'apple ai': 'apple_ai', 'apple': 'apple_ai', 'apple intelligence': 'apple_ai',
    # Stability AI
    'stability ai': 'stability_ai', 'stability': 'stability_ai', 'stable diffusion': 'stability_ai',
}

def normalize_company_name(name: str) -> str:
    """Normalize company name for matching."""
    if not name:
        return ''
    return re.sub(r'[^a-z0-9\s]', '', name.lower()).strip()

def map_company_name_to_id(conn: sqlite3.Connection, company_name: str) -> Optional[str]:
    """
    Map a raw company name to companies.company_id.
    Returns company_id if matched, None otherwise.
    """
    if not company_name:
        return None

    norm = normalize_company_name(company_name)

    # Fast path: alias map
    if norm in ALIAS_MAP:
        return ALIAS_MAP[norm]

    # DB lookup: exact match on company_name or ticker
    cursor = conn.cursor()
    row = cursor.execute(
        'SELECT company_id FROM companies WHERE LOWER(company_name) = ? AND is_active = 1',
        (norm,)
    ).fetchone()
    if row:
        return row[0]

    # DB lookup: ticker match
    row = cursor.execute(
        'SELECT company_id FROM companies WHERE LOWER(ticker) = ? AND is_active = 1',
        (norm.upper() if len(norm) <= 10 else norm,)
    ).fetchone()
    if row:
        return row[0]

    # Fuzzy: check if norm contains any alias key
    for alias, cid in ALIAS_MAP.items():
        if alias in norm or norm in alias:
            return cid

    return None

def get_company_info(conn: sqlite3.Connection, company_id: str) -> Optional[dict]:
    """Get company metadata."""
    cursor = conn.cursor()
    row = cursor.execute(
        'SELECT company_id, company_name, ticker, primary_theme, description, founded_year, headquarters, industry_tags '
        'FROM companies WHERE company_id = ?',
        (company_id,)
    ).fetchone()
    if row:
        return dict(row)
    return None

def get_all_companies(conn: sqlite3.Connection) -> list:
    """Get all active companies."""
    cursor = conn.cursor()
    return cursor.execute(
        'SELECT company_id, company_name, ticker, primary_theme FROM companies '
        'WHERE is_active = 1 ORDER BY company_name'
    ).fetchall()
