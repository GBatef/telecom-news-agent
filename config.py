"""
config.py - Central configuration for Global Telecom Operators News AI Agent
"""

from dataclasses import dataclass, field
from typing import List, Dict

# ─────────────────────────────────────────────
#  Company Definitions
# ─────────────────────────────────────────────

@dataclass
class Company:
    name: str
    region: str
    country: str
    aliases: List[str] = field(default_factory=list)
    ticker: str = ""
    ir_page: str = ""


COMPANIES: List[Company] = [
    # ── Middle East & Africa ──────────────────
    Company(
        name="Ooredoo",
        region="Middle East & Africa",
        country="Qatar",
        aliases=["Ooredoo Group", "Qatar Telecom", "QTel", "اوريدو"],
        ticker="ORDS.QA",
        ir_page="https://www.ooredoo.com/en/media/news/",
    ),
    Company(
        name="STC",
        region="Middle East & Africa",
        country="Saudi Arabia",
        aliases=[
            "Saudi Telecom Company",
            "Saudi Telecom",
            "الاتصالات السعودية",
            "STC Group",
            "stc",
        ],
        ticker="7010.SR",
        ir_page="https://www.stc.com.sa/wps/wcm/connect/english/individual/individual",
    ),
    Company(
        name="Etisalat",
        region="Middle East & Africa",
        country="UAE",
        aliases=["e&", "Emirates Telecommunications", "e& Group", "اتصالات"],
        ticker="ETISALAT.AD",
        ir_page="https://www.etisalat.com/en/about/media-centre/press-releases.html",
    ),
    Company(
        name="Zain",
        region="Middle East & Africa",
        country="Kuwait",
        aliases=["Zain Group", "Zain Telecom", "MTC", "زين"],
        ticker="ZAIN.KW",
        ir_page="https://www.zain.com/en/media-center/",
    ),
    Company(
        name="Mobily",
        region="Middle East & Africa",
        country="Saudi Arabia",
        aliases=["Etihad Etisalat", "موبايلي"],
        ticker="7020.SR",
        ir_page="https://www.mobily.com.sa/en/about-mobily/media-center/press-releases",
    ),
    Company(
        name="du",
        region="Middle East & Africa",
        country="UAE",
        aliases=["du Telecom", "EITC", "Emirates Integrated Telecommunications"],
        ticker="DU.AD",
        ir_page="https://www.du.ae/en/about/media-centre",
    ),
    Company(
        name="Orange MEA",
        region="Middle East & Africa",
        country="France/Africa",
        aliases=["Orange Middle East", "Orange Africa", "Orange MEA"],
        ticker="ORA.PA",
    ),
    Company(
        name="MTN",
        region="Middle East & Africa",
        country="South Africa",
        aliases=["MTN Group", "MTN Nigeria", "MTN Ghana"],
        ticker="MTN.JSE",
        ir_page="https://www.mtn.com/news/",
    ),
    Company(
        name="Vodacom",
        region="Middle East & Africa",
        country="South Africa",
        aliases=["Vodacom Group"],
        ticker="VOD.JSE",
        ir_page="https://www.vodacom.com/news-media.php",
    ),
    # ── Europe ────────────────────────────────
    Company(
        name="Vodafone",
        region="Europe",
        country="UK",
        aliases=["Vodafone Group", "Vodafone UK", "Vodafone Germany"],
        ticker="VOD.L",
        ir_page="https://newsroom.vodafone.com/",
    ),
    Company(
        name="Orange",
        region="Europe",
        country="France",
        aliases=["Orange France", "France Telecom", "Orange Group"],
        ticker="ORA.PA",
        ir_page="https://www.orange.com/en/newsroom/press-releases",
    ),
    Company(
        name="Deutsche Telekom",
        region="Europe",
        country="Germany",
        aliases=["T-Mobile", "T-Mobile Europe", "DT", "Deutsche Telekom AG"],
        ticker="DTE.DE",
        ir_page="https://www.telekom.com/en/media/media-information",
    ),
    Company(
        name="Telefónica",
        region="Europe",
        country="Spain",
        aliases=["Telefonica", "Movistar", "O2", "Telefónica Group"],
        ticker="TEF.MC",
        ir_page="https://www.telefonica.com/en/communication-room/press-room/press-releases/",
    ),
    Company(
        name="BT Group",
        region="Europe",
        country="UK",
        aliases=["British Telecom", "BT", "EE"],
        ticker="BT.L",
        ir_page="https://newsroom.bt.com/",
    ),
    Company(
        name="Telecom Italia",
        region="Europe",
        country="Italy",
        aliases=["TIM", "TIM Group", "Telecom Italia Group"],
        ticker="TELECOM.MI",
        ir_page="https://www.gruppotim.it/en/media/press-releases.html",
    ),
    Company(
        name="Swisscom",
        region="Europe",
        country="Switzerland",
        aliases=["Swisscom AG"],
        ticker="SCMN.SW",
        ir_page="https://www.swisscom.ch/en/about/news/media-releases.html",
    ),
    Company(
        name="KPN",
        region="Europe",
        country="Netherlands",
        aliases=["KPN Group", "Koninklijke KPN"],
        ticker="KPN.AS",
        ir_page="https://over.kpn.com/en/news/press-releases/",
    ),
    # ── Americas ──────────────────────────────
    Company(
        name="Verizon",
        region="Americas",
        country="USA",
        aliases=["Verizon Communications", "Verizon Wireless"],
        ticker="VZ",
        ir_page="https://www.verizon.com/about/news/",
    ),
    Company(
        name="AT&T",
        region="Americas",
        country="USA",
        aliases=["AT&T Inc", "AT&T Communications"],
        ticker="T",
        ir_page="https://about.att.com/news/",
    ),
    Company(
        name="T-Mobile US",
        region="Americas",
        country="USA",
        aliases=["T-Mobile USA", "TMUS"],
        ticker="TMUS",
        ir_page="https://newsroom.t-mobile.com/",
    ),
    Company(
        name="América Móvil",
        region="Americas",
        country="Mexico",
        aliases=["America Movil", "Telcel", "Claro", "Carlos Slim"],
        ticker="AMX",
        ir_page="https://www.americamovil.com/English/press/default.aspx",
    ),
    Company(
        name="Rogers",
        region="Americas",
        country="Canada",
        aliases=["Rogers Communications", "Rogers Wireless"],
        ticker="RCI",
        ir_page="https://about.rogers.com/news/",
    ),
    Company(
        name="Bell Canada",
        region="Americas",
        country="Canada",
        aliases=["Bell", "BCE", "Bell Mobility"],
        ticker="BCE",
        ir_page="https://www.bell.ca/en/news",
    ),
    # ── Asia-Pacific ──────────────────────────
    Company(
        name="China Mobile",
        region="Asia-Pacific",
        country="China",
        aliases=["中国移动", "CMCC"],
        ticker="0941.HK",
        ir_page="https://www.chinamobileltd.com/en/media/prdetail.php",
    ),
    Company(
        name="China Telecom",
        region="Asia-Pacific",
        country="China",
        aliases=["中国电信"],
        ticker="0728.HK",
        ir_page="https://www.chinatelecom-h.com/en/news/index.html",
    ),
    Company(
        name="China Unicom",
        region="Asia-Pacific",
        country="China",
        aliases=["中国联通"],
        ticker="0762.HK",
        ir_page="https://www.chinaunicom.com.hk/en/news/index.html",
    ),
    Company(
        name="NTT",
        region="Asia-Pacific",
        country="Japan",
        aliases=["NTT Group", "NTT Docomo", "Nippon Telegraph"],
        ticker="9432.T",
        ir_page="https://group.ntt/en/newsrelease/",
    ),
    Company(
        name="SoftBank",
        region="Asia-Pacific",
        country="Japan",
        aliases=["SoftBank Corp", "SoftBank Group"],
        ticker="9434.T",
        ir_page="https://www.softbank.jp/en/corp/news/",
    ),
    Company(
        name="SK Telecom",
        region="Asia-Pacific",
        country="South Korea",
        aliases=["SKT", "SK텔레콤"],
        ticker="017670.KS",
        ir_page="https://news.sktelecom.com/en",
    ),
    Company(
        name="Singtel",
        region="Asia-Pacific",
        country="Singapore",
        aliases=["Singapore Telecommunications", "Singtel Group"],
        ticker="Z74.SI",
        ir_page="https://www.singtel.com/about-us/media-centre/news-releases",
    ),
    Company(
        name="Telstra",
        region="Asia-Pacific",
        country="Australia",
        aliases=["Telstra Corporation"],
        ticker="TLS.AX",
        ir_page="https://exchange.telstra.com.au/media-releases/",
    ),
    Company(
        name="Reliance Jio",
        region="Asia-Pacific",
        country="India",
        aliases=["Jio", "Jio Platforms", "RIL Telecom"],
        ticker="RELIANCE.NS",
        ir_page="https://www.jio.com/en-in/press-release/",
    ),
    Company(
        name="Bharti Airtel",
        region="Asia-Pacific",
        country="India",
        aliases=["Airtel", "Airtel India"],
        ticker="BHARTIARTL.NS",
        ir_page="https://www.airtel.in/press-release/",
    ),
]

# ─────────────────────────────────────────────
#  Regions
# ─────────────────────────────────────────────

REGIONS = ["Middle East & Africa", "Europe", "Americas", "Asia-Pacific"]

# ─────────────────────────────────────────────
#  News Sources
# ─────────────────────────────────────────────

@dataclass
class NewsSource:
    name: str
    base_url: str
    rss_url: str = ""
    scrape_url: str = ""
    region: str = "Global"
    credibility_score: float = 0.8  # 0.0 – 1.0
    language: str = "en"


NEWS_SOURCES: List[NewsSource] = [
    # ── Global Telecom ────────────────────────
    NewsSource(
        name="TelecomPaper",
        base_url="https://www.telecompaper.com",
        rss_url="https://www.telecompaper.com/rss/all-rss",
        credibility_score=0.9,
    ),
    NewsSource(
        name="FierceWireless",
        base_url="https://www.fiercewireless.com",
        rss_url="https://www.fiercewireless.com/rss/xml",
        credibility_score=0.85,
    ),
    NewsSource(
        name="LightReading",
        base_url="https://www.lightreading.com",
        rss_url="https://www.lightreading.com/rss.xml",
        credibility_score=0.85,
    ),
    NewsSource(
        name="CapacityMedia",
        base_url="https://www.capacitymedia.com",
        rss_url="https://www.capacitymedia.com/rss.xml",
        credibility_score=0.8,
    ),
    NewsSource(
        name="TeleGeography",
        base_url="https://www.telegeography.com",
        rss_url="https://www.telegeography.com/feeds/news/",
        credibility_score=0.9,
    ),
    NewsSource(
        name="RCR Wireless",
        base_url="https://www.rcrwireless.com",
        rss_url="https://www.rcrwireless.com/feed",
        credibility_score=0.8,
    ),
    NewsSource(
        name="Mobile World Live",
        base_url="https://www.mobileworldlive.com",
        rss_url="https://www.mobileworldlive.com/feed/",
        credibility_score=0.85,
    ),
    # ── Financial News ────────────────────────
    NewsSource(
        name="Reuters Technology",
        base_url="https://www.reuters.com",
        rss_url="https://www.reuters.com/technology/rss",
        credibility_score=0.95,
    ),
    NewsSource(
        name="Bloomberg Technology",
        base_url="https://www.bloomberg.com",
        rss_url="https://feeds.bloomberg.com/technology/news.rss",
        credibility_score=0.95,
    ),
    # ── Middle East Specific ──────────────────
    NewsSource(
        name="Zawya",
        base_url="https://www.zawya.com",
        rss_url="https://www.zawya.com/mena/en/rss/",
        region="Middle East & Africa",
        credibility_score=0.85,
    ),
    NewsSource(
        name="Arabian Business",
        base_url="https://www.arabianbusiness.com",
        rss_url="https://www.arabianbusiness.com/rss",
        region="Middle East & Africa",
        credibility_score=0.8,
    ),
    NewsSource(
        name="Telecom Review",
        base_url="https://www.telecomreview.com",
        rss_url="https://www.telecomreview.com/feed/",
        region="Middle East & Africa",
        credibility_score=0.8,
    ),
    # ── Company IR pages (RSS/atom where available) ──
    NewsSource(
        name="Ooredoo Newsroom",
        base_url="https://www.ooredoo.com",
        scrape_url="https://www.ooredoo.com/en/media/news/",
        region="Middle East & Africa",
        credibility_score=1.0,
    ),
    NewsSource(
        name="Vodafone Newsroom",
        base_url="https://www.vodafone.com",
        scrape_url="https://www.vodafone.com/news-and-media",
        region="Europe",
        credibility_score=1.0,
    ),
    NewsSource(
        name="Deutsche Telekom Newsroom",
        base_url="https://www.telekom.com",
        rss_url="https://www.telekom.com/en/media/rss-feeds",
        region="Europe",
        credibility_score=1.0,
    ),
    NewsSource(
        name="Verizon Newsroom",
        base_url="https://www.verizon.com",
        scrape_url="https://www.verizon.com/about/news/",
        region="Americas",
        credibility_score=1.0,
    ),
    NewsSource(
        name="T-Mobile Newsroom",
        base_url="https://newsroom.t-mobile.com",
        rss_url="https://newsroom.t-mobile.com/feed/",
        region="Americas",
        credibility_score=1.0,
    ),
]

# ─────────────────────────────────────────────
#  Important Keywords & Scoring
# ─────────────────────────────────────────────

# Weight: higher = more important
IMPORTANCE_KEYWORDS: Dict[str, float] = {
    # Deals
    "merger": 10.0,
    "acquisition": 10.0,
    "takeover": 9.5,
    "buyout": 9.0,
    "joint venture": 8.5,
    "partnership": 7.0,
    # Financial
    "earnings": 8.0,
    "revenue": 7.5,
    "profit": 7.0,
    "ipo": 9.0,
    "dividend": 6.5,
    "guidance": 7.0,
    "quarterly results": 8.0,
    "annual results": 8.5,
    "full year results": 8.5,
    # Technology
    "5g": 8.0,
    "6g": 9.0,
    "fiber": 7.0,
    "fttx": 7.0,
    "ftth": 7.5,
    "network slicing": 7.0,
    "open ran": 7.5,
    "openran": 7.5,
    "edge computing": 6.5,
    "ai": 6.0,
    "spectrum": 7.5,
    "spectrum auction": 8.5,
    "license": 6.5,
    # Strategy
    "launch": 6.0,
    "rollout": 6.5,
    "expansion": 6.0,
    "layoffs": 7.5,
    "restructuring": 7.5,
    "ceo": 7.0,
    "leadership": 6.0,
    "regulatory": 7.0,
    "antitrust": 8.0,
    "fine": 6.5,
    "breach": 8.0,
    "outage": 7.5,
}

NEWS_CATEGORIES = {
    "5G & Network": ["5g", "6g", "network", "spectrum", "open ran", "openran", "network slicing", "edge computing"],
    "Fiber & Fixed": ["fiber", "fttx", "ftth", "broadband", "fixed line", "fixed broadband"],
    "Mergers & Acquisitions": ["merger", "acquisition", "takeover", "buyout", "deal", "purchase"],
    "Financial Results": ["earnings", "revenue", "profit", "loss", "quarterly", "annual", "results", "guidance"],
    "Partnerships": ["partnership", "joint venture", "collaboration", "agreement", "contract"],
    "Leadership": ["ceo", "cfo", "cto", "appoint", "resign", "leadership", "executive"],
    "Regulatory": ["regulatory", "antitrust", "fine", "license", "ruling", "compliance"],
    "Cybersecurity": ["breach", "hack", "security", "cyber", "data leak"],
    "Outage & Incidents": ["outage", "down", "disruption", "incident"],
    "Innovation & AI": ["ai", "artificial intelligence", "machine learning", "innovation", "digital"],
    "Subscriber & Market": ["subscriber", "customer", "market share", "growth", "churn"],
}

SENTIMENT_POSITIVE_WORDS = [
    "profit", "growth", "record", "launch", "success", "award", "expand",
    "strong", "beat", "exceed", "win", "partnership", "upgrade", "positive",
]
SENTIMENT_NEGATIVE_WORDS = [
    "loss", "decline", "fall", "drop", "fine", "breach", "outage", "layoff",
    "cut", "resign", "miss", "fail", "concern", "risk", "down",
]

# ─────────────────────────────────────────────
#  Scheduling
# ─────────────────────────────────────────────

SCHEDULE_TIME = "07:00"          # Daily run time (local time)
REPORT_OUTPUT_DIR = "reports"    # Directory for report files
LOG_DIR = "logs"                 # Directory for log files

# ─────────────────────────────────────────────
#  HTTP / Scraping Settings
# ─────────────────────────────────────────────

REQUEST_TIMEOUT = 30            # seconds
MAX_RETRIES = 3
RETRY_DELAY = 5                 # seconds between retries
MAX_ARTICLES_PER_SOURCE = 50    # max articles to fetch per source

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# ─────────────────────────────────────────────
#  AI / Summarization Settings
# ─────────────────────────────────────────────

# Options: "groq" (free API) | "extractive" (instant, no download)
#           "local" (BART, ~1.6GB) | "claude" (Anthropic API) | "none"
SUMMARIZER_BACKEND = "groq"

# For "local" backend
LOCAL_SUMMARIZER_MODEL = "facebook/bart-large-cnn"
SUMMARY_MAX_LENGTH = 150
SUMMARY_MIN_LENGTH = 40

# For "groq" backend — set via environment variable GROQ_API_KEY or .env file
# Free models: llama-3.1-8b-instant (fastest) | llama-3.3-70b-versatile (best quality)
GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_MAX_TOKENS = 200

# For "claude" backend — set via environment variable ANTHROPIC_API_KEY
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
CLAUDE_MAX_TOKENS = 200

# Deduplication similarity threshold (0.0 – 1.0)
DEDUP_THRESHOLD = 0.85

# ─────────────────────────────────────────────
#  Email Settings (optional)
# ─────────────────────────────────────────────

EMAIL_ENABLED = False
EMAIL_FROM = "telecom-agent@example.com"
EMAIL_TO: List[str] = []
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# ─────────────────────────────────────────────
#  Export Settings
# ─────────────────────────────────────────────

EXPORT_FORMATS = ["txt", "html"]   # Add "pdf" if weasyprint is installed
