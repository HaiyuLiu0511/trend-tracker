"""Daily Briefing V2 — Slice 1 (Phase 4).

A minimal, dependency-free renderer that turns a validated JSON briefing
contract into the frozen five-tab HTML report.

Frozen references (must not be redesigned by this package):
  - docs/daily/product.md            five-tab definition and responsibilities
  - docs/daily/workflow.md           generation workflow and quality gates
  - docs/core/REPORT_DESIGN.md       report structure and evidence annotation
  - docs/evidence/EVIDENCE_LAYER.md  confidence standard, missing-data rules

Scope note (Slice 1):
  No real data collection, no automatic cross-verification, and no complete
  Evidence Layer. BACKLOG P0-003 is therefore NOT closed by this slice.
"""

__version__ = "0.1.0"
