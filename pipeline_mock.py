"""
Trend Tracker MVP v1.2 — Mock Data Pipeline
Adds Company Layer (company_actions + company_weekly_summary).

Changes from v1.1:
- stage_collect: writes company_actions per event
- NEW stage_company_weekly_summary
- stage_export_weekly_json: adds company_actions + company_weekly_summary blocks
- stage_verify: checks new tables
"""

import sqlite3
import json
import hashlib
import uuid
import os
from datetime import datetime, timedelta

sys_path = __import__('sys').path
sys_path.insert(0, os.path.dirname(__file__))
from processors.company_mapper import map_company_name_to_id

DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'trend_tracker.db')
EXPORT_DIR = os.path.join(os.path.dirname(__file__), 'trend_data', 'weekly')

WEIGHT_CAPITAL   = 0.45
WEIGHT_STRATEGIC = 0.35
WEIGHT_RESEARCH  = 0.20

EVENT_TO_ACTION = {
    'FUNDING_ROUND': 'FUNDING_ROUND',
    'PRODUCT_LAUNCH': 'PRODUCT_LAUNCH',
    'PRODUCT_BETA':   'PRODUCT_BETA',
    'RESEARCH_PAPER': 'RESEARCH_PAPER',
    'ACQUISITION':    'ACQUISITION',
    'PARTNERSHIP':   'PARTNERSHIP',
    'OPEN_SOURCE':    'OPEN_SOURCE',
    'INFRASTRUCTURE': 'INFRASTRUCTURE',
    'MILESTONE':     'OTHER',
}

def _event_to_action_type(event_type: str) -> str:
    return EVENT_TO_ACTION.get(event_type, 'OTHER')

def classify_trend(accel_pct):
    if accel_pct is None:
        return 'Stable', 'Watchlist'
    if accel_pct > 20:
        return 'Accelerating', 'Strong Trend'
    elif accel_pct > 8:
        return 'Rising', 'Strong Trend'
    elif accel_pct > -8:
        return 'Stable', 'Watchlist'
    elif accel_pct > -20:
        return 'Cooling', 'Cooling'
    else:
        return 'Declining', 'Cooling'

# ============================================================================
# Mock events — 2 weeks, 8 themes
# ============================================================================
MOCK_EVENTS_W22 = [
    {"tier":"P1","source":"Reuters","type":"PRODUCT_LAUNCH","theme":"llm_frontier","title":"OpenAI releases GPT-5 with 2x reasoning improvement","desc":"GPT-5 scores 94% on MATH benchmark, doubles context window to 2M tokens","url":"https://example.com/gpt5","date":"2026-05-26","amount":None,"company":"OpenAI"},
    {"tier":"P0","source":"arXiv","type":"RESEARCH_PAPER","theme":"llm_frontier","title":"Anthropic publishes Constitutional AI v3 framework","desc":"New constitutional approach reduces harmful outputs by 98%","url":"https://arxiv.org/abs/2605.12345","date":"2026-05-28","amount":None,"company":"Anthropic"},
    {"tier":"P2","source":"TechCrunch","type":"PARTNERSHIP","theme":"llm_frontier","title":"Meta releases Llama 4 open-source with 400B parameters","desc":"Llama 4 matches GPT-4 performance on multiple benchmarks","url":"https://example.com/llama4","date":"2026-05-29","amount":None,"company":"Meta AI"},
    {"tier":"P1","source":"TechCrunch","type":"PRODUCT_BETA","theme":"ai_agent","title":"Anthropic launches Claude Agent SDK for autonomous task execution","desc":"Agent SDK enables multi-step web browsing, coding, and data analysis","url":"https://example.com/claude-agent","date":"2026-05-27","amount":None,"company":"Anthropic"},
    {"tier":"P0","source":"arXiv","type":"RESEARCH_PAPER","theme":"ai_agent","title":"Google DeepMind: AgentBench shows 3x improvement in tool use","desc":"New benchmark reveals 300% improvement in agent tool-calling accuracy","url":"https://arxiv.org/abs/2605.23456","date":"2026-05-30","amount":None,"company":"Google DeepMind"},
    {"tier":"P1","source":"TechCrunch","type":"PRODUCT_LAUNCH","theme":"inference_compute","title":"Groq launches LPU v2 with 5x inference speed improvement","desc":"New chip delivers 500 tokens/sec for Llama 4 inference","url":"https://example.com/groq-v2","date":"2026-05-26","amount":None,"company":"Groq"},
    {"tier":"P0","source":"arXiv","type":"RESEARCH_PAPER","theme":"inference_compute","title":"Speculative decoding breakthrough reduces inference cost by 70%","desc":"New technique from Stanford achieves 3x throughput with no quality loss","url":"https://arxiv.org/abs/2605.34567","date":"2026-05-28","amount":None,"company":None},
    {"tier":"P1","source":"TechCrunch","type":"PRODUCT_LAUNCH","theme":"ai_coding","title":"GitHub Copilot X adds full-repository refactoring","desc":"New feature can refactor entire codebases with one prompt","url":"https://example.com/copilot-x","date":"2026-05-27","amount":None,"company":"Microsoft AI"},
    {"tier":"P1","source":"TechCrunch","type":"FUNDING_ROUND","theme":"ai_coding","title":"Cognition AI raises $500M Series C at $4B valuation","desc":"Devin creator raises massive round to scale AI software engineering","url":"https://example.com/cognition-c","date":"2026-05-29","amount":500_000_000,"company":"Cognition AI"},
    {"tier":"P1","source":"Reuters","type":"PRODUCT_LAUNCH","theme":"compute_gpu","title":"Nvidia announces Blackwell Ultra with 2x HBM4 memory","desc":"Next-gen GPU delivers 2x training throughput for trillion-parameter models","url":"https://example.com/blackwell-ultra","date":"2026-05-28","amount":None,"company":"Nvidia"},
    {"tier":"P2","source":"TechCrunch","type":"INFRASTRUCTURE","theme":"compute_gpu","title":"Microsoft pledges $10B for new AI data center in Texas","desc":"Facility will host 100K GPUs, operational by 2027","url":"https://example.com/msft-dc","date":"2026-05-30","amount":10_000_000_000,"company":"Microsoft AI"},
    {"tier":"P0","source":"arXiv","type":"RESEARCH_PAPER","theme":"ai_video","title":"Video generation achieves real-time 4K at 60fps","desc":"New diffusion architecture enables real-time high-res video synthesis","url":"https://arxiv.org/abs/2605.45678","date":"2026-05-26","amount":None,"company":None},
    {"tier":"P1","source":"Reuters","type":"FUNDING_ROUND","theme":"robotics","title":"Figure AI raises $1.5B Series D for humanoid robot production","desc":"Funding at $12B valuation to begin mass production of Figure 02","url":"https://example.com/figure-d","date":"2026-05-27","amount":1_500_000_000,"company":"Figure AI"},
    {"tier":"P0","source":"arXiv","type":"RESEARCH_PAPER","theme":"robotics","title":"End-to-end visuomotor policy achieves 95% success on dexterous manipulation","desc":"MIT-CMU collaboration achieves near-human dexterity","url":"https://arxiv.org/abs/2605.56789","date":"2026-05-29","amount":None,"company":None},
    {"tier":"P1","source":"TechCrunch","type":"FUNDING_ROUND","theme":"ai_infrastructure","title":"Pinecone raises $200M for vector database expansion","desc":"Funding to scale real-time vector search for enterprise AI apps","url":"https://example.com/pinecone","date":"2026-05-28","amount":200_000_000,"company":"Pinecone"},
]

MOCK_EVENTS_W23 = [
    {"tier":"P1","source":"TechCrunch","type":"PRODUCT_LAUNCH","theme":"llm_frontier","title":"Google DeepMind launches Gemini 3 Ultra with native multimodality","desc":"3x faster than Gemini 2, native vision+audio+text understanding","url":"https://example.com/gemini3","date":"2026-06-01","amount":None,"company":"Google DeepMind"},
    {"tier":"P0","source":"arXiv","type":"RESEARCH_PAPER","theme":"llm_frontier","title":"Scaling laws revisited: optimal compute allocation for 10T parameter models","desc":"New framework predicts diminishing returns beyond 10T parameters without architectural innovation","url":"https://arxiv.org/abs/2606.11111","date":"2026-06-02","amount":None,"company":None},
    {"tier":"P0","source":"arXiv","type":"RESEARCH_PAPER","theme":"llm_frontier","title":"Mixture-of-Experts achieves GPT-5 level at 1/10th training cost","desc":"New MoE architecture from Tsinghua sets new efficiency record","url":"https://arxiv.org/abs/2606.11112","date":"2026-06-03","amount":None,"company":None},
    {"tier":"P1","source":"Reuters","type":"PRODUCT_LAUNCH","theme":"ai_agent","title":"OpenAI launches Operator: AI agent that books flights and orders groceries","desc":"Operator achieves 89% task completion rate on WebArena benchmark","url":"https://example.com/operator","date":"2026-06-01","amount":None,"company":"OpenAI"},
    {"tier":"P1","source":"TechCrunch","type":"FUNDING_ROUND","theme":"ai_agent","title":"Adept raises $800M for enterprise AI agents","desc":"Enterprise agent platform valued at $5B","url":"https://example.com/adept","date":"2026-06-02","amount":800_000_000,"company":"Adept"},
    {"tier":"P2","source":"TechCrunch","type":"PARTNERSHIP","theme":"ai_agent","title":"Salesforce integrates AI agents into CRM platform","desc":"Einstein Agent handles 40% of customer service tickets autonomously","url":"https://example.com/salesforce-agent","date":"2026-06-03","amount":None,"company":None},
    {"tier":"P1","source":"TechCrunch","type":"PRODUCT_BETA","theme":"inference_compute","title":"Cloudflare launches edge AI inference with 5ms latency","desc":"150+ cities covered, supports all major open-source models","url":"https://example.com/cloudflare-ai","date":"2026-06-01","amount":None,"company":None},
    {"tier":"P1","source":"TechCrunch","type":"PRODUCT_LAUNCH","theme":"ai_coding","title":"JetBrains releases AI-powered refactoring for all 12 IDEs","desc":"New AI assistant understands project-wide context and suggests refactors","url":"https://example.com/jetbrains-ai","date":"2026-06-02","amount":None,"company":None},
    {"tier":"P2","source":"TechCrunch","type":"FUNDING_ROUND","theme":"ai_coding","title":"Poolside raises $300M for AI-native development environment","desc":"Full-stack AI coding platform raises at $2B valuation","url":"https://example.com/poolside","date":"2026-06-03","amount":300_000_000,"company":"Poolside"},
    {"tier":"P1","source":"Reuters","type":"PRODUCT_LAUNCH","theme":"compute_gpu","title":"AMD launches MI400 with 2x inference performance over MI300","desc":"New chip narrows gap with Nvidia in AI inference workloads","url":"https://example.com/mi400","date":"2026-06-01","amount":None,"company":"AMD"},
    {"tier":"P1","source":"Reuters","type":"FUNDING_ROUND","theme":"compute_gpu","title":"Cerebras files for IPO, valuation expected at $8-10B","desc":"Wafer-scale chip maker targets public listing in July","url":"https://example.com/cerebras-ipo","date":"2026-06-02","amount":None,"company":"Cerebras"},
    {"tier":"P1","source":"TechCrunch","type":"PRODUCT_LAUNCH","theme":"ai_video","title":"Runway Gen-4 enables real-time video editing with natural language","desc":"New model edits videos in real-time, supports 8K resolution","url":"https://example.com/runway-gen4","date":"2026-06-01","amount":None,"company":None},
    {"tier":"P1","source":"Reuters","type":"FUNDING_ROUND","theme":"ai_video","title":"Pika raises $300M for enterprise video generation platform","desc":"Pika 2.0 targets Hollywood and advertising industries","url":"https://example.com/pika","date":"2026-06-03","amount":300_000_000,"company":"Pika"},
    {"tier":"P1","source":"Reuters","type":"PRODUCT_LAUNCH","theme":"robotics","title":"Tesla Optimus Gen 3 begins limited production","desc":"First 100 units deployed in Tesla factories for logistics tasks","url":"https://example.com/optimus3","date":"2026-06-01","amount":None,"company":"Tesla"},
    {"tier":"P1","source":"TechCrunch","type":"FUNDING_ROUND","theme":"robotics","title":"1X Technologies raises $500M for consumer humanoid robot","desc":"Norwegian startup targets home assistant robot market","url":"https://example.com/1x","date":"2026-06-02","amount":500_000_000,"company":"1X Technologies"},
    {"tier":"P1","source":"TechCrunch","type":"PRODUCT_BETA","theme":"ai_infrastructure","title":"Databricks launches LLM fine-tuning platform","desc":"New MosaicML-powered platform for enterprise fine-tuning","url":"https://example.com/databricks-llm","date":"2026-06-02","amount":None,"company":"Databricks"},
]

ALL_MOCK_EVENTS = {'2026-W22': MOCK_EVENTS_W22, '2026-W23': MOCK_EVENTS_W23}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def clear_pipeline_data(conn):
    """Clear all non-seed data for clean mock run."""
    for tbl in ['company_weekly_summary', 'company_actions',
                'event_theme_mapping', 'events', 'signals', 'trends_weekly',
                'capital_flow', 'weekly_snapshots', 'pipeline_runs']:
        conn.execute(f'DELETE FROM {tbl}')
    conn.commit()


def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


# ============================================================================
# Stage 1: Collect (events + company_actions)
# ============================================================================
def stage_collect(conn):
    """Collect mock events and insert into events + event_theme_mapping + company_actions."""
    print("[1/9] Collecting mock events...")
    events_inserted = 0
    company_action_count = 0

    for week_label, events_list in ALL_MOCK_EVENTS.items():
        for ev in events_list:
            eid = generate_id('evt')

            # Insert event
            conn.execute('''
                INSERT INTO events (event_id, source_tier, source_name, event_type,
                    primary_theme, title, description, url, published_date,
                    amount_usd, noise_flag, week_label, company_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
            ''', (eid, ev['tier'], ev['source'], ev['type'], ev['theme'],
                  ev['title'], ev['desc'], ev['url'], ev['date'],
                  ev['amount'], week_label, ev['company']))

            # Insert theme mapping
            conn.execute('''
                INSERT INTO event_theme_mapping (event_id, theme_id, weight, mapped_by)
                VALUES (?, ?, 1.0, 'rules')
            ''', (eid, ev['theme']))

            # --- Company Layer ---
            company_name = ev.get('company')
            company_id = None
            if company_name:
                company_id = map_company_name_to_id(conn, company_name)

            if company_id:
                action_type = _event_to_action_type(ev['type'])
                action_id = generate_id('ca')
                conn.execute('''
                    INSERT INTO company_actions (
                        action_id, company_id, event_id, action_type,
                        action_date, week_label, theme_id,
                        amount_usd, description, source_tier)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    action_id, company_id, eid, action_type,
                    ev['date'], week_label, ev['theme'],
                    ev['amount'],
                    ev['title'][:200],
                    ev['tier']
                ))
                company_action_count += 1

            events_inserted += 1

    conn.commit()
    print(f"  Inserted {events_inserted} events across 2 weeks")
    print(f"  {company_action_count} company_actions written")
    return events_inserted


# ============================================================================
# Stage 2: Signal Calculation
# ============================================================================
def stage_signal_calculation(conn):
    print("[2/9] Calculating signal scores...")
    cursor = conn.cursor()
    themes = cursor.execute('SELECT theme_id FROM themes WHERE is_active = 1').fetchall()

    for week_label in ALL_MOCK_EVENTS.keys():
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
                import math
                capital_score = min(10, (math.log10(total_funding) - 6) * 2 + funding_events * 1.5)
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

            total_all = funding_events + strategic_events + research_events
            if total_all >= 4:
                dq = 'HIGH'
            elif total_all >= 2:
                dq = 'MEDIUM'
            else:
                dq = 'LOW'

            conn.execute('''
                INSERT OR REPLACE INTO signals (signal_id, theme_id, week_label,
                    capital_score, strategic_score, research_score, theme_score,
                    signal_count, data_quality)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (f"sig_{theme_id}_{week_label}", theme_id, week_label,
                  round(capital_score, 2), round(strategic_score, 2),
                  round(research_score, 2), theme_score, event_count, dq))

    conn.commit()
    signal_count = cursor.execute('SELECT COUNT(*) FROM signals').fetchone()[0]
    print(f"  Calculated {signal_count} signal records")


# ============================================================================
# Stage 3: Trend Calculation
# ============================================================================
def stage_trend_calculation(conn):
    print("[3/9] Calculating trend acceleration...")
    cursor = conn.cursor()
    weeks = sorted(ALL_MOCK_EVENTS.keys())
    themes = cursor.execute('SELECT theme_id FROM themes WHERE is_active = 1').fetchall()

    for (theme_id,) in themes:
        prev_score = None
        for week_label in weeks:
            signal = cursor.execute('''
                SELECT theme_score, signal_count FROM signals
                WHERE theme_id = ? AND week_label = ?
            ''', (theme_id, week_label)).fetchone()
            if not signal:
                continue

            current_score, event_count = signal
            accel_4w = None
            if prev_score is not None and prev_score > 0:
                accel_4w = round(((current_score - prev_score) / prev_score) * 100, 1)

            trend_class, validation_class = classify_trend(accel_4w)
            conn.execute('''
                INSERT OR REPLACE INTO trends_weekly (trend_id, theme_id, week_label,
                    current_score, prev_week_score, accel_4w, trend_class,
                    validation_class, event_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (f"trd_{theme_id}_{week_label}", theme_id, week_label,
                  current_score, prev_score, accel_4w,
                  trend_class, validation_class, event_count))
            prev_score = current_score

    conn.commit()
    trend_count = cursor.execute('SELECT COUNT(*) FROM trends_weekly').fetchone()[0]
    print(f"  Calculated {trend_count} trend records")


# ============================================================================
# Stage 4: Capital Flow
# ============================================================================
def stage_capital_flow(conn):
    print("[4/9] Calculating capital flow...")
    cursor = conn.cursor()
    weeks = sorted(ALL_MOCK_EVENTS.keys())

    for week_label in weeks:
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
            conn.execute('''
                INSERT OR REPLACE INTO capital_flow (flow_id, theme_id, week_label,
                    funding_amount_usd, capital_share_pct, flow_direction, event_count)
                VALUES (?, ?, ?, ?, ?, 'Inflow', ?)
            ''', (f"cap_{theme_id}_{week_label}", theme_id, week_label, theme_funding or 0, share, event_count))

    conn.commit()
    cf_count = cursor.execute('SELECT COUNT(*) FROM capital_flow').fetchone()[0]
    print(f"  Calculated {cf_count} capital flow records")


# ============================================================================
# Stage 5: Company Weekly Summary (NEW v1.2)
# ============================================================================
def stage_company_weekly_summary(conn):
    print("[5/9] Calculating company weekly summaries...")
    cursor = conn.cursor()

    for week_label in ALL_MOCK_EVENTS.keys():
        companies_with_actions = cursor.execute('''
            SELECT DISTINCT company_id FROM company_actions
            WHERE week_label = ?
        ''', (week_label,)).fetchall()

        for (company_id,) in companies_with_actions:
            action_counts = cursor.execute('''
                SELECT action_type, COUNT(*) FROM company_actions
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

            company_signal = min(10, (
                (funding_usd > 0) * 3 +
                launch_count * 2.5 +
                research_count * 2 +
                total_actions * 0.5
            ))

            conn.execute('''
                INSERT OR REPLACE INTO company_weekly_summary (
                    summary_id, company_id, week_label,
                    action_count, funding_usd, launch_count, research_count,
                    signal_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (f"cws_{company_id}_{week_label}", company_id, week_label,
                  total_actions, funding_usd or 0, launch_count, research_count,
                  round(company_signal, 2)))

    conn.commit()
    summary_count = cursor.execute('SELECT COUNT(*) FROM company_weekly_summary').fetchone()[0]
    print(f"  Calculated {summary_count} company weekly summaries")


# ============================================================================
# Stage 6: Export Weekly JSON
# ============================================================================
def stage_export_weekly_json(conn):
    print("[6/9] Exporting weekly.json...")
    cursor = conn.cursor()
    os.makedirs(EXPORT_DIR, exist_ok=True)

    latest_week = sorted(ALL_MOCK_EVENTS.keys())[-1]

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
    ''', (latest_week,)).fetchall()

    # Top events
    top_events = cursor.execute('''
        SELECT e.title, e.description, e.source_name, e.event_type,
               e.primary_theme, e.url, e.company_name
        FROM events e
        WHERE e.week_label = ? AND e.noise_flag = 0
        ORDER BY CASE e.source_tier WHEN 'P0' THEN 1 WHEN 'P1' THEN 2 ELSE 3 END
        LIMIT 15
    ''', (latest_week,)).fetchall()

    # Capital allocation
    capital_data = cursor.execute('''
        SELECT cf.theme_id, t.theme_name, cf.funding_amount_usd,
               cf.capital_share_pct, cf.event_count
        FROM capital_flow cf
        JOIN themes t ON cf.theme_id = t.theme_id
        WHERE cf.week_label = ?
        ORDER BY cf.funding_amount_usd DESC
    ''', (latest_week,)).fetchall()

    # --- NEW v1.2 ---
    # Company actions
    company_actions_data = cursor.execute('''
        SELECT ca.company_id, c.company_name, c.ticker,
               ca.action_type, ca.action_date, ca.theme_id,
               ca.amount_usd, ca.description, ca.source_tier
        FROM company_actions ca
        JOIN companies c ON ca.company_id = c.company_id
        WHERE ca.week_label = ?
        ORDER BY c.company_name, ca.action_date
    ''', (latest_week,)).fetchall()

    # Company weekly summary
    company_summary_data = cursor.execute('''
        SELECT cws.company_id, c.company_name, c.ticker, c.primary_theme,
               cws.action_count, cws.funding_usd, cws.launch_count,
               cws.research_count, cws.signal_score
        FROM company_weekly_summary cws
        JOIN companies c ON cws.company_id = c.company_id
        WHERE cws.week_label = ?
        ORDER BY cws.signal_score DESC
    ''', (latest_week,)).fetchall()

    weekly_json = {
        "meta": {
            "week_label": latest_week,
            "generated_at": datetime.now().isoformat(),
            "pipeline_version": "v1.2",
            "scoring_version": "v1.2",
            "event_count": cursor.execute(
                'SELECT COUNT(*) FROM events WHERE week_label = ? AND noise_flag = 0',
                (latest_week,)).fetchone()[0],
            "data_source": "mock"
        },
        "theme_scores": [
            {
                "theme_id": r['theme_id'], "theme_name": r['theme_name'],
                "theme_score": r['theme_score'], "capital_score": r['capital_score'],
                "strategic_score": r['strategic_score'], "research_score": r['research_score'],
                "signal_count": r['signal_count'], "data_quality": r['data_quality']
            } for r in theme_data
        ],
        "trend_acceleration": [
            {
                "theme_id": r['theme_id'], "theme_name": r['theme_name'],
                "accel_4w_pct": r['accel_4w'], "trend_class": r['trend_class'],
                "validation_class": r['validation_class']
            } for r in theme_data if r['accel_4w'] is not None
        ],
        "capital_allocation": [
            {
                "theme_id": r['theme_id'], "theme_name": r['theme_name'],
                "funding_usd": r['funding_amount_usd'], "share_pct": r['capital_share_pct'],
                "deal_count": r['event_count']
            } for r in capital_data
        ],
        "company_actions": [
            {
                "company_id": r['company_id'], "company_name": r['company_name'],
                "ticker": r['ticker'], "action_type": r['action_type'],
                "action_date": r['action_date'], "theme_id": r['theme_id'],
                "amount_usd": r['amount_usd'], "description": r['description'],
                "source_tier": r['source_tier']
            } for r in company_actions_data
        ],
        "company_weekly_summary": [
            {
                "company_id": r['company_id'], "company_name": r['company_name'],
                "ticker": r['ticker'], "primary_theme": r['primary_theme'],
                "action_count": r['action_count'], "funding_usd": r['funding_usd'],
                "launch_count": r['launch_count'], "research_count": r['research_count'],
                "signal_score": r['signal_score']
            } for r in company_summary_data
        ],
        "top_events": [
            {
                "title": r['title'], "description": r['description'],
                "source": r['source_name'], "type": r['event_type'],
                "theme": r['primary_theme'], "url": r['url'],
                "company": r['company_name']
            } for r in top_events
        ],
        "data_warnings": [
            "Mock data — not based on real events",
            "accel_4w based on 2 data points only",
        ]
    }

    json_path = os.path.join(EXPORT_DIR, f"{latest_week}.json")
    with open(json_path, 'w') as f:
        json.dump(weekly_json, f, indent=2, ensure_ascii=False)
    print(f"  Exported to {json_path}")

    # Store snapshot
    json_str = json.dumps(weekly_json, ensure_ascii=False)
    checksum = hashlib.sha256(json_str.encode()).hexdigest()
    snap_id = f"snap_{latest_week}"
    conn.execute('''
        INSERT OR REPLACE INTO weekly_snapshots (snapshot_id, week_label, json_blob,
            scoring_version, checksum)
        VALUES (?, ?, ?, 'v1.2', ?)
    ''', (snap_id, latest_week, json_str, checksum))
    conn.commit()
    print(f"  Snapshot stored with checksum: {checksum[:16]}...")

    return json_path


# ============================================================================
# Stage 7: Log Pipeline
# ============================================================================
def stage_log_pipeline(conn, status, events_collected=0, events_filtered=0, error=None):
    print("[7/9] Logging pipeline run...")
    run_id = generate_id('run')
    conn.execute('''
        INSERT INTO pipeline_runs (run_id, pipeline_version, status, started_at,
            completed_at, error_log, events_collected, events_filtered, week_label)
        VALUES (?, 'v1.2', ?, datetime('now'), datetime('now'), ?, ?, ?, ?)
    ''', (run_id, status, error, events_collected, events_filtered,
          sorted(ALL_MOCK_EVENTS.keys())[-1]))
    conn.commit()
    print(f"  Logged run {run_id}: {status}")


# ============================================================================
# Stage 8: Verify
# ============================================================================
def stage_verify(conn):
    print("[8/9] Verifying data integrity...")
    cursor = conn.cursor()

    checks = [
        ("events", "SELECT COUNT(*) FROM events"),
        ("event_theme_mapping", "SELECT COUNT(*) FROM event_theme_mapping"),
        ("signals", "SELECT COUNT(*) FROM signals"),
        ("trends_weekly", "SELECT COUNT(*) FROM trends_weekly"),
        ("capital_flow", "SELECT COUNT(*) FROM capital_flow"),
        ("company_actions", "SELECT COUNT(*) FROM company_actions"),
        ("company_weekly_summary", "SELECT COUNT(*) FROM company_weekly_summary"),
        ("weekly_snapshots", "SELECT COUNT(*) FROM weekly_snapshots"),
        ("pipeline_runs", "SELECT COUNT(*) FROM pipeline_runs"),
    ]

    all_ok = True
    for name, sql in checks:
        count = cursor.execute(sql).fetchone()[0]
        status = 'OK' if count > 0 else 'EMPTY'
        if status == 'EMPTY' and name not in ('company_actions', 'company_weekly_summary'):
            all_ok = False
        print(f"  {name:25s} {count:>4d} records  [{status}]")

    # Verify orphan checks
    orphan_events = cursor.execute('''
        SELECT COUNT(*) FROM events e
        LEFT JOIN event_theme_mapping etm ON e.event_id = etm.event_id
        WHERE etm.event_id IS NULL
    ''').fetchone()[0]
    if orphan_events > 0:
        print(f"  WARNING: {orphan_events} events without theme mapping")
        all_ok = False

    signal_themes = set(cursor.execute('SELECT theme_id, week_label FROM signals').fetchall())
    trend_themes = set(cursor.execute('SELECT theme_id, week_label FROM trends_weekly').fetchall())
    missing_trends = signal_themes - trend_themes
    if missing_trends:
        print(f"  WARNING: {len(missing_trends)} signals without trend records")
        all_ok = False

    return all_ok


# ============================================================================
# Runner
# ============================================================================
def run():
    print("=" * 60)
    print("Trend Tracker MVP v1.2 — Mock Data Pipeline")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    conn = get_db()
    try:
        clear_pipeline_data(conn)
        events_count = stage_collect(conn)
        stage_signal_calculation(conn)
        stage_trend_calculation(conn)
        stage_capital_flow(conn)
        stage_company_weekly_summary(conn)   # NEW v1.2
        json_path = stage_export_weekly_json(conn)
        stage_log_pipeline(conn, 'completed', events_count, 0)
        ok = stage_verify(conn)

        print("\n" + "=" * 60)
        if ok:
            print("PIPELINE COMPLETE — All stages verified OK")
        else:
            print("PIPELINE COMPLETE — Warnings found (see above)")
        print(f"Weekly JSON: {json_path}")
        print("=" * 60)
    except Exception as e:
        stage_log_pipeline(conn, 'failed', error=str(e))
        print(f"\nPIPELINE FAILED: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    run()
