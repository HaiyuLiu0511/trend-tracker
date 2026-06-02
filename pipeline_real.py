"""
Trend Tracker MVP v1.2 — Real Data Pipeline
Adds Company Layer (company_actions + company_weekly_summary).

Changes from v1.1:
- Imports company_mapper for company_name → company_id mapping
- stage_map_and_insert: writes company_actions per event
- NEW stage_company_weekly_summary: materializes company weekly signals
- stage_export: adds "company_actions" block to weekly.json
- run(): steps renumbered 1-8 (was 1-6)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import sqlite3
import json
import hashlib
import uuid
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from collectors.arxiv_collector import fetch_recent_papers
from collectors.techcrunch_collector import fetch_recent_articles
from collectors.github_collector import fetch_trending_repos
from processors.theme_mapper import map_event_to_themes, get_theme_name
from processors.company_mapper import map_company_name_to_id

DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'trend_tracker.db')
EXPORT_DIR = os.path.join(os.path.dirname(__file__), 'trend_data', 'weekly')

WEIGHT_CAPITAL   = 0.45
WEIGHT_STRATEGIC = 0.35
WEIGHT_RESEARCH  = 0.20

# Action type mapping from event_type
EVENT_TO_ACTION = {
    'FUNDING_ROUND': 'FUNDING_ROUND',
    'PRODUCT_LAUNCH': 'PRODUCT_LAUNCH',
    'PRODUCT_BETA':   'PRODUCT_BETA',
    'RESEARCH_PAPER': 'RESEARCH_PAPER',
    'ACQUISITION':    'ACQUISITION',
    'PARTNERSHIP':   'PARTNERSHIP',
    'OPEN_SOURCE':    'OPEN_SOURCE',
    'INFRASTRUCTURE': 'INFRASTRUCTURE',
}

# ============================================================================
# Helpers
# ============================================================================
def _normalize_title(title: str) -> str:
    return re.sub(r'[^a-z0-9]', '', title.lower())[:80]

def deduplicate(events: List[Dict]) -> List[Dict]:
    seen = set()
    unique = []
    for ev in events:
        norm = _normalize_title(ev['title'])
        if norm not in seen:
            seen.add(norm)
            unique.append(ev)
    return unique

def _event_to_action_type(event_type: str) -> str:
    return EVENT_TO_ACTION.get(event_type, 'OTHER')

def get_current_week_label() -> str:
    return datetime.now().strftime('%Y-W%W')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# Stage 1: Collect
# ============================================================================
def stage_collect_all() -> tuple:
    all_events = []
    warnings = []
    stats = {}

    print("[Collect] TechCrunch RSS...")
    tc = fetch_recent_articles()
    stats['techcrunch'] = len(tc)
    all_events.extend(tc)

    print("[Collect] GitHub Trending...")
    gh = fetch_trending_repos()
    stats['github'] = len(gh)
    for ev in gh:
        ev['title'] = ev['title'][:200]
        ev['event_type'] = 'PRODUCT_BETA'
    all_events.extend(gh)

    print("[Collect] arXiv API...")
    ax = fetch_recent_papers(3)
    stats['arxiv'] = len(ax)
    if len(ax) == 0:
        warnings.append("arXiv: rate-limited, 0 papers collected")
    all_events.extend(ax)

    stats['reuters'] = 0
    warnings.append("Reuters: requires WebSearch tool integration (not collected)")

    before = len(all_events)
    all_events = deduplicate(all_events)
    after = len(all_events)

    print(f"[Collect] Total: {before} raw → {after} deduplicated")
    for src, count in stats.items():
        print(f"  {src:15s}: {count}")

    return all_events, warnings

# ============================================================================
# Stage 2: Map & Insert (events + company_actions)
# ============================================================================
def stage_map_and_insert(conn, events: List[Dict], week_label: str) -> tuple:
    print("[Map] Theme mapping + company actions...")
    cursor = conn.cursor()

    inserted = 0
    filtered = 0
    theme_counts = {}
    company_action_count = 0

    for ev in events:
        cat_hint = ev.pop('cat_hint', '')
        github_topics = ev.pop('topics', None)
        stars = ev.pop('stars', 0)

        mappings = map_event_to_themes(
            ev['title'], ev.get('description', ''),
            ev['event_type'], ev['source_name'],
            cat_hint, github_topics
        )

        if not mappings:
            filtered += 1
            continue

        primary_theme = mappings[0][0]
        eid = f"evt_{uuid.uuid4().hex[:12]}"

        # Insert event
        conn.execute('''
            INSERT INTO events (event_id, source_tier, source_name, event_type,
                primary_theme, title, description, url, published_date,
                amount_usd, noise_flag, week_label, company_name, raw_content)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
        ''', (eid, ev.get('source_tier', 'P2'), ev['source_name'],
              ev['event_type'], primary_theme,
              ev['title'][:200], ev.get('description', '')[:500],
              ev.get('url', ''), ev.get('published_date', ''),
              ev.get('amount_usd'), week_label,
              ev.get('company_name', ''),
              ev.get('raw_content', ev.get('description', ''))[:1000]))

        # Insert theme mappings
        for theme_id, weight in mappings:
            conn.execute('''
                INSERT INTO event_theme_mapping (event_id, theme_id, weight, mapped_by)
                VALUES (?, ?, ?, 'rules')
            ''', (eid, theme_id, weight))
            theme_counts[theme_id] = theme_counts.get(theme_id, 0) + 1

        # --- Company Layer: map company_name → company_id, write company_actions ---
        raw_company = ev.get('company_name', '')
        company_id = None
        if raw_company:
            company_id = map_company_name_to_id(conn, raw_company)

        if company_id:
            action_type = _event_to_action_type(ev['event_type'])
            action_id = f"ca_{uuid.uuid4().hex[:10]}"
            # Use first theme as theme_id for the action
            theme_id_ca = mappings[0][0] if mappings else None
            conn.execute('''
                INSERT INTO company_actions (
                    action_id, company_id, event_id, action_type,
                    action_date, week_label, theme_id,
                    amount_usd, description, source_tier)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                action_id, company_id, eid, action_type,
                ev.get('published_date', '')[:10], week_label, theme_id_ca,
                ev.get('amount_usd'),
                ev.get('title', '')[:200],
                ev.get('source_tier', 'P2')
            ))
            company_action_count += 1

        inserted += 1

    conn.commit()
    print(f"[Map] {inserted} events mapped, {filtered} filtered (no theme match)")
    print(f"[Map] {company_action_count} company_actions written")
    for tid, cnt in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tid:25s}: {cnt}")

    return inserted, filtered

# ============================================================================
# Stage 3: Signal Calculation
# ============================================================================
def stage_signal_calculation(conn, week_label: str):
    print("[Signal] Calculating scores...")
    cursor = conn.cursor()
    import math

    themes = cursor.execute('SELECT theme_id FROM themes WHERE is_active = 1').fetchall()

    for (theme_id,) in themes:
        event_count = cursor.execute('''
            SELECT COUNT(*) FROM event_theme_mapping etm
            JOIN events e ON etm.event_id = e.event_id
            WHERE etm.theme_id = ? AND e.week_label = ? AND e.noise_flag = 0
        ''', (theme_id, week_label)).fetchone()[0]

        if event_count == 0:
            continue

        funding_data = cursor.execute('''
            SELECT COUNT(*), COALESCE(SUM(e.amount_usd), 0)
            FROM event_theme_mapping etm
            JOIN events e ON etm.event_id = e.event_id
            WHERE etm.theme_id = ? AND e.week_label = ?
              AND e.event_type = 'FUNDING_ROUND' AND e.noise_flag = 0
        ''', (theme_id, week_label)).fetchone()
        funding_events, total_funding = funding_data

        strategic_events = cursor.execute('''
            SELECT COUNT(*) FROM event_theme_mapping etm
            JOIN events e ON etm.event_id = e.event_id
            WHERE etm.theme_id = ? AND e.week_label = ?
              AND e.event_type IN ('PRODUCT_LAUNCH','PRODUCT_BETA','PARTNERSHIP','INFRASTRUCTURE')
              AND e.noise_flag = 0
        ''', (theme_id, week_label)).fetchone()[0]

        research_events = cursor.execute('''
            SELECT COUNT(*) FROM event_theme_mapping etm
            JOIN events e ON etm.event_id = e.event_id
            WHERE etm.theme_id = ? AND e.week_label = ?
              AND e.event_type = 'RESEARCH_PAPER' AND e.noise_flag = 0
        ''', (theme_id, week_label)).fetchone()[0]

        if total_funding > 0:
            capital_score = min(10, (math.log10(max(total_funding, 1)) - 6) * 2 + funding_events * 1.5)
        elif funding_events > 0:
            capital_score = funding_events * 2
        else:
            capital_score = 0

        strategic_score = min(10, strategic_events * 2.5)
        research_score = min(10, research_events * 3.0)

        theme_score = round(
            capital_score * WEIGHT_CAPITAL +
            strategic_score * WEIGHT_STRATEGIC +
            research_score * WEIGHT_RESEARCH, 2
        )

        total_events = funding_events + strategic_events + research_events
        if total_events >= 5:
            dq = 'HIGH'
        elif total_events >= 3:
            dq = 'MEDIUM'
        else:
            dq = 'LOW'

        signal_id = f"sig_{theme_id}_{week_label}"
        conn.execute('''
            INSERT OR REPLACE INTO signals (signal_id, theme_id, week_label,
                capital_score, strategic_score, research_score, theme_score,
                signal_count, data_quality)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (signal_id, theme_id, week_label,
              round(capital_score, 2), round(strategic_score, 2),
              round(research_score, 2), theme_score, event_count, dq))

    conn.commit()
    signal_count = cursor.execute('SELECT COUNT(*) FROM signals WHERE week_label = ?',
                                  (week_label,)).fetchone()[0]
    print(f"[Signal] {signal_count} theme signals calculated")

# ============================================================================
# Stage 4: Trend Calculation
# ============================================================================
def stage_trend_calculation(conn, week_label: str):
    print("[Trend] Calculating acceleration...")
    cursor = conn.cursor()

    prev_week = cursor.execute(
        'SELECT week_label FROM signals WHERE week_label < ? ORDER BY week_label DESC LIMIT 1',
        (week_label,)).fetchone()
    prev_week = prev_week[0] if prev_week else None

    themes = cursor.execute('SELECT theme_id FROM themes WHERE is_active = 1').fetchall()

    for (theme_id,) in themes:
        current = cursor.execute(
            'SELECT theme_score, signal_count FROM signals WHERE theme_id = ? AND week_label = ?',
            (theme_id, week_label)).fetchone()

        if not current:
            continue

        current_score, event_count = current
        prev_score = None
        accel_4w = None

        if prev_week:
            prev = cursor.execute(
                'SELECT theme_score FROM signals WHERE theme_id = ? AND week_label = ?',
                (theme_id, prev_week)).fetchone()
            if prev and prev[0] > 0:
                prev_score = prev[0]
                accel_4w = round(((current_score - prev_score) / prev_score) * 100, 1)

        trend_class, validation_class = 'Stable', 'Watchlist'
        if accel_4w is not None:
            if accel_4w > 20:
                trend_class, validation_class = 'Accelerating', 'Strong Trend'
            elif accel_4w > 8:
                trend_class, validation_class = 'Rising', 'Strong Trend'
            elif accel_4w >= -8:
                trend_class, validation_class = 'Stable', 'Watchlist'
            elif accel_4w >= -20:
                trend_class, validation_class = 'Cooling', 'Cooling'
            else:
                trend_class, validation_class = 'Declining', 'Cooling'

        trend_id = f"trd_{theme_id}_{week_label}"
        conn.execute('''
            INSERT OR REPLACE INTO trends_weekly (trend_id, theme_id, week_label,
                current_score, prev_week_score, accel_4w, trend_class,
                validation_class, event_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (trend_id, theme_id, week_label, current_score, prev_score,
              accel_4w, trend_class, validation_class, event_count))

    conn.commit()
    print(f"[Trend] Trends calculated (prev week: {prev_week or 'none'})")

# ============================================================================
# Stage 5: Capital Flow
# ============================================================================
def stage_capital_flow(conn, week_label: str):
    print("[Capital] Calculating flows...")
    cursor = conn.cursor()

    total_week = cursor.execute('''
        SELECT COALESCE(SUM(amount_usd), 0) FROM events
        WHERE week_label = ? AND event_type = 'FUNDING_ROUND' AND noise_flag = 0
    ''', (week_label,)).fetchone()[0]

    themes = cursor.execute('''
        SELECT DISTINCT etm.theme_id FROM event_theme_mapping etm
        JOIN events e ON etm.event_id = e.event_id
        WHERE e.week_label = ? AND e.event_type = 'FUNDING_ROUND' AND e.noise_flag = 0
    ''', (week_label,)).fetchall()

    for (theme_id,) in themes:
        data = cursor.execute('''
            SELECT COALESCE(SUM(e.amount_usd), 0), COUNT(*)
            FROM event_theme_mapping etm
            JOIN events e ON etm.event_id = e.event_id
            WHERE etm.theme_id = ? AND e.week_label = ?
              AND e.event_type = 'FUNDING_ROUND' AND e.noise_flag = 0
        ''', (theme_id, week_label)).fetchone()

        theme_funding, event_count = data
        share = round((theme_funding / total_week) * 100, 1) if total_week > 0 else 0

        flow_id = f"cap_{theme_id}_{week_label}"
        conn.execute('''
            INSERT OR REPLACE INTO capital_flow (flow_id, theme_id, week_label,
                funding_amount_usd, capital_share_pct, flow_direction, event_count)
            VALUES (?, ?, ?, ?, ?, 'Inflow', ?)
        ''', (flow_id, theme_id, week_label, theme_funding or 0, share, event_count))

    conn.commit()
    print(f"[Capital] {len(themes)} themes with capital flows")

# ============================================================================
# Stage 6: Company Weekly Summary (NEW in v1.2)
# ============================================================================
def stage_company_weekly_summary(conn, week_label: str):
    """Materialize company_weekly_summary from company_actions."""
    print("[Company] Calculating company weekly summaries...")
    cursor = conn.cursor()

    # Get all companies with actions this week
    companies_with_actions = cursor.execute('''
        SELECT DISTINCT company_id FROM company_actions
        WHERE week_label = ?
    ''', (week_label,)).fetchall()

    for (company_id,) in companies_with_actions:
        # Aggregate action counts by type
        action_counts = cursor.execute('''
            SELECT action_type, COUNT(*)
            FROM company_actions
            WHERE company_id = ? AND week_label = ?
            GROUP BY action_type
        ''', (company_id, week_label)).fetchall()
        action_counts_dict = {r[0]: r[1] for r in action_counts}

        total_actions = sum(action_counts_dict.values())
        funding_usd = cursor.execute('''
            SELECT COALESCE(SUM(amount_usd), 0)
            FROM company_actions
            WHERE company_id = ? AND week_label = ? AND amount_usd IS NOT NULL
        ''', (company_id, week_label)).fetchone()[0]
        launch_count = action_counts_dict.get('PRODUCT_LAUNCH', 0) + action_counts_dict.get('PRODUCT_BETA', 0)
        research_count = action_counts_dict.get('RESEARCH_PAPER', 0) + action_counts_dict.get('OPEN_SOURCE', 0)

        # Simple signal score for company (0-10)
        company_signal = min(10, (
            (funding_usd > 0) * 3 +
            launch_count * 2.5 +
            research_count * 2 +
            total_actions * 0.5
        ))

        summary_id = f"cws_{company_id}_{week_label}"
        conn.execute('''
            INSERT OR REPLACE INTO company_weekly_summary (
                summary_id, company_id, week_label,
                action_count, funding_usd, launch_count, research_count,
                signal_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (summary_id, company_id, week_label,
              total_actions, funding_usd or 0, launch_count, research_count,
              round(company_signal, 2)))

    conn.commit()
    summary_count = cursor.execute(
        'SELECT COUNT(*) FROM company_weekly_summary WHERE week_label = ?',
        (week_label,)).fetchone()[0]
    print(f"[Company] {summary_count} company weekly summaries calculated")

# ============================================================================
# Stage 7: Export Weekly JSON (adds company_actions block)
# ============================================================================
def stage_export(conn, week_label: str, data_warnings: List[str]) -> str:
    print("[Export] Generating weekly.json...")
    cursor = conn.cursor()
    os.makedirs(EXPORT_DIR, exist_ok=True)

    # Theme scores
    theme_data = cursor.execute('''
        SELECT s.theme_id, t.theme_name, s.theme_score, s.capital_score,
               s.strategic_score, s.research_score, s.signal_count, s.data_quality,
               tr.accel_4w, tr.trend_class, tr.validation_class
        FROM signals s
        JOIN themes t ON s.theme_id = t.theme_id
        LEFT JOIN trends_weekly tr ON s.theme_id = tr.theme_id AND s.week_label = tr.week_label
        WHERE s.week_label = ?
        ORDER BY s.theme_score DESC
    ''', (week_label,)).fetchall()

    # Top events
    top_events = cursor.execute('''
        SELECT e.title, e.description, e.source_name, e.event_type,
               e.primary_theme, e.url, e.company_name
        FROM events e
        WHERE e.week_label = ? AND e.noise_flag = 0
        ORDER BY CASE e.source_tier WHEN 'P0' THEN 1 WHEN 'P1' THEN 2 ELSE 3 END,
                 e.published_date DESC
        LIMIT 20
    ''', (week_label,)).fetchall()

    # Capital allocation
    capital_data = cursor.execute('''
        SELECT cf.theme_id, t.theme_name, cf.funding_amount_usd,
               cf.capital_share_pct, cf.event_count
        FROM capital_flow cf
        JOIN themes t ON cf.theme_id = t.theme_id
        WHERE cf.week_label = ?
        ORDER BY cf.funding_amount_usd DESC
    ''', (week_label,)).fetchall()

    # --- NEW in v1.2: company_actions block ---
    company_actions_data = cursor.execute('''
        SELECT ca.company_id, c.company_name, c.ticker,
               ca.action_type, ca.action_date, ca.theme_id,
               ca.amount_usd, ca.description, ca.source_tier
        FROM company_actions ca
        JOIN companies c ON ca.company_id = c.company_id
        WHERE ca.week_label = ?
        ORDER BY c.company_name, ca.action_date
    ''', (week_label,)).fetchall()

    # Company weekly summaries (top companies by signal score)
    company_summary_data = cursor.execute('''
        SELECT cws.company_id, c.company_name, c.ticker, c.primary_theme,
               cws.action_count, cws.funding_usd, cws.launch_count,
               cws.research_count, cws.signal_score
        FROM company_weekly_summary cws
        JOIN companies c ON cws.company_id = c.company_id
        WHERE cws.week_label = ?
        ORDER BY cws.signal_score DESC
        LIMIT 15
    ''', (week_label,)).fetchall()

    total_events = cursor.execute(
        'SELECT COUNT(*) FROM events WHERE week_label = ? AND noise_flag = 0',
        (week_label,)).fetchone()[0]

    weekly_json = {
        "meta": {
            "week_label": week_label,
            "generated_at": datetime.now().isoformat(),
            "pipeline_version": "v1.2",
            "scoring_version": "v1.2",
            "event_count": total_events,
            "data_source": "real"
        },
        "theme_scores": [
            {
                "theme_id": r['theme_id'],
                "theme_name": r['theme_name'],
                "theme_score": r['theme_score'],
                "capital_score": r['capital_score'],
                "strategic_score": r['strategic_score'],
                "research_score": r['research_score'],
                "signal_count": r['signal_count'],
                "data_quality": r['data_quality']
            } for r in theme_data
        ],
        "trend_acceleration": [
            {
                "theme_id": r['theme_id'],
                "theme_name": r['theme_name'],
                "accel_4w_pct": r['accel_4w'],
                "trend_class": r['trend_class'],
                "validation_class": r['validation_class']
            } for r in theme_data if r['accel_4w'] is not None
        ],
        "capital_allocation": [
            {
                "theme_id": r['theme_id'],
                "theme_name": r['theme_name'],
                "funding_usd": r['funding_amount_usd'],
                "share_pct": r['capital_share_pct'],
                "deal_count": r['event_count']
            } for r in capital_data
        ],
        # --- NEW v1.2 ---
        "company_actions": [
            {
                "company_id": r['company_id'],
                "company_name": r['company_name'],
                "ticker": r['ticker'],
                "action_type": r['action_type'],
                "action_date": r['action_date'],
                "theme_id": r['theme_id'],
                "amount_usd": r['amount_usd'],
                "description": r['description'],
                "source_tier": r['source_tier']
            } for r in company_actions_data
        ],
        "company_weekly_summary": [
            {
                "company_id": r['company_id'],
                "company_name": r['company_name'],
                "ticker": r['ticker'],
                "primary_theme": r['primary_theme'],
                "action_count": r['action_count'],
                "funding_usd": r['funding_usd'],
                "launch_count": r['launch_count'],
                "research_count": r['research_count'],
                "signal_score": r['signal_score']
            } for r in company_summary_data
        ],
        # --- end NEW ---
        "top_events": [
            {
                "title": r['title'],
                "description": r['description'],
                "source": r['source_name'],
                "type": r['event_type'],
                "theme": r['primary_theme'],
                "url": r['url'],
                "company": r['company_name']
            } for r in top_events
        ],
        "data_warnings": data_warnings
    }

    json_path = os.path.join(EXPORT_DIR, f"{week_label}.json")
    with open(json_path, 'w') as f:
        json.dump(weekly_json, f, indent=2, ensure_ascii=False)

    json_str = json.dumps(weekly_json, ensure_ascii=False)
    checksum = hashlib.sha256(json_str.encode()).hexdigest()
    snap_id = f"snap_{week_label}"

    conn.execute('''
        INSERT OR REPLACE INTO weekly_snapshots (snapshot_id, week_label, json_blob,
            scoring_version, checksum)
        VALUES (?, ?, ?, 'v1.2', ?)
    ''', (snap_id, week_label, json_str, checksum))
    conn.commit()

    print(f"[Export] {json_path}")
    print(f"[Export] Snapshot checksum: {checksum[:16]}...")
    return json_path

# ============================================================================
# Verify
# ============================================================================
def verify(conn, week_label):
    cursor = conn.cursor()
    ok = True
    checks = [
        ('events', 'SELECT COUNT(*) FROM events WHERE week_label = ?', (week_label,)),
        ('event_theme_mapping', 'SELECT COUNT(*) FROM event_theme_mapping etm JOIN events e ON etm.event_id = e.event_id WHERE e.week_label = ?', (week_label,)),
        ('signals', 'SELECT COUNT(*) FROM signals WHERE week_label = ?', (week_label,)),
        ('trends_weekly', 'SELECT COUNT(*) FROM trends_weekly WHERE week_label = ?', (week_label,)),
        ('company_actions', 'SELECT COUNT(*) FROM company_actions WHERE week_label = ?', (week_label,)),
        ('company_weekly_summary', 'SELECT COUNT(*) FROM company_weekly_summary WHERE week_label = ?', (week_label,)),
    ]
    for name, sql, params in checks:
        cnt = cursor.execute(sql, params).fetchone()[0]
        status = 'OK' if cnt > 0 else 'EMPTY'
        if status == 'EMPTY' and name not in ('company_actions', 'company_weekly_summary'):
            ok = False
        print(f"  [Verify] {name:30s}: {cnt:>3d} [{status}]")
    return ok

# ============================================================================
# Pipeline Runner
# ============================================================================
def log_pipeline(conn, status, events_collected=0, events_filtered=0,
                 error=None, week_label=''):
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    conn.execute('''
        INSERT INTO pipeline_runs (run_id, pipeline_version, status, started_at,
            completed_at, error_log, events_collected, events_filtered, week_label)
        VALUES (?, 'v1.2', ?, datetime('now'), datetime('now'), ?, ?, ?, ?)
    ''', (run_id, status, error, events_collected, events_filtered, week_label))
    conn.commit()
    return run_id

def run():
    week_label = get_current_week_label()
    print("=" * 60)
    print(f"Trend Tracker MVP v1.2 — Real Data Pipeline")
    print(f"Week: {week_label}")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    conn = get_db()
    data_warnings = []
    events_collected = 0
    events_filtered = 0

    # Clear existing data for this week
    conn.execute('DELETE FROM company_weekly_summary WHERE week_label = ?', (week_label,))
    conn.execute('DELETE FROM company_actions WHERE week_label = ?', (week_label,))
    conn.execute('DELETE FROM event_theme_mapping WHERE event_id IN (SELECT event_id FROM events WHERE week_label = ?)', (week_label,))
    conn.execute('DELETE FROM events WHERE week_label = ?', (week_label,))
    conn.execute('DELETE FROM signals WHERE week_label = ?', (week_label,))
    conn.execute('DELETE FROM trends_weekly WHERE week_label = ?', (week_label,))
    conn.execute('DELETE FROM capital_flow WHERE week_label = ?', (week_label,))
    conn.commit()

    try:
        # Step 1: Collect
        print("\n[1/8] COLLECT")
        raw_events, collect_warnings = stage_collect_all()
        data_warnings.extend(collect_warnings)
        events_collected = len(raw_events)

        # Step 2: Map & Insert
        print("\n[2/8] MAP & INSERT")
        inserted, filtered = stage_map_and_insert(conn, raw_events, week_label)
        events_filtered = filtered
        if filtered > 0:
            data_warnings.append(f"{filtered} events filtered (no theme match)")

        # Step 3: Signal
        print("\n[3/8] SIGNAL CALCULATION")
        stage_signal_calculation(conn, week_label)

        # Step 4: Trend
        print("\n[4/8] TREND CALCULATION")
        stage_trend_calculation(conn, week_label)
        prev = conn.execute(
            'SELECT week_label FROM signals WHERE week_label < ? LIMIT 1',
            (week_label,)).fetchone()
        if not prev:
            data_warnings.append("First week: no prior data for acceleration comparison")

        # Step 5: Capital Flow
        print("\n[5/8] CAPITAL FLOW")
        stage_capital_flow(conn, week_label)

        # Step 6: Company Weekly Summary (NEW)
        print("\n[6/8] COMPANY WEEKLY SUMMARY")
        stage_company_weekly_summary(conn, week_label)

        # Step 7: Export
        print("\n[7/8] EXPORT")
        json_path = stage_export(conn, week_label, data_warnings)

        # Step 8: Verify & Log
        print("\n[8/8] VERIFY & LOG")
        ok = verify(conn, week_label)
        log_pipeline(conn, 'completed', events_collected, events_filtered,
                     week_label=week_label)

        print("\n" + "=" * 60)
        if ok:
            print("PIPELINE COMPLETE")
        else:
            print("PIPELINE COMPLETE — Some tables empty (first run?)")
        print(f"Weekly JSON: {json_path}")
        print(f"Events: {events_collected} collected, {inserted} inserted, {events_filtered} filtered")
        print("=" * 60)
    except Exception as e:
        log_pipeline(conn, 'failed', events_collected, events_filtered,
                     error=str(e), week_label=week_label)
        print(f"\nPIPELINE FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    run()
