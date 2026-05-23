"""
summarizer.py - AI-powered article summarization.

Backends (set SUMMARIZER_BACKEND in config.py):
  "local"      → HuggingFace facebook/bart-large-cnn loaded directly (no pipeline)
  "extractive" → Keyword-ranked sentence extraction (no model download, instant)
  "claude"     → Anthropic Claude API (requires ANTHROPIC_API_KEY env var)
  "none"       → First 300 chars of content as-is
"""

import logging
import os
import re
import textwrap
from typing import List

from config import (
    CLAUDE_MAX_TOKENS,
    CLAUDE_MODEL,
    GROQ_MAX_TOKENS,
    GROQ_MODEL,
    IMPORTANCE_KEYWORDS,
    LOCAL_SUMMARIZER_MODEL,
    SUMMARIZER_BACKEND,
    SUMMARY_MAX_LENGTH,
    SUMMARY_MIN_LENGTH,
)
from scraper import RawArticle

# Load .env file if present (for GROQ_API_KEY etc.)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  Extractive summarizer (zero dependencies)
# ─────────────────────────────────────────────

def _split_sentences(text: str) -> List[str]:
    """Split text into sentences using punctuation heuristics."""
    text = re.sub(r"\s+", " ", text).strip()
    # Split on . ! ? followed by a space and capital letter
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"])", text)
    return [s.strip() for s in parts if len(s.strip()) > 30]


def _score_sentence(sentence: str) -> float:
    sl = sentence.lower()
    score = 0.0
    for kw, weight in IMPORTANCE_KEYWORDS.items():
        if kw in sl:
            score += weight
    return score


def _summarize_extractive(text: str, n_sentences: int = 3) -> str:
    sentences = _split_sentences(text)
    if not sentences:
        return text[:300]
    if len(sentences) <= n_sentences:
        return " ".join(sentences)

    scored = sorted(
        enumerate(sentences),
        key=lambda idx_s: _score_sentence(idx_s[1]),
        reverse=True,
    )
    top_indices = sorted(i for i, _ in scored[:n_sentences])
    return " ".join(sentences[i] for i in top_indices)


# ─────────────────────────────────────────────
#  Local BART (direct model loading — no pipeline registry)
# ─────────────────────────────────────────────

_bart_model = None
_bart_tokenizer = None


def _load_bart():
    global _bart_model, _bart_tokenizer
    if _bart_model is None:
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            logger.info("Loading BART model: %s (first run downloads ~1.6 GB)", LOCAL_SUMMARIZER_MODEL)
            _bart_tokenizer = AutoTokenizer.from_pretrained(LOCAL_SUMMARIZER_MODEL)
            _bart_model = AutoModelForSeq2SeqLM.from_pretrained(LOCAL_SUMMARIZER_MODEL)
            logger.info("BART model loaded.")
        except ImportError:
            logger.error("transformers not installed. Run: pip install transformers torch")
            raise
        except Exception as exc:
            logger.error("Failed to load BART model: %s — falling back to extractive.", exc)
            _bart_model = None
            _bart_tokenizer = None
            raise
    return _bart_tokenizer, _bart_model


def _summarize_bart(text: str) -> str:
    try:
        tokenizer, model = _load_bart()
    except Exception:
        return _summarize_extractive(text)

    try:
        import torch
        inputs = tokenizer(
            text[:3000],
            return_tensors="pt",
            max_length=1024,
            truncation=True,
        )
        with torch.no_grad():
            summary_ids = model.generate(
                inputs["input_ids"],
                max_length=SUMMARY_MAX_LENGTH,
                min_length=SUMMARY_MIN_LENGTH,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True,
            )
        return tokenizer.decode(summary_ids[0], skip_special_tokens=True).strip()
    except Exception as exc:
        logger.warning("BART inference failed: %s — using extractive fallback.", exc)
        return _summarize_extractive(text)


# ─────────────────────────────────────────────
#  Groq API backend (free)
# ─────────────────────────────────────────────

_groq_client = None


def _get_groq_client():
    global _groq_client
    if _groq_client is None:
        try:
            from groq import Groq
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                try:
                    import streamlit as st
                    api_key = st.secrets.get("GROQ_API_KEY")
                except Exception:
                    pass
            if not api_key:
                raise EnvironmentError(
                    "GROQ_API_KEY not set. Add it to .env or set the environment variable."
                )
            _groq_client = Groq(api_key=api_key)
        except ImportError:
            logger.error("groq SDK not installed. Run: pip install groq")
            raise
    return _groq_client


def _summarize_groq(text: str, title: str = "") -> str:
    client = _get_groq_client()
    prompt = (
        f"Summarize this telecom industry news in 2-3 concise sentences. "
        f"Focus on: what happened, which company, and why it matters.\n"
        f"Title: {title}\n"
        f"Article: {text[:3000]}"
    )
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=GROQ_MAX_TOKENS,
            temperature=0.3,
        )
        return completion.choices[0].message.content.strip()
    except Exception as exc:
        logger.warning("Groq summarization failed: %s — using extractive fallback.", exc)
        return _summarize_extractive(text)


# ─────────────────────────────────────────────
#  Claude API backend
# ─────────────────────────────────────────────

_claude_client = None


def _get_claude_client():
    global _claude_client
    if _claude_client is None:
        try:
            import anthropic
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise EnvironmentError("ANTHROPIC_API_KEY environment variable not set.")
            _claude_client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            logger.error("anthropic SDK not installed. Run: pip install anthropic")
            raise
    return _claude_client


def _summarize_claude(text: str, title: str = "") -> str:
    client = _get_claude_client()
    prompt = textwrap.dedent(f"""
        Summarize the following telecom industry news article in 2-3 concise sentences.
        Focus on: what happened, which company, and why it matters.
        Title: {title}
        Article: {text[:4000]}
    """).strip()
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()
    except Exception as exc:
        logger.warning("Claude summarization failed: %s", exc)
        return _summarize_extractive(text)


# ─────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────

def summarize_text(text: str, title: str = "") -> str:
    """Summarize text using the configured backend."""
    if not text or len(text) < 50:
        return text

    backend = SUMMARIZER_BACKEND.lower()

    if backend == "groq":
        return _summarize_groq(text, title)
    elif backend == "local":
        return _summarize_bart(text)
    elif backend == "extractive":
        return _summarize_extractive(text)
    elif backend == "claude":
        return _summarize_claude(text, title)
    else:  # "none"
        return text[:300].rstrip() + "..."


def summarize_article(article: RawArticle) -> None:
    """Mutate article in place: populate article.summary."""
    if article.summary:
        return
    source_text = article.content or article.title
    article.summary = summarize_text(source_text, article.title)


def batch_summarize(articles: list, max_workers: int = 4) -> None:
    """
    Summarize a list of articles.
    Serial for local/extractive (CPU-safe); threaded for Claude API.
    """
    backend = SUMMARIZER_BACKEND.lower()
    if backend in ("local", "extractive", "none"):
        for art in articles:
            summarize_article(art)
    else:  # groq / claude — parallel via threads
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(summarize_article, art): art for art in articles}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    art = futures[future]
                    logger.error("Summarization error for '%s': %s", art.title, exc)
