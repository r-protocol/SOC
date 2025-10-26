import sqlite3
from collections import Counter

conn = sqlite3.connect('threat_intel.db')
cursor = conn.cursor()

# Total articles
cursor.execute('SELECT COUNT(*) FROM articles')
total = cursor.fetchone()[0]
print(f"📊 Total articles in database: {total}")

# By threat_risk (not severity)
cursor.execute('SELECT threat_risk, COUNT(*) FROM articles GROUP BY threat_risk')
print("\n📈 By threat risk:")
for row in cursor.fetchall():
    risk = row[0] if row[0] else "None"
    count = row[1]
    percentage = (count / total * 100) if total > 0 else 0
    print(f"  {risk}: {count} ({percentage:.1f}%)")

# By category
cursor.execute('SELECT category, COUNT(*) FROM articles GROUP BY category')
print("\n📂 By category:")
for row in cursor.fetchall():
    cat = row[0] if row[0] else "None"
    count = row[1]
    percentage = (count / total * 100) if total > 0 else 0
    print(f"  {cat}: {count} ({percentage:.1f}%)")

# Recent articles (last 50)
cursor.execute('''
    SELECT title, threat_risk, category, published_date 
    FROM articles 
    ORDER BY published_date DESC 
    LIMIT 50
''')
recent = cursor.fetchall()

print("\n🔍 Recent 50 articles breakdown:")
risk_counts = Counter([r[1] for r in recent])
for risk, count in risk_counts.items():
    risk_name = risk if risk else "None"
    print(f"  {risk_name}: {count}")

print("\n📝 Sample recent articles:")
for i, (title, risk, cat, date) in enumerate(recent[:10], 1):
    risk_display = risk if risk else "None"
    cat_display = cat if cat else "None"
    print(f"{i}. [{risk_display} | {cat_display}] {title[:60]}")

conn.close()
