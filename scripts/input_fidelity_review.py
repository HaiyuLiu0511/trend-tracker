#!/usr/bin/env python3
"""Research Input Quality Guard V1 — Input Fidelity Review.

Turns a Daily Briefing **source document** into a complete, deterministic,
field-by-field *fidelity review checklist*: every Event Record, every source,
every piece of non-event body text and every Knowledge Bite → Event reference
is transcribed **verbatim** into a Markdown checklist that a human reviewer can
work through.

What this tool is
----------------
A transcription and coverage instrument. It answers exactly two questions:

1. *What did the input actually say?*  (verbatim transcription, byte-exact)
2. *Which of those fields reach the HTML body, and which do not?*
   (expected render status, derived structurally from the input)

What this tool is **not**
------------------------
- It is **not** a verification mechanism. Text appearing in the checklist means
  the bytes were copied, never that the claim is correct, verified or checked.
- It does not judge facts, does not cross-check against source material, does
  not upgrade ``confidence`` and does not modify the input.
- It does not implement Evidence Verification (BACKLOG P0-003) or Provider
  Routing, and it does not close either of them.

Frozen behaviour it mirrors (read-only)
---------------------------------------
The expected render position of an event is derived from the source document
alone — this tool never calls ``build_document()`` or the renderer, so an
over-budget or otherwise unrenderable input can still be reviewed.

======  ==========================================  ==========================
Rule    Derivation                                  Frozen source
======  ==========================================  ==========================
R1      ``selection.tab1_event_ids`` -> Tab 1      pipeline.py:393-395,
        (title **and** summary render)              pipeline.py:424-426
                                                    (TAB1_TEXT_FORMAT:57)
R2      ``selection.tab3_event_ids`` -> Tab 3      pipeline.py:396-401,
        (summary only — the title never renders)    pipeline.py:439
R3      ``follow_up_plan[].event_id`` -> Tab 5     pipeline.py:281-317
        (action / next_check / linked_theme)        pipeline.py:319-333
                                                    pipeline.py:337-349
R4      everything else -> not rendered            pipeline.py:112-116
                                                    pipeline.py:393-401
======  ==========================================  ==========================

R3 is driven by the **actual follow-up plan**, not by ``status == "open"``:
the pipeline enforces that relation in both directions and rejects a document
when an open event carries no plan entry. An event that is open but unplanned
therefore does **not** reach Tab 5 and is reported as ``FOLLOW_UP_MISSING``.

Fidelity rules
--------------
* No normalisation, no stripping, no truncation, no re-encoding, no escaping,
  no re-ordering and no merging of any transcribed field.
* Every free-text field is emitted inside its own fenced block whose fence
  length adapts to the payload (a payload can never close its own fence).
* A payload that ends in a newline keeps it; a payload containing CRLF keeps
  it. The extraction rule is ``"\\n".join(lines between the fences)`` with no
  further trimming, which restores the payload byte-for-byte.
* A field whose value does not match its controlled vocabulary is degraded to
  a verbatim block and registered as an anomaly — never silently normalised.
* Every checklist row carries the review status ``NOT_REVIEWED``. The tool
  never writes a verdict of any kind.

Dependencies
------------
Standard library only, plus a read-only reuse of the shared contract layer
(``contracts.event.validate_events`` / ``contracts.evidence.ContractError``).
No third-party package, no packaging metadata, no change to any existing
module, contract, renderer or pipeline behaviour.

Usage
-----
    python scripts/input_fidelity_review.py --input <source.json> [--out <path>]

Exit codes
----------
``0``  checklist written
``2``  input file missing or not valid JSON (no file is produced)
``4``  the input violates the Event Contract (no file is produced)

There is deliberately no exit code ``3``: this tool has no word budget, and
it never calls the renderer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

# --------------------------------------------------------------------------
# Read-only reuse of the shared contract layer
# --------------------------------------------------------------------------
#
# The repository has no packaging metadata; ``tests/conftest.py`` already
# inserts ``src`` on ``sys.path`` for the same reason. The script resolves the
# repository root from its own location so it runs from any working directory.

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from contracts.evidence import ContractError  # noqa: E402
from contracts.event import validate_events  # noqa: E402

# --------------------------------------------------------------------------
# Frozen presentation constants
# --------------------------------------------------------------------------

#: Minimum fence length for a verbatim block (CommonMark requires three).
FENCE_MIN_LENGTH = 3

#: The one and only review status this tool is allowed to write.
REVIEW_STATUS = "NOT_REVIEWED"

#: Render label for a field that reaches no tab body.
NOT_RENDERED = "否"

#: Statement that must appear at the top of every checklist.
NOT_VERIFICATION_NOTICE = (
    "**本清单不构成事实验证。** 文本出现在清单中，仅表示该内容按原样从输入 JSON "
    "逐字转录；不代表其正确、已验证或已通过人工核对。Confidence 与 Evidence 均为"
    "输入数据的自述标注，本工具未做任何核验。全部条目的核对状态恒为 "
    "`NOT_REVIEWED`。"
)

_BACKTICK_RUN_RE = re.compile(r"`+")


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------


def fence_for(payload: str) -> str:
    """Return a fence long enough that the payload can never close it.

    The fence is one backtick longer than the longest backtick run inside the
    payload, with a floor of three backticks. A payload therefore cannot break
    out of its own block, no matter what it contains.
    """
    longest = max((len(run) for run in _BACKTICK_RUN_RE.findall(payload)), default=0)
    return "`" * max(FENCE_MIN_LENGTH, longest + 1)


def verbatim_block(path: str, payload: str, render_note: str) -> str:
    """Render one field as a verbatim fenced block.

    The block is written as::

        **<path>** — 逐字转录 ｜ HTML 正文：<note>
        <blank>
        <fence>text
        <payload>
        <fence>

    Writing ``payload + "\\n"`` before the closing fence is what makes the
    round trip exact: CommonMark drops the final line break of the block, so
    the recovered text is the payload again — including a payload that already
    ends in a newline (it then contributes one extra empty line).
    """
    fence = fence_for(payload)
    return (
        f"**{path}** — 逐字转录 ｜ HTML 正文：{render_note}\n\n"
        f"{fence}text\n{payload}\n{fence}\n"
    )


def inline_safe(value: str) -> bool:
    """Whether a value may be shown inline between backticks.

    Controlled identifiers are shown inline for readability; anything that
    could break the inline-code span or the line layout is degraded to a
    verbatim block instead.
    """
    return (
        isinstance(value, str)
        and "`" not in value
        and "\n" not in value
        and "\r" not in value
        and len(value) <= 160
        and all(ord(ch) >= 32 for ch in value)
    )


def display_safe(text: str) -> str:
    """Make an arbitrary string safe to show inside an inline code span.

    Only used for values that are *not* part of the fidelity guarantee (the
    input file name). Transcribed payloads never pass through this function.
    """
    return text.replace("`", "'").replace("\n", " ").replace("\r", " ")


def sha256_hex(data: bytes) -> str:
    """SHA256 of the raw bytes, lowercase hex."""
    return hashlib.sha256(data).hexdigest()


def _tab_label(tab_number: int) -> str:
    return f"Tab {tab_number}"


# --------------------------------------------------------------------------
# Render status derivation
# --------------------------------------------------------------------------


def derive_render_map(source: Dict[str, Any]) -> Dict[str, Any]:
    """Derive the expected render position of every event from the input.

    Returns a mapping with three keys:

    ``positions``
        ``event_id`` -> list of ``{"tab": str, "index": int}`` entries, in the
        order the tabs are numbered. An event may occupy more than one tab.
    ``anomalies``
        Contract conflicts that the pipeline would reject. They are reported,
        never repaired and never fatal for this tool.
    ``plan_ids``
        The event ids that carry a follow-up plan entry.
    """
    events = source.get("events") or []
    index: Dict[str, Dict[str, Any]] = {}
    for event in events:
        if isinstance(event, dict) and isinstance(event.get("event_id"), str):
            index[event["event_id"]] = event

    selection = source.get("selection")
    selection = selection if isinstance(selection, dict) else {}
    tab1_ids = [i for i in (selection.get("tab1_event_ids") or []) if isinstance(i, str)]
    tab3_ids = [i for i in (selection.get("tab3_event_ids") or []) if isinstance(i, str)]

    follow_up_plan = source.get("follow_up_plan")
    follow_up_plan = follow_up_plan if isinstance(follow_up_plan, list) else []
    plan_ids: List[str] = []
    anomalies: List[Dict[str, str]] = []
    for idx, entry in enumerate(follow_up_plan):
        if not isinstance(entry, dict):
            continue
        event_id = entry.get("event_id")
        if not isinstance(event_id, str):
            continue
        plan_ids.append(event_id)
        if event_id not in index:
            anomalies.append(
                {
                    "kind": "DANGLING_REFERENCE",
                    "where": f"follow_up_plan[{idx}].event_id",
                    "reference": event_id,
                    "detail": "计划条目指向不存在的 Event；Pipeline 会以 "
                              "ContractError 拒绝该文档。",
                }
            )
        elif index[event_id].get("status") != "open":
            anomalies.append(
                {
                    "kind": "INVALID_REFERENCE",
                    "where": f"follow_up_plan[{idx}].event_id",
                    "reference": event_id,
                    "detail": "计划条目指向的 Event 的 status 不是 'open'；"
                              "Pipeline 会以 ContractError 拒绝该文档。",
                }
            )

    plan_set = set(plan_ids)

    # Tab 5 items follow the pipeline's own ordering: the open events in
    # ``events`` array order.
    tracked_order = [
        event["event_id"]
        for event in events
        if isinstance(event, dict)
        and isinstance(event.get("event_id"), str)
        and event.get("status") == "open"
    ]
    tab5_index = {event_id: pos for pos, event_id in enumerate(tracked_order, 1)}

    positions: Dict[str, List[Dict[str, Any]]] = {}
    for event_id, event in index.items():
        slots: List[Dict[str, Any]] = []
        if event_id in tab1_ids:
            slots.append({"tab": _tab_label(1), "index": tab1_ids.index(event_id) + 1})
        if event_id in tab3_ids:
            slots.append({"tab": _tab_label(3), "index": tab3_ids.index(event_id) + 1})
        if event_id in plan_set and event_id in tab5_index:
            slots.append({"tab": _tab_label(5), "index": tab5_index[event_id]})
        if event.get("status") == "open" and event_id not in plan_set:
            anomalies.append(
                {
                    "kind": "FOLLOW_UP_MISSING",
                    "where": f"events[{event_id}].status",
                    "reference": event_id,
                    "detail": "该 Event 的 status 为 'open' 但 follow_up_plan 中"
                              "没有对应条目；Pipeline 会以 ContractError 拒绝该"
                              "文档，该 Event 不会进入 Tab 5。",
                }
            )
        if slots:
            positions[event_id] = slots

    # Selection conflicts: the pipeline resolves the selection against the
    # event index and the required assertion type.
    for list_name, ids, required_type in (
        ("selection.tab1_event_ids", tab1_ids, "fact"),
        ("selection.tab3_event_ids", tab3_ids, "inference"),
    ):
        for event_id in ids:
            if event_id not in index:
                anomalies.append(
                    {
                        "kind": "SELECTION_DANGLING",
                        "where": f"{list_name}",
                        "reference": event_id,
                        "detail": "选择列表引用了不存在的 Event；Pipeline 会以 "
                                  "ContractError 拒绝该文档。",
                    }
                )
                continue
            actual = index[event_id].get("assertion_type")
            if actual != required_type:
                anomalies.append(
                    {
                        "kind": "SELECTION_TYPE_MISMATCH",
                        "where": f"{list_name}",
                        "reference": event_id,
                        "detail": f"选择列表要求 assertion_type 为 "
                                  f"'{required_type}'，实际为 '{actual}'；"
                                  "Pipeline 会以 ContractError 拒绝该文档。",
                    }
                )

    # Knowledge Bite → Event references. The source document layer does not
    # check that they exist; the report contract does (DV-2). A reference that
    # points nowhere is registered instead of being dropped silently.
    knowledge_bites = source.get("knowledge_bites")
    knowledge_bites = knowledge_bites if isinstance(knowledge_bites, list) else []
    for kb_pos, bite in enumerate(knowledge_bites):
        if not isinstance(bite, dict):
            continue
        event_ids = bite.get("event_ids")
        if not isinstance(event_ids, list):
            continue
        for idx, event_id in enumerate(event_ids):
            if not isinstance(event_id, str) or event_id in index:
                continue
            anomalies.append(
                {
                    "kind": "DANGLING_REFERENCE",
                    "where": f"knowledge_bites[{kb_pos}].event_ids[{idx}]",
                    "reference": event_id,
                    "detail": "Knowledge Bite 引用了不存在的 Event；报告契约 "
                              "(DV-2) 会以 ContractError 拒绝该文档，"
                              "该引用不会进入任何 Tab。",
                }
            )

    return {
        "positions": positions,
        "anomalies": anomalies,
        "plan_ids": plan_ids,
        "index": index,
    }


def event_field_visibility(
    event: Dict[str, Any],
    slots: Sequence[Dict[str, Any]],
) -> Dict[str, str]:
    """Return ``field path -> tab label`` for one event.

    The mapping mirrors what the renderer actually emits:

    * ``title`` reaches the body only in Tab 1 (Tab 3 renders the summary
      alone, Tab 5 renders neither);
    * ``summary`` reaches Tab 1 and Tab 3;
    * ``confidence`` / ``estimated`` are rendered as badges wherever the event
      renders;
    * only ``sources[0]`` is carried into a tab item, and therefore rendered;
    * every other event field never reaches the HTML body.
    """
    tabs = [slot["tab"] for slot in slots]
    visibility: Dict[str, str] = {}

    def primary() -> str:
        for candidate in ("Tab 1", "Tab 3", "Tab 5"):
            if candidate in tabs:
                return candidate
        return NOT_RENDERED

    visibility["title"] = "Tab 1" if "Tab 1" in tabs else NOT_RENDERED
    if "Tab 1" in tabs:
        visibility["summary"] = "Tab 1"
    elif "Tab 3" in tabs:
        visibility["summary"] = "Tab 3"
    else:
        visibility["summary"] = NOT_RENDERED
    visibility["confidence"] = primary()
    visibility["estimated"] = primary()
    for idx in range(len(event.get("sources") or [])):
        label = primary() if idx == 0 else NOT_RENDERED
        visibility[f"sources[{idx}].name"] = label
        visibility[f"sources[{idx}].provider_tier"] = label
        visibility[f"sources[{idx}].locator"] = label
        visibility[f"sources[{idx}].routing"] = label
    for field in (
        "event_id",
        "assertion_type",
        "status",
        "occurred_at",
        "collected_at",
        "data_date",
        "themes",
        "companies",
        "derived_from",
        "related_event_ids",
        "supersedes",
        "verification_criteria",
    ):
        visibility[field] = NOT_RENDERED
    return visibility


# --------------------------------------------------------------------------
# Payload collection
# --------------------------------------------------------------------------


def collect_event_payloads(
    event: Dict[str, Any],
    event_pos: int,
    visibility: Dict[str, str],
) -> List[Dict[str, Any]]:
    """Collect every transcribed field of one event.

    Each entry is ``{"path", "value", "class", "render"}`` where ``class`` is
    either ``"FVB"`` (free text, emitted as a verbatim block) or ``"CI"``
    (controlled identifier, emitted inline). Nothing is dropped: every field
    that exists in the input produces exactly one entry.
    """
    prefix = f"events[{event_pos}]"
    payloads: List[Dict[str, Any]] = []

    def add(path: str, value: str, render: str, force_block: bool = False) -> None:
        if force_block or not inline_safe(value):
            payloads.append(
                {"path": path, "value": value, "class": "FVB", "render": render}
            )
        else:
            payloads.append(
                {"path": path, "value": value, "class": "CI", "render": render}
            )

    for field in ("title", "summary"):
        value = event.get(field)
        if isinstance(value, str):
            # title and summary are always verbatim blocks: they are the
            # research content itself and must never share a line with
            # anything else.
            add(f"{prefix}.{field}", value, visibility.get(field, NOT_RENDERED),
                force_block=True)

    for field in (
        "event_id",
        "assertion_type",
        "status",
        "confidence",
        "occurred_at",
        "collected_at",
        "data_date",
    ):
        value = event.get(field)
        if isinstance(value, str):
            add(f"{prefix}.{field}", value, visibility.get(field, NOT_RENDERED))

    estimated = event.get("estimated")
    if isinstance(estimated, bool):
        add(
            f"{prefix}.estimated",
            "true" if estimated else "false",
            visibility.get("estimated", NOT_RENDERED),
        )

    for field in ("themes", "companies"):
        values = event.get(field)
        if isinstance(values, list):
            for idx, value in enumerate(values):
                if isinstance(value, str):
                    add(
                        f"{prefix}.{field}[{idx}]",
                        value,
                        visibility.get(field, NOT_RENDERED),
                        force_block=True,
                    )

    for field in ("derived_from", "related_event_ids"):
        values = event.get(field)
        if isinstance(values, list):
            for idx, value in enumerate(values):
                if isinstance(value, str):
                    add(
                        f"{prefix}.{field}[{idx}]",
                        value,
                        visibility.get(field, NOT_RENDERED),
                    )

    for field in ("supersedes", "verification_criteria"):
        value = event.get(field)
        if isinstance(value, str):
            add(f"{prefix}.{field}", value, visibility.get(field, NOT_RENDERED))

    sources = event.get("sources")
    if isinstance(sources, list):
        for sidx, source in enumerate(sources):
            if not isinstance(source, dict):
                continue
            for field in ("name", "provider_tier", "locator"):
                value = source.get(field)
                if isinstance(value, str):
                    add(
                        f"{prefix}.sources[{sidx}].{field}",
                        value,
                        visibility.get(f"sources[{sidx}].{field}", NOT_RENDERED),
                        force_block=(field != "provider_tier"),
                    )
            routing = source.get("routing")
            if isinstance(routing, dict):
                attempted = routing.get("attempted")
                if isinstance(attempted, list):
                    for aidx, attempt in enumerate(attempted):
                        if not isinstance(attempt, dict):
                            continue
                        for field in ("tier", "provider", "outcome"):
                            value = attempt.get(field)
                            if isinstance(value, str):
                                add(
                                    f"{prefix}.sources[{sidx}].routing"
                                    f".attempted[{aidx}].{field}",
                                    value,
                                    visibility.get(
                                        f"sources[{sidx}].routing", NOT_RENDERED
                                    ),
                                    force_block=(field == "provider"),
                                )
    return payloads


def collect_knowledge_bite_payloads(
    bite: Dict[str, Any], kb_pos: int, known_event_ids: Iterable[str]
) -> List[Dict[str, Any]]:
    """Collect the transcribed fields of one Knowledge Bite.

    ``cognitive_unit`` and ``why_it_matters`` are the only two fields the Tab 4
    body carries; ``event_ids`` is a reference relation that never renders.
    """
    prefix = f"knowledge_bites[{kb_pos}]"
    known = set(known_event_ids)
    payloads: List[Dict[str, Any]] = []
    for field in ("cognitive_unit", "why_it_matters"):
        value = bite.get(field)
        if isinstance(value, str):
            payloads.append(
                {
                    "path": f"{prefix}.{field}",
                    "value": value,
                    "class": "FVB",
                    "render": "Tab 4",
                }
            )
    for field in ("confidence", "estimated"):
        value = bite.get(field)
        if isinstance(value, bool):
            payloads.append(
                {
                    "path": f"{prefix}.{field}",
                    "value": "true" if value else "false",
                    "class": "CI",
                    "render": "Tab 4",
                }
            )
        elif isinstance(value, str):
            payloads.append(
                {
                    "path": f"{prefix}.{field}",
                    "value": value,
                    "class": "CI",
                    "render": "Tab 4",
                }
            )
    source = bite.get("source")
    if isinstance(source, dict):
        for field in ("name", "provider_tier", "locator"):
            value = source.get(field)
            if isinstance(value, str):
                payloads.append(
                    {
                        "path": f"{prefix}.source.{field}",
                        "value": value,
                        "class": "FVB" if field != "provider_tier" else "CI",
                        "render": "Tab 4",
                    }
                )
    event_ids = bite.get("event_ids")
    if isinstance(event_ids, list):
        for idx, value in enumerate(event_ids):
            if not isinstance(value, str):
                continue
            payloads.append(
                {
                    "path": f"{prefix}.event_ids[{idx}]",
                    "value": value,
                    "class": "CI" if value in known else "FVB",
                    "render": NOT_RENDERED,
                }
            )
    return payloads


def collect_follow_up_payloads(entry: Dict[str, Any], plan_pos: int) -> List[Dict[str, Any]]:
    """Collect the transcribed fields of one follow-up plan entry."""
    prefix = f"follow_up_plan[{plan_pos}]"
    payloads: List[Dict[str, Any]] = []
    for field in ("action", "next_check", "linked_theme"):
        value = entry.get(field)
        if isinstance(value, str):
            payloads.append(
                {
                    "path": f"{prefix}.{field}",
                    "value": value,
                    "class": "FVB" if field != "next_check" else "CI",
                    "render": "Tab 5",
                }
            )
    event_id = entry.get("event_id")
    if isinstance(event_id, str):
        payloads.append(
            {
                "path": f"{prefix}.event_id",
                "value": event_id,
                "class": "CI",
                "render": NOT_RENDERED,
            }
        )
    return payloads


def collect_market_payloads(market_data: Any) -> List[Dict[str, Any]]:
    """Collect the transcribed fields of the market snapshot block."""
    payloads: List[Dict[str, Any]] = []
    if not isinstance(market_data, dict):
        return payloads
    items = market_data.get("items")
    if isinstance(items, list):
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            text = item.get("text")
            if isinstance(text, str):
                payloads.append(
                    {
                        "path": f"market_data.items[{idx}].text",
                        "value": text,
                        "class": "FVB",
                        "render": "Tab 2",
                    }
                )
            source = item.get("source")
            if isinstance(source, dict):
                for field in ("name", "provider_tier", "locator"):
                    value = source.get(field)
                    if isinstance(value, str):
                        payloads.append(
                            {
                                "path": f"market_data.items[{idx}].source.{field}",
                                "value": value,
                                "class": "FVB" if field != "provider_tier" else "CI",
                                "render": "Tab 2",
                            }
                        )
            for field in ("confidence", "estimated"):
                value = item.get(field)
                if isinstance(value, bool):
                    payloads.append(
                        {
                            "path": f"market_data.items[{idx}].{field}",
                            "value": "true" if value else "false",
                            "class": "CI",
                            "render": "Tab 2",
                        }
                    )
                elif isinstance(value, str):
                    payloads.append(
                        {
                            "path": f"market_data.items[{idx}].{field}",
                            "value": value,
                            "class": "CI",
                            "render": "Tab 2",
                        }
                    )
    reason = market_data.get("unavailable_reason")
    if isinstance(reason, str):
        payloads.append(
            {
                "path": "market_data.unavailable_reason",
                "value": reason,
                "class": "FVB",
                "render": "Tab 2",
            }
        )
    return payloads


# --------------------------------------------------------------------------
# Markdown assembly
# --------------------------------------------------------------------------


def _payload_block(payload: Dict[str, Any]) -> str:
    if payload["class"] == "FVB":
        return verbatim_block(payload["path"], payload["value"], payload["render"])
    return f"- **{payload['path']}**: `{payload['value']}`\n"


def _checklist_table(payloads: Sequence[Dict[str, Any]]) -> str:
    lines = [
        "| 字段路径 | 进入 HTML 正文 | 核对状态 |",
        "|---|---|---|",
    ]
    for payload in payloads:
        lines.append(
            f"| `{payload['path']}` | {payload['render']} | `{REVIEW_STATUS}` |"
        )
    return "\n".join(lines) + "\n"


def _render_blocks(blocks: Sequence[str]) -> str:
    """Join the output blocks, guaranteeing that every block ends a line.

    An empty block is a deliberate blank line; a block that does not end with
    a newline gets one, so that a table row can never be glued to the next
    line. Nothing inside a verbatim block is touched — those blocks already
    end with a newline and are passed through unchanged.
    """
    parts: List[str] = []
    for block in blocks:
        if not block:
            parts.append("\n")
        elif block.endswith("\n"):
            parts.append(block)
        else:
            parts.append(block + "\n")
    return "".join(parts)


def _render_status_text(slots: Sequence[Dict[str, Any]], event: Dict[str, Any]) -> str:
    if not slots:
        reason = "未被 selection 选中"
        if event.get("status") == "open":
            reason += "，且无 follow_up_plan 条目"
        return f"未渲染（{reason}）"
    parts = []
    for slot in slots:
        if slot["tab"] == "Tab 1":
            parts.append(f"Tab 1 #{slot['index']}（title 渲染 · summary 渲染）")
        elif slot["tab"] == "Tab 3":
            parts.append(f"Tab 3 #{slot['index']}（summary 渲染 · **title 不渲染**）")
        else:
            parts.append(
                f"Tab 5 #{slot['index']}（action / next_check 渲染 · "
                "**title 与 summary 均不渲染**）"
            )
    return " ｜ ".join(parts)


def build_checklist(source: Dict[str, Any], input_meta: Dict[str, Any]) -> str:
    """Assemble the complete Markdown checklist for one source document."""
    events = source.get("events") or []
    render_map = derive_render_map(source)
    positions = render_map["positions"]
    anomalies = render_map["anomalies"]
    known_event_ids = set(render_map["index"].keys())

    out: List[str] = []
    out.append(f"# Research Input Fidelity Review — {input_meta.get('data_date', '(未提供)')}\n")
    out.append(f"> {NOT_VERIFICATION_NOTICE}\n")
    out.append("\n---\n")

    # ---- header table ----------------------------------------------------
    out.append("## 输入概览\n")
    out.append("| 项 | 值 |")
    out.append("|---|---|")
    out.append(f"| 输入文件 | `{display_safe(input_meta.get('file_name', ''))}` |")
    out.append(f"| 输入 SHA256 | `{input_meta.get('sha256', '')}` |")
    out.append(f"| 输入字节数 | {input_meta.get('byte_count', 0)} |")
    out.append(f"| run_date | `{input_meta.get('run_date', '(未提供)')}` |")
    out.append(f"| data_date | `{input_meta.get('data_date', '(未提供)')}` |")
    out.append(f"| data_mode | `{input_meta.get('data_mode', '(未提供)')}` |")
    out.append(f"| Event 总数 | {len(events)} |")

    tab_counts: Dict[str, int] = {}
    unrendered = 0
    title_not_rendered = 0
    for event in events:
        if not isinstance(event, dict):
            continue
        event_id = event.get("event_id")
        slots = positions.get(event_id, [])
        if not slots:
            unrendered += 1
        for slot in slots:
            tab_counts[slot["tab"]] = tab_counts.get(slot["tab"], 0) + 1
        visibility = event_field_visibility(event, slots)
        if visibility.get("title") == NOT_RENDERED:
            title_not_rendered += 1
    coverage = " ｜ ".join(
        f"{tab}: {tab_counts.get(tab, 0)}" for tab in ("Tab 1", "Tab 3", "Tab 5")
    )
    out.append(f"| 渲染覆盖 | {coverage} ｜ 未渲染: {unrendered} |")
    out.append(f"| title 不进入正文的事件 | {title_not_rendered} |")

    knowledge_bites = source.get("knowledge_bites")
    knowledge_bites = knowledge_bites if isinstance(knowledge_bites, list) else []
    kb_refs = 0
    for bite in knowledge_bites:
        if isinstance(bite, dict) and isinstance(bite.get("event_ids"), list):
            kb_refs += len(bite["event_ids"])
    out.append(f"| Knowledge Bite | {len(knowledge_bites)}（引用 {kb_refs} 条 event_id） |")
    out.append("")

    # ---- coverage summary ------------------------------------------------
    out.append("## 覆盖汇总\n")
    out.append("### 按渲染位置\n")
    out.append("| 渲染位置 | 事件数 | 事件 id |")
    out.append("|---|---|---|")
    for tab, description in (
        ("Tab 1", "title + summary"),
        ("Tab 3", "仅 summary"),
        ("Tab 5", "仅 action / next_check"),
    ):
        members = [
            event.get("event_id")
            for event in events
            if isinstance(event, dict)
            and any(
                slot["tab"] == tab for slot in positions.get(event.get("event_id"), [])
            )
        ]
        rendered = " ｜ ".join(f"`{event_id}`" for event_id in members) or "（无）"
        out.append(f"| {tab}（{description}） | {len(members)} | {rendered} |")
    not_rendered_members = [
        event.get("event_id")
        for event in events
        if isinstance(event, dict) and not positions.get(event.get("event_id"), [])
    ]
    out.append(
        f"| 未渲染 | {len(not_rendered_members)} | "
        + (" ｜ ".join(f"`{event_id}`" for event_id in not_rendered_members) or "（无）")
        + " |"
    )
    out.append("")

    out.append(f"### title 不进入 HTML 正文的事件（{title_not_rendered}）\n")
    out.append("| event_id | 原因 |")
    out.append("|---|---|")
    for event in events:
        if not isinstance(event, dict):
            continue
        event_id = event.get("event_id")
        slots = positions.get(event_id, [])
        visibility = event_field_visibility(event, slots)
        if visibility.get("title") != NOT_RENDERED:
            continue
        if "Tab 3" in [slot["tab"] for slot in slots]:
            reason = "渲染于 Tab 3，仅 summary 进入正文"
        elif "Tab 5" in [slot["tab"] for slot in slots]:
            reason = "渲染于 Tab 5，title 与 summary 均不进入正文"
        else:
            reason = "完全未渲染（未被 selection 选中，且无 follow_up_plan 条目）"
        out.append(f"| `{event_id}` | {reason} |")
    out.append("")

    out.append("### Knowledge Bite → Event 反向引用\n")
    out.append("| KB | 引用 event_id | 引用有效性 | 是否进入 HTML 正文 |")
    out.append("|---|---|---|---|")
    for kb_pos, bite in enumerate(knowledge_bites, 1):
        if not isinstance(bite, dict):
            continue
        event_ids = bite.get("event_ids")
        if not isinstance(event_ids, list) or not event_ids:
            continue
        for event_id in event_ids:
            if not isinstance(event_id, str):
                continue
            validity = "有效" if event_id in known_event_ids else "**悬空引用**"
            out.append(f"| KB {kb_pos} | `{event_id}` | {validity} | {NOT_RENDERED} |")
    out.append("")
    out.append(
        "> Tab 4 的 `content_fields` 仅含 `cognitive_unit` / `why_it_matters`；"
        "`event_ids` 是引用关系，不进入 HTML 正文。\n"
    )

    # ---- anomalies -------------------------------------------------------
    out.append("## 异常与契约冲突登记\n")
    if anomalies:
        out.append("| 类型 | 位置 | 引用 | 说明 |")
        out.append("|---|---|---|---|")
        for anomaly in anomalies:
            out.append(
                f"| `{anomaly['kind']}` | `{anomaly['where']}` | "
                f"`{anomaly['reference']}` | {anomaly['detail']} |"
            )
        out.append("")
        out.append(
            "> 以上为源文档层的契约冲突。工具只登记事实，不判定对错，也不中断输出；"
            "Pipeline 在生成报告时会以 ContractError 拒绝这些文档。\n"
        )
    else:
        out.append("无异常登记项。\n")

    # ---- events ----------------------------------------------------------
    out.append("---\n")
    out.append("## Event 逐条转录\n")
    total = len(events)
    for event_pos, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        event_id = event.get("event_id")
        slots = positions.get(event_id, [])
        visibility = event_field_visibility(event, slots)
        payloads = collect_event_payloads(event, event_pos, visibility)

        out.append(f"### Event {event_pos + 1} / {total} — `{event_id}`\n")
        out.append(f"- **渲染状态**: {_render_status_text(slots, event)}")
        out.append(f"- **核对状态**: {REVIEW_STATUS}\n")

        for payload in payloads:
            if payload["class"] == "CI":
                out.append(_payload_block(payload))
        out.append("")
        for payload in payloads:
            if payload["class"] == "FVB":
                out.append(_payload_block(payload))
                out.append("")

        out.append(f"#### 核对清单 — Event {event_pos + 1}\n")
        out.append(_checklist_table(payloads))
        out.append("")

    # ---- non-event bodies ------------------------------------------------
    out.append("---\n")
    out.append("## 非 Event 正文转录（Tab 2 / Tab 4 / Tab 5 文本）\n")
    non_event_payloads: List[Dict[str, Any]] = []
    for kb_pos, bite in enumerate(knowledge_bites):
        if not isinstance(bite, dict):
            continue
        non_event_payloads.extend(
            collect_knowledge_bite_payloads(bite, kb_pos, known_event_ids)
        )
    follow_up_plan = source.get("follow_up_plan")
    follow_up_plan = follow_up_plan if isinstance(follow_up_plan, list) else []
    for plan_pos, entry in enumerate(follow_up_plan):
        if not isinstance(entry, dict):
            continue
        non_event_payloads.extend(collect_follow_up_payloads(entry, plan_pos))
    non_event_payloads.extend(collect_market_payloads(source.get("market_data")))

    if not non_event_payloads:
        out.append("（输入未提供 Knowledge Bite / follow_up_plan / market_data 文本）\n")
    else:
        for payload in non_event_payloads:
            if payload["class"] == "CI":
                out.append(_payload_block(payload))
        out.append("")
        for payload in non_event_payloads:
            if payload["class"] == "FVB":
                out.append(_payload_block(payload))
                out.append("")
        out.append("### 核对清单 — 非 Event 正文\n")
        out.append(_checklist_table(non_event_payloads))
        out.append("")

    # ---- rule appendix ----------------------------------------------------
    out.append("---\n")
    out.append("## 渲染状态映射规则（推导依据）\n")
    out.append("| 规则 | 判定条件 | 渲染位置 | 原文可见性 | 冻结来源 |")
    out.append("|---|---|---|---|---|")
    out.append(
        "| R1 | `event_id ∈ selection.tab1_event_ids` | Tab 1 | title + summary 均渲染 | "
        "`pipeline.py:393-395`、`:424-426`（`TAB1_TEXT_FORMAT` `:57`） |"
    )
    out.append(
        "| R2 | `event_id ∈ selection.tab3_event_ids` | Tab 3 | 仅 summary；**title 不渲染** | "
        "`pipeline.py:396-401`、`:439` |"
    )
    out.append(
        "| R3 | `event_id ∈ follow_up_plan[].event_id` | Tab 5 | "
        "**title 与 summary 均不渲染**（action / next_check / linked_theme） | "
        "`pipeline.py:281-317`、`:319-333`、`:337-349` |"
    )
    out.append(
        "| R4 | 其余 | 未渲染 | 全部不渲染（含全部 hypothesis） | "
        "`pipeline.py:112-116`、`:393-401` |"
    )
    out.append("")
    out.append(
        "> R3 以 `follow_up_plan` 的实际条目为准，而非 `status == \"open\"`："
        "Pipeline 双向强制该关系，缺任一侧即拒绝文档。`status` 为 `open` 却无计划"
        "条目的事件不进入 Tab 5，并登记为 `FOLLOW_UP_MISSING`。\n"
    )
    out.append(
        "> 本清单为输入字段的逐字转录与覆盖核对，**不构成事实验证**，"
        "不判定事实真伪，不升级 Confidence，不修改输入文档。\n"
    )
    return _render_blocks(out)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def default_output_path(data_date: str) -> Path:
    """Default checklist location, named after the data date."""
    return Path("output") / f"input-fidelity-review-{data_date}.md"


def main(argv: Optional[List[str]] = None) -> int:
    """Read a source document and write the fidelity review checklist.

    Exit codes follow the discipline established by the Daily Briefing
    pipeline: ``0`` success, ``2`` input problem, ``4`` contract violation.
    This tool has no word budget, so there is no ``3``.
    """
    parser = argparse.ArgumentParser(
        prog="input_fidelity_review",
        description=(
            "Generate a deterministic, field-by-field fidelity review checklist "
            "for a Daily Briefing source document. The checklist transcribes "
            "every field verbatim and states the expected render position of "
            "each one. It does NOT verify facts, adjust confidence or modify "
            "the input."
        ),
        epilog=(
            "Exit codes: 0 = checklist written | 2 = input missing or invalid "
            "JSON | 4 = Event Contract violation. There is no exit code 3: "
            "this tool has no word budget and never calls the renderer."
        ),
    )
    parser.add_argument("--input", required=True, help="Path to the source JSON")
    parser.add_argument(
        "--out",
        default=None,
        help=(
            "Output Markdown path "
            "(default: output/input-fidelity-review-<data_date>.md)"
        ),
    )
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"error: input file not found: {input_path}", file=sys.stderr)
        return 2
    try:
        raw = input_path.read_bytes()
    except OSError as exc:
        print(f"error: cannot read input file: {exc}", file=sys.stderr)
        return 2
    try:
        source = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"error: input is not valid JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(source, dict):
        print("error: source document root must be an object", file=sys.stderr)
        return 4

    try:
        validate_events(source.get("events"), "events")
    except ContractError as exc:
        print(f"error: contract violation: {exc}", file=sys.stderr)
        return 4

    meta = source.get("meta")
    meta = meta if isinstance(meta, dict) else {}
    data_date = meta.get("data_date")
    if args.out:
        out_path = Path(args.out)
    else:
        if not isinstance(data_date, str) or not data_date:
            print(
                "error: meta.data_date is required to derive the default "
                "output file name; pass --out explicitly to override",
                file=sys.stderr,
            )
            return 4
        out_path = default_output_path(data_date)

    input_meta = {
        "file_name": input_path.name,
        "sha256": sha256_hex(raw),
        "byte_count": len(raw),
        "run_date": meta.get("run_date", "(未提供)"),
        "data_date": data_date or "(未提供)",
        "data_mode": meta.get("data_mode", "(未提供)"),
    }

    checklist = build_checklist(source, input_meta)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(checklist)
    print(
        f"wrote {out_path}  "
        f"({len(checklist.encode('utf-8'))} bytes, "
        f"events={len(source.get('events') or [])}, "
        f"data_date={data_date})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
