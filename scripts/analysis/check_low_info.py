import sqlite3

conn = sqlite3.connect('threat_intel.db')
cursor = conn.cursor()

print('\n=== LOW RISK ARTICLES ===')
cursor.execute('SELECT title, published_date, category FROM articles WHERE threat_risk = "LOW"')
for r in cursor.fetchall():
    print(f'\nTitle: {r[0]}')
    print(f'Date: {r[1]}')
    print(f'Category: {r[2]}')

print('\n\n=== INFORMATIONAL ARTICLES ===')
cursor.execute('SELECT title, published_date, category FROM articles WHERE threat_risk = "INFORMATIONAL"')
for r in cursor.fetchall():
    print(f'\nTitle: {r[0]}')
    print(f'Date: {r[1]}')
    print(f'Category: {r[2]}')

print('\n\n=== Sample of MEDIUM RISK ARTICLES (first 5) ===')
cursor.execute('SELECT title, category FROM articles WHERE threat_risk = "MEDIUM" LIMIT 5')
for r in cursor.fetchall():
    print(f'\nTitle: {r[0]}')
    print(f'Category: {r[1]}')

conn.close()
