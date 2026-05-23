"""
report_generator.py - Generate TXT, HTML and PDF reports from processed articles.
"""

import logging
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from config import COMPANIES, EXPORT_FORMATS, REGIONS, REPORT_OUTPUT_DIR
from categorizer import (
    category_counts,
    company_mention_counts,
    region_mention_counts,
)
from scraper import RawArticle

logger = logging.getLogger(__name__)

SENTIMENT_ICON = {"positive": "↑", "negative": "↓", "neutral": "─"}
SENTIMENT_LABEL = {"positive": "POSITIVE", "negative": "NEGATIVE", "neutral": "NEUTRAL"}


# ─────────────────────────────────────────────
#  Report data structure
# ─────────────────────────────────────────────

class ReportData:
    def __init__(self, articles: List[RawArticle], run_date: datetime = None):
        self.articles = articles
        self.date = run_date or datetime.now()
        self.by_region: Dict[str, Dict[str, List[RawArticle]]] = defaultdict(lambda: defaultdict(list))
        self.highlight: Optional[RawArticle] = None
        self.company_counts = company_mention_counts(articles)
        self.region_counts = region_mention_counts(articles)
        self.cat_counts = category_counts(articles)
        self._organize()

    def _organize(self):
        """Group articles by region → company."""
        # Map company → region
        cname_to_region = {c.name: c.region for c in COMPANIES}

        for art in self.articles:
            if not art.companies_detected:
                continue
            for cname in art.companies_detected:
                region = cname_to_region.get(cname, art.region)
                self.by_region[region][cname].append(art)

        # Highlight = highest importance score with a company detected
        with_companies = [a for a in self.articles if a.companies_detected]
        if with_companies:
            self.highlight = max(with_companies, key=lambda a: a.importance_score)


# ─────────────────────────────────────────────
#  TXT Report
# ─────────────────────────────────────────────

def _txt_divider(char: str = "─", width: int = 70) -> str:
    return char * width


def _txt_header(date: datetime) -> str:
    date_str = date.strftime("%A, %B %d, %Y")
    lines = [
        "╔" + "═" * 68 + "╗",
        "║" + "  GLOBAL TELECOM OPERATORS DAILY REPORT".center(68) + "║",
        "║" + date_str.center(68) + "║",
        "╚" + "═" * 68 + "╝",
    ]
    return "\n".join(lines)


def _txt_article_block(art: RawArticle, idx: int) -> str:
    icon = SENTIMENT_ICON.get(art.sentiment, "─")
    cats = ", ".join(art.categories[:3])
    score = f"Score: {art.importance_score:.1f}"
    summary = art.summary or art.content[:250]

    lines = [
        f"  {idx}. {icon} {art.title}",
        f"     Source : {art.source_name}  |  {score}  |  {cats}",
        f"     URL    : {art.url}",
    ]
    if summary:
        import textwrap
        wrapped = textwrap.fill(summary, width=66, initial_indent="     ", subsequent_indent="     ")
        lines.append(f"     Summary: {wrapped[9:]}")
    return "\n".join(lines)


def generate_txt_report(data: ReportData) -> str:
    """Return the full TXT report as a string."""
    lines = [_txt_header(data.date), ""]

    for region in REGIONS:
        companies_in_region = data.by_region.get(region)
        if not companies_in_region:
            continue

        total = sum(len(v) for v in companies_in_region.values())
        lines.append(f"\n{'─'*70}")
        lines.append(f"  REGION: {region.upper()}  ({total} articles)")
        lines.append(f"{'─'*70}")

        for cname in sorted(companies_in_region.keys()):
            articles = companies_in_region[cname]
            lines.append(f"\n  [{cname}]  — {len(articles)} article(s)")
            for i, art in enumerate(articles[:10], 1):
                lines.append(_txt_article_block(art, i))

    # ── Summary stats ──
    lines.append(f"\n{'═'*70}")
    lines.append("  REPORT STATISTICS")
    lines.append(f"{'═'*70}")
    lines.append(f"  Total articles processed : {len(data.articles)}")
    lines.append(f"  Companies tracked        : {len(data.company_counts)}")
    lines.append("")
    lines.append("  TOP COMPANIES BY MENTIONS:")
    for cname, count in list(data.company_counts.items())[:10]:
        lines.append(f"    {cname:<30} {count} mentions")

    lines.append("")
    lines.append("  TOP CATEGORIES:")
    for cat, count in list(data.cat_counts.items())[:8]:
        lines.append(f"    {cat:<30} {count} articles")

    # ── Highlight ──
    lines.append(f"\n{'═'*70}")
    lines.append("  HIGHLIGHT OF THE DAY")
    lines.append(f"{'═'*70}")
    if data.highlight:
        h = data.highlight
        lines.append(f"  {h.title}")
        lines.append(f"  Source: {h.source_name}  |  Score: {h.importance_score:.1f}")
        lines.append(f"  {h.url}")
        if h.summary:
            import textwrap
            lines.append(textwrap.fill(h.summary, width=68, initial_indent="  ", subsequent_indent="  "))
    else:
        lines.append("  No major highlights today.")

    lines.append(f"\n{'═'*70}")
    lines.append(f"  Generated at: {data.date.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"{'═'*70}\n")

    return "\n".join(lines)


# ─────────────────────────────────────────────
#  HTML Report
# ─────────────────────────────────────────────

_HTML_CSS = """
<style>
  body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 1000px; margin: auto; padding: 20px; background: #f5f7fa; color: #1a1a2e; }
  h1 { background: linear-gradient(135deg, #1a1a2e, #16213e); color: white; padding: 24px; border-radius: 8px; text-align: center; }
  h2 { border-left: 5px solid #0f3460; padding-left: 12px; color: #0f3460; }
  h3 { color: #533483; margin-top: 20px; }
  .article { background: white; border-radius: 6px; padding: 14px 18px; margin: 10px 0; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
  .article-title { font-weight: 600; font-size: 1.05em; }
  .article-title a { color: #0f3460; text-decoration: none; }
  .article-title a:hover { text-decoration: underline; }
  .meta { color: #888; font-size: 0.85em; margin: 4px 0 8px; }
  .summary { color: #444; line-height: 1.6; }
  .tag { display: inline-block; background: #e8f4fd; color: #0f3460; border-radius: 12px; padding: 2px 10px; font-size: 0.78em; margin: 2px; }
  .positive { color: #27ae60; font-weight: bold; }
  .negative { color: #e74c3c; font-weight: bold; }
  .neutral  { color: #7f8c8d; }
  .highlight-box { background: #fff3e0; border-left: 5px solid #ff6b35; padding: 18px 22px; border-radius: 6px; margin: 20px 0; }
  .stats-box { background: white; border-radius: 6px; padding: 18px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
  table { width: 100%; border-collapse: collapse; }
  td, th { padding: 8px 12px; text-align: left; border-bottom: 1px solid #eee; }
  th { background: #f0f0f5; font-weight: 600; }
  .score-bar { display: inline-block; background: #0f3460; height: 8px; border-radius: 4px; min-width: 4px; }
  footer { text-align: center; color: #aaa; margin-top: 40px; font-size: 0.85em; }
</style>
"""


def generate_html_report(data: ReportData) -> str:
    date_str = data.date.strftime("%A, %B %d, %Y")
    parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        f'<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f"<title>Global Telecom Report – {date_str}</title>",
        _HTML_CSS,
        "</head><body>",
        f"<h1>Global Telecom Operators Daily Report<br><small style='font-weight:300;font-size:0.7em'>{date_str}</small></h1>",
    ]

    # ── Highlight ──
    if data.highlight:
        h = data.highlight
        sent_cls = h.sentiment
        parts += [
            '<div class="highlight-box">',
            '<strong>★ HIGHLIGHT OF THE DAY</strong>',
            f'<p class="article-title"><a href="{h.url}" target="_blank">{h.title}</a></p>',
            f'<p class="meta">Source: {h.source_name} | Score: {h.importance_score:.1f} | '
            f'<span class="{sent_cls}">{SENTIMENT_LABEL[h.sentiment]}</span></p>',
            f'<p class="summary">{h.summary or ""}</p>',
            "</div>",
        ]

    # ── Regions ──
    for region in REGIONS:
        companies_in_region = data.by_region.get(region)
        if not companies_in_region:
            continue
        total = sum(len(v) for v in companies_in_region.values())
        parts.append(f"<h2>{region} <small style='font-size:0.6em;color:#888'>({total} articles)</small></h2>")

        for cname in sorted(companies_in_region.keys()):
            articles = companies_in_region[cname]
            parts.append(f"<h3>{cname} — {len(articles)} article(s)</h3>")
            for art in articles[:10]:
                cats_html = "".join(f'<span class="tag">{c}</span>' for c in art.categories[:4])
                sent_cls = art.sentiment
                bar_w = min(int(art.importance_score * 4), 120)
                parts += [
                    '<div class="article">',
                    f'<p class="article-title"><a href="{art.url}" target="_blank">{art.title}</a></p>',
                    f'<p class="meta">',
                    f'  {art.source_name} | Score: {art.importance_score:.1f} '
                    f'<span class="score-bar" style="width:{bar_w}px"></span> | '
                    f'<span class="{sent_cls}">{SENTIMENT_LABEL[art.sentiment]}</span>',
                    f'</p>',
                    f'<div>{cats_html}</div>',
                ]
                if art.summary:
                    parts.append(f'<p class="summary">{art.summary}</p>')
                parts.append("</div>")

    # ── Stats ──
    parts += [
        "<h2>Report Statistics</h2>",
        '<div class="stats-box">',
        f"<p><strong>Total articles processed:</strong> {len(data.articles)}</p>",
        f"<p><strong>Companies tracked today:</strong> {len(data.company_counts)}</p>",
        "<table><tr><th>Company</th><th>Mentions</th></tr>",
    ]
    for cname, cnt in list(data.company_counts.items())[:15]:
        parts.append(f"<tr><td>{cname}</td><td>{cnt}</td></tr>")
    parts += ["</table></div>"]

    parts += [
        f"<footer>Generated by Global Telecom AI Agent · {data.date.strftime('%Y-%m-%d %H:%M:%S')}</footer>",
        "</body></html>",
    ]
    return "\n".join(parts)


# ─────────────────────────────────────────────
#  Save helpers
# ─────────────────────────────────────────────

def _ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def save_reports(data: ReportData, output_dir: str = REPORT_OUTPUT_DIR) -> Dict[str, str]:
    """
    Save all configured export formats to disk.
    Returns dict of {format: filepath}.
    """
    _ensure_dir(output_dir)
    date_tag = data.date.strftime("%Y%m%d")
    saved: Dict[str, str] = {}

    if "txt" in EXPORT_FORMATS:
        txt_path = os.path.join(output_dir, f"telecom_operators_report_{date_tag}.txt")
        content = generate_txt_report(data)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(content)
        saved["txt"] = txt_path
        logger.info("TXT report saved: %s", txt_path)

    if "html" in EXPORT_FORMATS:
        html_path = os.path.join(output_dir, f"telecom_operators_report_{date_tag}.html")
        content = generate_html_report(data)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
        saved["html"] = html_path
        logger.info("HTML report saved: %s", html_path)

    if "pdf" in EXPORT_FORMATS:
        html_path = saved.get("html")
        if html_path:
            pdf_path = os.path.join(output_dir, f"telecom_operators_report_{date_tag}.pdf")
            _save_pdf(html_path, pdf_path)
            saved["pdf"] = pdf_path

    return saved


def _save_pdf(html_path: str, pdf_path: str) -> None:
    try:
        from weasyprint import HTML
        HTML(filename=html_path).write_pdf(pdf_path)
        logger.info("PDF report saved: %s", pdf_path)
    except ImportError:
        logger.warning("weasyprint not installed – skipping PDF export.")
    except Exception as exc:
        logger.error("PDF export failed: %s", exc)
