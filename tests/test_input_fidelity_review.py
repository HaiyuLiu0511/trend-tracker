"""Tests for the Input Fidelity Review tool (``scripts/input_fidelity_review.py``).

The suite is split in two halves on purpose:

* **T-series** — unit tests. They never import ``daily_briefing``; they
  exercise the tool's transcription, coverage, determinism and exit-code
  behaviour on their own. ``test_tool_has_no_pipeline_dependency`` guards the
  separation.
* **X-series** — cross-validation tests. They import the existing pipeline to
  prove that the tool's *expected* render status matches what the real
  renderer actually produces.

The fidelity assertions are deliberately **not** "the string appears somewhere
in the output". They are:

* exact byte equality between the recovered payload and the input value,
* a character census (Counter) as a second, independent equality proof,
* a per-payload SHA256 as a third,
* and a path-driven ownership check that resolves every checklist path back
  against the source document.

A substring check cannot distinguish "transcribed verbatim" from "paraphrased
somewhere else"; these four can.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

SCRIPT = ROOT / "scripts" / "input_fidelity_review.py"
FIXTURE = Path(__file__).parent / "fixtures" / "fidelity_adversarial.json"

#: The vocabulary of review statuses the tool is allowed to write.
ALLOWED_REVIEW_STATUS = "NOT_REVIEWED"

#: Words that would turn a transcription instrument into a verdict machine.
FORBIDDEN_VERDICT_WORDS = ("VERIFIED", "已验证", "已核实", "确认无误", "PASSED")


# --------------------------------------------------------------------------
# Tool loading
# --------------------------------------------------------------------------


def _load_tool():
    """Load the tool by path, the way an operator would run it."""
    spec = importlib.util.spec_from_file_location("input_fidelity_review", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TOOL = _load_tool()


# --------------------------------------------------------------------------
# Independent scanner (written against the documented grammar, not the tool)
# --------------------------------------------------------------------------

_FENCE_RE = re.compile(r"^(`{3,})([A-Za-z0-9_+-]*)\s*$")
_LABEL_RE = re.compile(r"^\*\*(?P<path>[^*]+)\*\* — 逐字转录")
_INLINE_RE = re.compile(r"^- \*\*(?P<path>[^*]+)\*\*: `(?P<value>.*)`$")

#: A transcribed field path always starts with one of the input blocks.
_FIELD_PATH_RE = re.compile(
    r"^(?:events|knowledge_bites|follow_up_plan|market_data)[\[.]"
)


def scan_checklist(text: str) -> Tuple[Dict[str, str], Dict[str, str], List[str]]:
    """Recover every transcribed payload from a checklist.

    Returns ``(blocks, inline, order)`` where ``blocks`` maps a field path to
    a verbatim fenced payload, ``inline`` maps a field path to an inline
    controlled value, and ``order`` is the document order of every path.

    The scanner is fence-aware: once inside a block it skips to the matching
    closing fence, so a payload that itself contains a label line and a fence
    is never mistaken for a separate block.
    """
    lines = text.split("\n")
    blocks: Dict[str, str] = {}
    inline: Dict[str, str] = {}
    order: List[str] = []
    index = 0
    while index < len(lines):
        label = _LABEL_RE.match(lines[index])
        if label:
            fence_index = index + 1
            if fence_index < len(lines) and lines[fence_index] == "":
                fence_index += 1
            fence_match = (
                _FENCE_RE.match(lines[fence_index])
                if fence_index < len(lines)
                else None
            )
            if fence_match:
                fence = fence_match.group(1)
                body: List[str] = []
                cursor = fence_index + 1
                while cursor < len(lines) and lines[cursor] != fence:
                    body.append(lines[cursor])
                    cursor += 1
                path = label.group("path")
                blocks[path] = "\n".join(body)
                order.append(path)
                index = cursor + 1
                continue
        inline_match = _INLINE_RE.match(lines[index])
        if inline_match and _FIELD_PATH_RE.match(inline_match.group("path")):
            path = inline_match.group("path")
            inline[path] = inline_match.group("value")
            order.append(path)
        index += 1
    return blocks, inline, order


# --------------------------------------------------------------------------
# Path-driven resolver: the ownership proof
# --------------------------------------------------------------------------


def resolve(source: Dict[str, Any], path: str) -> Any:
    """Resolve a checklist path against the source document.

    This is the ownership check: the path itself says which event and which
    field the payload must come from, so a payload copied under the wrong
    heading cannot pass.
    """
    match = re.match(r"^events\[(\d+)\]\.(?P<rest>.+)$", path)
    if match:
        event = source["events"][int(match.group(1))]
        return _resolve_event_path(event, match.group("rest"))

    match = re.match(r"^knowledge_bites\[(\d+)\]\.(?P<rest>.+)$", path)
    if match:
        bite = source["knowledge_bites"][int(match.group(1))]
        rest = match.group("rest")
        if rest.startswith("source."):
            return bite["source"][rest.split(".", 1)[1]]
        if rest.startswith("event_ids["):
            index = int(re.match(r"^event_ids\[(\d+)\]$", rest).group(1))
            return bite["event_ids"][index]
        if rest == "estimated":
            return "true" if bite["estimated"] else "false"
        return bite[rest]

    match = re.match(r"^follow_up_plan\[(\d+)\]\.(?P<rest>.+)$", path)
    if match:
        return source["follow_up_plan"][int(match.group(1))][match.group("rest")]

    match = re.match(r"^market_data\.items\[(\d+)\]\.(?P<rest>.+)$", path)
    if match:
        item = source["market_data"]["items"][int(match.group(1))]
        rest = match.group("rest")
        if rest.startswith("source."):
            return item["source"][rest.split(".", 1)[1]]
        if rest == "estimated":
            return "true" if item["estimated"] else "false"
        return item[rest]

    if path == "market_data.unavailable_reason":
        return source["market_data"]["unavailable_reason"]

    raise AssertionError(f"unresolvable checklist path: {path}")


def _resolve_event_path(event: Dict[str, Any], rest: str) -> Any:
    match = re.match(r"^sources\[(\d+)\]\.routing\.attempted\[(\d+)\]\.(?P<f>.+)$", rest)
    if match:
        source = event["sources"][int(match.group(1))]
        attempt = source["routing"]["attempted"][int(match.group(2))]
        return attempt[match.group("f")]

    match = re.match(r"^sources\[(\d+)\]\.(?P<f>.+)$", rest)
    if match:
        return event["sources"][int(match.group(1))][match.group("f")]

    match = re.match(r"^(?P<f>[a-z_]+)\[(?P<i>\d+)\]$", rest)
    if match:
        return event[match.group("f")][int(match.group("i"))]

    if rest == "estimated":
        return "true" if event["estimated"] else "false"

    return event[rest]


# --------------------------------------------------------------------------
# Fixtures / helpers
# --------------------------------------------------------------------------


def load_fixture() -> Dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def input_meta(name: str = "fixture.json") -> Dict[str, Any]:
    return {
        "file_name": name,
        "sha256": "0" * 64,
        "byte_count": 0,
        "run_date": "2026-10-23",
        "data_date": "2026-10-23",
        "data_mode": "mock",
    }


def render_fixture(source: Dict[str, Any] | None = None) -> str:
    src = source if source is not None else load_fixture()
    return TOOL.build_checklist(src, input_meta())


def make_event(
    event_id: str,
    *,
    title: str = "标题",
    summary: str = "摘要",
    assertion_type: str = "fact",
    status: str = "active",
    sources: List[Dict[str, Any]] | None = None,
    **extra: Any,
) -> Dict[str, Any]:
    event: Dict[str, Any] = {
        "event_id": event_id,
        "title": title,
        "summary": summary,
        "assertion_type": assertion_type,
        "status": status,
        "occurred_at": "2026-10-23",
        "collected_at": "2026-10-23",
        "data_date": "2026-10-23",
        "sources": sources
        or [
            {
                "name": "p",
                "provider_tier": "P0",
                "locator": "fixture://x",
            }
        ],
        "confidence": "MEDIUM",
        "estimated": False,
    }
    event.update(extra)
    return event


def make_source(
    events: List[Dict[str, Any]],
    *,
    selection: Dict[str, List[str]] | None = None,
    knowledge_bites: List[Dict[str, Any]] | None = None,
    follow_up_plan: List[Dict[str, Any]] | None = None,
    market_data: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "meta": {
            "report_type": "Daily Briefing",
            "run_date": "2026-10-23",
            "data_date": "2026-10-23",
            "data_mode": "mock",
        },
        "events": events,
        "selection": selection or {"tab1_event_ids": [], "tab3_event_ids": []},
        "market_data": market_data if market_data is not None else {"items": []},
        "knowledge_bites": knowledge_bites
        if knowledge_bites is not None
        else [
            {
                "cognitive_unit": "c",
                "why_it_matters": "w",
                "event_ids": [],
                "source": {"name": "s", "provider_tier": "P0", "locator": "l"},
                "confidence": "MEDIUM",
                "estimated": False,
            }
        ],
        "follow_up_plan": follow_up_plan or [],
        "methodology": {"methods": ["m"], "limitations": ["l"]},
    }


#: Payloads that stress the transcription layer. Every one of them survives
#: the Event Contract (non-empty after stripping), so all of them can travel
#: through a real event field.
HOSTILE_PAYLOADS: List[str] = [
    "含 ``` 三反引号",
    "含 ```` 四反引号与 ```",
    "含 ````` 五反引号",
    "首行\n第二行\n第三行",
    "以换行结尾\n",
    "带孤立 CR\r回车",
    "带 CRLF\r\n回车换行",
    "尾随空格   ",
    "  前导空格",
    "管道符|星号*下划线_井号#尖括号<>与&符号",
    "全角（括号）与｛｝［］【】",
    "**events[0].title** — 逐字转录\n```text\n伪造块\n```",
    "行首>引用\n- 列表项\n1. 有序项",
    "```\n```\n```",
    "emoji 🚀 与组合字符 é",
    "引号形态：“即将实施”与'单引号'",
    "反斜杠 \\ 与制表\t符",
]

#: Payloads that only the fence primitive itself has to survive; the Event
#: Contract rejects them because they are blank after stripping.
BLANKISH_PAYLOADS: List[str] = ["", "\n", "\n\n\n"]


# --------------------------------------------------------------------------
# T-series: unit tests (no pipeline import)
# --------------------------------------------------------------------------


def test_tool_has_no_pipeline_dependency() -> None:
    """T-guard: the tool must not depend on the pipeline at runtime."""
    text = SCRIPT.read_text(encoding="utf-8")
    assert not re.search(
        r"^\s*(?:from|import)\s+.*daily_briefing", text, re.M
    ), "the tool must not import the pipeline"
    assert not hasattr(TOOL, "build_document")
    assert not hasattr(TOOL, "render")


def test_verbatim_fidelity_is_byte_exact() -> None:
    """T1: every payload round-trips byte-for-byte."""
    source = load_fixture()
    blocks, inline, _ = scan_checklist(render_fixture(source))
    assert blocks, "the fixture must produce verbatim blocks"
    for path, payload in blocks.items():
        expected = resolve(source, path)
        assert payload == expected, f"payload mismatch for {path}"
        assert Counter(payload) == Counter(expected), f"census mismatch for {path}"
        assert hashlib.sha256(payload.encode("utf-8")).hexdigest() == (
            hashlib.sha256(expected.encode("utf-8")).hexdigest()
        )


def test_inline_values_are_exact() -> None:
    """T1 (controlled identifiers): inline values equal the input exactly."""
    source = load_fixture()
    _, inline, _ = scan_checklist(render_fixture(source))
    assert inline
    for path, value in inline.items():
        assert value == resolve(source, path), f"inline mismatch for {path}"


def test_no_field_is_dropped_or_duplicated() -> None:
    """T2 + T3: coverage is complete, paths are unique, ownership holds."""
    source = load_fixture()
    blocks, inline, order = scan_checklist(render_fixture(source))
    paths = set(blocks) | set(inline)
    assert len(order) == len(paths), "a path was emitted twice"
    assert len(blocks) + len(inline) == len(order)
    # Ownership: every path resolves against the source document.
    for path in paths:
        resolve(source, path)


def test_expected_paths_are_all_present() -> None:
    """T2: a hand-written list of the fields that must exist.

    This is the guard against a shared blind spot: the list is written by
    hand from the fixture, so a field that both the tool and the scanner
    forgot still fails here.
    """
    source = load_fixture()
    blocks, inline, _ = scan_checklist(render_fixture(source))
    paths = set(blocks) | set(inline)

    expected = {
        "events[0].title",
        "events[0].summary",
        "events[0].event_id",
        "events[0].assertion_type",
        "events[0].status",
        "events[0].confidence",
        "events[0].estimated",
        "events[0].occurred_at",
        "events[0].collected_at",
        "events[0].data_date",
        "events[0].themes[0]",
        "events[0].companies[0]",
        "events[0].sources[0].name",
        "events[0].sources[0].provider_tier",
        "events[0].sources[0].locator",
        "events[1].sources[1].name",
        "events[1].sources[1].provider_tier",
        "events[1].sources[1].locator",
        "events[1].sources[1].routing.attempted[0].tier",
        "events[1].sources[1].routing.attempted[0].provider",
        "events[1].sources[1].routing.attempted[0].outcome",
        "events[1].sources[1].routing.attempted[1].tier",
        "events[1].sources[1].routing.attempted[1].provider",
        "events[1].sources[1].routing.attempted[1].outcome",
        "events[1].sources[2].name",
        "events[1].sources[2].locator",
        "events[3].derived_from[0]",
        "events[3].derived_from[1]",
        "events[3].companies[0]",
        "events[4].verification_criteria",
        "events[5].verification_criteria",
        "knowledge_bites[0].cognitive_unit",
        "knowledge_bites[0].why_it_matters",
        "knowledge_bites[0].event_ids[0]",
        "knowledge_bites[0].event_ids[1]",
        "knowledge_bites[1].event_ids[0]",
        "follow_up_plan[0].action",
        "follow_up_plan[0].next_check",
        "follow_up_plan[0].linked_theme",
        "follow_up_plan[0].event_id",
        "market_data.items[0].text",
        "market_data.items[0].source.name",
        "market_data.items[0].source.locator",
        "market_data.items[1].text",
    }
    missing = expected - paths
    assert not missing, f"fields missing from the checklist: {sorted(missing)}"


def test_unselected_event_is_covered_and_marked() -> None:
    """T4: an unselected fact is transcribed and marked as not rendered."""
    source = load_fixture()
    text = render_fixture(source)
    blocks, _, _ = scan_checklist(text)
    unselected = source["events"][2]["event_id"]
    assert "events[2].title" in blocks
    assert unselected in text
    assert "完全未渲染" in text


def test_hypothesis_is_covered_and_marked() -> None:
    """T4: a hypothesis can never reach Tab 1/3 and is still transcribed."""
    source = load_fixture()
    text = render_fixture(source)
    blocks, _, _ = scan_checklist(text)
    assert "events[4].title" in blocks
    assert source["events"][4]["event_id"] in text


def test_title_of_non_tab1_events_is_flagged() -> None:
    """T5: the title of a Tab 3 / Tab 5 event is transcribed and flagged."""
    source = load_fixture()
    text = render_fixture(source)
    blocks, _, _ = scan_checklist(text)
    # Tab 3 only (events[3]) and Tab 5 (events[5]) never render their title.
    assert "events[3].title" in blocks
    assert "events[5].title" in blocks
    assert "**title 不渲染**" in text
    assert "title 与 summary 均不渲染" in text


def test_all_sources_are_kept() -> None:
    """T6: every source of an event survives, not only sources[0]."""
    source = load_fixture()
    blocks, _, _ = scan_checklist(render_fixture(source))
    for index in range(3):
        assert f"events[1].sources[{index}].name" in blocks
        assert f"events[1].sources[{index}].locator" in blocks
    assert blocks["events[1].sources[1].name"] == "fixture-provider-secondary"
    assert blocks["events[1].sources[2].name"] == "fixture-provider-tertiary"


def test_only_first_source_is_reported_as_rendered() -> None:
    """T6: the report shows sources[0] only — the checklist must say so."""
    source = load_fixture()
    text = render_fixture(source)
    assert "| `events[1].sources[0].name` | Tab 1 |" in text
    assert "| `events[1].sources[1].name` | 否 |" in text
    assert "| `events[1].sources[2].name` | 否 |" in text


@pytest.mark.parametrize("payload", HOSTILE_PAYLOADS)
def test_hostile_payload_survives_the_pipeline(payload: str) -> None:
    """T7: hostile text travels through a real event field unchanged."""
    event = make_event("evt-20261023-hostile", title=payload, summary=payload)
    source = make_source([event], selection={"tab1_event_ids": [event["event_id"]], "tab3_event_ids": []})
    blocks, _, _ = scan_checklist(TOOL.build_checklist(source, input_meta()))
    assert blocks["events[0].title"] == payload
    assert blocks["events[0].summary"] == payload


@pytest.mark.parametrize("payload", HOSTILE_PAYLOADS + BLANKISH_PAYLOADS)
def test_fence_primitive_never_loses_a_byte(payload: str) -> None:
    """T7: the fence primitive itself is lossless, blank payloads included."""
    block = TOOL.verbatim_block("events[0].summary", payload, "否")
    blocks, _, _ = scan_checklist(block)
    assert blocks["events[0].summary"] == payload


def test_hostile_payload_cannot_break_the_structure() -> None:
    """T8: a payload that mimics the checklist grammar stays one payload."""
    forged = "**events[0].title** — 逐字转录\n```text\n伪造块\n```"
    event = make_event("evt-20261023-forged", title=forged, summary=forged)
    source = make_source([event])
    blocks, _, order = scan_checklist(TOOL.build_checklist(source, input_meta()))
    assert blocks["events[0].title"] == forged
    assert blocks["events[0].summary"] == forged
    assert "events[0].title" in blocks
    assert len(order) == len(set(order)), "a forged block was parsed separately"


def test_knowledge_bite_references_are_listed_and_dangling_is_registered() -> None:
    """T9: KB → Event references are shown; a dangling one is registered."""
    source = load_fixture()
    text = render_fixture(source)
    assert "evt-20261023-fixture-does-not-exist" in text
    assert "悬空引用" in text
    assert "DANGLING_REFERENCE" in text
    # A valid reference is shown as valid.
    assert "evt-20261023-fixture-tab1-basic` | 有效 |" in text


def test_no_verdict_is_ever_written() -> None:
    """T10: the tool states facts about coverage, never about correctness."""
    source = load_fixture()
    text = render_fixture(source)
    assert "不构成事实验证" in text
    # The notice itself has to name the thing it is not doing; the rest of
    # the checklist must never contain a verdict word.
    body = text.split("\n", 2)[2]
    for word in FORBIDDEN_VERDICT_WORDS:
        assert word not in body, f"forbidden verdict word in output: {word}"
    # Every checklist row carries the one allowed status.
    statuses = set(re.findall(r"\| `(NOT_REVIEWED|VERIFIED|REVIEWED|OK)` \|", text))
    assert statuses == {ALLOWED_REVIEW_STATUS}
    # The confidence values shown are only the ones the input declares.
    input_confidences = {
        event["confidence"] for event in source["events"]
    } | {
        bite.get("confidence") for bite in source["knowledge_bites"]
    }
    for value in re.findall(r"\.confidence`: `([A-Z\-]+)`", text):
        assert value in input_confidences


def test_output_is_deterministic() -> None:
    """T11: the same input always produces the same bytes."""
    source = load_fixture()
    first = TOOL.build_checklist(source, input_meta())
    second = TOOL.build_checklist(copy.deepcopy(source), input_meta())
    assert first.encode("utf-8") == second.encode("utf-8")
    assert hashlib.sha256(first.encode("utf-8")).hexdigest() == (
        hashlib.sha256(second.encode("utf-8")).hexdigest()
    )


def test_output_carries_no_timestamp_or_path() -> None:
    """T11: no run time, no absolute path, no host name in the output."""
    text = render_fixture()
    assert str(ROOT) not in text
    assert not re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", text)


def test_open_event_without_follow_up_is_not_rendered_in_tab5() -> None:
    """T-A: an open event without a plan entry does not reach Tab 5."""
    open_event = make_event(
        "evt-20261023-open-unplanned",
        status="open",
        verification_criteria="待核实",
    )
    source = make_source([open_event])
    render_map = TOOL.derive_render_map(source)
    assert open_event["event_id"] not in render_map["positions"]
    kinds = {anomaly["kind"] for anomaly in render_map["anomalies"]}
    assert "FOLLOW_UP_MISSING" in kinds

    text = TOOL.build_checklist(source, input_meta())
    blocks, _, _ = scan_checklist(text)
    assert "events[0].title" in blocks, "the event is still transcribed"
    assert "FOLLOW_UP_MISSING" in text
    assert "未渲染" in text


def test_follow_up_plan_references_are_checked() -> None:
    """T-A: dangling and invalid follow-up references are registered."""
    good = make_event("evt-20261023-tracked", status="open", verification_criteria="c")
    source = make_source(
        [good],
        follow_up_plan=[
            {"event_id": "evt-20261023-tracked", "action": "a", "next_check": "2026-10-30"},
            {"event_id": "evt-20261023-missing", "action": "a", "next_check": "2026-10-30"},
        ],
    )
    render_map = TOOL.derive_render_map(source)
    kinds = {anomaly["kind"] for anomaly in render_map["anomalies"]}
    assert "DANGLING_REFERENCE" in kinds


# --------------------------------------------------------------------------
# CLI behaviour
# --------------------------------------------------------------------------


def _run_cli(args: List[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )


def test_cli_writes_a_checklist(tmp_path: Path) -> None:
    """X3: the CLI produces a checklist and exits 0."""
    out = tmp_path / "review.md"
    result = _run_cli(["--input", str(FIXTURE), "--out", str(out)], tmp_path)
    assert result.returncode == 0, result.stderr
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert "Research Input Fidelity Review" in text
    assert "不构成事实验证" in text


def test_cli_is_deterministic_across_runs(tmp_path: Path) -> None:
    """T11 at CLI level: two runs produce identical bytes."""
    first = tmp_path / "a.md"
    second = tmp_path / "b.md"
    for target in (first, second):
        result = _run_cli(["--input", str(FIXTURE), "--out", str(target)], tmp_path)
        assert result.returncode == 0, result.stderr
    assert first.read_bytes() == second.read_bytes()


def test_cli_does_not_modify_the_input(tmp_path: Path) -> None:
    """T12: the input file is never written to."""
    source_copy = tmp_path / "input.json"
    source_copy.write_bytes(FIXTURE.read_bytes())
    before = hashlib.sha256(source_copy.read_bytes()).hexdigest()
    result = _run_cli(
        ["--input", str(source_copy), "--out", str(tmp_path / "review.md")], tmp_path
    )
    assert result.returncode == 0, result.stderr
    after = hashlib.sha256(source_copy.read_bytes()).hexdigest()
    assert before == after


def test_cli_exit_code_2_for_missing_input(tmp_path: Path) -> None:
    """T13: a missing input is an input problem (exit 2), no file produced."""
    out = tmp_path / "review.md"
    result = _run_cli(["--input", str(tmp_path / "nope.json"), "--out", str(out)], tmp_path)
    assert result.returncode == 2
    assert not out.exists()


def test_cli_exit_code_2_for_invalid_json(tmp_path: Path) -> None:
    """T13: invalid JSON is an input problem (exit 2), no file produced."""
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    out = tmp_path / "review.md"
    result = _run_cli(["--input", str(bad), "--out", str(out)], tmp_path)
    assert result.returncode == 2
    assert not out.exists()


def test_cli_exit_code_4_for_contract_violation(tmp_path: Path) -> None:
    """T13: a contract violation exits 4 and produces no file."""
    source = make_source([make_event("not-an-event-id")])
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(source, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "review.md"
    result = _run_cli(["--input", str(bad), "--out", str(out)], tmp_path)
    assert result.returncode == 4
    assert not out.exists()
    assert "contract violation" in result.stderr


def test_cli_default_output_name_uses_data_date(tmp_path: Path) -> None:
    """D5: the default file name is derived from data_date."""
    source = make_source([make_event("evt-20261023-named")])
    path = tmp_path / "input.json"
    path.write_text(json.dumps(source, ensure_ascii=False), encoding="utf-8")
    result = _run_cli(["--input", str(path)], tmp_path)
    assert result.returncode == 0, result.stderr
    expected = tmp_path / "output" / "input-fidelity-review-2026-10-23.md"
    assert expected.is_file()


# --------------------------------------------------------------------------
# X-series: cross-validation against the existing pipeline
# --------------------------------------------------------------------------


def _pipeline_renderable_fixture() -> Dict[str, Any]:
    """The fixture without the dangling KB reference.

    ``build_document`` rejects a Knowledge Bite that points at an unknown
    event (DV-2). The dangling reference is deliberately part of the fixture
    for the fidelity tests; the cross-validation needs a document the
    pipeline actually accepts, so the dangling id is dropped here.
    """
    source = load_fixture()
    source["knowledge_bites"][1]["event_ids"] = [
        "evt-20261023-fixture-tab5-tracked"
    ]
    return source


#: Tab key -> the label the tool prints.
TAB_LABELS = {
    "highlights": "Tab 1",
    "market_snapshot": "Tab 2",
    "impact_analysis": "Tab 3",
    "knowledge_bite": "Tab 4",
    "follow_up": "Tab 5",
}


def test_render_status_matches_the_real_pipeline() -> None:
    """X1: the derived render position equals the pipeline's own output."""
    from daily_briefing.pipeline import build_document

    source = _pipeline_renderable_fixture()
    document = build_document(source)
    actual: Dict[str, List[str]] = {}
    for tab_key, tab in document["tabs"].items():
        for item in tab["items"]:
            event_id = item.get("event_id")
            if event_id:
                actual.setdefault(event_id, []).append(TAB_LABELS[tab_key])

    render_map = TOOL.derive_render_map(source)
    derived = {
        event_id: sorted(slot["tab"] for slot in slots)
        for event_id, slots in render_map["positions"].items()
    }
    expected = {
        event_id: sorted(tabs) for event_id, tabs in actual.items()
    }
    assert derived == expected
    # Four of the six fixture events render; the unselected fact and the
    # hypothesis reach no tab at all.
    assert len(derived) == 4
    assert len(source["events"]) - len(derived) == 2


def test_field_visibility_matches_the_real_renderer() -> None:
    """X2: a field marked as rendered really reaches a tab item."""
    from daily_briefing.pipeline import build_document

    source = _pipeline_renderable_fixture()
    document = build_document(source)
    render_map = TOOL.derive_render_map(source)
    checked = 0
    for event in source["events"]:
        slots = render_map["positions"].get(event["event_id"], [])
        visibility = TOOL.event_field_visibility(event, slots)
        for tab_key, tab in document["tabs"].items():
            for item in tab["items"]:
                if item.get("event_id") != event["event_id"]:
                    continue
                checked += 1
                text = item.get("text")
                if text is None:
                    # Tab 5 carries action / next_check, never a title or a
                    # summary.
                    assert "title" not in item and "summary" not in item
                    continue
                if visibility["title"] == "Tab 1":
                    assert tab_key == "highlights"
                    assert event["title"] in text
                else:
                    assert event["title"] not in text
                if visibility["summary"] in ("Tab 1", "Tab 3"):
                    assert event["summary"] in text
                else:
                    assert event["summary"] not in text
    assert checked > 0


def test_pipeline_rejects_the_dangling_knowledge_bite_reference() -> None:
    """X1 (negative): the dangling reference is a real contract conflict."""
    from contracts.evidence import ContractError
    from daily_briefing.pipeline import build_document

    with pytest.raises(ContractError):
        build_document(load_fixture())
