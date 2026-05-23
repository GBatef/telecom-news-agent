"""
categorizer.py - Categorize articles by news type, score importance, detect sentiment.
Also handles deduplication of articles across sources.
"""

import hashlib
import logging
import re
import unicodedata
from typing import Dict, List, Set, Tuple

from config import (
    DEDUP_THRESHOLD,
    IMPORTANCE_KEYWORDS,
    NEWS_CATEGORIES,
    SENTIMENT_NEGATIVE_WORDS,
    SENTIMENT_POSITIVE_WORDS,
)
from scraper import RawArticle

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  Text normalization helper
# ─────────────────────────────────────────────

def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", text.lower()).strip()


# ─────────────────────────────────────────────
#  Importance scoring
# ─────────────────────────────────────────────

def score_importance(article: RawArticle) -> float:
    """
    Score an article's importance (0.0+) based on keyword presence.
    Title matches count 2×; credibility multiplier applied.
    """
    haystack_title = _normalize(article.title)
    haystack_body = _normalize(article.content + " " + article.summary)

    score = 0.0
    for keyword, weight in IMPORTANCE_KEYWORDS.items():
        if keyword in haystack_title:
            score += weight * 2.0
        elif keyword in haystack_body:
            score += weight

    # Credibility multiplier (0.8–1.0 range → keeps scores comparable)
    score *= article.source_credibility

    return round(score, 2)


# ─────────────────────────────────────────────
#  Category detection
# ─────────────────────────────────────────────

def detect_categories(article: RawArticle) -> List[str]:
    """Return all matching news categories for an article."""
    haystack = _normalize(f"{article.title} {article.content} {article.summary}")
    matched: List[str] = []

    for category, keywords in NEWS_CATEGORIES.items():
        if any(kw in haystack for kw in keywords):
            matched.append(category)

    return matched or ["General"]


# ─────────────────────────────────────────────
#  Sentiment analysis (rule-based)
# ─────────────────────────────────────────────

def detect_sentiment(article: RawArticle) -> str:
    """
    Simple rule-based sentiment: count positive vs negative word hits.
    Returns "positive", "negative", or "neutral".
    """
    haystack = _normalize(f"{article.title} {article.summary}")

    pos = sum(1 for w in SENTIMENT_POSITIVE_WORDS if w in haystack)
    neg = sum(1 for w in SENTIMENT_NEGATIVE_WORDS if w in haystack)

    if pos > neg:
        return "positive"
    elif neg > pos:
        return "negative"
    return "neutral"


# ─────────────────────────────────────────────
#  Deduplication
# ─────────────────────────────────────────────

def _title_fingerprint(title: str) -> str:
    """Bag-of-words fingerprint of a title for similarity comparison."""
    words = set(_normalize(title).split())
    # Remove stop words
    stop = {"the", "a", "an", "in", "of", "to", "and", "for", "is", "its", "with", "on"}
    words -= stop
    return " ".join(sorted(words))


def _jaccard(a: str, b: str) -> float:
    sa = set(a.split())
    sb = set(b.split())
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)


def deduplicate(articles: List[RawArticle]) -> List[RawArticle]:
    """
    Remove near-duplicate articles using Jaccard similarity on title fingerprints.
    Keeps the article with the highest source credibility score.
    """
    seen: List[Tuple[str, RawArticle]] = []
    unique: List[RawArticle] = []

    for art in articles:
        fp = _title_fingerprint(art.title)
        duplicate = False
        for i, (seen_fp, seen_art) in enumerate(seen):
            if _jaccard(fp, seen_fp) >= DEDUP_THRESHOLD:
                # Keep higher-credibility source
                if art.source_credibility > seen_art.source_credibility:
                    seen[i] = (fp, art)
                    for j, u in enumerate(unique):
                        if u.url == seen_art.url:
                            unique[j] = art
                            break
                duplicate = True
                break
        if not duplicate:
            seen.append((fp, art))
            unique.append(art)

    logger.info("Deduplication: %d -> %d articles", len(articles), len(unique))
    return unique


# ─────────────────────────────────────────────
#  Content hash (for exact duplicate detection)
# ─────────────────────────────────────────────

def compute_content_hash(article: RawArticle) -> str:
    raw = _normalize(article.title)
    return hashlib.sha256(raw.encode()).hexdigest()


# ─────────────────────────────────────────────
#  Main pipeline step
# ─────────────────────────────────────────────

def categorize_and_score(articles: List[RawArticle]) -> List[RawArticle]:
    """
    Run all categorization, scoring, and deduplication steps.
    Mutates articles in place, then deduplicates.
    """
    for art in articles:
        art.categories = detect_categories(art)
        art.importance_score = score_importance(art)
        art.sentiment = detect_sentiment(art)
        art.content_hash = compute_content_hash(art)

    articles = deduplicate(articles)

    # Sort: companies-with-detection first, then by importance
    articles.sort(
        key=lambda a: (
            len(a.companies_detected) > 0,
            a.importance_score,
        ),
        reverse=True,
    )

    return articles


# ─────────────────────────────────────────────
#  Trend analysis helpers
# ─────────────────────────────────────────────

def company_mention_counts(articles: List[RawArticle]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for art in articles:
        for cname in art.companies_detected:
            counts[cname] = counts.get(cname, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def region_mention_counts(articles: List[RawArticle]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for art in articles:
        counts[art.region] = counts.get(art.region, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def category_counts(articles: List[RawArticle]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for art in articles:
        for cat in art.categories:
            counts[cat] = counts.get(cat, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
