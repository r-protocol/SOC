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
