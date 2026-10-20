"""Daily Briefing V2 (Slice 1) — five-tab HTML renderer.

Pure standard library. Produces a single self-contained HTML file: no external
CSS, JS, fonts or network calls, so the report stays readable offline and can
be archived as-is.

Visual constants below are inlined on purpose. REPORT_DESIGN.md requires the
generator to consult ``~/.workbuddy/frameworks/VISUAL_IDENTITY_ENGINE.md``,
which lives outside the repository and therefore does not travel with Git.
Inlining keeps rendering deterministic across machines and agents; the source
document and section are cited next to each value.

Frozen references:
  - docs/core/REPORT_DESIGN.md        title form, tab heading form, evidence marks
  - docs/daily/product.md             tab names and responsibilities
  - docs/evidence/EVIDENCE_LAYER.md   confidence standard, missing-data wording
  - docs/daily/workflow.md            quality gates
"""

from __future__ import annotations

import html
from string import Template
from typing import Any, Dict, List

from .schema import (
    CONFIDENCE_BADGE,
    ESTIMATED_LABEL,
    MOCK_BANNER,
    PROVIDER_TIERS,
    REAL_MODE_BANNER,
    TAB_DEFS,
    TAB_ORDER,
    UNAVAILABLE_LABEL,
    WORD_LIMIT,
    WordLimitExceeded,
    count_tab_words,
    get_fallback_chain,
    validate,
)

# --------------------------------------------------------------------------
# Visual identity (inlined from VISUAL_IDENTITY_ENGINE.md §三 色板规则;
# dark-theme-first and card-grid layout per user preference)
# --------------------------------------------------------------------------
PALETTE = {
    "bg": "#0f1117",          # page background
    "surface": "#171a23",     # card surface
    "surface_alt": "#1e222d",  # nested surface / header
    "border": "#2a2f3d",
    "text": "#e7e9ee",
    "muted": "#98a1b3",
    "brand_purple": "#6c5ce7",
    "brand_blue": "#2d7ff9",
    "brand_gold": "#d4a94e",
    "danger": "#e05252",
}
CONFIDENCE_COLOR = {
    "HIGH": "#2ecc71",
    "MEDIUM": "#f1c40f",
    "LOW-MEDIUM": "#e67e22",
    "LOW": "#e74c3c",
}


def _esc(value: Any) -> str:
    """Escape all user-supplied text (defends against HTML injection)."""
    return html.escape("" if value is None else str(value), quote=True)


def _source_line(item: Dict[str, Any]) -> str:
    """Build the source annotation for one available item.

    The fallback suffix is rendered only when ``routing`` evidences that a
    higher-priority provider was tried and did not succeed. A bare P1/P2/P3
    tier never implies a P0 failure.
    """
    source = item["source"]
    line = f"Source: {source['name']} ({source['provider_tier']}"
    chain = get_fallback_chain(item)
    if chain:
        failed = ", ".join(
            f"{c['tier']} {c['provider']} {c['outcome']}" for c in chain
        )
        line += f", fallback from {failed}"
    line += ")"
    return line


def _badges(item: Dict[str, Any]) -> str:
    confidence = item["confidence"]
    parts = [
        f'<span class="badge" style="--badge:{CONFIDENCE_COLOR[confidence]}" '
        f'data-confidence="{_esc(confidence)}">'
        f"{CONFIDENCE_BADGE[confidence]} {_esc(confidence)}</span>"
    ]
    if item.get("estimated", False):
        parts.append(
            f'<span class="badge badge-est" data-estimated="true">'
            f"{_esc(ESTIMATED_LABEL)}</span>"
        )
    return "".join(parts)


def _render_item(item: Dict[str, Any], tab_key: str) -> str:
    """Render one card. Missing data is stated explicitly, never faked."""
    if item["availability"] == "unavailable":
        return (
            '<article class="card card-missing" data-availability="unavailable">'
            f'<p class="missing-label">{_esc(UNAVAILABLE_LABEL)}</p>'
            f'<p class="missing-reason">{_esc(item["unavailable_reason"])}</p>'
            "</article>"
        )

    body: List[str] = []
    for field in TAB_DEFS[tab_key]["content_fields"]:
        value = item.get(field)
        if value:
            css = "bite-unit" if field == "cognitive_unit" else "bite-why"
            body.append(f'<p class="{css}">{_esc(value)}</p>')

    extra: List[str] = []
    if tab_key == "follow_up" and item.get("next_check"):
        extra.append(
            f'<p class="meta-line"><span class="meta-key">下次检查</span>'
            f'{_esc(item["next_check"])}</p>'
        )
    if tab_key == "follow_up" and item.get("linked_theme"):
        extra.append(
            f'<p class="meta-line"><span class="meta-key">衔接主题</span>'
            f'{_esc(item["linked_theme"])}</p>'
        )

    return (
        f'<article class="card" data-availability="available">'
        + "".join(body)
        + "".join(extra)
        + f'<footer class="card-meta">{_badges(item)}'
        + f'<span class="src" title="{_esc(item["source"]["locator"])}">'
        + f'{_esc(_source_line(item))}</span></footer>'
        + "</article>"
    )


def _render_tab(tab_key: str, tab: Dict[str, Any], is_first: bool = False) -> str:
    definition = TAB_DEFS[tab_key]
    items = tab["items"]
    if items:
        cards = "".join(_render_item(i, tab_key) for i in items)
    else:
        cards = (
            f'<article class="card card-missing">'
            f'<p class="missing-label">{_esc(UNAVAILABLE_LABEL)}</p>'
            f'<p class="missing-reason">本 Tab 未提供任何条目</p>'
            "</article>"
        )
    # The first panel ships visible so the report is still readable when
    # scripting is unavailable; JavaScript takes over from there.
    hidden = "" if is_first else " hidden"
    return (
        f'<section class="tab-panel" id="tab-{_esc(tab_key)}" '
        f'data-tab="{_esc(tab_key)}" role="tabpanel" '
        f'aria-labelledby="tabbtn-{_esc(tab_key)}"{hidden}>'
        f'<h2 class="tab-title">Tab {definition["number"]}: '
        f'{_esc(definition["question"])}</h2>'
        f'<p class="tab-name">{_esc(definition["name"])}</p>'
        f'<div class="grid">{cards}</div>'
        "</section>"
    )


def _collect_tiers(document: Dict[str, Any]) -> List[str]:
    used = []
    for tab_key in TAB_ORDER:
        for item in document["tabs"][tab_key]["items"]:
            if item.get("availability") == "available":
                tier = item["source"]["provider_tier"]
                if tier not in used:
                    used.append(tier)
    return used


def _render_footer(document: Dict[str, Any]) -> str:
    methods = "".join(
        f"<li>{_esc(m)}</li>" for m in document["methodology"]["methods"]
    )
    limits = "".join(
        f"<li>{_esc(m)}</li>" for m in document["methodology"]["limitations"]
    )
    used = _collect_tiers(document)
    chain = " → ".join(PROVIDER_TIERS)
    used_text = ", ".join(used) if used else "无（全部数据不可用）"
    mode = document["meta"]["data_mode"]
    provenance_line = (
        "本报告由 Mock 演示数据生成，未接入真实数据源"
        "（无实时行情 / 新闻 / 宏观采集）"
        if mode == "mock"
        else "本报告输入声明 data_mode=real；Slice 1 未接入任何真实数据源，"
        "数据真实性由输入方负责，系统未做核验"
    )

    return (
        '<footer class="report-footer">'
        '<section class="footer-block">'
        "<h3>Methodology — 使用的方法</h3>"
        f"<ul>{methods}</ul>"
        "</section>"
        '<section class="footer-block">'
        "<h3>Methodology — 适用条件与局限</h3>"
        f"<ul>{limits}</ul>"
        "</section>"
        '<section class="footer-block">'
        "<h3>Provider Routing Chain — 路由透明记录</h3>"
        f'<p class="mono">路由链：{_esc(chain)}</p>'
        f'<p class="mono">本报告实际使用：{_esc(used_text)}</p>'
        "<p class=\"mono note\">仅当输入中存在真实回退记录时才渲染 fallback 标注；"
        "provider_tier 为 P1/P2/P3 本身不构成 P0 失败的证据。</p>"
        "</section>"
        '<section class="footer-block">'
        "<h3>Slice 1 范围声明</h3>"
        "<ul>"
        f"<li>{_esc(provenance_line)}</li>"
        "<li>未实现自动交叉验证，Evidence 验证机制（BACKLOG P0-003）<strong>尚未完成</strong></li>"
        "<li>可信度徽章仅反映输入数据自带标注，不代表本系统已验证该结论</li>"
        "<li><code>data_mode=real</code> 仅描述数据来源，<strong>不等于已验证（NOT VERIFIED）</strong>；"
        "四级 Confidence 定义未因本 Slice 发生任何改变</li>"
        "</ul>"
        "</section>"
        "</footer>"
    )


_CSS_TEMPLATE = Template(
    """
:root{--bg:$bg;--surface:$surface;--surface-alt:$surface_alt;--border:$border;
--text:$text;--muted:$muted;--purple:$brand_purple;--blue:$brand_blue;--gold:$brand_gold;
--danger:$danger;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB",
"Microsoft YaHei",sans-serif;line-height:1.6}
.wrap{max-width:1180px;margin:0 auto;padding:28px 20px 64px}
header.rhead{background:var(--surface-alt);border:1px solid var(--border);
border-radius:14px;padding:22px 24px;margin-bottom:20px}
.rhead h1{margin:0 0 6px;font-size:26px;letter-spacing:.2px}
.rhead .sub{color:var(--muted);font-size:14px;margin:0}
.banner{margin:0 0 18px;padding:12px 16px;border-radius:10px;font-weight:600;
font-size:14px;border:1px solid var(--gold);
background:rgba(212,169,78,.12);color:var(--gold)}
.banner-real{border-color:var(--blue);background:rgba(45,127,249,.12);color:var(--blue)}
.tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px}
.tabs button{appearance:none;cursor:pointer;font:inherit;font-size:14px;
color:var(--muted);background:var(--surface);border:1px solid var(--border);
border-radius:999px;padding:9px 16px;transition:all .15s ease}
.tabs button:hover{color:var(--text);border-color:var(--blue)}
.tabs button[aria-selected="true"]{color:#fff;border-color:var(--purple);
background:linear-gradient(135deg,var(--purple),var(--blue))}
.tab-title{margin:0 0 2px;font-size:20px}
.tab-name{margin:0 0 16px;color:var(--muted);font-size:13px;letter-spacing:.08em;
text-transform:uppercase}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:14px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;
padding:16px 18px}
.card-missing{border-style:dashed;border-color:var(--danger);
background:rgba(224,82,82,.06)}
.bite-unit{margin:0 0 8px;font-weight:600;font-size:16px}
.bite-why{margin:0;color:var(--muted);font-size:14px}
.meta-line{margin:6px 0 0;font-size:13px;color:var(--muted)}
.meta-key{display:inline-block;min-width:72px;color:var(--gold);font-size:12px}
.card-meta{margin-top:12px;padding-top:10px;border-top:1px solid var(--border);
display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.badge{font-size:12px;font-weight:600;padding:2px 9px;border-radius:999px;
color:#0f1117;background:var(--badge,#888)}
.badge-est{background:var(--gold);color:#0f1117}
.src{font-size:12px;color:var(--muted);margin-left:auto}
.missing-label{margin:0 0 6px;font-weight:700;color:var(--danger)}
.missing-reason{margin:0;font-size:14px;color:var(--muted)}
.report-footer{margin-top:28px;display:grid;gap:14px}
.footer-block{background:var(--surface);border:1px solid var(--border);
border-radius:12px;padding:16px 18px}
.footer-block h3{margin:0 0 8px;font-size:15px;color:var(--gold)}
.footer-block ul{margin:0;padding-left:20px;font-size:14px;color:var(--muted)}
.footer-block li{margin:3px 0}
.mono{margin:4px 0;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
font-size:13px;color:var(--muted)}
.note{font-size:12px;opacity:.85}
"""
)

_CSS = _CSS_TEMPLATE.safe_substitute(**PALETTE)

_JS = """
(function(){
  var btns = Array.prototype.slice.call(document.querySelectorAll('.tabs button'));
  var panels = Array.prototype.slice.call(document.querySelectorAll('.tab-panel'));
  function select(i){
    btns.forEach(function(b,j){ b.setAttribute('aria-selected', String(i===j)); });
    panels.forEach(function(p,j){ p.hidden = (i!==j); });
  }
  btns.forEach(function(b,i){
    b.addEventListener('click', function(){ select(i); });
    b.addEventListener('keydown', function(e){
      if(e.key!=='ArrowRight' && e.key!=='ArrowLeft') return;
      e.preventDefault();
      var n = (i + (e.key==='ArrowRight' ? 1 : btns.length-1)) % btns.length;
      btns[n].focus(); select(n);
    });
  });
  select(0);
})();
"""


def render(document: Dict[str, Any]) -> str:
    """Render a validated briefing document into five-tab HTML.

    The 500-word budget is a mandatory quality gate and is always enforced;
    there is deliberately no bypass switch. An over-budget tab raises
    :class:`WordLimitExceeded` and no output is produced.

    Args:
        document: briefing document; validated here as a safety net.

    Raises:
        ContractError: input violates the frozen contract.
        WordLimitExceeded: a tab exceeds the 500-word budget.
    """
    doc = validate(document)

    for tab_key in TAB_ORDER:
        count = count_tab_words(doc["tabs"][tab_key]["items"], tab_key)
        if count > WORD_LIMIT:
            raise WordLimitExceeded(tab_key, count)

    meta = doc["meta"]
    data_mode = meta["data_mode"]
    if data_mode == "mock":
        banner = (
            f'<p class="banner banner-mock" role="alert" '
            f'data-banner="mock">{_esc(MOCK_BANNER)}</p>'
        )
    else:
        # data_mode="real" states provenance only. Slice 1 has no verification
        # mechanism, so the report must say so out loud.
        banner = (
            f'<p class="banner banner-real" role="alert" '
            f'data-banner="unverified-evidence">{_esc(REAL_MODE_BANNER)}</p>'
        )

    buttons = "".join(
        f'<button type="button" role="tab" id="tabbtn-{_esc(key)}" '
        f'aria-controls="tab-{_esc(key)}" aria-selected="false">'
        f"{TAB_DEFS[key]['number']}. {_esc(TAB_DEFS[key]['name'])}</button>"
        for key in TAB_ORDER
    )
    panels = "".join(
        _render_tab(k, doc["tabs"][k], is_first=(i == 0))
        for i, k in enumerate(TAB_ORDER)
    )

    return (
        "<!DOCTYPE html>"
        f'<html lang="zh-CN"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="data-mode" content="{_esc(meta["data_mode"])}">'
        f'<title>Daily Briefing — {_esc(meta["data_date"])}</title>'
        f"<style>{_CSS}</style></head><body><div class=\"wrap\">"
        f'<header class="rhead"><h1>Daily Briefing — {_esc(meta["data_date"])}</h1>'
        f'<p class="sub">Run Date: {_esc(meta["run_date"])} ｜ '
        f'Data Date: {_esc(meta["data_date"])} ｜ '
        f'Data Mode: {_esc(meta["data_mode"].upper())}</p></header>'
        f"{banner}"
        f'<div class="tabs" role="tablist">{buttons}</div>'
        f"{panels}"
        f"{_render_footer(doc)}"
        f"</div><script>{_JS}</script></body></html>"
    )


__all__ = ["render", "PALETTE", "CONFIDENCE_COLOR"]
