import sqlite3
from textwrap import shorten

DB_PATH = 'threat_intel.db'

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""
    SELECT id, title, url, published_date
    FROM articles
    WHERE threat_risk = 'UNANALYZED' OR category = 'Pending Analysis'
    ORDER BY published_date DESC
""")
rows = cur.fetchall()
print(f"UNANALYZED: {len(rows)}")
for i, (aid, title, url, date) in enumerate(rows, 1):
    title_disp = shorten(title or '', width=100, placeholder='...')
    print(f"{i}. [{aid}] {title_disp} | {date}\n   {url}")
conn.close()
