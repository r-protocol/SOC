import sqlite3

# Articles that should be re-analyzed
article_ids = [210, 211, 212, 213, 214, 215, 216, 217, 218, 219]

conn = sqlite3.connect('threat_intel.db')
cursor = conn.cursor()

# Reset these articles to UNANALYZED
for article_id in article_ids:
    cursor.execute("""
        UPDATE articles
        SET threat_risk = 'UNANALYZED',
            category = 'Pending Analysis',
            summary = 'Not analyzed - needs re-analysis'
        WHERE id = ?
    """, (article_id,))

conn.commit()
print(f"✓ Reset {cursor.rowcount} articles to UNANALYZED status")

# Show the articles
cursor.execute("""
    SELECT id, title FROM articles WHERE id IN ({})
""".format(','.join('?' * len(article_ids))), article_ids)

print("\nArticles reset for re-analysis:")
for article_id, title in cursor.fetchall():
    print(f"  [{article_id}] {title}")

conn.close()
