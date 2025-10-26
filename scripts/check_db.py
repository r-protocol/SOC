import sqlite3

conn = sqlite3.connect('threat_intel.db')
cursor = conn.cursor()

# Get recent articles
cursor.execute('SELECT title, threat_risk, published_date FROM articles ORDER BY published_date DESC LIMIT 30')
results = cursor.fetchall()

print('\n--- Recent 30 Articles ---')
for r in results:
    date = r[2][:10] if r[2] else "N/A"
    risk = r[1] if r[1] else "NONE"
    title = r[0][:70] if r[0] else "No title"
    print(f'{date:10} | {risk:15} | {title}')

# Get risk distribution
cursor.execute('SELECT threat_risk, COUNT(*) FROM articles GROUP BY threat_risk')
risk_counts = cursor.fetchall()

print('\n\n--- Risk Level Distribution (All Articles) ---')
for r in risk_counts:
    print(f'{r[0]}: {r[1]}')

# Get date range
cursor.execute('SELECT MIN(published_date), MAX(published_date), COUNT(*) FROM articles')
date_info = cursor.fetchone()
print(f'\n--- Database Stats ---')
print(f'Total articles: {date_info[2]}')
print(f'Date range: {date_info[0][:10] if date_info[0] else "N/A"} to {date_info[1][:10] if date_info[1] else "N/A"}')

conn.close()
