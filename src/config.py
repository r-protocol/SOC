# config.py
import datetime

RSS_FEEDS = [
    # Major News Sites
    "https://www.bleepingcomputer.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.darkreading.com/rss_simple.asp",
    "https://threatpost.com/feed/",
    "https://krebsonsecurity.com/feed/",
    "https://feeds.feedburner.com/Securityweek",
    "https://www.cybersecuritydive.com/feeds/news/",
    
    # Vendor Security Blogs
    "https://msrc.microsoft.com/blog/rss/",
    "https://security.googleblog.com/feeds/posts/default",
    "https://blog.talosintelligence.com/feeds/posts/default",
    "https://unit42.paloaltonetworks.com/feed/",
    "https://news.sophos.com/en-us/feed/",
    "https://blog.malwarebytes.com/feed/",
    "https://www.fortinet.com/blog/rss",
    "https://www.crowdstrike.com/blog/feed/",
    "https://www.rapid7.com/blog/rss/",
    "https://feeds.trendmicro.com/TrendMicroResearch",
    "https://blog.checkpoint.com/feed/",
    "https://www.proofpoint.com/us/rss.xml",
    "https://nakedsecurity.sophos.com/feed/",
    
    # Government & CERT
    "https://www.cisa.gov/cybersecurity-advisories.xml",
    "https://www.ncsc.gov.uk/api/1/services/v1/news-rss-feed.xml",
    "https://cert.europa.eu/publications/security-advisories/feed.xml",
    "https://isc.sans.edu/rssfeed_full.xml",
    "https://attack.mitre.org/resources/rss.xml",
    
    # Threat Intelligence & Research
    "https://redcanary.com/feed/",
    "https://darktrace.com/en/blog/rss",
    "https://www.trellix.com/en-us/about/newsroom/rss.xml",
    "https://www.elastic.co/security-labs/feed.xml",
    "https://www.welivesecurity.com/feed/",
    "https://www.bitdefender.com/blog/labs/feed/",
    "https://securelist.com/feed/",
    "https://www.intezer.com/blog/feed/",
    "https://www.sentinelone.com/feed/",
    "https://www.mandiant.com/resources/rss",
    
    # Tech News Security
    "https://feeds.arstechnica.com/arstechnica/security",
    "https://www.wired.com/feed/category/security/latest/rss",
    "https://www.zdnet.com/topic/security/rss.xml",
    "https://www.infosecurity-magazine.com/rss/news/",
    "https://www.csoonline.com/index.rss",
    "https://securityaffairs.com/feed",
    "https://www.zdnet.com/blog/feeds/rss.xml",
    
    # Enterprise Security
    "https://logrhythm.com/blog/feed/",
    "https://www.splunk.com/en_us/blog/security/_jcr_content.feed",
    "https://blogs.blackberry.com/en/rss",
    "https://www.cyberark.com/resources/rss.xml",
    "https://www.tenable.com/blog/feed",
    "https://sec.okta.com/feed.xml",
    "https://blog.1password.com/rss/"
]
DATABASE_PATH = "threat_intel.db"
OLLAMA_MODEL = "deepseek-coder-v2:16b"  # Specialized coding model - better for IOC extraction & KQL
OLLAMA_HOST = "http://localhost:11434"
TEMPLATE_DOCX_PATH = "template.docx"
OUTPUT_DOCX_PATH = f"Threat_Intelligence_Report_{datetime.date.today()}.docx"

# Fetcher Settings
FETCH_DAYS_BACK = 14  # How many days back to fetch articles (2 weeks rolling window)
MIN_ARTICLE_LENGTH = 100  # Minimum content length in characters (lowered from 200)
FETCH_TIMEOUT = 30  # Request timeout in seconds for article fetching
SOCKET_TIMEOUT = 30  # Socket timeout in seconds for RSS feed parsing

# KQL Generator Settings
ENABLE_KQL_GENERATION = True
KQL_EXPORT_DIR = "kql_queries"
KQL_EXPORT_ENABLED = True
KQL_TIMEFRAME_DAYS = 30  # Default lookback period for queries

# LLM-Enhanced KQL Settings
KQL_USE_LLM = True  # Use LLM for IOC extraction and query generation (recommended)
KQL_LLM_TEMPERATURE = 0.2  # Lower = more consistent structured output
KQL_LLM_TIMEOUT = 120  # Timeout in seconds for LLM queries
KQL_CONFIDENCE_THRESHOLD = 'medium'  # Filter IOCs: 'low', 'medium', 'high'
KQL_FALLBACK_TO_REGEX = True  # Use regex if LLM fails (recommended)

# IOC Extraction Settings
AUTO_EXTRACT_IOCS = True  # Automatically extract IOCs during analysis (without requiring KQL generation)
EXTRACT_IOCS_FOR_RISK_LEVELS = ['HIGH', 'MEDIUM']  # Only extract IOCs for these risk levels (set to [] for all)
