"""
scraper.py - Web scraping engine with RSS and HTML fallback
"""

import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

from config import (
    MAX_ARTICLES_PER_SOURCE,
    MAX_RETRIES,
    NEWS_SOURCES,
    REQUEST_TIMEOUT,
    RETRY_DELAY,
    USER_AGENTS,
    NewsSource,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  Data Model
# ─────────────────────────────────────────────

@dataclass
class RawArticle:
    title: str
    url: str
    source_name: str
    source_credibility: float
    published_at: Optional[datetime] = None
    content: str = ""
    summary: str = ""
    companies_detected: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    importance_score: float = 0.0
    sentiment: str = "neutral"      # positive | negative | neutral
    region: str = "Global"
    language: str = "en"
    content_hash: str = ""          # for dedup


# ─────────────────────────────────────────────
#  HTTP helpers
# ─────────────────────────────────────────────

def _make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    return session


def _get(url: str, session: requests.Session, retries: int = MAX_RETRIES) -> Optional[requests.Response]:
    for attempt in range(1, retries + 1):
        try:
            session.headers["User-Agent"] = random.choice(USER_AGENTS)
            resp = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            resp.raise_for_status()
            return resp
        except requests.HTTPError as exc:
            # 4xx = client error; retrying won't help — bail immediately
            status = exc.response.status_code if exc.response is not None else 0
            if 400 <= status < 500:
                logger.debug("HTTP %d for %s — skipping (no retry)", status, url)
                return None
            logger.warning("Attempt %d/%d failed for %s: %s", attempt, retries, url, exc)
            if attempt < retries:
                time.sleep(RETRY_DELAY * attempt)
        except requests.RequestException as exc:
            logger.warning("Attempt %d/%d failed for %s: %s", attempt, retries, url, exc)
            if attempt < retries:
                time.sleep(RETRY_DELAY * attempt)
    logger.debug("All retries exhausted for %s", url)
    return None


# ─────────────────────────────────────────────
#  RSS Scraper
# ─────────────────────────────────────────────

def _parse_rss_date(entry) -> Optional[datetime]:
    """Try several feedparser date fields and return UTC datetime."""
    for attr in ("published_parsed", "updated_parsed", "created_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def scrape_rss(source: NewsSource, session: requests.Session) -> List[RawArticle]:
    if not source.rss_url:
        return []

    logger.info("Fetching RSS: %s", source.rss_url)
    resp = _get(source.rss_url, session)
    if not resp:
        return []

    feed = feedparser.parse(resp.text)
    articles: List[RawArticle] = []

    for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
        title = getattr(entry, "title", "").strip()
        url = getattr(entry, "link", "").strip()
        if not title or not url:
            continue

        # Prefer summary/content from feed, fall back to description
        content = ""
        for attr in ("content", "summary", "description"):
            val = getattr(entry, attr, None)
            if val:
                if isinstance(val, list):
                    val = val[0].get("value", "")
                soup = BeautifulSoup(val, "html.parser")
                content = soup.get_text(separator=" ").strip()
                if content:
                    break

        articles.append(
            RawArticle(
                title=title,
                url=url,
                source_name=source.name,
                source_credibility=source.credibility_score,
                published_at=_parse_rss_date(entry),
                content=content,
                region=source.region,
                language=source.language,
            )
        )

    logger.info("  -> %d articles from %s (RSS)", len(articles), source.name)
    return articles


# ─────────────────────────────────────────────
#  Generic HTML Scraper
# ─────────────────────────────────────────────

_ARTICLE_LINK_SELECTORS = [
    "article a[href]",
    ".news-item a[href]",
    ".post a[href]",
    ".entry-title a[href]",
    "h2 a[href]",
    "h3 a[href]",
    ".headline a[href]",
    ".article-title a[href]",
    ".item-title a[href]",
    "li.news a[href]",
]

_CONTENT_SELECTORS = [
    "article",
    "[class*='article-body']",
    "[class*='post-content']",
    "[class*='entry-content']",
    "[class*='story-body']",
    "main",
]


def _extract_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Extract candidate article URLs from a listing page."""
    seen: set = set()
    links: List[str] = []
    base_domain = urlparse(base_url).netloc

    for selector in _ARTICLE_LINK_SELECTORS:
        for tag in soup.select(selector):
            href = tag.get("href", "")
            if not href or href.startswith("#"):
                continue
            full = urljoin(base_url, href)
            domain = urlparse(full).netloc
            # Stay on same domain
            if domain != base_domain:
                continue
            if full not in seen:
                seen.add(full)
                links.append(full)
        if links:
            break  # Use first selector that finds results

    return links[:MAX_ARTICLES_PER_SOURCE]


def _extract_article_content(url: str, session: requests.Session) -> str:
    """Fetch and parse a single article page, returning cleaned text."""
    resp = _get(url, session)
    if not resp:
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove noise
    for tag in soup(["script", "style", "nav", "footer", "aside", "header"]):
        tag.decompose()

    for selector in _CONTENT_SELECTORS:
        el = soup.select_one(selector)
        if el:
            return el.get_text(separator=" ").strip()

    return soup.get_text(separator=" ").strip()


def scrape_html(source: NewsSource, session: requests.Session) -> List[RawArticle]:
    """Scrape articles from an HTML listing page."""
    url = source.scrape_url or source.base_url
    logger.info("Fetching HTML listing: %s", url)

    resp = _get(url, session)
    if not resp:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    links = _extract_links(soup, url)

    if not links:
        logger.warning("No article links found on %s", url)
        return []

    articles: List[RawArticle] = []
    for link in links:
        title_tag = soup.find("a", href=lambda h: h and link.endswith(h))
        title = title_tag.get_text().strip() if title_tag else link

        # Avoid fetching every article page (rate-limit friendly); get title from listing
        articles.append(
            RawArticle(
                title=title,
                url=link,
                source_name=source.name,
                source_credibility=source.credibility_score,
                published_at=datetime.now(timezone.utc),
                region=source.region,
                language=source.language,
            )
        )
        time.sleep(0.5)  # polite delay

    logger.info("  -> %d articles from %s (HTML)", len(articles), source.name)
    return articles


# ─────────────────────────────────────────────
#  Article full-text fetcher
# ─────────────────────────────────────────────

# Domains known to block scrapers — skip content enrichment silently
_BLOCKED_DOMAINS = {
    "fierce-network.com",
    "bloomberg.com",
    "wsj.com",
    "ft.com",
    "reuters.com",     # Reuters blocks direct article fetches; RSS content is sufficient
}

_enrichment_failures: dict = {}   # domain → failure count (runtime circuit-breaker)


def _domain(url: str) -> str:
    return urlparse(url).netloc.lstrip("www.")


def enrich_article_content(article: RawArticle, session: requests.Session) -> None:
    """Fetch full text if article.content is empty or very short."""
    if len(article.content) >= 200:
        return

    dom = _domain(article.url)

    # Skip known-blocked domains
    if dom in _BLOCKED_DOMAINS:
        return

    # Circuit-breaker: stop trying a domain after 3 consecutive failures
    if _enrichment_failures.get(dom, 0) >= 3:
        return

    logger.debug("Fetching full content for: %s", article.url)
    text = _extract_article_content(article.url, session)
    if text:
        article.content = text
        _enrichment_failures[dom] = 0   # reset on success
    else:
        _enrichment_failures[dom] = _enrichment_failures.get(dom, 0) + 1


# ─────────────────────────────────────────────
#  Main scrape orchestrator
# ─────────────────────────────────────────────

def scrape_all_sources(
    sources: List[NewsSource] = None,
    enrich_content: bool = True,
) -> List[RawArticle]:
    """
    Scrape all configured news sources.
    Returns a flat list of raw articles.
    """
    if sources is None:
        sources = NEWS_SOURCES

    session = _make_session()
    all_articles: List[RawArticle] = []
    failed_sources: List[str] = []

    for source in sources:
        try:
            if source.rss_url:
                articles = scrape_rss(source, session)
            else:
                articles = scrape_html(source, session)

            if enrich_content:
                for art in articles:
                    enrich_article_content(art, session)
                    time.sleep(0.1)  # polite delay between article fetches

            all_articles.extend(articles)

        except Exception as exc:
            logger.error("Failed to scrape %s: %s", source.name, exc, exc_info=True)
            failed_sources.append(source.name)

    if failed_sources:
        logger.warning("Sources with errors: %s", ", ".join(failed_sources))

    logger.info("Total articles collected: %d", len(all_articles))
    return all_articles
