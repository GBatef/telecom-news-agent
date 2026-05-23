"""
main.py - Global Telecom Operators News AI Agent — main orchestrator.

Usage:
  python main.py              # Run once immediately
  python main.py --schedule   # Run daily at time set in config.py (SCHEDULE_TIME)
  python main.py --week       # Weekly summary (last 7 days)
  python main.py --email      # Run + send email digest
  python main.py --sources telecompaper,reuters  # Only specific sources

Environment variables:
  ANTHROPIC_API_KEY   → Required if SUMMARIZER_BACKEND="claude"
  SMTP_PASSWORD       → Required if email sending is enabled
"""

import argparse
import logging
import os
import smtplib
import sys
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import schedule

from config import (
    EMAIL_ENABLED,
    EMAIL_FROM,
    EMAIL_TO,
    LOG_DIR,
    NEWS_SOURCES,
    REPORT_OUTPUT_DIR,
    SCHEDULE_TIME,
    SMTP_HOST,
    SMTP_PORT,
    SUMMARIZER_BACKEND,
)
from categorizer import categorize_and_score
from company_detector import assign_companies_to_article
from report_generator import ReportData, generate_html_report, generate_txt_report, save_reports
from scraper import scrape_all_sources
from summarizer import batch_summarize


# ─────────────────────────────────────────────
#  Logging setup
# ─────────────────────────────────────────────

def setup_logging(log_dir: str = LOG_DIR) -> None:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_file = os.path.join(log_dir, f"agent_{datetime.now().strftime('%Y%m%d')}.log")

    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    # Force UTF-8 on Windows consoles (cp1252 can't encode → ™ etc.)
    stream = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1, closefd=False)
    stream_handler = logging.StreamHandler(stream)
    stream_handler.setFormatter(logging.Formatter(fmt))

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(fmt))

    logging.basicConfig(level=logging.INFO, handlers=[stream_handler, file_handler])


logger = logging.getLogger("telecom_agent")


# ─────────────────────────────────────────────
#  Core pipeline
# ─────────────────────────────────────────────

def run_pipeline(
    source_names: list = None,
    send_email: bool = False,
    enrich_content: bool = True,
) -> dict:
    """
    Full pipeline: scrape → detect companies → categorize → summarize → report.
    Returns dict with paths to saved report files.
    """
    run_start = datetime.now()
    logger.info("=" * 60)
    logger.info("Telecom Agent pipeline started: %s", run_start.strftime("%Y-%m-%d %H:%M:%S"))

    # ── Filter sources if specified ──
    sources = NEWS_SOURCES
    if source_names:
        names_lower = [n.lower() for n in source_names]
        sources = [s for s in NEWS_SOURCES if any(n in s.name.lower() for n in names_lower)]
        logger.info("Using %d sources: %s", len(sources), [s.name for s in sources])

    # ── Step 1: Scrape ──
    logger.info("Step 1/5: Scraping news sources...")
    articles = scrape_all_sources(sources=sources, enrich_content=enrich_content)

    if not articles:
        logger.warning("No articles collected. Check network connectivity or sources.")
        return {}

    # ── Step 2: Detect companies ──
    logger.info("Step 2/5: Detecting companies in %d articles...", len(articles))
    for art in articles:
        assign_companies_to_article(art)

    telecom_articles = [a for a in articles if a.companies_detected]
    logger.info("  -> %d articles matched to tracked companies", len(telecom_articles))

    if not telecom_articles:
        logger.warning("No articles matched any tracked company. Keeping all articles.")
        telecom_articles = articles

    # ── Step 3: Categorize & score ──
    logger.info("Step 3/5: Categorizing and scoring articles...")
    telecom_articles = categorize_and_score(telecom_articles)

    # ── Step 4: Summarize ──
    logger.info("Step 4/5: Summarizing articles (backend=%s)...", SUMMARIZER_BACKEND)
    if SUMMARIZER_BACKEND != "none":
        batch_summarize(telecom_articles)
    else:
        for art in telecom_articles:
            art.summary = art.content[:300] + "..." if art.content else art.title

    # ── Step 5: Generate reports ──
    logger.info("Step 5/5: Generating reports...")
    data = ReportData(telecom_articles, run_date=run_start)
    saved_files = save_reports(data, output_dir=REPORT_OUTPUT_DIR)

    elapsed = (datetime.now() - run_start).total_seconds()
    logger.info("Pipeline complete in %.1f seconds.", elapsed)
    logger.info("Reports saved: %s", saved_files)

    # ── Print TXT report to console ──
    print("\n" + generate_txt_report(data))

    # ── Optional email digest ──
    if send_email or EMAIL_ENABLED:
        _send_email_digest(data, saved_files)

    return saved_files


# ─────────────────────────────────────────────
#  Weekly summary
# ─────────────────────────────────────────────

def run_weekly_summary() -> None:
    """Aggregate the last 7 daily report files into a weekly summary."""
    report_dir = Path(REPORT_OUTPUT_DIR)
    txt_files = sorted(report_dir.glob("telecom_operators_report_*.txt"), reverse=True)[:7]

    if not txt_files:
        logger.warning("No daily reports found for weekly summary.")
        return

    weekly_path = report_dir / f"telecom_weekly_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(weekly_path, "w", encoding="utf-8") as out:
        out.write("=" * 70 + "\n")
        out.write("  GLOBAL TELECOM OPERATORS — WEEKLY SUMMARY\n")
        out.write(f"  Week ending: {datetime.now().strftime('%B %d, %Y')}\n")
        out.write("=" * 70 + "\n\n")
        for f in txt_files:
            out.write(f"\n{'─' * 70}\n")
            out.write(f"  {f.name}\n")
            out.write("─" * 70 + "\n")
            out.write(f.read_text(encoding="utf-8"))

    logger.info("Weekly summary saved: %s", weekly_path)


# ─────────────────────────────────────────────
#  Email digest
# ─────────────────────────────────────────────

def _send_email_digest(data: ReportData, saved_files: dict) -> None:
    if not EMAIL_TO:
        logger.warning("EMAIL_TO is empty; skipping email.")
        return

    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    if not smtp_pass:
        logger.warning("SMTP_PASSWORD not set; skipping email.")
        return

    date_str = data.date.strftime("%B %d, %Y")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Telecom Daily Report – {date_str}"
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(EMAIL_TO)

    txt_content = generate_txt_report(data)
    html_content = generate_html_report(data)

    msg.attach(MIMEText(txt_content, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_FROM, smtp_pass)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        logger.info("Email digest sent to %s", EMAIL_TO)
    except Exception as exc:
        logger.error("Failed to send email: %s", exc)


# ─────────────────────────────────────────────
#  Scheduler
# ─────────────────────────────────────────────

def start_scheduler() -> None:
    logger.info("Scheduler started. Daily run at %s.", SCHEDULE_TIME)
    schedule.every().day.at(SCHEDULE_TIME).do(run_pipeline)
    # Also run immediately on start
    run_pipeline()
    while True:
        schedule.run_pending()
        time.sleep(30)


# ─────────────────────────────────────────────
#  CLI entry point
# ─────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Global Telecom Operators News AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help=f"Run daily at {SCHEDULE_TIME} (set SCHEDULE_TIME in config.py to change)",
    )
    parser.add_argument(
        "--week",
        action="store_true",
        help="Generate weekly summary from existing daily reports",
    )
    parser.add_argument(
        "--email",
        action="store_true",
        help="Send email digest after report generation",
    )
    parser.add_argument(
        "--sources",
        type=str,
        default=None,
        help="Comma-separated list of source names to use (e.g., telecompaper,reuters)",
    )
    parser.add_argument(
        "--no-content",
        action="store_true",
        help="Skip fetching full article content (faster but less detailed)",
    )
    return parser.parse_args()


def main() -> None:
    # Force UTF-8 on Windows consoles (cp1252 can't handle box-drawing chars)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    setup_logging()
    args = parse_args()

    source_list = [s.strip() for s in args.sources.split(",")] if args.sources else None

    if args.week:
        run_weekly_summary()
    elif args.schedule:
        start_scheduler()
    else:
        run_pipeline(
            source_names=source_list,
            send_email=args.email,
            enrich_content=not args.no_content,
        )


if __name__ == "__main__":
    main()
