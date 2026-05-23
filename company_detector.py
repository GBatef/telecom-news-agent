"""
company_detector.py - Detect which telecom companies are mentioned in an article.

Uses:
  1. Direct alias string matching (fast, handles Arabic/non-ASCII)
  2. Word-boundary regex for English names
  3. Optional: spaCy NER as a fallback
"""

import hashlib
import re
import unicodedata
from typing import List, Set

from config import COMPANIES, Company
from scraper import RawArticle


# ─────────────────────────────────────────────
#  Pre-compile patterns for performance
# ─────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Lower-case, strip accents, collapse whitespace."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", text.lower()).strip()


# Build a lookup: normalized alias → Company
_ALIAS_MAP: dict = {}
_PATTERN_MAP: dict = {}   # company.name → compiled regex

for _company in COMPANIES:
    all_names = [_company.name] + _company.aliases
    for alias in all_names:
        _ALIAS_MAP[_normalize(alias)] = _company

    # Word-boundary pattern (English aliases)
    english_aliases = [a for a in all_names if all(ord(c) < 0x0600 for c in a)]
    if english_aliases:
        pattern_str = r"\b(?:" + "|".join(re.escape(a) for a in english_aliases) + r")\b"
        _PATTERN_MAP[_company.name] = re.compile(pattern_str, re.IGNORECASE)


def detect_companies(article: RawArticle) -> List[Company]:
    """
    Return all companies detected in the article's title + content.
    Deduplicates by company name.
    """
    haystack = f"{article.title} {article.content}"
    haystack_norm = _normalize(haystack)

    found: Set[str] = set()
    result: List[Company] = []

    # 1. Direct substring match on normalized text
    for alias_norm, company in _ALIAS_MAP.items():
        if alias_norm in haystack_norm and company.name not in found:
            found.add(company.name)
            result.append(company)

    # 2. Regex word-boundary for any remaining English names
    for cname, pattern in _PATTERN_MAP.items():
        if cname not in found and pattern.search(haystack):
            for c in COMPANIES:
                if c.name == cname:
                    found.add(cname)
                    result.append(c)
                    break

    return result


def assign_companies_to_article(article: RawArticle) -> None:
    """Mutate article in place: set companies_detected and primary region."""
    companies = detect_companies(article)
    article.companies_detected = [c.name for c in companies]

    # Primary region: most common region among detected companies
    if companies:
        region_counts: dict = {}
        for c in companies:
            region_counts[c.region] = region_counts.get(c.region, 0) + 1
        article.region = max(region_counts, key=region_counts.get)


def compute_content_hash(article: RawArticle) -> str:
    """SHA-256 of normalized title for deduplication."""
    return hashlib.sha256(_normalize(article.title).encode()).hexdigest()
