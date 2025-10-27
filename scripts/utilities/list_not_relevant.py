import sqlite3
from textwrap import shorten

DB_PATH = 'threat_intel.db'

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""
    SELECT id, title, url, published_date, summary, category
    FROM articles
    WHERE threat_risk = 'NOT_RELEVANT'
    ORDER BY published_date DESC
""")
rows = cur.fetchall()

print(f"\n{'='*100}")
print(f"NOT_RELEVANT Articles: {len(rows)}")
print(f"{'='*100}\n")

for i, (aid, title, url, date, summary, category) in enumerate(rows, 1):
    print(f"{i}. [{aid}] {title}")
    print(f"   Date: {date}")
    print(f"   Category: {category}")
    print(f"   URL: {url}")
    if summary:
        summary_text = summary.replace('\n', ' ').strip()
        print(f"   Summary: {shorten(summary_text, width=200, placeholder='...')}")
    print(f"   {'-'*100}\n")

conn.close()
