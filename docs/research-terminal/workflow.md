# Workflow — Research Terminal

> **Layer:** 2 — Research Navigator
> **Status:** Frozen (V1, 2026-07-06)

---

## Generation Process

```
Step 1: Collect Follow-up Items
  ↓ Gather items from Daily Briefing Follow-up Tracker
Step 2: Theme Radar Update
  ↓ Identify themes worth investigating
Step 3: Company Radar Update
  ↓ Identify companies worth researching
Step 4: Priority Ranking
  ↓ Rank themes and companies by research priority
Step 5: Navigation Output
  ↓ Generate dashboard with links to Layer 3/4
```

## Update Frequency

- Triggered by Daily Briefing Follow-up Tracker
- Can be triggered by user active query
- Not a daily mandatory output (unlike Daily Briefing)

## Quality Gates

- Must not store deep content (only navigation)
- Must link to Layer 3 (Industry Research) or Layer 4 (Company Research)
- Theme and Company radar must have clear priority ranking

## Known Issues

See: [core/REFACTOR_BACKLOG.md](../core/REFACTOR_BACKLOG.md) — P0-002
