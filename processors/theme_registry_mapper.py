"""
Theme Registry Mapper — Alias → Canonical Theme normalization.
Part of the Data Governance layer. Ensures all theme_ids flowing
through the pipeline are normalized to canonical forms before
reaching the Signal/Trend/Export layers.

Architecture:
  Theme Mapper (keyword rules) → Theme Registry Mapper (alias normalization)
  → Signal Layer → Trend Layer → Export

This module is a governance pass-through: for the 8 MVP themes, it should
be a no-op since all map directly. It protects against future drift when
LLM-based or cross-source classification introduces aliases.
"""
from typing import Dict, Optional


def load_registry(conn) -> Dict[str, str]:
    """
    Load the theme alias registry into an in-memory mapping.
    Returns: {alias_or_theme_id: canonical_theme_id}

    Multi-level lookup:
      1. canonical themes → map to themselves (identity)
      2. aliases → map to their canonical theme
      3. unknown → not in map (pass-through handled by caller)
    """
    registry = {}

    # Level 1: Canonical themes self-map
    rows = conn.execute(
        "SELECT canonical_theme FROM theme_registry WHERE status = 'ACTIVE'"
    ).fetchall()
    for (theme_id,) in rows:
        registry[theme_id] = theme_id
        # Also register lowercase variant for robustness
        registry[theme_id.lower()] = theme_id

    # Level 2: Aliases → canonical
    rows = conn.execute(
        "SELECT alias_name, theme_id FROM theme_aliases"
    ).fetchall()
    for alias, canonical in rows:
        registry[alias] = canonical
        registry[alias.lower()] = canonical

    return registry


def normalize_theme(registry: Dict[str, str], theme_id: str) -> Optional[str]:
    """
    Normalize a theme_id to its canonical form.
    Returns:
      - canonical theme_id if found in registry
      - None if not found (caller should pass through or log)
    """
    if not theme_id:
        return None
    return registry.get(theme_id) or registry.get(theme_id.lower())


def stage_theme_registry_normalization(conn, week_label: str) -> Dict:
    """
    Pipeline stage: normalize all events and event_theme_mapping entries
    for the given week to canonical themes.

    Must run AFTER stage_map_and_insert and BEFORE stage_signal_calculation.

    Returns stats dict:
      - total_events: events in week
      - normalized: count of events whose theme was changed
      - normalized_themes: set of (from_theme → to_theme) pairs
    """
    registry = load_registry(conn)
    stats = {'total_events': 0, 'normalized': 0, 'normalized_themes': set()}

    # Get all events for this week
    events = conn.execute(
        'SELECT event_id, primary_theme FROM events WHERE week_label = ?',
        (week_label,)
    ).fetchall()

    stats['total_events'] = len(events)

    for event_id, primary_theme in events:
        if not primary_theme:
            continue

        canonical = normalize_theme(registry, primary_theme)
        if canonical is None or canonical == primary_theme:
            continue  # Already canonical or unknown (pass-through)

        # Update events.primary_theme
        conn.execute(
            'UPDATE events SET primary_theme = ? WHERE event_id = ?',
            (canonical, event_id)
        )

        # Update event_theme_mapping.theme_id
        conn.execute(
            'UPDATE event_theme_mapping SET theme_id = ? WHERE event_id = ?',
            (canonical, event_id)
        )

        stats['normalized'] += 1
        stats['normalized_themes'].add((primary_theme, canonical))

    conn.commit()

    if stats['normalized'] > 0:
        print(f"[Registry] Normalized {stats['normalized']} events:")
        for from_t, to_t in sorted(stats['normalized_themes']):
            print(f"  {from_t} → {to_t}")
    else:
        print(f"[Registry] All {stats['total_events']} events already canonical (no drift)")

    return stats


# ============================================================================
# Self-test
# ============================================================================
if __name__ == '__main__':
    import sqlite3, os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'trend_tracker.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    registry = load_registry(conn)
    print(f"Registry loaded: {len(registry)} entries")
    print(f"  Canonical themes: {len(set(v for v in registry.values()))}")

    # Test normalize
    tests = [
        ('ai_agent', 'ai_agent'),            # canonical → canonical
        ('Agentic AI', 'ai_agent'),          # alias → canonical
        ('AGENTIC AI', 'ai_agent'),          # case-insensitive
        ('Autonomous Agent', 'ai_agent'),    # alias → canonical
        ('GPT-class Model', 'llm_frontier'), # alias → canonical
        ('unknown_theme', None),             # unknown → None (pass-through)
        ('', None),                          # empty → None
    ]
    all_pass = True
    for input_val, expected in tests:
        result = normalize_theme(registry, input_val)
        status = 'OK' if result == expected else 'FAIL'
        if status == 'FAIL':
            all_pass = False
        print(f"  {status}: '{input_val}' → {result} (expected: {expected})")

    conn.close()
    if all_pass:
        print("\nAll tests passed.")
    else:
        print("\nSome tests FAILED.")
        sys.exit(1)
