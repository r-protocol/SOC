# config.py
import datetime

RSS_FEEDS = [
    "https://www.bleepingcomputer.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.darkreading.com/rss_simple.asp",
    "https://threatpost.com/feed/",
    "https://krebsonsecurity.com/feed/"
]
DATABASE_PATH = "threat_intel.db"
OLLAMA_MODEL = "llama3"
OLLAMA_HOST = "http://localhost:11434"
TEMPLATE_DOCX_PATH = "template.docx"
OUTPUT_DOCX_PATH = f"Threat_Intelligence_Report_{datetime.date.today()}.docx"

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
