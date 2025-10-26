import sqlite3

conn = sqlite3.connect('threat_intel.db')
cursor = conn.cursor()

print('\n=== RECENT HIGH RISK ARTICLES (Last 10) ===')
cursor.execute('''SELECT title, published_date, category, summary 
                  FROM articles 
                  WHERE threat_risk = "HIGH" 
                  ORDER BY published_date DESC 
                  LIMIT 10''')
for idx, r in enumerate(cursor.fetchall(), 1):
    print(f'\n{idx}. {r[0]}')
    print(f'   Date: {r[1]}')
    print(f'   Category: {r[2]}')
    if r[3]:
        print(f'   Summary: {r[3][:200]}...')

conn.close()
