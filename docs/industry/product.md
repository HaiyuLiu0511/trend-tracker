# Product — Industry Research

> **Layer:** 3 — Industry Framework
> **Status:** Frozen (concept, implementation pending)
> **Architecture Reference:** [core/ARCHITECTURE.md](../core/ARCHITECTURE.md)

---

## Responsibility

Build industry analysis frameworks, accumulate industry knowledge, form reusable analysis templates.

## Critical Clarification

> **Industry Research is a Framework, NOT a Report.**
> It outputs industry analysis frameworks (supply side / demand side / drivers / key variables), not one-time reports.

## What This Layer Is

- Industry analysis framework (reusable)
- Supply side / demand side / Drivers / Key variables
- Framework that evolves with research (Version 1 → Version 2 → ...)
- Prerequisite for Company Research (Layer 4)

## What This Layer Is NOT

- One-time industry report
- News summary
- Company analysis

## Must Build On

- Layer 1 provides event input
- Layer 2 provides theme filtering

## Deliverable

`industry-framework-{industry-name}.md`

## Design Principles

- Must output Framework, not Report
- Must be reusable
- Must evolve with research
- Must be referenced by Company Research (Layer 4)
