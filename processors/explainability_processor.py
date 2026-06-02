"""
Snapshot Explainability Processor — v1.3

Aggregates events by theme, computes impact_score, and extracts
Top 3-5 driver events per theme to explain trend formation.

No database schema changes. Reads from existing events + event_theme_mapping.
Impact score is computed on-the-fly based on source_tier, event_type, and amount_usd.
"""

import math
import sqlite3
from typing import List, Dict, Optional, Tuple


# --- Impact Score Weights ---
SOURCE_SCORES = {
    'P0': 8,
    'P1': 5,
    'P2': 2,
}

EVENT_TYPE_SCORES = {
    'FUNDING_ROUND': 3,
    'PRODUCT_LAUNCH': 4,
    'PRODUCT_BETA': 3,
    'RESEARCH_PAPER': 2,
    'PARTNERSHIP': 2,
    'INFRASTRUCTURE': 2,
    'ACQUISITION': 4,
    'OPEN_SOURCE': 2,
}

MAX_IMPACT = 10
MAX_DRIVERS = 5


def compute_impact_score(source_tier: str, event_type: str, amount_usd: Optional[float]) -> float:
    """
    Compute a 0-10 impact score for an event.

    Formula:
      base = SOURCE_SCORES[tier] + EVENT_TYPE_SCORES[type]
      amount_bonus = min(5, log10(amount) - 6) if amount > 0
      (FUNDING_ROUND gets +1 extra if amount present)
      final = min(10, base + amount_bonus)
    """
    base = SOURCE_SCORES.get(source_tier, 1) + EVENT_TYPE_SCORES.get(event_type, 1)

    # Amount bonus for funding events
    amount_bonus = 0.0
    if amount_usd and amount_usd > 0:
        try:
            amount_bonus = math.log10(amount_usd) - 6
            amount_bonus = max(0, min(5, amount_bonus))
        except (ValueError, OverflowError):
            pass

    # Extra point for FUNDING_ROUND with actual amount
    if event_type == 'FUNDING_ROUND' and amount_usd and amount_usd > 0:
        base += 1

    return round(min(MAX_IMPACT, base + amount_bonus), 2)


def get_theme_drivers(conn: sqlite3.Connection, week_label: str,
                       theme_id: str, top_n: int = MAX_DRIVERS) -> List[Dict]:
    """
    Get top-N driver events for a theme in a given week, ranked by impact_score.

    Returns:
        List[Dict] with keys: title, source, published_at, impact_score, event_type, url
    """
    cursor = conn.cursor()

    rows = cursor.execute('''
        SELECT e.title, e.source_name, e.published_date,
               e.event_type, e.source_tier, e.amount_usd, e.url
        FROM event_theme_mapping etm
        JOIN events e ON etm.event_id = e.event_id
        WHERE etm.theme_id = ? AND e.week_label = ? AND e.noise_flag = 0
        ORDER BY e.source_tier, e.published_date DESC
    ''', (theme_id, week_label)).fetchall()

    scored = []
    for row in rows:
        impact = compute_impact_score(
            row['source_tier'], row['event_type'], row['amount_usd']
        )
        scored.append({
            "title": row['title'][:200],
            "source": row['source_name'],
            "published_at": row['published_date'] or '',
            "impact_score": impact,
            "event_type": row['event_type'],
            "url": row['url'] or '',
        })

    # Sort by impact_score descending, then by published_at descending
    scored.sort(key=lambda x: (x['impact_score'], x['published_at'] or ''), reverse=True)
    return scored[:top_n]


def build_snapshot_explainability(conn: sqlite3.Connection,
                                   week_label: str) -> List[Dict]:
    """
    Build the full explainability snapshot for all themes with signals this week.

    Returns:
        List[Dict] with keys: theme, theme_name, trend, drivers[]
        Each driver: title, source, published_at, impact_score
    """
    cursor = conn.cursor()

    # Get all themes with trends this week
    themes = cursor.execute('''
        SELECT tr.theme_id, t.theme_name, tr.trend_class, tr.current_score
        FROM trends_weekly tr
        JOIN themes t ON tr.theme_id = t.theme_id
        WHERE tr.week_label = ?
        ORDER BY tr.current_score DESC
    ''', (week_label,)).fetchall()

    results = []
    for theme_id, theme_name, trend_class, current_score in themes:
        drivers = get_theme_drivers(conn, week_label, theme_id)

        if not drivers:
            continue

        results.append({
            "theme": theme_id,
            "theme_name": theme_name,
            "trend": trend_class,
            "current_score": current_score,
            "drivers": drivers,
        })

    return results


def stage_snapshot_explainability(conn: sqlite3.Connection,
                                    week_label: str) -> List[Dict]:
    """
    Pipeline stage: compute snapshot explainability for the current week.

    Prints a summary to stdout and returns the explainability data for export.
    """
    print("[Explainability] Building snapshot explainability...")
    explain = build_snapshot_explainability(conn, week_label)

    if not explain:
        print("  No themes with signals this week — explainability empty")
    else:
        for item in explain:
            driver_list = ", ".join(
                f"{d['title'][:40]}...({d['impact_score']:.1f})"
                for d in item['drivers'][:3]
            )
            print(f"  [{item['trend']}] {item['theme']:25s}: {len(item['drivers'])} drivers → {driver_list}")

    print(f"  {len(explain)} themes with explainability data")
    return explain


# ============================================================================
# Self-test
# ============================================================================
if __name__ == '__main__':
    import os
    db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'trend_tracker.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Find latest week
    cursor = conn.cursor()
    latest = cursor.execute(
        'SELECT week_label FROM trends_weekly ORDER BY week_label DESC LIMIT 1'
    ).fetchone()

    if latest:
        week = latest[0]
        print(f"Testing with week: {week}\n")

        # Test impact_score
        print("=== Impact Score Tests ===")
        test_cases = [
            ('P0', 'FUNDING_ROUND', 500_000_000),
            ('P1', 'PRODUCT_LAUNCH', None),
            ('P2', 'OPEN_SOURCE', None),
            ('P1', 'RESEARCH_PAPER', None),
            ('P0', 'PRODUCT_LAUNCH', None),
        ]
        for tier, etype, amount in test_cases:
            score = compute_impact_score(tier, etype, amount)
            print(f"  {tier:3s} {etype:17s} ${amount or 0:>14,} → impact={score}")

        print("\n=== Driver Events per Theme ===")
        explain = build_snapshot_explainability(conn, week)
        for item in explain:
            print(f"  [{item['trend']}] {item['theme']}:")
            for d in item['drivers']:
                print(f"    {d['impact_score']:.1f} | {d['source']:10s} | {d['title'][:80]}")
    else:
        print("No trend data found. Run pipeline first.")

    conn.close()
