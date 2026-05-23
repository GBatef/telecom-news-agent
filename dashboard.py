"""
dashboard.py - Modern SaaS Analytics Dashboard
Global Telecom Operators News AI Agent

Run with:  streamlit run dashboard.py
"""

import sys
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

# Load .env before anything else
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ─────────────────────────────────────────────
#  Page config  (must be FIRST Streamlit call)
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="TelecomPulse · AI News Intelligence",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  Design tokens & CSS
# ─────────────────────────────────────────────

# Palette
C = {
    "bg":        "#07090f",
    "surface":   "#0d1117",
    "card":      "#111827",
    "card_alt":  "#131c2e",
    "border":    "#1e2d45",
    "border2":   "#263045",
    "accent":    "#3b82f6",
    "accent2":   "#6366f1",
    "accent3":   "#0ea5e9",
    "gold":      "#f59e0b",
    "green":     "#10b981",
    "red":       "#ef4444",
    "gray":      "#6b7280",
    "text":      "#f1f5f9",
    "text2":     "#94a3b8",
    "text3":     "#64748b",
}

CUSTOM_CSS = f"""
<style>
/* ── Google Font ────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & base ───────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; }}
html, body, .stApp {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: {C["bg"]} !important;
    color: {C["text"]} !important;
}}

/* ── Hide Streamlit chrome ──────────────────── */
#MainMenu, footer {{ visibility: hidden; }}

/* Keep header visible but blend it with our theme so the sidebar toggle works */
header {{
    background: {C["bg"]} !important;
    border-bottom: 1px solid {C["border"]} !important;
    box-shadow: none !important;
}}

/* Hide toolbar items we don't need (deploy button, share, etc.) */
[data-testid="stToolbarActions"] {{ visibility: hidden; }}

.block-container {{ padding: 0.5rem 2rem 3rem !important; max-width: 1600px !important; }}

/* ── Sidebar ────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: {C["surface"]} !important;
    border-right: 1px solid {C["border"]} !important;
}}
[data-testid="stSidebar"] .stButton > button {{
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.875rem;
    transition: all 0.2s ease;
}}
[data-testid="stSidebar"] label {{
    color: {C["text2"]} !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
}}

/* ── Primary button (Run Now) ───────────────── */
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {C["accent"]}, {C["accent2"]}) !important;
    border: none !important;
    color: #fff !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
    box-shadow: 0 4px 15px rgba(59,130,246,0.35) !important;
    transition: all 0.25s ease !important;
}}
.stButton > button[kind="primary"]:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(59,130,246,0.5) !important;
}}

/* ── Metrics ─────────────────────────────────── */
[data-testid="stMetric"] {{
    background: {C["card"]} !important;
    border: 1px solid {C["border"]} !important;
    border-radius: 12px !important;
    padding: 18px 22px !important;
    transition: border-color 0.2s ease;
}}
[data-testid="stMetric"]:hover {{ border-color: {C["accent"]} !important; }}
[data-testid="stMetricValue"] {{
    color: {C["text"]} !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}}
[data-testid="stMetricLabel"] {{
    color: {C["text3"]} !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}}
[data-testid="stMetricDelta"] {{ font-size: 0.82rem !important; }}

/* ── Tabs ────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {{
    background: {C["card"]} !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid {C["border"]} !important;
    gap: 2px !important;
}}
[data-testid="stTabs"] [role="tab"] {{
    border-radius: 7px !important;
    color: {C["text3"]} !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 8px 16px !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
    background: {C["accent"]} !important;
    color: #fff !important;
    font-weight: 600 !important;
}}

/* ── Expander ────────────────────────────────── */
[data-testid="stExpander"] {{
    background: {C["card"]} !important;
    border: 1px solid {C["border"]} !important;
    border-radius: 10px !important;
    margin-bottom: 6px !important;
}}
[data-testid="stExpander"] summary {{
    color: {C["text"]} !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}}

/* ── Dataframe ───────────────────────────────── */
[data-testid="stDataFrame"] {{ border-radius: 10px !important; overflow: hidden !important; }}

/* ── Selectbox / Multiselect ─────────────────── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {{
    background: {C["card_alt"]} !important;
    border-color: {C["border"]} !important;
    border-radius: 8px !important;
    color: {C["text"]} !important;
}}

/* ── Status widget ───────────────────────────── */
[data-testid="stStatus"] {{
    background: {C["card"]} !important;
    border: 1px solid {C["border2"]} !important;
    border-radius: 10px !important;
}}

/* ── Divider ─────────────────────────────────── */
hr {{ border-color: {C["border"]} !important; margin: 1rem 0 !important; }}

/* ──────────────────────────────────────────────
   CUSTOM COMPONENT CLASSES
   ────────────────────────────────────────────── */

/* Top header bar */
.tp-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 0 20px;
    border-bottom: 1px solid {C["border"]};
    margin-bottom: 24px;
}}
.tp-logo {{
    display: flex;
    align-items: center;
    gap: 12px;
}}
.tp-logo-icon {{
    width: 40px; height: 40px;
    background: linear-gradient(135deg, {C["accent"]}, {C["accent2"]});
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3em;
}}
.tp-logo-text h1 {{
    margin: 0;
    font-size: 1.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, {C["text"]}, {C["accent"]});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
}}
.tp-logo-text p {{
    margin: 0;
    font-size: 0.75rem;
    color: {C["text3"]};
    font-weight: 400;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}}
.tp-status-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.3);
    color: {C["green"]};
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.78rem;
    font-weight: 600;
}}
.tp-status-dot {{
    width: 7px; height: 7px;
    border-radius: 50%;
    background: {C["green"]};
    animation: pulse 2s infinite;
}}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.6; transform: scale(0.85); }}
}}

/* Section label */
.tp-section-label {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 28px 0 16px;
}}
.tp-section-label .line {{
    flex: 1;
    height: 1px;
    background: {C["border"]};
}}
.tp-section-label span {{
    font-size: 0.72rem;
    font-weight: 700;
    color: {C["text3"]};
    letter-spacing: 0.12em;
    text-transform: uppercase;
    white-space: nowrap;
}}

/* Highlight / Feature card */
.tp-highlight {{
    background: linear-gradient(135deg, {C["card_alt"]}, {C["card"]});
    border: 1px solid {C["accent"]};
    border-radius: 14px;
    padding: 22px 26px;
    margin: 0 0 24px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 40px rgba(59,130,246,0.08);
}}
.tp-highlight::before {{
    content: '';
    position: absolute; top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, {C["accent"]}, {C["accent2"]}, {C["accent3"]});
}}
.tp-highlight-badge {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(245,158,11,0.15);
    border: 1px solid rgba(245,158,11,0.4);
    color: {C["gold"]};
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 10px;
}}
.tp-highlight-title {{
    font-size: 1.15rem;
    font-weight: 700;
    color: {C["text"]};
    margin: 0 0 8px;
    line-height: 1.4;
}}
.tp-highlight-title a {{
    color: {C["text"]};
    text-decoration: none;
    transition: color 0.2s;
}}
.tp-highlight-title a:hover {{ color: {C["accent3"]}; }}
.tp-highlight-meta {{
    color: {C["text3"]};
    font-size: 0.82rem;
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
    margin-bottom: 10px;
}}
.tp-highlight-summary {{
    color: {C["text2"]};
    font-size: 0.88rem;
    line-height: 1.65;
    border-top: 1px solid {C["border"]};
    padding-top: 10px;
    margin-top: 8px;
}}

/* Article card */
.tp-article {{
    background: {C["card"]};
    border: 1px solid {C["border"]};
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
    transition: all 0.2s ease;
    position: relative;
}}
.tp-article:hover {{
    border-color: {C["accent"]};
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(59,130,246,0.1);
}}
.tp-article-title {{
    font-size: 0.95rem;
    font-weight: 600;
    color: {C["text"]};
    margin: 0 0 6px;
    line-height: 1.45;
}}
.tp-article-title a {{
    color: {C["text"]};
    text-decoration: none;
    transition: color 0.2s;
}}
.tp-article-title a:hover {{ color: {C["accent3"]}; }}
.tp-article-meta {{
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    margin: 5px 0 8px;
    font-size: 0.78rem;
    color: {C["text3"]};
}}
.tp-article-summary {{
    color: {C["text2"]};
    font-size: 0.82rem;
    line-height: 1.6;
    margin-top: 6px;
    border-top: 1px solid {C["border"]};
    padding-top: 8px;
}}

/* Score badge */
.tp-score {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.25);
    color: {C["accent3"]};
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-weight: 700;
}}
.tp-score-high {{
    background: rgba(245,158,11,0.12);
    border-color: rgba(245,158,11,0.3);
    color: {C["gold"]};
}}

/* Sentiment tags */
.tp-sent {{
    display: inline-flex;
    align-items: center;
    gap: 3px;
    border-radius: 20px;
    padding: 2px 9px;
    font-size: 0.72rem;
    font-weight: 600;
}}
.tp-sent-pos {{ background: rgba(16,185,129,0.12); color: {C["green"]}; border: 1px solid rgba(16,185,129,0.3); }}
.tp-sent-neg {{ background: rgba(239,68,68,0.12); color: {C["red"]}; border: 1px solid rgba(239,68,68,0.3); }}
.tp-sent-neu {{ background: rgba(107,114,128,0.12); color: {C["gray"]}; border: 1px solid rgba(107,114,128,0.25); }}

/* Category chip */
.tp-chip {{
    display: inline-block;
    background: {C["card_alt"]};
    border: 1px solid {C["border2"]};
    color: {C["text2"]};
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.7rem;
    font-weight: 500;
    margin: 2px 2px 2px 0;
}}

/* Company badge */
.tp-company {{
    display: inline-flex;
    align-items: center;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.25);
    color: #a5b4fc;
    border-radius: 6px;
    padding: 2px 9px;
    font-size: 0.72rem;
    font-weight: 600;
    margin: 2px 3px 2px 0;
}}

/* Region summary card */
.tp-region-summary {{
    background: {C["card"]};
    border: 1px solid {C["border"]};
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}
.tp-region-summary .stat {{
    text-align: center;
}}
.tp-region-summary .stat .val {{
    font-size: 1.4rem;
    font-weight: 700;
    color: {C["text"]};
}}
.tp-region-summary .stat .lbl {{
    font-size: 0.7rem;
    color: {C["text3"]};
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

/* Welcome screen */
.tp-welcome {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 20px 60px;
    text-align: center;
}}
.tp-welcome-icon {{
    width: 90px; height: 90px;
    background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(99,102,241,0.2));
    border: 1px solid {C["accent"]};
    border-radius: 22px;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.8em;
    margin-bottom: 28px;
    box-shadow: 0 0 40px rgba(59,130,246,0.15);
    animation: float 4s ease-in-out infinite;
}}
@keyframes float {{
    0%, 100% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-8px); }}
}}
.tp-welcome h2 {{
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, {C["text"]}, {C["accent"]});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 12px;
    letter-spacing: -0.03em;
}}
.tp-welcome p {{
    color: {C["text2"]};
    font-size: 1rem;
    max-width: 480px;
    line-height: 1.7;
    margin: 0 0 32px;
}}
.tp-feature-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    max-width: 640px;
    width: 100%;
    margin: 0 0 40px;
}}
.tp-feature-card {{
    background: {C["card"]};
    border: 1px solid {C["border"]};
    border-radius: 10px;
    padding: 14px;
    text-align: left;
}}
.tp-feature-card .icon {{ font-size: 1.5em; margin-bottom: 6px; }}
.tp-feature-card .title {{ font-size: 0.82rem; font-weight: 600; color: {C["text"]}; }}
.tp-feature-card .desc {{ font-size: 0.74rem; color: {C["text3"]}; margin-top: 3px; }}

/* Sidebar branding */
.sb-brand {{
    padding: 8px 0 16px;
    border-bottom: 1px solid {C["border"]};
    margin-bottom: 16px;
}}
.sb-brand h2 {{
    font-size: 1rem;
    font-weight: 800;
    color: {C["text"]};
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.sb-brand p {{
    font-size: 0.72rem;
    color: {C["text3"]};
    margin: 4px 0 0;
}}
.sb-section {{
    font-size: 0.68rem;
    font-weight: 700;
    color: {C["text3"]};
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 20px 0 8px;
}}
.sb-footer {{
    text-align: center;
    padding: 12px 0 4px;
    border-top: 1px solid {C["border"]};
    margin-top: 16px;
}}
.sb-footer p {{
    font-size: 0.7rem;
    color: {C["text3"]};
    margin: 3px 0;
}}

/* Progress bar override */
.stProgress > div > div {{ background: {C["accent"]} !important; }}

/* Chart container */
.tp-chart-card {{
    background: {C["card"]};
    border: 1px solid {C["border"]};
    border-radius: 12px;
    padding: 4px;
    margin: 0;
}}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────

REGION_ICONS = {
    "Middle East & Africa": "MEA",
    "Europe":               "EU",
    "Americas":             "AM",
    "Asia-Pacific":         "APAC",
    "Global":               "GL",
}

CHART_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor":  "rgba(0,0,0,0)",
    "font_color":    "#94a3b8",
    "font_family":   "Inter, sans-serif",
}

CHART_GRIDCOLOR  = "#1e2d45"
ACCENT_PALETTE   = ["#3b82f6", "#6366f1", "#0ea5e9", "#8b5cf6", "#06b6d4",
                    "#a78bfa", "#60a5fa", "#818cf8", "#38bdf8", "#c084fc"]
SENT_PALETTE     = {"positive": "#10b981", "negative": "#ef4444", "neutral": "#6b7280"}


# ─────────────────────────────────────────────
#  HTML helpers
# ─────────────────────────────────────────────

def _sent_tag(sent: str) -> str:
    cls = {"positive": "tp-sent-pos", "negative": "tp-sent-neg"}.get(sent, "tp-sent-neu")
    arrow = {"positive": "▲", "negative": "▼"}.get(sent, "●")
    return f'<span class="tp-sent {cls}">{arrow} {sent.capitalize()}</span>'


def _score_badge(score: float) -> str:
    cls = "tp-score-high" if score >= 7 else "tp-score"
    return f'<span class="{cls}">{score:.1f}</span>'


def _chip(text: str) -> str:
    return f'<span class="tp-chip">{text}</span>'


def _company_badge(name: str) -> str:
    return f'<span class="tp-company">{name}</span>'


def _cat_chips(cats: list) -> str:
    return "".join(_chip(c) for c in cats[:4])


def _article_card(art, idx: int) -> str:
    cats_html = _cat_chips(art.categories)
    sent_html = _sent_tag(art.sentiment)
    score_html = _score_badge(art.importance_score)
    companies_html = "".join(_company_badge(c) for c in art.companies_detected[:3])
    summary_block = (
        f'<div class="tp-article-summary">{art.summary}</div>'
        if art.summary else ""
    )
    pub_str = ""
    if art.published_at:
        try:
            pub_str = f'<span>{art.published_at.strftime("%b %d, %H:%M")}</span>'
        except Exception:
            pass

    return f"""
<div class="tp-article">
  <div class="tp-article-title">
    <a href="{art.url}" target="_blank">{idx}. {art.title}</a>
  </div>
  <div class="tp-article-meta">
    <span>{art.source_name}</span>
    {pub_str}
    {score_html}
    {sent_html}
  </div>
  <div style="margin:4px 0 2px">{companies_html}{cats_html}</div>
  {summary_block}
</div>
"""


def _highlight_card(art) -> str:
    sent_html = _sent_tag(art.sentiment)
    score_html = _score_badge(art.importance_score)
    companies_html = "".join(_company_badge(c) for c in art.companies_detected[:3])
    summary_block = (
        f'<div class="tp-highlight-summary">{art.summary}</div>'
        if art.summary else ""
    )
    return f"""
<div class="tp-highlight">
  <div class="tp-highlight-badge">HIGHLIGHT OF THE DAY</div>
  <div class="tp-highlight-title">
    <a href="{art.url}" target="_blank">{art.title}</a>
  </div>
  <div class="tp-highlight-meta">
    <span>{art.source_name}</span>
    {score_html}
    {sent_html}
    {companies_html}
  </div>
  {summary_block}
</div>
"""


def _section_label(text: str) -> str:
    return f"""
<div class="tp-section-label">
  <div class="line"></div>
  <span>{text}</span>
  <div class="line"></div>
</div>
"""


# ─────────────────────────────────────────────
#  Charts
# ─────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def chart_company_mentions(company_counts_items: tuple) -> go.Figure:
    """Horizontal bar — top companies by mentions."""
    data = dict(list(company_counts_items)[:15])
    df = pd.DataFrame({"Company": list(data.keys()), "Mentions": list(data.values())})
    df = df.sort_values("Mentions", ascending=True)

    fig = go.Figure(go.Bar(
        x=df["Mentions"],
        y=df["Company"],
        orientation="h",
        marker=dict(
            color=df["Mentions"],
            colorscale=[[0, "#1e3a5f"], [0.5, "#3b82f6"], [1, "#60a5fa"]],
            line=dict(width=0),
        ),
        text=df["Mentions"],
        textposition="outside",
        textfont=dict(color="#94a3b8", size=11),
    ))
    fig.update_layout(
        **CHART_THEME,
        title=dict(text="Top Companies", font=dict(size=13, color="#f1f5f9"), x=0),
        xaxis=dict(showgrid=True, gridcolor=CHART_GRIDCOLOR, zeroline=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=False, tickfont=dict(size=10)),
        margin=dict(l=0, r=40, t=40, b=0),
        height=280,
        bargap=0.3,
    )
    return fig


@st.cache_data(ttl=300, show_spinner=False)
def chart_categories(cat_counts_items: tuple) -> go.Figure:
    """Horizontal bar — category distribution (clean, no overlap)."""
    data = dict(cat_counts_items)
    # Sort ascending for horizontal bar readability
    sorted_items = sorted(data.items(), key=lambda x: x[1])
    labels = [k for k, v in sorted_items]
    values = [v for k, v in sorted_items]

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(
            color=values,
            colorscale=[[0, "#312e81"], [0.5, "#6366f1"], [1, "#a78bfa"]],
            line=dict(width=0),
        ),
        text=values,
        textposition="outside",
        textfont=dict(color="#94a3b8", size=11),
    ))
    fig.update_layout(
        **CHART_THEME,
        title=dict(text="Categories", font=dict(size=13, color="#f1f5f9"), x=0),
        xaxis=dict(showgrid=True, gridcolor=CHART_GRIDCOLOR, zeroline=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=False, tickfont=dict(size=10)),
        margin=dict(l=0, r=40, t=40, b=0),
        height=280,
        bargap=0.3,
    )
    return fig


@st.cache_data(ttl=300, show_spinner=False)
def chart_sentiment(pos: int, neg: int, neu: int) -> go.Figure:
    """Donut chart — sentiment split."""
    fig = go.Figure(go.Pie(
        labels=["Positive", "Negative", "Neutral"],
        values=[pos, neg, neu],
        hole=0.55,
        marker=dict(
            colors=[SENT_PALETTE["positive"], SENT_PALETTE["negative"], SENT_PALETTE["neutral"]],
            line=dict(color=C["bg"], width=2),
        ),
        textinfo="label+percent",
        textfont=dict(size=10, color="#94a3b8"),
        hovertemplate="<b>%{label}</b><br>%{value} articles (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        **CHART_THEME,
        title=dict(text="Sentiment", font=dict(size=13, color="#f1f5f9"), x=0),
        legend=dict(font=dict(size=9, color="#64748b"), orientation="v", x=1.0, y=0.5),
        margin=dict(l=0, r=0, t=40, b=0),
        height=280,
    )
    return fig


@st.cache_data(ttl=300, show_spinner=False)
def chart_regions(region_counts_items: tuple) -> go.Figure:
    """Vertical bar — articles by region."""
    data = dict(region_counts_items)
    regions = list(data.keys())
    counts = list(data.values())
    colors = ACCENT_PALETTE[:len(regions)]

    fig = go.Figure(go.Bar(
        x=regions,
        y=counts,
        marker=dict(color=colors, line=dict(width=0)),
        text=counts,
        textposition="outside",
        textfont=dict(color="#94a3b8", size=11),
    ))
    fig.update_layout(
        **CHART_THEME,
        title=dict(text="By Region", font=dict(size=13, color="#f1f5f9"), x=0),
        xaxis=dict(showgrid=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor=CHART_GRIDCOLOR, tickfont=dict(size=10)),
        margin=dict(l=0, r=20, t=40, b=0),
        height=280,
        bargap=0.35,
    )
    return fig


@st.cache_data(ttl=300, show_spinner=False)
def chart_score_distribution(scores_tuple: tuple) -> go.Figure:
    """Histogram — importance score distribution."""
    scores = list(scores_tuple)
    fig = go.Figure(go.Histogram(
        x=scores,
        nbinsx=20,
        marker=dict(
            color="#3b82f6",
            opacity=0.8,
            line=dict(color=C["bg"], width=1),
        ),
    ))
    fig.update_layout(
        **CHART_THEME,
        title=dict(text="Score Distribution", font=dict(size=13, color="#f1f5f9"), x=0),
        xaxis=dict(title="Importance Score", showgrid=True, gridcolor=CHART_GRIDCOLOR, tickfont=dict(size=10)),
        yaxis=dict(title="Articles", showgrid=True, gridcolor=CHART_GRIDCOLOR, tickfont=dict(size=10)),
        margin=dict(l=0, r=10, t=40, b=40),
        height=220,
    )
    return fig


@st.cache_data(ttl=300, show_spinner=False)
def chart_timeline(dates_list: tuple) -> go.Figure:
    """Line chart — articles published per day."""
    if not dates_list:
        return go.Figure()
    df = pd.DataFrame({"date": list(dates_list)})
    df["date"] = pd.to_datetime(df["date"]).dt.date
    counts = df["date"].value_counts().sort_index()
    
    fig = go.Figure(go.Scatter(
        x=counts.index.astype(str),
        y=counts.values,
        mode="lines+markers",
        line=dict(color="#3b82f6", width=2.5),
        marker=dict(size=6, color="#60a5fa"),
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.08)",
    ))
    fig.update_layout(
        **CHART_THEME,
        title=dict(text="Publication Timeline", font=dict(size=13, color="#f1f5f9"), x=0),
        xaxis=dict(showgrid=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor=CHART_GRIDCOLOR, tickfont=dict(size=10)),
        margin=dict(l=0, r=10, t=40, b=40),
        height=220,
    )
    return fig


# ─────────────────────────────────────────────
#  Pipeline runner
# ─────────────────────────────────────────────

def run_pipeline_streamlit(
    source_names: Optional[List[str]],
    backend: str,
    enrich_content: bool,
) -> Optional[object]:
    """Run the full pipeline inside a Streamlit status widget."""
    import config as cfg
    cfg.SUMMARIZER_BACKEND = backend  # runtime override

    from scraper import scrape_all_sources
    from company_detector import assign_companies_to_article
    from categorizer import categorize_and_score
    from summarizer import batch_summarize
    from report_generator import ReportData, save_reports
    from config import NEWS_SOURCES

    sources = NEWS_SOURCES
    if source_names:
        names_lower = [n.lower() for n in source_names]
        sources = [s for s in NEWS_SOURCES if any(n in s.name.lower() for n in names_lower)]

    with st.status("Running pipeline…", expanded=True) as status:
        prog = st.progress(0, text="Initializing…")

        # Step 1
        prog.progress(10, text="Scraping news sources…")
        articles = scrape_all_sources(sources=sources, enrich_content=enrich_content)
        st.write(f"   Collected **{len(articles)}** raw articles")
        prog.progress(30, text="Detecting companies…")

        if not articles:
            status.update(label="No articles found. Check connectivity.", state="error")
            prog.empty()
            return None

        # Step 2
        for art in articles:
            assign_companies_to_article(art)
        matched = [a for a in articles if a.companies_detected] or articles
        st.write(f"   **{len(matched)}** articles matched to tracked companies")
        prog.progress(50, text="Categorizing & scoring…")

        # Step 3
        matched = categorize_and_score(matched)
        st.write(f"   After deduplication: **{len(matched)}** unique articles")
        prog.progress(70, text=f"Summarizing with {backend}…")

        # Step 4
        batch_summarize(matched)
        st.write("   Summaries generated")
        prog.progress(90, text="Saving reports…")

        # Step 5
        data = ReportData(matched, run_date=datetime.now())
        saved = save_reports(data)
        st.write(f"   Reports saved: {', '.join(saved.values())}")
        prog.progress(100, text="Done")

        status.update(
            label=f"Pipeline complete — {len(matched)} articles, {len(data.company_counts)} companies",
            state="complete",
        )

    return data


# ─────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        # Branding
        st.markdown("""
        <div class="sb-brand">
          <h2>TelecomPulse</h2>
          <p>AI News Intelligence Platform</p>
        </div>
        """, unsafe_allow_html=True)

        # Pipeline controls hidden — always use groq
        backend = "groq"
        enrich = False
        selected_sources = []

        st.markdown("")
        run_btn = st.button("Run Pipeline", use_container_width=True, type="primary")

        # ── Auto-refresh ──────────────────────────
        st.markdown('<div class="sb-section">AUTO REFRESH</div>', unsafe_allow_html=True)
        auto_refresh = st.checkbox("Enable auto-refresh", value=False)
        refresh_interval = 30
        if auto_refresh:
            refresh_interval = st.slider("Interval (seconds)", 15, 300, 60, step=15)

        # ── Historical reports ────────────────────
        st.markdown('<div class="sb-section">SAVED REPORTS</div>', unsafe_allow_html=True)
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        txt_files = sorted(report_dir.glob("telecom_operators_report_*.txt"), reverse=True)

        if txt_files:
            report_labels = [f.stem.replace("telecom_operators_report_", "") for f in txt_files]
            selected_idx = st.selectbox(
                "Load saved report",
                range(len(report_labels)),
                format_func=lambda i: report_labels[i],
            )
            load_btn = st.button("Load Report", use_container_width=True)
        else:
            st.caption("No saved reports yet. Run pipeline first.")
            load_btn = False
            selected_idx = None

        # ── Downloads ─────────────────────────────
        st.markdown('<div class="sb-section">EXPORT</div>', unsafe_allow_html=True)
        if "data" in st.session_state and st.session_state["data"]:
            data = st.session_state["data"]
            date_tag = data.date.strftime("%Y%m%d")
            txt_path  = report_dir / f"telecom_operators_report_{date_tag}.txt"
            html_path = report_dir / f"telecom_operators_report_{date_tag}.html"

            if txt_path.exists():
                st.download_button(
                    "Download TXT Report",
                    data=txt_path.read_text(encoding="utf-8"),
                    file_name=txt_path.name,
                    mime="text/plain",
                    use_container_width=True,
                )
            if html_path.exists():
                st.download_button(
                    "Download HTML Report",
                    data=html_path.read_bytes(),
                    file_name=html_path.name,
                    mime="text/html",
                    use_container_width=True,
                )
        else:
            st.caption("Run the pipeline to generate downloadable reports.")

        # ── Footer ────────────────────────────────
        st.markdown("""
        <div class="sb-footer">
          <p>Powered by Groq · Streamlit · Python</p>
          <p>37 operators · 4 regions</p>
        </div>
        """, unsafe_allow_html=True)

    return run_btn, load_btn, backend, enrich, selected_sources, txt_files, selected_idx, auto_refresh, refresh_interval


# ─────────────────────────────────────────────
#  KPI metrics row
# ─────────────────────────────────────────────

def render_kpi_row(data):
    from config import REGIONS
    articles = data.articles
    pos = sum(1 for a in articles if a.sentiment == "positive")
    neg = sum(1 for a in articles if a.sentiment == "negative")
    top_score = max((a.importance_score for a in articles), default=0)
    regions_active = len([r for r in REGIONS if r in data.by_region])
    avg_score = sum(a.importance_score for a in articles) / max(len(articles), 1)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Articles", len(articles), help="Total deduplicated articles")
    c2.metric("Companies", len(data.company_counts), help="Distinct companies mentioned")
    c3.metric("Active Regions", regions_active, help="Regions with coverage")
    c4.metric("Top Score", f"{top_score:.1f}", help="Highest importance score")
    c5.metric("Avg Score", f"{avg_score:.1f}", help="Average importance score")
    c6.metric("Positive / Negative", f"{pos} / {neg}", help="Positive vs Negative articles")


# ─────────────────────────────────────────────
#  Analytics charts row
# ─────────────────────────────────────────────

def render_charts_row(data):
    articles = data.articles
    pos = sum(1 for a in articles if a.sentiment == "positive")
    neg = sum(1 for a in articles if a.sentiment == "negative")
    neu = sum(1 for a in articles if a.sentiment == "neutral")

    # First row: 4 main charts
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="tp-chart-card">', unsafe_allow_html=True)
        st.plotly_chart(
            chart_company_mentions(tuple(data.company_counts.items())),
            use_container_width=True, config={"displayModeBar": False}
        )
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="tp-chart-card">', unsafe_allow_html=True)
        st.plotly_chart(
            chart_categories(tuple(data.cat_counts.items())),
            use_container_width=True, config={"displayModeBar": False}
        )
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="tp-chart-card">', unsafe_allow_html=True)
        st.plotly_chart(
            chart_sentiment(pos, neg, neu),
            use_container_width=True, config={"displayModeBar": False}
        )
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="tp-chart-card">', unsafe_allow_html=True)
        st.plotly_chart(
            chart_regions(tuple(data.region_counts.items())),
            use_container_width=True, config={"displayModeBar": False}
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Second row: score distribution + timeline
    c5, c6 = st.columns([1, 2])
    with c5:
        st.markdown('<div class="tp-chart-card">', unsafe_allow_html=True)
        scores = tuple(a.importance_score for a in articles)
        st.plotly_chart(
            chart_score_distribution(scores),
            use_container_width=True, config={"displayModeBar": False}
        )
        st.markdown('</div>', unsafe_allow_html=True)
    with c6:
        st.markdown('<div class="tp-chart-card">', unsafe_allow_html=True)
        dates = tuple(a.published_at for a in articles if a.published_at)
        st.plotly_chart(
            chart_timeline(dates),
            use_container_width=True, config={"displayModeBar": False}
        )
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Region tabs with article cards
# ─────────────────────────────────────────────

def render_region_tabs(data):
    from config import REGIONS

    tab_labels = [f"{REGION_ICONS.get(r, 'GL')}  {r}" for r in REGIONS]
    tabs = st.tabs(tab_labels)

    for tab, region in zip(tabs, REGIONS):
        with tab:
            companies_in_region = data.by_region.get(region, {})
            if not companies_in_region:
                st.markdown(f"""
                <div style="text-align:center;padding:40px;color:#64748b;">
                  <p style="font-size:0.9rem;font-weight:500">No articles for {region} in this report.</p>
                </div>
                """, unsafe_allow_html=True)
                continue

            total = sum(len(v) for v in companies_in_region.values())
            n_companies = len(companies_in_region)

            # Region summary banner
            st.markdown(f"""
            <div class="tp-region-summary">
              <div class="stat"><div class="val">{total}</div><div class="lbl">Articles</div></div>
              <div class="stat"><div class="val">{n_companies}</div><div class="lbl">Companies</div></div>
              <div class="stat"><div class="val">{REGION_ICONS.get(region,'GL')}</div><div class="lbl">{region}</div></div>
            </div>
            """, unsafe_allow_html=True)

            # Sort companies by article count desc
            sorted_companies = sorted(companies_in_region.items(), key=lambda x: len(x[1]), reverse=True)

            for cname, arts in sorted_companies:
                avg_score = sum(a.importance_score for a in arts) / max(len(arts), 1)
                with st.expander(
                    f"**{cname}** — {len(arts)} article(s) · avg score {avg_score:.1f}",
                    expanded=len(arts) >= 3,
                ):
                    # Sort articles by score desc
                    for i, art in enumerate(sorted(arts, key=lambda a: a.importance_score, reverse=True)[:10], 1):
                        st.markdown(_article_card(art, i), unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Full article table
# ─────────────────────────────────────────────

def render_article_table(data):
    articles = data.articles
    rows = []
    for art in sorted(articles, key=lambda a: a.importance_score, reverse=True):
        rows.append({
            "Title":       art.title[:90] + ("…" if len(art.title) > 90 else ""),
            "Company":     ", ".join(art.companies_detected[:2]) or "—",
            "Region":      art.region,
            "Source":      art.source_name,
            "Score":       art.importance_score,
            "Sentiment":   art.sentiment,
            "Category":    ", ".join(art.categories[:2]) or "—",
            "Published":   art.published_at.strftime("%Y-%m-%d") if art.published_at else "—",
            "URL":         art.url,
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        use_container_width=True,
        height=450,
        column_config={
            "URL":      st.column_config.LinkColumn("URL", display_text="Open →"),
            "Score":    st.column_config.NumberColumn("Score", format="%.1f"),
            "Sentiment": st.column_config.TextColumn("Sentiment"),
        },
    )


# ─────────────────────────────────────────────
#  Main dashboard render
# ─────────────────────────────────────────────

def render_dashboard(data):
    run_date_str = data.date.strftime("%A, %B %d, %Y · %H:%M")
    articles = data.articles

    # ── Header bar ────────────────────────────
    st.markdown(f"""
    <div class="tp-header">
      <div class="tp-logo">
        <div class="tp-logo-icon">TP</div>
        <div class="tp-logo-text">
          <h1>TelecomPulse</h1>
          <p>AI News Intelligence · {run_date_str}</p>
        </div>
      </div>
      <div class="tp-status-pill">
        <div class="tp-status-dot"></div>
        Live · {len(articles)} Articles
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI row ───────────────────────────────
    st.markdown(_section_label("KEY PERFORMANCE INDICATORS"), unsafe_allow_html=True)
    render_kpi_row(data)

    # ── Highlight ─────────────────────────────
    if data.highlight:
        st.markdown(_section_label("HIGHLIGHT OF THE DAY"), unsafe_allow_html=True)
        st.markdown(_highlight_card(data.highlight), unsafe_allow_html=True)

    # ── Charts ────────────────────────────────
    st.markdown(_section_label("ANALYTICS & INSIGHTS"), unsafe_allow_html=True)
    render_charts_row(data)

    # ── Region tabs ───────────────────────────
    st.markdown(_section_label("ARTICLES BY REGION"), unsafe_allow_html=True)
    render_region_tabs(data)

    # ── Full article table ────────────────────
    st.markdown(_section_label("FULL ARTICLE TABLE"), unsafe_allow_html=True)
    with st.expander(f"All {len(articles)} Articles (sortable)", expanded=False):
        # Sorting controls
        col_sort, col_filter = st.columns([2, 3])
        with col_sort:
            sort_by = st.selectbox(
                "Sort by",
                ["Score ↓", "Score ↑", "Sentiment", "Source", "Published ↓"],
                label_visibility="collapsed",
            )
        with col_filter:
            sent_filter = st.multiselect(
                "Filter sentiment",
                ["positive", "negative", "neutral"],
                default=[],
                label_visibility="collapsed",
                placeholder="Filter by sentiment…",
            )

        filtered = articles
        if sent_filter:
            filtered = [a for a in articles if a.sentiment in sent_filter]

        sort_map = {
            "Score ↓":    lambda a: -a.importance_score,
            "Score ↑":    lambda a:  a.importance_score,
            "Sentiment":  lambda a:  a.sentiment,
            "Source":     lambda a:  a.source_name,
            "Published ↓": lambda a: -(a.published_at.timestamp() if a.published_at else 0),
        }
        filtered = sorted(filtered, key=sort_map.get(sort_by, lambda a: -a.importance_score))

        rows = []
        for art in filtered:
            rows.append({
                "Title":     art.title[:90] + ("…" if len(art.title) > 90 else ""),
                "Company":   ", ".join(art.companies_detected[:2]) or "—",
                "Region":    art.region,
                "Source":    art.source_name,
                "Score":     art.importance_score,
                "Sentiment": art.sentiment,
                "Category":  ", ".join(art.categories[:2]) or "—",
                "Published": art.published_at.strftime("%Y-%m-%d") if art.published_at else "—",
                "URL":       art.url,
            })
        df = pd.DataFrame(rows)
        st.dataframe(
            df,
            use_container_width=True,
            height=420,
            column_config={
                "URL":      st.column_config.LinkColumn("URL", display_text="Open →"),
                "Score":    st.column_config.NumberColumn("Score", format="%.1f"),
            },
        )
        st.caption(f"Showing {len(filtered)} of {len(articles)} articles")


# ─────────────────────────────────────────────
#  Welcome screen
# ─────────────────────────────────────────────

def _render_welcome():
    # Show raw TXT report if one was loaded from disk
    if "raw_report_txt" in st.session_state:
        st.markdown(_section_label("LOADED FROM DISK"), unsafe_allow_html=True)
        with st.expander("Report Text", expanded=True):
            st.text(st.session_state["raw_report_txt"])
        if "raw_report_html" in st.session_state:
            st.components.v1.html(
                st.session_state["raw_report_html"], height=900, scrolling=True
            )
        return

    # Full welcome experience
    st.markdown("""
    <div class="tp-welcome">
      <div class="tp-welcome-icon" style="font-size:1.6em;font-weight:800;color:#60a5fa">TP</div>
      <h2>Global Telecom News Intelligence</h2>
      <p>
        AI-powered daily monitoring of 37 global telecom operators across 4 regions.
        Click <strong>Run Pipeline</strong> in the sidebar to fetch the latest news and generate your report.
      </p>
      <div class="tp-feature-grid">
        <div class="tp-feature-card">
          <div class="icon" style="font-size:1.1em;font-weight:700;color:#3b82f6">17+</div>
          <div class="title">Sources</div>
          <div class="desc">Global & regional feeds</div>
        </div>
        <div class="tp-feature-card">
          <div class="icon" style="font-size:1.1em;font-weight:700;color:#6366f1">AI</div>
          <div class="title">Summaries</div>
          <div class="desc">Groq LLaMA-3 powered</div>
        </div>
        <div class="tp-feature-card">
          <div class="icon" style="font-size:1.1em;font-weight:700;color:#0ea5e9">4x</div>
          <div class="title">Analytics</div>
          <div class="desc">Charts, scores, sentiment</div>
        </div>
        <div class="tp-feature-card">
          <div class="icon" style="font-size:1.1em;font-weight:700;color:#8b5cf6">37</div>
          <div class="title">Operators</div>
          <div class="desc">MEA · Europe · Americas · APAC</div>
        </div>
        <div class="tp-feature-card">
          <div class="icon" style="font-size:1.1em;font-weight:700;color:#f59e0b">Score</div>
          <div class="title">Smart Ranking</div>
          <div class="desc">AI relevance ranking</div>
        </div>
        <div class="tp-feature-card">
          <div class="icon" style="font-size:1.1em;font-weight:700;color:#10b981">Export</div>
          <div class="title">Reports</div>
          <div class="desc">TXT & HTML formats</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Show tracked companies
    st.markdown(_section_label("TRACKED OPERATORS"), unsafe_allow_html=True)
    with st.expander("All 37 tracked companies by region", expanded=False):
        from config import COMPANIES, REGIONS
        cols = st.columns(4)
        for i, region in enumerate(REGIONS):
            with cols[i]:
                tag = REGION_ICONS.get(region, "GL")
                st.markdown(f"**{tag}  {region}**")
                for c in COMPANIES:
                    if c.region == region:
                        st.markdown(
                            f'<div style="font-size:0.8rem;color:#94a3b8;padding:3px 0;'
                            f'border-bottom:1px solid #1e2d45">'
                            f'<strong style="color:#f1f5f9">{c.name}</strong> '
                            f'<span style="color:#64748b">· {c.country}</span></div>',
                            unsafe_allow_html=True
                        )


# ─────────────────────────────────────────────
#  Load report from file
# ─────────────────────────────────────────────

def _load_report_from_file(txt_path: Path):
    """Store raw TXT/HTML content in session state for display."""
    st.session_state["raw_report_txt"] = txt_path.read_text(encoding="utf-8")
    html_path = txt_path.with_suffix(".html")
    if html_path.exists():
        st.session_state["raw_report_html"] = html_path.read_text(encoding="utf-8")
    # Clear live data so welcome/file view is shown
    st.session_state.pop("data", None)


# ─────────────────────────────────────────────
#  App entry point
# ─────────────────────────────────────────────

def main():
    # Force UTF-8 on Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # Sidebar
    (
        run_btn, load_btn, backend, enrich,
        selected_sources, txt_files, selected_idx,
        auto_refresh, refresh_interval,
    ) = render_sidebar()

    # ── Auto-refresh ──────────────────────────
    if auto_refresh:
        import time as _time
        st.markdown(
            f'<meta http-equiv="refresh" content="{refresh_interval}">',
            unsafe_allow_html=True,
        )

    # ── Handle Run ────────────────────────────
    if run_btn:
        # Clear any previously loaded file report
        st.session_state.pop("raw_report_txt", None)
        st.session_state.pop("raw_report_html", None)
        src_list = selected_sources if selected_sources else None
        with st.spinner(""):
            data = run_pipeline_streamlit(src_list, backend, enrich)
        if data:
            st.session_state["data"] = data

    # ── Handle Load ───────────────────────────
    if load_btn and txt_files and selected_idx is not None:
        _load_report_from_file(txt_files[selected_idx])
        st.rerun()

    # ── Render ────────────────────────────────
    if "data" in st.session_state and st.session_state["data"]:
        render_dashboard(st.session_state["data"])
    else:
        _render_welcome()


if __name__ == "__main__":
    main()
