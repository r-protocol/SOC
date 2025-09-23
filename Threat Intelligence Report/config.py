# config.py
import datetime

# --- CONFIGURATION ---
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

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/109.0 Safari/537.36',
]
# --- END OF CONFIGURATION ---