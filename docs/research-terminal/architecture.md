# Architecture — Research Terminal

> **Layer:** 2 — Research Navigator
> **Status:** Frozen (V1, 2026-07-06)

---

## Data Inputs

- Follow-up Tracker (from Layer 1 — Daily Briefing)
- User active queries
- Historical research records

## Processing

```
Follow-up Tracker + User Queries
  ↓
Theme Identification → Company Identification
  ↓
Priority Ranking
  ↓
Navigation Output (links to Layer 3/4)
```

## Output Structure

3 Tabs (frozen V1):
1. Dashboard — research landscape overview
2. Theme Radar — themes worth investigating
3. Company Radar — companies worth researching

## Cross-Layer Interface

**Input from Layer 1:**
- Marked important events
- Follow-up Tracker items

**Output to Layer 3/4:**
- Theme list (navigation to Industry Research)
- Company list (navigation to Company Research)
- Research priority ranking

## Key Design Rule

Research Terminal does NOT store knowledge content. It only navigates.
Knowledge accumulation happens in Layer 3 (Industry Research) and Layer 4 (Company Research).
