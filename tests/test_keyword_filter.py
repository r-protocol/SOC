import sqlite3
import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.filtering import is_article_relevant_keywords

conn = sqlite3.connect('threat_intel.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT id, title, content
    FROM articles
    WHERE id IN (210, 211, 212, 213, 214, 215, 216, 217, 218, 219)
""")

articles = cursor.fetchall()

print("Testing keyword filter on CrowdStrike/Falcon articles:\n")
for article_id, title, content in articles:
    article_dict = {'title': title, 'content': content or ''}
    is_relevant = is_article_relevant_keywords(article_dict)
    status = "✓ RELEVANT" if is_relevant else "✗ NOT RELEVANT"
    print(f"{status} [{article_id}] {title[:80]}")

conn.close()
