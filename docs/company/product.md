# Product — Company Research

> **Layer:** 4 — Decision Support
> **Status:** Frozen (concept, implementation pending)
> **Architecture Reference:** [core/ARCHITECTURE.md](../core/ARCHITECTURE.md)

---

## Responsibility

Company deep research, output investment decision support.

## Critical Clarification

> **Company Research must build on Industry Research.**
> Without industry framework, no company research. Industry framework is a prerequisite.

## What This Layer Is

- Company deep research within industry framework
- Investment decision support (Buy/Hold/Sell + rationale)
- Evidence-based conclusions
- Traceable research chain

## What This Layer Is NOT

- Company profile (general introduction)
- Independent company analysis (without industry context)
- Trading signal generator

## Must Build On

- Layer 3 provides industry framework
- Layer 4 analyzes specific companies within the framework

## Deliverable

`company-research-{company-name}.md`

## Design Principles

- Must reference Industry Framework
- Must output investment recommendation
- Conclusions must be traceable to Evidence
- Must use unified analysis framework
