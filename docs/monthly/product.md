# Product — Monthly Outlook

> **Layer:** 5 — Knowledge Evolution
> **Status:** Frozen (concept, implementation pending)
> **Architecture Reference:** [core/ARCHITECTURE.md](../core/ARCHITECTURE.md)

---

## Responsibility

Monthly cognitive evolution, update investment map, evolve analysis frameworks.

## Critical Clarification

> **Monthly Outlook is Knowledge Evolution, NOT News Summary.**
> It outputs cognitive changes (framework evolution / investment map update / new themes), not a list of past month's news.

## What This Layer Is

- Cognitive evolution tracking (what changed in understanding?)
- Investment map update (add/remove/adjust)
- New theme identification
- Framework evolution (Industry Framework updates)
- Feedback to Layer 1 (influences next cycle's Daily Briefing focus)

## What This Layer Is NOT

- Monthly news summary
- Monthly report card
- Performance tracker

## Must Build On

- Layer 1-4 provide all research records
- Layer 5 extracts cognitive evolution from them

## Deliverables

- `monthly-outlook-YYYY-MM.md`
- `investment-mapping.md` (updated)

## Design Principles

- Must compare with previous month's cognition
- Must mark evolution (what changed and why)
- Must update Investment Mapping
- Must influence next cycle's Daily Briefing
