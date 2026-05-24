# Global Telecom Operators News AI Agent

An automated AI agent that scrapes major telecom news sources daily and generates
comprehensive reports on **37+ global telecom operators** across four regions.
Includes a **Streamlit dashboard** with interactive charts and **free AI summaries via Groq**.

---

## Quick Start

### Double-click to run (easiest)

| File | What it does |
|------|-------------|
| `RUN_DASHBOARD.bat` | Opens the visual dashboard in your browser |
| `RUN_REPORT.bat` | Generates a TXT + HTML report in the terminal |

### Or use the terminal

```powershell
cd "C:\Users\pc\Desktop\NET IA agent"
.\venv\Scripts\activate

# Launch dashboard
streamlit run dashboard.py

# Or generate report only
python main.py --no-content
```

---

## Installation (first time only)

```powershell
# 1. Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) CPU-only PyTorch for local BART model
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

---

## Features

| Feature | Details |
|---------|---------|
| **Coverage** | 37 operators across Middle East & Africa, Europe, Americas, Asia-Pacific |
| **Sources** | 17+ news sources (RSS feeds + HTML scraping) |
| **AI Summaries** | Groq API (free) · BART local model · Extractive fallback |
| **Dashboard** | Streamlit with interactive charts, region tabs, article cards |
| **Deduplication** | Jaccard similarity across sources |
| **Importance Scoring** | Keyword-weighted scoring per article |
| **Sentiment Analysis** | Positive / Negative / Neutral per article |
| **Categorization** | 11 news categories (5G, M&A, Financial Results, etc.) |
| **Multi-language** | English + Arabic alias matching |
| **Export Formats** | TXT, HTML (PDF optional via weasyprint) |
| **Scheduling** | Daily at configurable time |
| **Email Digest** | Optional SMTP delivery |

---

## Dashboard

```powershell
streamlit run dashboard.py
# Opens at http://localhost:8501
```

### Dashboard sections

| Section | Description |
|---------|-------------|
| **Metrics row** | Total articles · Companies tracked · Regions active · Top score · Sentiment |
| **Highlight of the Day** | Most important article in a featured card |
| **Analytics charts** | Top companies · Categories · Sentiment · Regions |
| **Region tabs** | MEA / Europe / Americas / Asia-Pacific — expandable per company |
| **Article cards** | Title link · Source · Importance score · Sentiment · AI summary |
| **Full table** | Sortable DataFrame of all articles with links |
| **Sidebar** | Run controls · Backend selector · Source filter · Download reports · Load history |

---

## Command-line Usage

```powershell
# Fast run — RSS content only (~30 seconds)
python main.py --no-content

# Full run — fetches article pages (~5 minutes)
python main.py

# Daily automatic schedule (runs at 07:00 every day)
python main.py --schedule

# Weekly summary from existing daily reports
python main.py --week

# Use specific sources only
python main.py --no-content --sources lightreading,bloomberg

# Run + send email digest
python main.py --email
```

---

## Configuration

All settings are in **`config.py`**.

### AI Summarization Backend

```python
# config.py
SUMMARIZER_BACKEND = "groq"   # default — free AI via Groq API
```

| Backend | Quality | Speed | Cost | Requires |
|---------|---------|-------|------|----------|
| `"groq"` | ★★★★ | Fast | **Free** | `GROQ_API_KEY` in `.env` |
| `"extractive"` | ★★★ | Instant | Free | Nothing |
| `"local"` | ★★★★ | Slow | Free | ~1.6 GB download (BART) |
| `"none"` | ★ | Instant | Free | Nothing |

### Groq API Key

Your key is stored in `.env` (never commit this file):
```
GROQ_API_KEY=gsk_...
```

Change the Groq model in `config.py`:
```python
GROQ_MODEL = "llama-3.1-8b-instant"      # fastest (default)
GROQ_MODEL = "llama-3.3-70b-versatile"   # best quality
```

### Schedule Time

```python
SCHEDULE_TIME = "07:00"   # 24h format, local time
```

### Email Digest

```python
EMAIL_ENABLED = True
EMAIL_FROM    = "your@gmail.com"
EMAIL_TO      = ["recipient@example.com"]
SMTP_HOST     = "smtp.gmail.com"
SMTP_PORT     = 587
```

```powershell
$env:SMTP_PASSWORD = "your_app_password"
```

> Gmail users: use an [App Password](https://myaccount.google.com/apppasswords).

### Adding a Company

```python
# config.py — COMPANIES list
Company(
    name="My Telecom",
    region="Europe",
    country="Germany",
    aliases=["MyTel", "My Telecom AG"],
    ticker="MYTEL.DE",
    ir_page="https://myteleco.com/news/",
),
```

### Adding a News Source

```python
# config.py — NEWS_SOURCES list
NewsSource(
    name="My Source",
    base_url="https://example.com",
    rss_url="https://example.com/feed.xml",   # preferred over HTML scraping
    credibility_score=0.85,
),
```

---

## Project Structure

```
NET IA agent/
├── dashboard.py          # Streamlit visual dashboard
├── main.py               # CLI orchestrator & scheduler
├── scraper.py            # RSS + HTML scraping engine
├── company_detector.py   # Multi-language company name matching
├── summarizer.py         # AI summarization (Groq / BART / extractive)
├── categorizer.py        # Scoring, categorization, dedup, sentiment
├── report_generator.py   # TXT, HTML, PDF report generation
├── config.py             # Companies, sources, keywords, settings
├── requirements.txt      # Python dependencies
├── .env                  # API keys (never commit)
├── .gitignore            # Protects .env and venv
├── RUN_DASHBOARD.bat     # Double-click to open dashboard
├── RUN_REPORT.bat        # Double-click to generate report
├── reports/              # Generated reports (auto-created)
└── logs/                 # Log files (auto-created)
```

---

## Report Format (TXT)

```
╔════════════════════════════════════════════════════════════════════╗
║           GLOBAL TELECOM OPERATORS DAILY REPORT                   ║
║                    Friday, May 23, 2026                           ║
╚════════════════════════════════════════════════════════════════════╝

──────────────────────────────────────────────────────────────────────
  REGION: MIDDLE EAST & AFRICA  (12 articles)
──────────────────────────────────────────────────────────────────────

  [STC]  — 3 article(s)
  1. ↑ STC announces Q1 2026 earnings beat
     Source : TelecomPaper  |  Score: 24.0  |  Financial Results
     URL    : https://...
     Summary: Saudi Telecom Company reported record Q1 revenue...

══════════════════════════════════════════════════════════════════════
  HIGHLIGHT OF THE DAY
══════════════════════════════════════════════════════════════════════
  BT plans mass layoffs after cutting 8,500 jobs in last year
  Source: LightReading  |  Score: 73.1
```

---

## News Categories

| Category | Keywords |
|----------|----------|
| 5G & Network | 5G, 6G, spectrum, Open RAN, edge computing |
| Fiber & Fixed | FTTH, FTTX, broadband, fiber rollout |
| Mergers & Acquisitions | merger, acquisition, takeover, buyout |
| Financial Results | earnings, revenue, quarterly results, guidance |
| Partnerships | joint venture, agreement, contract |
| Leadership | CEO, CFO, appoint, resign, executive |
| Regulatory | antitrust, fine, license, ruling, compliance |
| Cybersecurity | breach, hack, data leak, security |
| Outage & Incidents | outage, disruption, incident |
| Innovation & AI | AI, machine learning, innovation, digital |
| Subscriber & Market | subscriber, market share, growth, churn |

---

## Troubleshooting

**Dashboard won't open:**
```powershell
streamlit run dashboard.py --server.port 8502   # try a different port
```

**No articles collected:**
- Check internet connection
- Some sources block scrapers — run with specific sources: `--sources lightreading,bloomberg`
- Check `logs/agent_YYYYMMDD.log` for details

**Groq API error:**
- Verify `.env` contains your key: `GROQ_API_KEY=gsk_...`
- Switch to free fallback: set `SUMMARIZER_BACKEND = "extractive"` in `config.py`

**403 errors from article pages:**
- Normal — blocked sites are skipped automatically
- Use `--no-content` flag to skip article page fetching entirely

**PDF export:**
```powershell
pip install weasyprint
# Then add "pdf" to EXPORT_FORMATS in config.py
```

---

## Tracked Companies (37)

### Middle East & Africa (9)
Ooredoo · STC · Etisalat (e&) · Zain · Mobily · du · Orange MEA · MTN · Vodacom

### Europe (8)
Vodafone · Orange · Deutsche Telekom · Telefónica · BT Group · Telecom Italia · Swisscom · KPN

### Americas (6)
Verizon · AT&T · T-Mobile US · América Móvil · Rogers · Bell Canada

### Asia-Pacific (10)
China Mobile · China Telecom · China Unicom · NTT · SoftBank · SK Telecom · Singtel · Telstra · Reliance Jio · Bharti Airtel

---

## License

MIT — use freely, modify as needed.
